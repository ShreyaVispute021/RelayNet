def calculate_relay_score(node):
    """
    Calculate a baseline relay score.

    Higher score = better relay candidate.
    """

    # Normalize RSSI.
    # Typical values are negative, so -40 is better than -80.
    rssi_score = (node.rssi + 100) / 60
    rssi_score = max(0, min(1, rssi_score))

    # Battery is already represented as a percentage.
    battery_score = node.battery / 100

    # Smaller queue is better.
    queue_score = 1 - min(node.queue_length / 20, 1)

    # Lower mobility is preferred for a more stable relay.
    mobility_score = 1 - min(node.mobility, 1)

    # Link stability is already between 0 and 1.
    stability_score = node.link_stability

    # Fewer hops are preferred.
    hop_score = 1 - min(node.hop_count / 10, 1)

    # Weighted baseline score.
    score = (
        0.25 * rssi_score
        + 0.20 * battery_score
        + 0.15 * queue_score
        + 0.10 * mobility_score
        + 0.20 * stability_score
        + 0.10 * hop_score
    )

    return score


def select_best_relay(relays):
    """
    Select the highest-scoring available relay.
    """

    available_relays = [
        relay for relay in relays
        if relay.is_available()
    ]

    if not available_relays:
        return None, 0.0

    scored_relays = [
        (relay, calculate_relay_score(relay))
        for relay in available_relays
    ]

    best_relay, best_score = max(
        scored_relays,
        key=lambda item: item[1]
    )

    return best_relay, best_score


def select_static_relay(relays):
    """Traditional fixed hop-count baseline without context or learning."""

    available_relays = [relay for relay in relays if relay.is_available()]
    if not available_relays:
        return None, 0.0

    relay = min(
        available_relays,
        key=lambda item: (item.hop_count, item.node_id),
    )
    return relay, 1.0 / max(relay.hop_count, 1)


def relay_to_context_state(relay):
    """Convert a live relay object into the state schema used by the KG."""

    return {
        "relay_id": relay.node_id,
        "rssi": relay.rssi,
        "battery": relay.battery,
        "queue_length": relay.queue_length,
        "mobility": relay.mobility,
        "link_stability": relay.link_stability,
        "hop_count": relay.hop_count,
    }


def select_contextual_relay(relays, reasoner=None):
    """Select a live relay using the KG contextual reasoning rules.

    The live network attributes are represented with the same state schema
    stored in the temporal Knowledge Graph.  Relays are then classified as
    PREFER, CAUTION, or AVOID and ranked by contextual score.

    Returns:
        relay, contextual_score, analysis
    """

    if reasoner is None:
        from python.relaynet.contextual_reasoner import ContextualReasoner

        reasoner = ContextualReasoner()

    available_relays = {
        relay.node_id: relay
        for relay in relays
        if relay.is_available()
    }

    if not available_relays:
        return None, 0.0, None

    states = [
        relay_to_context_state(relay)
        for relay in available_relays.values()
    ]
    ranking = reasoner.rank_relays(states)

    for analysis in ranking:
        if analysis["recommendation"] == "AVOID":
            continue

        relay = available_relays[analysis["relay_id"]]
        return relay, analysis["contextual_score"], analysis

    # Emergency fallback: when every operational relay is degraded, use the
    # highest-ranked AVOID relay rather than dropping the packet immediately.
    # The warning remains available in the returned analysis.
    fallback = ranking[0]
    relay = available_relays[fallback["relay_id"]]
    return relay, fallback["contextual_score"], fallback


def select_relay_from_kg(relays, kg_graph, time_step):
    """
    Select an available relay using the Knowledge Graph.

    The KG provides the temporal relay ranking, while the
    current network objects are used to ensure that the
    selected relay is currently available.
    """

    available_relays = {
        relay.node_id: relay
        for relay in relays
        if relay.is_available()
    }

    if not available_relays:
        return None, 0.0

    ranking = kg_graph.get_relay_ranking(time_step)

    for kg_relay in ranking:
        relay_id = kg_relay["relay_id"]

        if relay_id in available_relays:
            relay = available_relays[relay_id]
            kg_score = kg_relay["score"]

            return relay, kg_score

    return None, 0.0
