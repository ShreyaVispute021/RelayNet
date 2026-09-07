import csv
from pathlib import Path

from python.experiments.scenario_experiment import run_scenario
from python.relaynet.scenarios import SCENARIOS


METHODS = ("baseline", "contextual_kg")
OUTPUT_PATH = Path("results/contextual_routing_comparison.csv")


def run_comparison(total_packets=1000):
    results = []

    for scenario in SCENARIOS:
        for method in METHODS:
            result = run_scenario(
                scenario,
                total_packets=total_packets,
                selection_method=method,
            )
            results.append(result)

    return results


def save_results(results):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for result in results:
        row = {
            key: value
            for key, value in result.items()
            if key != "relay_selections"
        }
        row.update(
            {
                f"{relay_id.lower()}_selections": count
                for relay_id, count in result["relay_selections"].items()
            }
        )
        rows.append(row)

    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 70)
    print("       RelayNet Baseline vs Contextual KG Routing")
    print("=" * 70)

    results = run_comparison()
    save_results(results)

    for result in results:
        print(
            f"{result['scenario']:20s} "
            f"{result['selection_method']:14s} "
            f"PDR={result['pdr']:.2%} "
            f"Loss={result['loss_ratio']:.2%} "
            f"Delay={result['average_delay']:.2f} "
            f"Selections={result['relay_selections']}"
        )

    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
