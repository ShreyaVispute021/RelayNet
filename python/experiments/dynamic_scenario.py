from python.relaynet.network import Node, DisasterNetwork
from python.relaynet.mobility import calculate_rssi, move_node
from python.relaynet.relay_selection import (
    calculate_relay_score,
    select_best_relay,
)

from python.relaynet.data_logger import DataLogger

def update_network(source, relays, time_step):
    """
    Deterministic network changes for each simulation time step.
    """

    for relay in relays:

        # Battery gradually decreases.
        relay.battery = max(0, relay.battery - 2)

        # Queue changes and relay movement.
        if relay.node_id == "R1":
            relay.queue_length += 1
            move_node(relay, 2, 1)

        elif relay.node_id == "R2":
            relay.queue_length += 2
            move_node(relay, -1, 2)

        elif relay.node_id == "R3":
            relay.queue_length += 1
            move_node(relay, 3, -2)

        # Mobility gradually increases.
        relay.mobility += 0.03

        # Link stability gradually decreases.
        relay.link_stability = max(
            0,
            relay.link_stability - 0.02
        )

        # Calculate RSSI from the relay's new position.
        relay.rssi = calculate_rssi(source, relay)

    # Special network degradation event for R2.
    if time_step >= 5:

        r2 = next(
            relay for relay in relays
            if relay.node_id == "R2"
        )

        r2.battery = max(0, r2.battery - 8)
        r2.queue_length += 5

        r2.link_stability = max(
            0,
            r2.link_stability - 0.10
        )

def print_scores(relays):
    for relay in relays:

        score = calculate_relay_score(relay)

        print(
            f"{relay.node_id}: "
            f"score={score:.4f}, "
            f"battery={relay.battery:.1f}%, "
            f"queue={relay.queue_length}, "
            f"mobility={relay.mobility:.2f}, "
            f"stability={relay.link_stability:.2f}"
        )


def create_network():
    network = DisasterNetwork()

    source = Node(
        node_id="S",
        node_type="SOURCE",
        x=0,
        y=0,
        battery=95,
        rssi=-45,
        queue_length=2,
        mobility=0.1,
        link_stability=0.95,
        hop_count=0
    )

    destination = Node(
        node_id="D",
        node_type="DESTINATION",
        x=100,
        y=100,
        battery=100,
        rssi=-40,
        queue_length=0,
        mobility=0.0,
        link_stability=1.0,
        hop_count=0
    )

    relay1 = Node(
        node_id="R1",
        node_type="RELAY",
        x=25,
        y=30,
        battery=80,
        rssi=-55,
        queue_length=5,
        mobility=0.3,
        link_stability=0.85,
        hop_count=2,
        platform="UAV",
        altitude=80.0
    )

    relay2 = Node(
        node_id="R2",
        node_type="RELAY",
        x=45,
        y=40,
        battery=65,
        rssi=-48,
        queue_length=2,
        mobility=0.2,
        link_stability=0.92,
        hop_count=2,
        platform="UAV",
        altitude=100.0
    )

    relay3 = Node(
        node_id="R3",
        node_type="RELAY",
        x=60,
        y=65,
        battery=90,
        rssi=-62,
        queue_length=8,
        mobility=0.6,
        link_stability=0.70,
        hop_count=3,
        platform="UAV",
        altitude=120.0
    )

    network.add_node(source)
    network.add_node(destination)
    network.add_node(relay1)
    network.add_node(relay2)
    network.add_node(relay3)

    return network


def main():

    network = create_network()

    relays = network.get_relays()
    source = next(
        node for node in network.nodes
        if node.node_type == "SOURCE"
    )
    logger = DataLogger()

    print("==============================================")
    print("       RelayNet Dynamic Network Test")
    print("==============================================")

    for time_step in range(11):

        print(f"\n========== TIME STEP {time_step} ==========")

        # Update the network after the initial state.
        if time_step > 0:
            update_network(source, relays, time_step)

        print_scores(relays)

        best_relay, best_score = select_best_relay(relays)

        print()

        if best_relay is None:
            print("Selected Relay : NONE")
            print("Status         : NO AVAILABLE RELAY")
        else:
            print(f"Selected Relay : {best_relay.node_id}")
            print(f"Best Score     : {best_score:.4f}")


        for relay in relays:

            score = calculate_relay_score(relay)

            selected = (
                best_relay is not None
                and relay.node_id == best_relay.node_id
            )

            logger.log_relay(
                time_step,
                relay,
                score,
                selected
            )

    logger.close()


if __name__ == "__main__":
    main()
