from python.relaynet.knowledge_graph_query import KnowledgeGraphQuery
from python.relaynet.network import Node
from python.relaynet.relay_selection import (
    select_best_relay,
    select_relay_from_kg
)


def build_network_from_kg(graph, time_step):
    network = []

    available_relays = graph.get_available_relays(time_step)

    for relay_id in available_relays:
        state = graph.get_state(relay_id, time_step)

        if state is None:
            continue

        relay = Node(
            node_id=relay_id,
            node_type="RELAY",
            x=0.0,
            y=0.0,
            battery=float(state["HAS_BATTERY"]),
            rssi=float(state["HAS_RSSI"]),
            queue_length=int(state["HAS_QUEUE_LENGTH"]),
            mobility=float(state["HAS_MOBILITY"]),
            link_stability=float(state["HAS_LINK_STABILITY"]),
            hop_count=int(state["HAS_HOP_COUNT"])
        )

        network.append(relay)

    return network


def main():

    graph = KnowledgeGraphQuery(
        "results/relaynet_knowledge_graph.csv"
    )

    print("==============================================")
    print("       RelayNet KG Integration Test")
    print("==============================================")

    for time_step in [0, 5, 10]:

        relays = build_network_from_kg(
            graph,
            time_step
        )

        baseline_relay, baseline_score = select_best_relay(
            relays
        )

        kg_relay, kg_score = select_relay_from_kg(
            relays,
            graph,
            time_step
        )

        print(f"\nTime Step: T{time_step}")

        if baseline_relay:
            print(
                f"Baseline Relay: {baseline_relay.node_id} "
                f"| Score: {baseline_score:.4f}"
            )
        else:
            print("Baseline Relay: None")

        if kg_relay:
            print(
                f"KG Relay: {kg_relay.node_id} "
                f"| KG Score: {kg_score:.4f}"
            )
        else:
            print("KG Relay: None")

        if baseline_relay and kg_relay:
            if baseline_relay.node_id == kg_relay.node_id:
                print("Decision: MATCH")
            else:
                print("Decision: DIFFERENT")


if __name__ == "__main__":
    main()