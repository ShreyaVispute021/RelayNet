from python.relaynet.packet import Packet
from python.relaynet.traffic import TrafficGenerator


def main():

    traffic = TrafficGenerator()

    print("==============================================")
    print("       RelayNet Packet Flow Test")
    print("==============================================")

    packets = []

    for time_step in range(5):

        packet = traffic.generate_packet(
            source="S",
            destination="D",
            time_step=time_step
        )

        packets.append(packet)

        print(
            f"Time {time_step}: "
            f"Generated Packet {packet.packet_id}"
        )

    print("\nPacket Summary")

    for packet in packets:

        print(
            f"Packet {packet.packet_id}: "
            f"{packet.source} -> {packet.destination}, "
            f"created at t={packet.creation_time}"
        )


if __name__ == "__main__":
    main()