from python.relaynet.packet import Packet


class TrafficGenerator:

    def __init__(self):
        self.next_packet_id = 1

    def generate_packet(
        self,
        source="S",
        destination="D",
        time_step=0
    ):
        packet = Packet(
            packet_id=self.next_packet_id,
            source=source,
            destination=destination,
            creation_time=time_step
        )

        self.next_packet_id += 1

        return packet