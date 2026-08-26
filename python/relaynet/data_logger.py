import csv
from pathlib import Path


class DataLogger:

    def __init__(self, filename="data/relaynet_simulation.csv"):

        self.filename = Path(filename)

        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file = open(
            self.filename,
            "w",
            newline=""
        )

        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "time_step",
            "relay_id",
            "rssi",
            "battery",
            "queue_length",
            "mobility",
            "link_stability",
            "hop_count",
            "score",
            "selected",
            "available"
        ])

    def log_relay(
        self,
        time_step,
        relay,
        score,
        selected
    ):

        self.writer.writerow([
            time_step,
            relay.node_id,
            relay.rssi,
            relay.battery,
            relay.queue_length,
            relay.mobility,
            relay.link_stability,
            relay.hop_count,
            round(score, 4),
            selected,
            relay.is_available()
        ])

        self.file.flush()

    def close(self):
        self.file.close()