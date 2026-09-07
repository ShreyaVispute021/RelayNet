from python.relaynet.knowledge_graph_query import KnowledgeGraphQuery
from python.relaynet.contextual_reasoner import ContextualReasoner


class KGRRelaySelector:
    """
    Knowledge-Graph-based relay selector with contextual reasoning.

    Pipeline:

        Temporal KG
            ↓
        Temporal relay states
            ↓
        Contextual reasoning
            ↓
        Relay recommendation
            ↓
        Adaptive relay selection
    """

    def __init__(self, kg_csv_path):
        self.kg_csv_path = kg_csv_path

        self.query = KnowledgeGraphQuery(
            kg_csv_path
        )

        self.reasoner = ContextualReasoner()

    def select_relay(self, time_step):
        """
        Select the best relay using contextual KG reasoning.

        Returns:
            relay_id, contextual_score
        """

        ranking = self.get_ranking(
            time_step
        )

        if not ranking:
            return None, 0.0

        for relay in ranking:

            if relay["recommendation"] != "AVOID":

                return (
                    relay["relay_id"],
                    relay["contextual_score"]
                )

        return None, 0.0

    def get_ranking(self, time_step):
        """
        Retrieve temporal relay states from the KG,
        analyze them contextually, and rank them.
        """

        states = self.query.get_available_relay_states(
            time_step
        )

        if not states:
            return []

        return self.reasoner.rank_relays(
            states
        )

    def explain_relay(self, relay_id, time_step):
        """
        Generate contextual reasoning for one relay.
        """

        state = self.query.get_state(
            relay_id,
            time_step
        )

        if state is None:
            return None

        state_data = {
            "relay_id": relay_id,
            "rssi": float(
                state["HAS_RSSI"]
            ),
            "battery": float(
                state["HAS_BATTERY"]
            ),
            "queue_length": int(
                state["HAS_QUEUE_LENGTH"]
            ),
            "mobility": float(
                state["HAS_MOBILITY"]
            ),
            "link_stability": float(
                state["HAS_LINK_STABILITY"]
            ),
            "hop_count": int(
                state["HAS_HOP_COUNT"]
            )
        }

        return self.reasoner.analyze(
            state_data
        )