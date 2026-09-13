from collections import defaultdict
import math
import random

from python.relaynet.rl_config import RLConfig


class MultiAgentRelayLearner:
    """Independent Q-learning agents for KG-assisted UAV relay selection.

    Every relay owns a Q-table.  The coordinator combines each agent's learned
    selection value with the contextual score produced from the Knowledge
    Graph state schema.  This keeps the prototype lightweight and explainable.
    """

    SELECT = 1

    def __init__(
        self,
        alpha=None,
        gamma=None,
        epsilon=None,
        kg_weight=None,
        seed=None,
        config=None,
    ):
        self.config = config or RLConfig()
        self.alpha = self.config.learning_rate if alpha is None else alpha
        self.gamma = self.config.discount_factor if gamma is None else gamma
        self.epsilon = self.config.epsilon_start if epsilon is None else epsilon
        self.kg_weight = self.config.kg_weight if kg_weight is None else kg_weight
        self.q_tables = defaultdict(lambda: defaultdict(float))
        self.random = random.Random(
            self.config.random_seed if seed is None else seed
        )

    @staticmethod
    def _level(value, low, high):
        if value < low:
            return 0
        if value < high:
            return 1
        return 2

    def encode_state(self, relay):
        """Discretize a live relay observation for tabular Q-learning."""

        return (
            self._level(relay.battery, 25, 60),
            self._level(relay.rssi, -85, -65),
            self._level(relay.queue_length, 7, 15),
            self._level(relay.mobility, 0.35, 0.70),
            self._level(relay.link_stability, 0.40, 0.70),
            self._level(relay.hop_count, 3, 5),
        )

    def select_relay(self, relays, reasoner, training=False):
        available = [relay for relay in relays if relay.is_available()]
        if not available:
            return None, 0.0, None, None

        from python.relaynet.relay_selection import relay_to_context_state

        candidates = []
        for relay in available:
            analysis = reasoner.analyze(relay_to_context_state(relay))
            state = self.encode_state(relay)
            q_value = self.q_tables[relay.node_id][state]
            learned_score = (math.tanh(q_value) + 1.0) / 2.0
            combined_score = (
                self.kg_weight * analysis["contextual_score"]
                + (1.0 - self.kg_weight) * learned_score
            )
            if analysis["recommendation"] == "AVOID":
                combined_score -= 0.25
            candidates.append(
                (relay, combined_score, analysis, state)
            )

        if training and self.random.random() < self.epsilon:
            return self.random.choice(candidates)

        return max(candidates, key=lambda item: item[1])

    def update(self, relay_id, state, reward, next_state):
        current_q = self.q_tables[relay_id][state]
        next_q = self.q_tables[relay_id][next_state]
        target = reward + self.gamma * next_q
        td_error = target - current_q
        self.q_tables[relay_id][state] = current_q + self.alpha * td_error
        return abs(td_error)

    def decay_exploration(self, factor=None, minimum=None):
        factor = self.config.epsilon_decay if factor is None else factor
        minimum = self.config.epsilon_min if minimum is None else minimum
        self.epsilon = max(minimum, self.epsilon * factor)

    def q_table_size(self):
        return sum(len(table) for table in self.q_tables.values())

    def save(self, output_path):
        import csv
        from pathlib import Path

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "relay_id",
                    "battery_state",
                    "rssi_state",
                    "queue_state",
                    "mobility_state",
                    "stability_state",
                    "hop_state",
                    "q_value",
                ]
            )
            for relay_id, table in sorted(self.q_tables.items()):
                for state, q_value in sorted(table.items()):
                    writer.writerow([relay_id, *state, q_value])
