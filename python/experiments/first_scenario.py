from python.relaynet.network import Node, DisasterNetwork
from python.relaynet.relay_selection import select_best_relay
def main():

    network = DisasterNetwork()

    # Emergency source
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

    # Rescue destination
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

    # Candidate relay nodes
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
        hop_count=2
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
        hop_count=2
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
        hop_count=3
    )

    network.add_node(source)
    network.add_node(destination)
    network.add_node(relay1)
    network.add_node(relay2)
    network.add_node(relay3)

    network.display_network()

    relays = network.get_relays()

    best_relay, score = select_best_relay(relays)

    print("===== RelayNet Relay Selection =====")
    print(f"Selected Relay: {best_relay.node_id}")
    print(f"Relay Score: {score:.4f}")


if __name__ == "__main__":
    main()