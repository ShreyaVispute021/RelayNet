import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt

from python.experiments.kg_marl_experiment import train_agents
from python.experiments.scenario_experiment import run_scenario
from python.relaynet.scenarios import SCENARIOS


METHODS = ("static", "baseline", "contextual_kg", "kg_marl")
METRICS = (
    "pdr",
    "loss_ratio",
    "average_delay",
    "throughput_kbps",
    "energy_consumed",
    "network_lifetime_steps",
)
RESULTS_DIR = Path("results")
DETAILED_PATH = RESULTS_DIR / "multi_seed_detailed.csv"
SUMMARY_PATH = RESULTS_DIR / "multi_seed_summary.csv"


def evaluate_seeds(learner, seeds=range(40, 50), total_packets=1000):
    detailed = []

    for seed in seeds:
        for scenario in SCENARIOS:
            for method in METHODS:
                result = run_scenario(
                    scenario,
                    total_packets=total_packets,
                    selection_method=method,
                    learner=learner,
                    training=False,
                    seed=seed,
                )
                row = {
                    key: value
                    for key, value in result.items()
                    if key != "relay_selections"
                }
                row["seed"] = seed
                detailed.append(row)

    return detailed


def summarize(detailed):
    groups = defaultdict(list)
    for row in detailed:
        groups[(row["scenario"], row["selection_method"])].append(row)

    summary = []
    for (scenario, method), rows in groups.items():
        item = {
            "scenario": scenario,
            "selection_method": method,
            "runs": len(rows),
        }
        for metric in METRICS:
            values = [float(row[metric]) for row in rows]
            item[f"{metric}_mean"] = mean(values)
            item[f"{metric}_std"] = stdev(values) if len(values) > 1 else 0.0
        summary.append(item)

    scenario_order = {item.name: index for index, item in enumerate(SCENARIOS)}
    method_order = {method: index for index, method in enumerate(METHODS)}
    summary.sort(
        key=lambda row: (
            scenario_order[row["scenario"]],
            method_order[row["selection_method"]],
        )
    )
    return summary


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def create_charts(summary):
    labels = [scenario.name.replace("_", " ").title() for scenario in SCENARIOS]
    colors = {
        "static": "#7f8c8d",
        "baseline": "#3498db",
        "contextual_kg": "#f39c12",
        "kg_marl": "#2ecc71",
    }
    titles = {
        "pdr": "Packet Delivery Ratio",
        "loss_ratio": "Packet Loss Ratio",
        "average_delay": "Average End-to-End Delay",
        "throughput_kbps": "Network Throughput",
        "energy_consumed": "Total UAV Energy Consumption",
        "network_lifetime_steps": "Network Lifetime",
    }
    ylabels = {
        "pdr": "Ratio",
        "loss_ratio": "Ratio",
        "average_delay": "Time steps",
        "throughput_kbps": "kbps",
        "energy_consumed": "Battery units",
        "network_lifetime_steps": "Time steps",
    }

    lookup = {
        (row["scenario"], row["selection_method"]): row
        for row in summary
    }
    x_positions = list(range(len(SCENARIOS)))
    width = 0.19

    for metric in METRICS:
        fig, axis = plt.subplots(figsize=(12, 6))
        for method_index, method in enumerate(METHODS):
            values = [
                lookup[(scenario.name, method)][f"{metric}_mean"]
                for scenario in SCENARIOS
            ]
            errors = [
                lookup[(scenario.name, method)][f"{metric}_std"]
                for scenario in SCENARIOS
            ]
            positions = [
                x + (method_index - 1.5) * width
                for x in x_positions
            ]
            axis.bar(
                positions,
                values,
                width,
                yerr=errors,
                capsize=3,
                label=method.replace("_", " ").upper(),
                color=colors[method],
            )

        axis.set_title(f"RelayNet: {titles[metric]} (10-Seed Mean)")
        axis.set_ylabel(ylabels[metric])
        axis.set_xticks(x_positions)
        axis.set_xticklabels(labels)
        axis.grid(axis="y", alpha=0.25)
        axis.legend(ncol=4, fontsize=9)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f"multi_seed_{metric}.png", dpi=200)
        plt.close(fig)


def print_summary(summary):
    print("\n10-seed average results:")
    print("-" * 112)
    for row in summary:
        print(
            f"{row['scenario']:20s} {row['selection_method']:14s} "
            f"PDR={row['pdr_mean']:.2%}±{row['pdr_std']:.2%} "
            f"Delay={row['average_delay_mean']:.2f} "
            f"Throughput={row['throughput_kbps_mean']:.3f}kbps "
            f"Energy={row['energy_consumed_mean']:.2f} "
            f"Lifetime={row['network_lifetime_steps_mean']:.1f}"
        )


def main():
    print("=" * 76)
    print("       RelayNet Multi-Seed Evaluation")
    print("=" * 76)
    print("Training KG-assisted independent Q-learning agents...")
    learner = train_agents()
    print("Evaluating 10 random seeds across all scenarios and methods...")

    detailed = evaluate_seeds(learner)
    summary = summarize(detailed)
    save_csv(DETAILED_PATH, detailed)
    save_csv(SUMMARY_PATH, summary)
    create_charts(summary)
    print_summary(summary)

    print(f"\nDetailed results: {DETAILED_PATH}")
    print(f"Summary results:  {SUMMARY_PATH}")
    print("Six comparison charts saved in results/.")


if __name__ == "__main__":
    main()
