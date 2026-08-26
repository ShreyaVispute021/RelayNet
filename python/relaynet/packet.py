from dataclasses import dataclass


@dataclass
class Packet:
    packet_id: int
    source: str
    destination: str
    creation_time: int
    delivery_time: int | None = None
    delivered: bool = False
    relay_id: str | None = None

    def deliver(self, time_step, relay_id):
        self.delivery_time = time_step
        self.delivered = True
        self.relay_id = relay_id

    def delay(self):
        if not self.delivered:
            return None

        return self.delivery_time - self.creation_time