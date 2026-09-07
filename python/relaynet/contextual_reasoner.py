class ContextualReasoner:
    """
    Lightweight rule-based reasoning layer for RelayNet.

    Converts temporal relay state information into:
    - contextual recommendations
    - human-readable reasoning
    - contextual relay scores

    This is intentionally rule-based and does not implement MARL.
    """

    def __init__(self):
        self.weights = {
            "battery": 0.20,
            "queue": 0.20,
            "stability": 0.25,
            "mobility": 0.10,
            "rssi": 0.15,
            "hop": 0.10,
        }

    def normalize_rssi(self, rssi):
        """
        Convert RSSI from approximately [-100, -40] dBm
        into a [0, 1] score.
        """
        score = (rssi + 100) / 60
        return max(0.0, min(1.0, score))

    def normalize_battery(self, battery):
        return max(0.0, min(1.0, battery / 100))

    def normalize_queue(self, queue_length):
        return 1.0 - min(queue_length / 20, 1.0)

    def normalize_mobility(self, mobility):
        return 1.0 - min(mobility, 1.0)

    def normalize_stability(self, stability):
        return max(0.0, min(1.0, stability))

    def normalize_hop(self, hop_count):
        return 1.0 - min(hop_count / 10, 1.0)

    def calculate_contextual_score(self, state):
        """
        Calculate a contextual score from the relay's current
        temporal state.

        The score is based on current conditions rather than
        simply retrieving the original stored routing score.
        """

        rssi_score = self.normalize_rssi(state["rssi"])
        battery_score = self.normalize_battery(state["battery"])
        queue_score = self.normalize_queue(state["queue_length"])
        mobility_score = self.normalize_mobility(state["mobility"])
        stability_score = self.normalize_stability(
            state["link_stability"]
        )
        hop_score = self.normalize_hop(state["hop_count"])

        score = (
            self.weights["rssi"] * rssi_score
            + self.weights["battery"] * battery_score
            + self.weights["queue"] * queue_score
            + self.weights["mobility"] * mobility_score
            + self.weights["stability"] * stability_score
            + self.weights["hop"] * hop_score
        )

        return round(score, 4)

    def analyze(self, state):
        """
        Analyze a relay's temporal state and generate
        contextual reasoning.
        """

        relay_id = state["relay_id"]

        battery = state["battery"]
        queue = state["queue_length"]
        stability = state["link_stability"]
        mobility = state["mobility"]
        rssi = state["rssi"]

        reasons = []
        warnings = []

        # Battery reasoning
        if battery < 20:
            warnings.append("low battery")
        elif battery >= 60:
            reasons.append("sufficient battery")

        # Queue / congestion reasoning
        if queue >= 15:
            warnings.append("high congestion")
        elif queue <= 5:
            reasons.append("low queue")

        # Link stability reasoning
        if stability < 0.40:
            warnings.append("poor link stability")
        elif stability >= 0.70:
            reasons.append("stable link")

        # Mobility reasoning
        if mobility >= 0.70:
            warnings.append("high mobility")
        elif mobility <= 0.30:
            reasons.append("low mobility")

        # RSSI reasoning
        if rssi < -85:
            warnings.append("weak RSSI")
        elif rssi >= -65:
            reasons.append("strong RSSI")

        # Determine recommendation
        critical_conditions = 0

        if battery < 20:
            critical_conditions += 1

        if queue >= 15:
            critical_conditions += 1

        if stability < 0.40:
            critical_conditions += 1

        if critical_conditions >= 2:
            recommendation = "AVOID"
        elif critical_conditions == 1:
            recommendation = "CAUTION"
        else:
            recommendation = "PREFER"

        # Generate explanation
        if recommendation == "AVOID":
            explanation = (
                f"Avoid relay {relay_id} due to "
                + " and ".join(warnings)
                + "."
            )

        elif recommendation == "CAUTION":
            if warnings:
                explanation = (
                    f"Use relay {relay_id} with caution due to "
                    + " and ".join(warnings)
                    + "."
                )
            else:
                explanation = (
                    f"Relay {relay_id} is usable but requires "
                    "contextual monitoring."
                )

        else:
            if reasons:
                explanation = (
                    f"Preferred relay {relay_id} due to "
                    + " and ".join(reasons)
                    + "."
                )
            else:
                explanation = (
                    f"Relay {relay_id} has acceptable current conditions."
                )

        contextual_score = self.calculate_contextual_score(state)

        return {
            "relay_id": relay_id,
            "recommendation": recommendation,
            "contextual_score": contextual_score,
            "reasons": reasons,
            "warnings": warnings,
            "explanation": explanation,
        }

    def rank_relays(self, states):
        """
        Analyze and rank multiple relay states.

        AVOID relays are placed below PREFER and CAUTION relays.
        Within each category, contextual score determines ranking.
        """

        analyzed = []

        for state in states:
            result = self.analyze(state)
            analyzed.append(result)

        priority = {
            "PREFER": 2,
            "CAUTION": 1,
            "AVOID": 0,
        }

        analyzed.sort(
            key=lambda item: (
                priority[item["recommendation"]],
                item["contextual_score"],
            ),
            reverse=True,
        )

        return analyzed