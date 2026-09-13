import csv
from collections import defaultdict
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt


KG_PATH = Path("results/relaynet_knowledge_graph.csv")
OUTPUT_PATH = Path("results/kg_simulation_graph.png")
DISPLAY_PREDICATES = {
    "HAS_BATTERY",
    "HAS_RSSI",
    "HAS_QUEUE_LENGTH",
    "HAS_CONTEXT",
    "HAS_RECOMMENDATION",
    "HAS_CONTEXTUAL_SCORE",
}


def load_state_triples(time_step):
    states = defaultdict(list)
    with KG_PATH.open(newline="") as file:
        for row in csv.DictReader(file):
            subject = row["subject"]
            if not subject.endswith(f":T{time_step}"):
                continue
            if row["predicate"] in DISPLAY_PREDICATES:
                states[subject].append((row["predicate"], row["object"]))
    return states


def short_predicate(predicate):
    return predicate.replace("HAS_", "").replace("_", " ").title()


def draw_state_graph(axis, states, time_step):
    relay_x = {"R1": 0.16, "R2": 0.50, "R3": 0.84}
    colors = {"PREFER": "#20bf6b", "CAUTION": "#f7b731", "AVOID": "#eb3b5a"}

    for subject, triples in sorted(states.items()):
        relay_id = subject.split(":")[1]
        x = relay_x.get(relay_id, 0.5)
        recommendation = next(
            (value for predicate, value in triples if predicate == "HAS_RECOMMENDATION"),
            "CAUTION",
        )
        axis.scatter(
            x,
            0.83,
            s=1200,
            color=colors.get(recommendation, "#778ca3"),
            edgecolor="white",
            linewidth=2,
            zorder=3,
        )
        axis.text(x, 0.83, relay_id, ha="center", va="center", color="white", fontweight="bold")

        values = defaultdict(list)
        for predicate, value in triples:
            values[predicate].append(value)
        details = []
        for predicate in (
            "HAS_RECOMMENDATION",
            "HAS_CONTEXTUAL_SCORE",
            "HAS_BATTERY",
            "HAS_RSSI",
            "HAS_QUEUE_LENGTH",
        ):
            if values[predicate]:
                value = values[predicate][0]
                if predicate == "HAS_CONTEXTUAL_SCORE":
                    value = f"{float(value):.3f}"
                elif predicate in ("HAS_BATTERY", "HAS_RSSI"):
                    value = f"{float(value):.1f}"
                details.append(f"{short_predicate(predicate)}: {value}")
        contexts = values["HAS_CONTEXT"][:3]
        if contexts:
            context_text = "Context: " + ", ".join(
                value.replace("_", " ") for value in contexts
            )
            details.append(fill(context_text, width=34))

        axis.plot([x, x], [0.76, 0.57], color="#a5b1c2", linewidth=1.5, zorder=1)
        axis.text(
            x,
            0.50,
            "\n".join(details),
            ha="center",
            va="center",
            fontsize=8.0,
            bbox={"boxstyle": "round,pad=0.6", "fc": "#f5f6fa", "ec": "#a5b1c2"},
        )

    axis.set_title(f"Temporal KG snapshot at T{time_step}", fontweight="bold")
    axis.set_xlim(0, 1)
    axis.set_ylim(0.18, 1.0)
    axis.axis("off")


def main():
    if not KG_PATH.exists():
        raise FileNotFoundError(
            f"{KG_PATH} not found. Run: python -m python.relaynet.knowledge_graph"
        )

    figure, axes = plt.subplots(3, 1, figsize=(15, 13))
    for axis, time_step in zip(axes, (0, 5, 10)):
        states = load_state_triples(time_step)
        if not states:
            raise ValueError(f"No Knowledge Graph states found for T{time_step}")
        draw_state_graph(axis, states, time_step)
    figure.suptitle(
        "RelayNet Knowledge Graph Simulation: State, Context and Recommendation",
        fontsize=16,
        fontweight="bold",
    )
    figure.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")
    plt.close(figure)
    print(f"Knowledge Graph visualization saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
