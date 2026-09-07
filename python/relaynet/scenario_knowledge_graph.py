import csv
from pathlib import Path


class ScenarioKnowledgeGraph:
    def __init__(self):
        self.triples = []

    def add_triple(self, subject, predicate, object_value):
        self.triples.append((subject, predicate, object_value))

    def add_scenario(self, row):
        scenario_name = row["scenario"]
        scenario = f"Scenario:{scenario_name}"

        self.add_triple(
            scenario,
            "HAS_PACKET_COUNT",
            int(row["packets"])
        )

        self.add_triple(
            scenario,
            "HAS_DELIVERED_PACKETS",
            int(row["delivered"])
        )

        self.add_triple(
            scenario,
            "HAS_LOST_PACKETS",
            int(row["lost"])
        )

        self.add_triple(
            scenario,
            "HAS_PDR",
            float(row["pdr"])
        )

        self.add_triple(
            scenario,
            "HAS_PACKET_LOSS",
            float(row["loss_ratio"])
        )

        self.add_triple(
            scenario,
            "HAS_AVERAGE_DELAY",
            float(row["average_delay"])
        )

    def load_csv(self, csv_path):
        with open(csv_path, "r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                self.add_scenario(row)

    def get_triples(self):
        return self.triples

    def save_triples(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(["subject", "predicate", "object"])

            for triple in self.triples:
                writer.writerow(triple)


if __name__ == "__main__":
    graph = ScenarioKnowledgeGraph()

    graph.load_csv("results/scenario_results.csv")

    print("==============================================")
    print("    RelayNet Scenario Knowledge Graph")
    print("==============================================")
    print(f"Total triples: {len(graph.get_triples())}")

    for triple in graph.get_triples():
        print(triple)

    graph.save_triples(
        "results/relaynet_scenario_knowledge_graph.csv"
    )

    print("\nScenario Knowledge Graph exported successfully.")