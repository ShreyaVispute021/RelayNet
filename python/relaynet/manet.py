from dataclasses import dataclass
from heapq import heappop, heappush
from math import sqrt


@dataclass(frozen=True)
class WirelessLink:
    source: str
    destination: str
    distance: float
    cost: float


class MANETTopology:
    """Range-based, infrastructure-less mobile ad hoc network topology.

    Nodes discover neighbours directly. A link exists only when both nodes are
    operational and their 3-D Euclidean separation is within radio range.
    Routes are discovered with Dijkstra's algorithm over current link costs.
    """

    def __init__(self, nodes, communication_range=140.0):
        self.nodes = {node.node_id: node for node in nodes}
        self.communication_range = communication_range
        self.links = []
        self.adjacency = {}
        self.refresh()

    @staticmethod
    def distance(first, second):
        return sqrt(
            (first.x - second.x) ** 2
            + (first.y - second.y) ** 2
            + (first.altitude - second.altitude) ** 2
        )

    @staticmethod
    def _operational(node):
        return node.is_available()

    def _link_cost(self, first, second, distance):
        relays = [
            node for node in (first, second)
            if node.node_type == "RELAY"
        ]
        if not relays:
            return distance / self.communication_range

        stability = sum(node.link_stability for node in relays) / len(relays)
        queue = sum(min(node.queue_length / 20, 1) for node in relays) / len(relays)
        mobility = sum(min(node.mobility, 1) for node in relays) / len(relays)
        battery = sum(node.battery / 100 for node in relays) / len(relays)

        return (
            0.55 * (distance / self.communication_range)
            + 0.20 * (1 - stability)
            + 0.10 * queue
            + 0.10 * mobility
            + 0.05 * (1 - battery)
        )

    def refresh(self):
        self.links = []
        self.adjacency = {node_id: [] for node_id in self.nodes}
        node_list = list(self.nodes.values())

        for index, first in enumerate(node_list):
            if not self._operational(first):
                continue
            for second in node_list[index + 1:]:
                if not self._operational(second):
                    continue
                distance = self.distance(first, second)
                if distance > self.communication_range:
                    continue
                cost = self._link_cost(first, second, distance)
                link = WirelessLink(first.node_id, second.node_id, distance, cost)
                self.links.append(link)
                self.adjacency[first.node_id].append((second.node_id, cost))
                self.adjacency[second.node_id].append((first.node_id, cost))

    def neighbours(self, node_id):
        return sorted(neighbour for neighbour, _ in self.adjacency[node_id])

    def discover_route(self, source_id="S", destination_id="D"):
        queue = [(0.0, source_id, [source_id])]
        best_cost = {source_id: 0.0}

        while queue:
            cost, node_id, path = heappop(queue)
            if node_id == destination_id:
                return path, cost
            if cost > best_cost.get(node_id, float("inf")):
                continue
            for neighbour, link_cost in self.adjacency.get(node_id, []):
                new_cost = cost + link_cost
                if new_cost < best_cost.get(neighbour, float("inf")):
                    best_cost[neighbour] = new_cost
                    heappush(queue, (new_cost, neighbour, path + [neighbour]))

        return None, float("inf")

    def snapshot(self):
        return {
            "node_count": len(self.nodes),
            "active_node_count": sum(
                self._operational(node) for node in self.nodes.values()
            ),
            "link_count": len(self.links),
            "neighbours": {
                node_id: self.neighbours(node_id) for node_id in self.nodes
            },
        }
