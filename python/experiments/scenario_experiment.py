import random

from python.relaynet.scenarios import SCENARIOS
from python.relaynet.traffic import TrafficGenerator
from python.relaynet.relay_selection import select_best_relay
from python.relaynet.mobility import calculate_rssi, move_node
from python.relaynet.delivery import (
    calculate_delivery_probability,
    packet_delivery_success,
)
from python.relaynet.queue import RelayQueue
from python.experiments.packet_routing_test import create_network
from python.relaynet.forwarding import (
    calculate_forwarding_delay,
    queue_overflow,
)


def update_network(
    source,
    relays,
    time_step,
    scenario
):

    for relay in relays:

        # Battery consumption
        relay.battery = max(
            0,
            relay.battery - scenario.battery_drain
        )

        # Movement
        if relay.node_id == "R1":

            move_node(
                relay,
                1.0 * scenario.mobility_factor,
                0.5 * scenario.mobility_factor
            )

        elif relay.node_id == "R2":

            move_node(
                relay,
                -0.5 * scenario.mobility_factor,
                1.0 * scenario.mobility_factor
            )

        elif relay.node_id == "R3":

            move_node(
                relay,
                0.8 * scenario.mobility_factor,
                -0.6 * scenario.mobility_factor
            )

        # Mobility
        relay.mobility = min(
            1.0,
            relay.mobility
            + 0.001 * scenario.mobility_factor
        )

        # Link stability
        relay.link_stability = max(
            0,
            relay.link_stability
            - scenario.stability_drain
        )

        # RSSI
        relay.rssi = calculate_rssi(
            source,
            relay
        )

        # Traffic / queue
        traffic_interval = max(
            1,
            int(5 / scenario.traffic_factor)
        )

        if time_step % traffic_interval == 0:
            relay.queue_length += 1

        # Relay processing capacity.
        processing_capacity = 1

        relay.queue_length = max(
            0,
            relay.queue_length - processing_capacity
        )

    # Explicit relay failure scenario
    if (
        scenario.failure_time is not None
        and time_step >= scenario.failure_time
    ):

        r2 = next(
            relay for relay in relays
            if relay.node_id == "R2"
        )

        r2.battery = 0
        r2.link_stability = 0


def run_scenario(
    scenario,
    total_packets=1000
):

    random.seed(42)

    network = create_network()

    source = next(
        node for node in network.nodes
        if node.node_type == "SOURCE"
    )

    relays = network.get_relays()

    relay_queues = {
        relay.node_id: RelayQueue(capacity=20)
        for relay in relays
    }

    traffic = TrafficGenerator()

    delivered_packets = 0
    total_delay = 0

    for time_step in range(total_packets):

        update_network(
            source,
            relays,
            time_step,
            scenario
        )

        packet = traffic.generate_packet(
            source="S",
            destination="D",
            time_step=time_step
        )

        best_relay, best_score = select_best_relay(
            relays
        )

        if best_relay is None:
            continue

        relay_queue = relay_queues[
            best_relay.node_id
        ]
        
        success = packet_delivery_success(
            best_relay
        )

        if success:

            if queue_overflow(best_relay):
                continue

            queued = relay_queue.enqueue(
                packet,
                time_step
            )

            # Process one packet that was already waiting
            # in this relay's queue.
            if relay_queue.size() > 0 and time_step > 0:

                queued_packet, arrival_time = (
                    relay_queue.dequeue()
                )

                waiting_time = (
                    time_step - arrival_time
                )

                forwarding_delay = (
                    1 + waiting_time
                )

                delivery_time = (
                    time_step + forwarding_delay
                )
                queued_packet.deliver(
                    delivery_time,
                    best_relay.node_id
                )
                delivered_packets += 1
                total_delay += (
                    queued_packet.delay()
                )

            if not queued:
                continue

            waiting_time = (
                time_step - arrival_time
            )

            forwarding_delay = (
                1 + waiting_time
            )

            delivery_time = (
                time_step + forwarding_delay
            )

            queued_packet.deliver(
                delivery_time,
                best_relay.node_id
            )

            delivered_packets += 1

            total_delay += (
                queued_packet.delay()
            )

    lost_packets = (
        total_packets - delivered_packets
    )

    pdr = (
        delivered_packets / total_packets
    )

    loss_ratio = (
        lost_packets / total_packets
    )

    average_delay = (
        total_delay / delivered_packets
        if delivered_packets > 0
        else 0
    )

    return {
        "scenario": scenario.name,
        "packets": total_packets,
        "delivered": delivered_packets,
        "lost": lost_packets,
        "pdr": pdr,
        "loss_ratio": loss_ratio,
        "average_delay": average_delay,
    }


def main():

    print("==============================================")
    print("       RelayNet Scenario Experiment")
    print("==============================================")

    results = []

    for scenario in SCENARIOS:

        print(
            f"\nRunning scenario: "
            f"{scenario.name}"
        )

        result = run_scenario(
            scenario,
            total_packets=1000
        )

        results.append(result)

        print(
            f"PDR: "
            f"{result['pdr']:.2%}"
        )

        print(
            f"Loss: "
            f"{result['loss_ratio']:.2%}"
        )

        print(
            f"Average Delay: "
            f"{result['average_delay']:.2f}"
        )

    print("\n==============================================")
    print("             SCENARIO SUMMARY")
    print("==============================================")

    for result in results:

        print(
            f"{result['scenario']:20s} "
            f"PDR={result['pdr']:.2%} "
            f"Loss={result['loss_ratio']:.2%} "
            f"Delay={result['average_delay']:.2f}"
        )


if __name__ == "__main__":
    main()