from python.relaynet.network import Node
from python.relaynet.mobility import (
    calculate_distance,
    calculate_rssi,
    move_node,
)


def main():

    source = Node(
        node_id="S",
        node_type="SOURCE",
        x=0,
        y=0,
        battery=100,
        rssi=-40,
        queue_length=0,
        mobility=0,
        link_stability=1,
        hop_count=0
    )

    relay = Node(
        node_id="R1",
        node_type="RELAY",
        x=20,
        y=20,
        battery=80,
        rssi=-50,
        queue_length=5,
        mobility=0.3,
        link_stability=0.9,
        hop_count=2
    )

    print("===== Mobility Test =====")

    for time_step in range(6):

        distance = calculate_distance(
            source,
            relay
        )

        rssi = calculate_rssi(
            source,
            relay
        )

        print(
            f"Time {time_step}: "
            f"Position=({relay.x:.1f}, {relay.y:.1f}), "
            f"Distance={distance:.2f}, "
            f"RSSI={rssi:.2f} dBm"
        )

        # Move relay farther away.
        move_node(
            relay,
            dx=10,
            dy=5
        )


if __name__ == "__main__":
    main()