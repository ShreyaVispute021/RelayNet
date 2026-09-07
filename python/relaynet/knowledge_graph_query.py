import csv


class KnowledgeGraphQuery:
    """
    Query interface for the RelayNet temporal Knowledge Graph.

    Supports both:
    1. Raw temporal relay-state knowledge.
    2. Derived contextual reasoning knowledge.
    """

    def __init__(self, csv_path):
        self.triples = []

        with open(csv_path, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                self.triples.append(
                    (
                        row["subject"],
                        row["predicate"],
                        row["object"]
                    )
                )

    def find(
        self,
        subject=None,
        predicate=None,
        object_value=None
    ):
        results = []

        for (
            subject_value,
            predicate_value,
            object_result
        ) in self.triples:

            if (
                subject is not None
                and subject_value != subject
            ):
                continue

            if (
                predicate is not None
                and predicate_value != predicate
            ):
                continue

            if (
                object_value is not None
                and object_result != object_value
            ):
                continue

            results.append(
                (
                    subject_value,
                    predicate_value,
                    object_result
                )
            )

        return results

    # ------------------------------------------------------
    # Existing temporal-state queries
    # ------------------------------------------------------

    def get_relay_states(self, relay_id):
        relay = f"Relay:{relay_id}"

        state_triples = self.find(
            subject=relay,
            predicate="HAS_STATE"
        )

        return [
            triple[2]
            for triple in state_triples
        ]

    def get_state(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state
        )

        if not triples:
            return None

        state_data = {}

        for _, predicate, object_value in triples:
            state_data[predicate] = object_value

        return state_data

    def get_available_relays(self, time_step=None):
        relays = []

        if time_step is None:
            available_triples = self.find(
                predicate="AVAILABLE",
                object_value="True"
            )

            for subject, _, _ in available_triples:
                if subject.startswith("State:"):
                    relay_id = subject.split(":")[1]

                    if relay_id not in relays:
                        relays.append(relay_id)

        else:
            for subject, _, _ in self.find(
                predicate="AVAILABLE",
                object_value="True"
            ):
                if subject == subject and subject.startswith("State:"):
                    parts = subject.split(":")

                    if len(parts) != 3:
                        continue

                    relay_id = parts[1]
                    state_time = parts[2]

                    if state_time == f"T{time_step}":
                        if relay_id not in relays:
                            relays.append(relay_id)

        return relays

    def get_available_relay_states(self, time_step):
        states = []

        available_relays = self.get_available_relays(
            time_step
        )

        for relay_id in available_relays:
            state = self.get_state(
                relay_id,
                time_step
            )

            if state is None:
                continue

            states.append(
                {
                    "relay_id": relay_id,
                    "rssi": float(state["HAS_RSSI"]),
                    "battery": float(state["HAS_BATTERY"]),
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
                    ),
                    "score": float(
                        state["HAS_SCORE"]
                    ),
                    "available": (
                        state["AVAILABLE"] == "True"
                    ),
                    "selected": (
                        state["SELECTED"] == "True"
                    )
                }
            )

        return states

    def get_selected_relays(self, time_step=None):
        relays = []

        selected_triples = self.find(
            predicate="SELECTED",
            object_value="True"
        )

        for subject, _, _ in selected_triples:
            if not subject.startswith("State:"):
                continue

            parts = subject.split(":")

            if len(parts) != 3:
                continue

            relay_id = parts[1]
            state_time = parts[2]

            if (
                time_step is None
                or state_time == f"T{time_step}"
            ):
                relays.append(relay_id)

        return relays

    def get_relay_ranking(self, time_step):
        states = self.get_available_relay_states(
            time_step
        )

        return sorted(
            states,
            key=lambda state: state["score"],
            reverse=True
        )

    def get_best_relay(self, time_step):
        ranking = self.get_relay_ranking(
            time_step
        )

        if not ranking:
            return None

        return ranking[0]

    # ------------------------------------------------------
    # Derived contextual knowledge queries
    # ------------------------------------------------------

    def get_contexts(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state,
            predicate="HAS_CONTEXT"
        )

        return [
            triple[2]
            for triple in triples
        ]

    def get_recommendation(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state,
            predicate="HAS_RECOMMENDATION"
        )

        if not triples:
            return None

        return triples[0][2]

    def get_contextual_score(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state,
            predicate="HAS_CONTEXTUAL_SCORE"
        )

        if not triples:
            return None

        return float(triples[0][2])

    def get_reasons(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state,
            predicate="HAS_REASON"
        )

        return [
            triple[2]
            for triple in triples
        ]

    def get_warnings(self, relay_id, time_step):
        state = f"State:{relay_id}:T{time_step}"

        triples = self.find(
            subject=state,
            predicate="HAS_WARNING"
        )

        return [
            triple[2]
            for triple in triples
        ]

    def get_contextual_knowledge(
        self,
        relay_id,
        time_step
    ):
        """
        Retrieve all derived contextual knowledge for
        a relay at a specific time step.
        """

        return {
            "relay_id": relay_id,
            "time_step": time_step,
            "contexts": self.get_contexts(
                relay_id,
                time_step
            ),
            "recommendation": self.get_recommendation(
                relay_id,
                time_step
            ),
            "contextual_score": self.get_contextual_score(
                relay_id,
                time_step
            ),
            "reasons": self.get_reasons(
                relay_id,
                time_step
            ),
            "warnings": self.get_warnings(
                relay_id,
                time_step
            )
        }
