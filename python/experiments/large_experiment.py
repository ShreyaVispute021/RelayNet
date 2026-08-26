import random

from python.relaynet.traffic import TrafficGenerator
from python.relaynet.relay_selection import select_best_relay
from python.relaynet.mobility import calculate_rssi, move_node
from python.relaynet.delivery import (
    calculate_delivery_probability,
    packet_delivery_success,
)
from python.experiments.packet_routing_test import create_network


def update_network(source, relays, time_step):

    for relay in relays:

        # Battery consumption
        relay.battery = max(
            0,
            relay.battery - 0.05
        )

        # Different mobility patterns
        if relay.node_id == "R1":
            move_node(relay, 1.0, 0.5)

        elif relay.node_id == "R2":
            move_node(relay, -0.5, 1.0)

        elif relay.node_id == "R3":
            move_node(relay, 0.8, -0.6)

        # Mobility increases slightly
        relay.mobility = min(
            1.0,
            relay.mobility + 0.001
        )

        # Link stability decreases slowly
        relay.link_stability = max(
            0,
            relay.link_stability - 0.0005
        )

        # Recalculate RSSI from position
        relay.rssi = calculate_rssi(
            source,
            relay
        )

        # Queue changes over time
        if time_step % 5 == 0:
            relay.queue_length += 1

        if relay.queue_length > 0:
            relay.queue_length -= 1


def main():

    random.seed(42)

    network = create_network()

    source = next(
        node for node in network.nodes
        if node.node_type == "SOURCE"
    )

    relays = network.get_relays()

    traffic = TrafficGenerator()

    total_packets = 1000
    delivered_packets = 0
    total_delay = 0

    print("==============================================")
    print("       RelayNet Large Experiment")
    print("==============================================")

    for time_step in range(total_packets):

        # Update the network
        update_network(
            source,
            relays,
            time_step
        )

        # Generate emergency packet
        packet = traffic.generate_packet(
            source="S",
            destination="D",
            time_step=time_step
        )

        # Select relay
        best_relay, best_score = select_best_relay(
            relays
        )

        if best_relay is None:
            continue

        # Estimate delivery probability
        probability = calculate_delivery_probability(
            best_relay
        )

        # Attempt delivery
        success = packet_delivery_success(
            best_relay
        )

        if success:

            packet.deliver(
                time_step + 1,
                best_relay.node_id
            )

            delivered_packets += 1

            total_delay += packet.delay()

    packet_loss = total_packets - delivered_packets

    pdr = (
        delivered_packets / total_packets
    )

    loss_ratio = (
        packet_loss / total_packets
    )

    average_delay = (
        total_delay / delivered_packets
        if delivered_packets > 0
        else 0
    )

    print("\n==============================================")
    print("             FINAL RESULTS")
    print("==============================================")

    print(
        f"Total Packets         : {total_packets}"
    )

    print(
        f"Delivered Packets     : {delivered_packets}"
    )

    print(
        f"Lost Packets          : {packet_loss}"
    )

    print(
        f"Packet Delivery Ratio : {pdr:.2%}"
    )

    print(
        f"Packet Loss Ratio     : {loss_ratio:.2%}"
    )

    print(
        f"Average Delay         : {average_delay:.2f}"
    )


if __name__ == "__main__":
    main()