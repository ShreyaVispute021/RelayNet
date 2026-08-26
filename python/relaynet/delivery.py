import random
def calculate_delivery_probability(relay):
    """
    Estimate the probability that a packet successfully
    crosses the selected relay.

    This is a simplified prototype model.
    """

    # Normalize RSSI from approximately -100 to -40 dBm.
    rssi_score = (relay.rssi + 100) / 60
    rssi_score = max(0, min(1, rssi_score))

    # Battery.
    battery_score = relay.battery / 100
    battery_score = max(0, min(1, battery_score))

    # Lower queue is better.
    queue_score = 1 - min(
        relay.queue_length / 20,
        1
    )

    # Link stability.
    stability_score = max(
        0,
        min(1, relay.link_stability)
    )

    probability = (
        0.35 * rssi_score
        + 0.25 * stability_score
        + 0.20 * battery_score
        + 0.20 * queue_score
    )

    return max(0, min(1, probability))


def packet_delivery_success(relay):
    """
    Simulate whether a packet is successfully delivered
    based on the relay's estimated delivery probability.
    """

    probability = calculate_delivery_probability(
        relay
    )

    return random.random() < probability