"""Summarize and visualize RelayNet's multi-seed NS-3 experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


EXPECTED_COLUMNS = {
    "protocol",
    "scenario",
    "run",
    "pdr_percent",
    "loss_ratio_percent",
    "average_delay_ms",
    "average_jitter_ms",
    "throughput_kbps",
    "energy_consumed_j",
    "network_lifetime_s",
}

METRICS = {
    "pdr_percent": ("Packet Delivery Ratio", "%", True),
    "loss_ratio_percent": ("Packet Loss Ratio", "%", False),
    "average_delay_ms": ("Average End-to-End Delay", "ms", False),
    "average_jitter_ms": ("Average Jitter", "ms", False),
    "throughput_kbps": ("Throughput", "kbps", True),
    "energy_consumed_j": ("Energy Consumed", "J", False),
    "network_lifetime_s": ("Network Lifetime", "s", True),
}

SCENARIO_ORDER = [
    "normal",
    "high_mobility",
    "high_congestion",
    "low_battery",
    "relay_failure",
]
PROTOCOL_ORDER = ["AODV", "OLSR", "DSR"]
COLORS = {"AODV": "#2563eb", "OLSR": "#16a34a", "DSR": "#f97316"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="results/ns3_multiseed_final.csv",
        help="Detailed NS-3 CSV produced by relaynet-manet.cc",
    )
    parser.add_argument(
        "--output-dir",
        default="results/ns3_analysis",
        help="Directory for summaries and charts",
    )
    return parser.parse_args()


def validate(data: pd.DataFrame) -> None:
    missing = EXPECTED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    duplicates = data.duplicated(["scenario", "protocol", "run"])
    if duplicates.any():
        rows = data.loc[duplicates, ["scenario", "protocol", "run"]]
        raise ValueError(f"Duplicate scenario/protocol/run rows found:\n{rows}")

    combinations = data.groupby(["scenario", "protocol"]).size()
    incomplete = combinations[combinations != 10]
    if not incomplete.empty:
        print("WARNING: Expected 10 runs per scenario/protocol; incomplete groups:")
        print(incomplete.to_string())


def build_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = data.groupby(["scenario", "protocol"])[list(METRICS)].agg(
        ["mean", "std"]
    )
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    return summary.reset_index()


def build_rankings(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario, group in summary.groupby("scenario"):
        for metric, (_, _, higher_is_better) in METRICS.items():
            ordered = group.sort_values(
                f"{metric}_mean", ascending=not higher_is_better
            ).reset_index(drop=True)
            for rank, record in ordered.iterrows():
                rows.append(
                    {
                        "scenario": scenario,
                        "metric": metric,
                        "rank": rank + 1,
                        "protocol": record["protocol"],
                        "mean": record[f"{metric}_mean"],
                        "std": record[f"{metric}_std"],
                    }
                )
    return pd.DataFrame(rows)


def plot_metric(summary: pd.DataFrame, metric: str, output_dir: Path) -> None:
    title, unit, _ = METRICS[metric]
    means = summary.pivot(index="scenario", columns="protocol", values=f"{metric}_mean")
    errors = summary.pivot(index="scenario", columns="protocol", values=f"{metric}_std")
    means = means.reindex(index=SCENARIO_ORDER, columns=PROTOCOL_ORDER)
    errors = errors.reindex(index=SCENARIO_ORDER, columns=PROTOCOL_ORDER).fillna(0)

    figure, axis = plt.subplots(figsize=(11, 6.2))
    means.plot(
        kind="bar",
        yerr=errors,
        capsize=3,
        color=[COLORS[name] for name in PROTOCOL_ORDER],
        edgecolor="#111827",
        linewidth=0.4,
        ax=axis,
    )
    axis.set_title(f"NS-3 Multi-Seed Comparison: {title}", fontsize=15, weight="bold")
    axis.set_xlabel("Scenario")
    axis.set_ylabel(f"{title} ({unit})")
    axis.set_xticklabels(
        [label.replace("_", " ").title() for label in SCENARIO_ORDER], rotation=18
    )
    axis.grid(axis="y", alpha=0.25)
    axis.legend(title="Protocol", frameon=False, ncol=3)
    figure.tight_layout()
    figure.savefig(output_dir / f"ns3_{metric}.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(input_path)
    validate(data)
    summary = build_summary(data)
    rankings = build_rankings(summary)

    summary_path = output_dir / "ns3_multiseed_summary.csv"
    rankings_path = output_dir / "ns3_protocol_rankings.csv"
    summary.to_csv(summary_path, index=False)
    rankings.to_csv(rankings_path, index=False)

    for metric in METRICS:
        plot_metric(summary, metric, output_dir)

    print("=" * 72)
    print("RelayNet NS-3 Multi-Seed Analysis")
    print("=" * 72)
    print(f"Input rows: {len(data)}")
    print(f"Summary: {summary_path}")
    print(f"Rankings: {rankings_path}")
    print(f"Charts: {len(METRICS)} saved in {output_dir}")
    print("\nPDR means (%):")
    pdr = summary.pivot(index="scenario", columns="protocol", values="pdr_percent_mean")
    print(pdr.reindex(index=SCENARIO_ORDER, columns=PROTOCOL_ORDER).round(3).to_string())


if __name__ == "__main__":
    main()
