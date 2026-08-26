import random
from python.relaynet.network import Node, DisasterNetwork
from python.relaynet.relay_selection import select_best_relay
from python.relaynet.mobility import calculate_rssi, move_node
from python.relaynet.traffic import TrafficGenerator
from python.relaynet.delivery import (
    calculate_delivery_probability,
    packet_delivery_success,
)
from python.relaynet.forwarding import (
    calculate_forwarding_delay,
    queue_overflow,
)

def create_network():

    network = DisasterNetwork()

    source = Node(
        node_id="S",
        node_type="SOURCE",
        x=0,
        y=0,
        battery=95,
        rssi=-40,
        queue_length=0,
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
        rssi=-50,
        queue_length=2,
        mobility=0.3,
        link_stability=0.90,
        hop_count=2
    )

    relay2 = Node(
        node_id="R2",
        node_type="RELAY",
        x=45,
        y=40,
        battery=65,
        rssi=-50,
        queue_length=2,
        mobility=0.2,
        link_stability=0.92,
        hop_count=2
    )

    relay3 = Node(
        node_id="R3",
        node_type="RELAY",
        x=60,
        y=65,
        battery=90,
        rssi=-60,
        queue_length=5,
        mobility=0.6,
        link_stability=0.70,
        hop_count=3
    )

    network.add_node(source)
    network.add_node(destination)
    network.add_node(relay1)
    network.add_node(relay2)
    network.add_node(relay3)

    return network


def update_relay_state(source, relays):

    for relay in relays:

        if relay.node_id == "R1":
            move_node(relay, 2, 1)

        elif relay.node_id == "R2":
            move_node(relay, -1, 2)

        elif relay.node_id == "R3":
            move_node(relay, 3, -2)

        relay.rssi = calculate_rssi(
            source,
            relay
        )

        relay.battery = max(
            0,
            relay.battery - 1
        )


def main():
    random.seed(42)
    network = create_network()

    source = next(
        node for node in network.nodes
        if node.node_type == "SOURCE"
    )

    relays = network.get_relays()

    traffic = TrafficGenerator()

    total_packets = 0
    delivered_packets = 0
    total_delay = 0

    print("==============================================")
    print("       RelayNet Packet Routing Test")
    print("==============================================")

    for time_step in range(10):

        print(f"\n========== TIME STEP {time_step} ==========")

        # Generate one emergency packet.
        packet = traffic.generate_packet(
            source="S",
            destination="D",
            time_step=time_step
        )

        total_packets += 1

        # Update network conditions.
        if time_step > 0:
            update_relay_state(
                source,
                relays
            )

        # Select the best available relay.
        best_relay, best_score = select_best_relay(
            relays
        )

        if best_relay is None:

            print(
                f"Packet {packet.packet_id}: "
                "DROPPED - no available relay"
            )

            continue

        # Simulate successful forwarding.
        delivery_probability = calculate_delivery_probability(
            best_relay
        )

        success = packet_delivery_success(
            best_relay
        )

        print(
            f"Packet {packet.packet_id}: "
            f"S -> {best_relay.node_id} -> D"
        )

        print(
            f"Relay Score: {best_score:.4f}"
        )

        print(
            f"Delivery Probability: "
            f"{delivery_probability:.2%}"
        )

        if success:

            if queue_overflow(best_relay):

                print("Status: LOST - relay queue overflow")

            else:

                forwarding_delay = calculate_forwarding_delay(
                    best_relay
                )

                delivery_time = (
                    time_step + forwarding_delay
                )

                packet.deliver(
                    delivery_time,
                    best_relay.node_id
                )

                delivered_packets += 1

                packet_delay = packet.delay()

                total_delay += packet_delay

                print("Status: DELIVERED")

                print(
                    f"Forwarding Delay: {forwarding_delay}"
                )

                print(
                    f"End-to-End Delay: {packet_delay}"
                )

                print(
                    f"Status: DELIVERED"
                )

                print(
                    f"Delay: {packet_delay}"
                )

        else:

            print(
                f"Status: LOST"
            )

    print("\n==============================================")
    print("             FINAL RESULTS")
    print("==============================================")

    pdr = (
        delivered_packets / total_packets
        if total_packets > 0
        else 0
    )

    packet_loss_ratio = 1 - pdr

    average_delay = (
        total_delay / delivered_packets
        if delivered_packets > 0
        else 0
    )

    print(
        f"Total Packets      : {total_packets}"
    )

    print(
        f"Delivered Packets  : {delivered_packets}"
    )

    print(
        f"Packet Delivery Ratio : {pdr:.2%}"
    )

    print(
        f"Packet Loss Ratio     : {packet_loss_ratio:.2%}"
    )

    print(
        f"Average Delay         : {average_delay:.2f}"
    )


if __name__ == "__main__":
    main()