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