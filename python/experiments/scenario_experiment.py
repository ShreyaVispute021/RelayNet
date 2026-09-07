import random
import csv
from python.relaynet.scenarios import SCENARIOS
from python.relaynet.traffic import TrafficGenerator
from python.relaynet.relay_selection import (
    select_best_relay,
    select_contextual_relay,
    select_static_relay,
)
from python.relaynet.contextual_reasoner import ContextualReasoner
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

        # Keep queue length bounded by relay capacity.
        relay.queue_length = min(
            relay.queue_length,
            20
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
    total_packets=1000,
    selection_method="baseline",
    learner=None,
    training=False,
    seed=42,
):

    random.seed(seed)

    network = create_network()

    source = next(
        node for node in network.nodes
        if node.node_type == "SOURCE"
    )

    relays = network.get_relays()
    initial_total_battery = sum(relay.battery for relay in relays)

    relay_queues = {
        relay.node_id: RelayQueue(capacity=20)
        for relay in relays
    }

    traffic = TrafficGenerator()
    reasoner = ContextualReasoner()

    delivered_packets = 0
    total_delay = 0
    delivered_bytes = 0
    network_lifetime_steps = 0
    relay_selections = {
        relay.node_id: 0
        for relay in relays
    }

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

        if any(relay.is_available() for relay in relays):
            network_lifetime_steps = time_step + 1

        if selection_method == "static":
            best_relay, best_score = select_static_relay(relays)
        elif selection_method == "baseline":
            best_relay, best_score = select_best_relay(relays)
        elif selection_method == "contextual_kg":
            best_relay, best_score, _ = select_contextual_relay(
                relays,
                reasoner,
            )
            learning_state = None
        elif selection_method == "kg_marl":
            if learner is None:
                raise ValueError("kg_marl requires a learner")
            (
                best_relay,
                best_score,
                _,
                learning_state,
            ) = learner.select_relay(
                relays,
                reasoner,
                training=training,
            )
        else:
            raise ValueError(
                f"Unknown selection method: {selection_method}"
            )

        if best_relay is None:
            continue

        relay_selections[best_relay.node_id] += 1

        transmission_energy = 0.03 + 0.0001 * best_relay.altitude
        best_relay.battery = max(
            0.0,
            best_relay.battery - transmission_energy,
        )

        relay_queue = relay_queues[
            best_relay.node_id
        ]
        
        success = packet_delivery_success(
            best_relay
        )

        queue_was_full = relay_queue.is_full()

        if selection_method == "kg_marl" and training:
            # Emergency delivery is the primary objective. A successful
            # transmission therefore receives a larger positive reward than
            # the penalty for one stochastic failure.
            reward = 4.0 if success and not queue_was_full else -1.0
            reward += 0.40 * best_relay.link_stability
            reward += 0.25 * (best_relay.battery / 100)
            reward -= 0.50 * (best_relay.queue_length / 20)
            next_state = learner.encode_state(best_relay)
            learner.update(
                best_relay.node_id,
                learning_state,
                reward,
                next_state,
            )

        if success:

            if queue_was_full:
                continue

            # Process a packet that was already waiting
            # before the current packet was added.
            if relay_queue.size() > 0:

                queued_packet, arrival_time = relay_queue.dequeue()

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
                delivered_bytes += queued_packet.size_bytes

                total_delay += (
                    queued_packet.delay()
                )

            # Add the current packet to the queue
            # for future processing.
            queued = relay_queue.enqueue(
                packet,
                time_step
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

    energy_consumed = initial_total_battery - sum(
        relay.battery for relay in relays
    )
    throughput_kbps = (
        delivered_bytes * 8 / max(total_packets, 1) / 1000
    )

    return {
        "scenario": scenario.name,
        "selection_method": selection_method,
        "packets": total_packets,
        "delivered": delivered_packets,
        "lost": lost_packets,
        "pdr": pdr,
        "loss_ratio": loss_ratio,
        "average_delay": average_delay,
        "throughput_kbps": throughput_kbps,
        "energy_consumed": energy_consumed,
        "network_lifetime_steps": network_lifetime_steps,
        "relay_selections": relay_selections,
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

    output_rows = [
        {
            key: value
            for key, value in result.items()
            if key != "relay_selections"
        }
        for result in results
    ]

    with open(
        "results/scenario_results.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=output_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(output_rows)

    print(
        "\nScenario results saved to "
        "results/scenario_results.csv"
    )


if __name__ == "__main__":
    main()
