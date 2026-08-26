def calculate_forwarding_delay(relay):
    """
    Estimate forwarding delay from relay congestion.

    Higher queue length means greater waiting time.
    """

    base_delay = 1

    queue_delay = relay.queue_length // 3

    return base_delay + queue_delay


def queue_overflow(relay, capacity=20):
    """
    Return True when the relay queue exceeds capacity.
    """

    return relay.queue_length >= capacity