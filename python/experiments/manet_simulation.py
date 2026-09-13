import csv
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt

from python.experiments.dynamic_scenario import create_network, update_network
from python.relaynet.manet import MANETTopology


RESULTS_DIR = Path("results")
LOG_PATH = RESULTS_DIR / "manet_routing_log.csv"
GRAPH_PATH = RESULTS_DIR / "manet_topology.png"


def draw_snapshot(axis, topology, route, time_step):
    colors = {
        "SOURCE": "#2e86de",
        "DESTINATION": "#8e44ad",
        "RELAY": "#20bf6b",
    }
    route_edges = {
        frozenset((route[index], route[index + 1]))
        for index in range(len(route or []) - 1)
    }

    for link in topology.links:
        first = topology.nodes[link.source]
        second = topology.nodes[link.destination]
        is_route = frozenset((link.source, link.destination)) in route_edges
        axis.plot(
            [first.x, second.x],
            [first.y, second.y],
            color="#e74c3c" if is_route else "#95a5a6",
            linewidth=3 if is_route else 1.2,
            linestyle="-" if is_route else "--",
            alpha=0.9,
            zorder=1,
        )

    for node in topology.nodes.values():
        available = node.is_available()
        axis.scatter(
            node.x,
            node.y,
            s=720 if node.node_type == "RELAY" else 850,
            color=colors[node.node_type] if available else "#7f8c8d",
            edgecolor="white",
            linewidth=2,
            zorder=2,
        )
        axis.text(
            node.x,
            node.y,
            node.node_id,
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            fontweight="bold",
            zorder=3,
        )
        if node.node_type == "RELAY":
            axis.text(
                node.x,
                node.y - 6.5,
                f"B:{node.battery:.0f}%  Q:{node.queue_length}",
                ha="center",
                va="top",
                fontsize=8,
                color="#2f3640",
                fontweight="bold",
                zorder=3,
            )

    route_text = " → ".join(route) if route else "No route available"
    axis.set_title(f"T{time_step}: {route_text}", fontweight="bold")
    axis.set_xlim(-10, 120)
    axis.set_ylim(-10, 120)
    axis.set_xlabel("X position (m)")
    axis.set_ylabel("Y position (m)")
    axis.grid(alpha=0.2)


def run_simulation(time_steps=11, communication_range=140.0):
    network = create_network()
    source = next(node for node in network.nodes if node.node_type == "SOURCE")
    relays = network.get_relays()
    snapshots = {}
    rows = []

    for time_step in range(time_steps):
        if time_step > 0:
            update_network(source, relays, time_step)

        topology = MANETTopology(network.nodes, communication_range)
        route, route_cost = topology.discover_route("S", "D")
        snapshot = topology.snapshot()
        rows.append(
            {
                "time_step": time_step,
                "active_nodes": snapshot["active_node_count"],
                "wireless_links": snapshot["link_count"],
                "route": " -> ".join(route) if route else "NO_ROUTE",
                "hop_count": len(route) - 1 if route else -1,
                "route_cost": route_cost if route else "",
            }
        )
        if time_step in (0, 5, 10):
            snapshots[time_step] = (deepcopy(topology), list(route) if route else None)

    return rows, snapshots


def save_outputs(rows, snapshots):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    figure, axes = plt.subplots(1, 3, figsize=(17, 5.5), sharex=True, sharey=True)
    for axis, time_step in zip(axes, (0, 5, 10)):
        topology, route = snapshots[time_step]
        draw_snapshot(axis, topology, route, time_step)
    figure.suptitle(
        "RelayNet Dynamic MANET: Neighbour Discovery and Multi-hop Routing",
        fontsize=15,
        fontweight="bold",
    )
    figure.tight_layout()
    figure.savefig(GRAPH_PATH, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main():
    print("=" * 68)
    print("       RelayNet Dynamic MANET Simulation")
    print("=" * 68)
    rows, snapshots = run_simulation()
    save_outputs(rows, snapshots)

    for row in rows:
        print(
            f"T{row['time_step']:02d} | active={row['active_nodes']} "
            f"links={row['wireless_links']:2d} | route={row['route']} "
            f"| hops={row['hop_count']}"
        )
    print(f"\nRouting log: {LOG_PATH}")
    print(f"Topology graph: {GRAPH_PATH}")


if __name__ == "__main__":
    main()
