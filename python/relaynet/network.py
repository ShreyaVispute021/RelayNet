from dataclasses import dataclass


@dataclass
class Node:
    node_id: str
    node_type: str
    x: float
    y: float
    battery: float
    rssi: float
    queue_length: int
    mobility: float
    link_stability: float
    hop_count: int

    def display(self):
        print(f"Node: {self.node_id}")
        print(f"  Type: {self.node_type}")
        print(f"  Position: ({self.x}, {self.y})")
        print(f"  Battery: {self.battery:.2f}%")
        print(f"  RSSI: {self.rssi:.2f} dBm")
        print(f"  Queue Length: {self.queue_length}")
        print(f"  Mobility: {self.mobility:.2f}")
        print(f"  Link Stability: {self.link_stability:.2f}")
        print(f"  Hop Count: {self.hop_count}")
        print()

    def is_available(self):
        return (
            self.battery > 0
            and self.link_stability > 0
        )


class DisasterNetwork:

    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def get_relays(self):
        return [
            node for node in self.nodes
            if node.node_type == "RELAY"
        ]

    def display_network(self):
        print("\n===== RelayNet Disaster Network =====\n")

        for node in self.nodes:
            node.display()