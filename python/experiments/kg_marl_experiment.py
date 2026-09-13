import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from python.experiments.scenario_experiment import run_scenario
from python.relaynet.marl_agent import MultiAgentRelayLearner
from python.relaynet.rl_config import RLConfig
from python.relaynet.scenarios import SCENARIOS


RESULTS_PATH = Path("results/kg_marl_comparison.csv")
MODEL_PATH = Path("results/marl_q_tables.csv")
PARAMETERS_PATH = Path("results/rl_parameters.json")
TRAINING_METRICS_PATH = Path("results/rl_training_metrics.csv")
TRAINING_GRAPH_PATH = Path("results/rl_training_progress.png")


def train_agents(
    episodes=None,
    packets_per_episode=None,
    config=None,
    collect_metrics=False,
):
    config = config or RLConfig()
    episodes = config.training_episodes if episodes is None else episodes
    packets_per_episode = (
        config.packets_per_episode
        if packets_per_episode is None
        else packets_per_episode
    )
    learner = MultiAgentRelayLearner(config=config)
    training_metrics = []

    for episode in range(episodes):
        episode_results = []
        for scenario_index, scenario in enumerate(SCENARIOS):
            result = run_scenario(
                scenario,
                total_packets=packets_per_episode,
                selection_method="kg_marl",
                learner=learner,
                training=True,
                seed=1000 + episode * len(SCENARIOS) + scenario_index,
            )
            episode_results.append(result)
        learner.decay_exploration()

        updates = sum(result["training_updates"] for result in episode_results)
        delivered = sum(result["delivered"] for result in episode_results)
        total_reward = sum(result["training_reward"] for result in episode_results)
        weighted_td_error = sum(
            result["mean_abs_td_error"] * result["training_updates"]
            for result in episode_results
        )
        training_metrics.append(
            {
                "episode": episode + 1,
                "epsilon": learner.epsilon,
                "average_reward": total_reward / updates if updates else 0.0,
                "delivery_success_rate": delivered / (packets_per_episode * len(SCENARIOS)),
                "mean_abs_td_error": weighted_td_error / updates if updates else 0.0,
                "q_table_entries": learner.q_table_size(),
                "updates": updates,
            }
        )

    if collect_metrics:
        return learner, training_metrics
    return learner


def save_training_artifacts(config, metrics):
    PARAMETERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PARAMETERS_PATH.open("w") as file:
        json.dump(config.as_dict(), file, indent=2)

    with TRAINING_METRICS_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=metrics[0].keys())
        writer.writeheader()
        writer.writerows(metrics)

    episodes = [row["episode"] for row in metrics]
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    series = (
        ("average_reward", "Average reward", "#2e86de"),
        ("delivery_success_rate", "Training delivery rate", "#20bf6b"),
        ("mean_abs_td_error", "Mean absolute TD error", "#eb3b5a"),
        ("epsilon", "Exploration rate (epsilon)", "#8854d0"),
    )
    for axis, (key, title, color) in zip(axes.flat, series):
        axis.plot(episodes, [row[key] for row in metrics], color=color, linewidth=2)
        axis.set_title(title)
        axis.set_xlabel("Training episode")
        axis.grid(alpha=0.25)
    figure.suptitle("RelayNet Q-Learning Training Metrics", fontsize=15, fontweight="bold")
    figure.tight_layout()
    figure.savefig(TRAINING_GRAPH_PATH, dpi=200, bbox_inches="tight")
    plt.close(figure)


def print_parameters(config):
    print("\nRL parameters:")
    print("-" * 52)
    for name, value in config.as_dict().items():
        print(f"{name:28s}: {value}")


def evaluate(learner, total_packets=1000):
    results = []
    for scenario in SCENARIOS:
        for method in (
            "static",
            "baseline",
            "contextual_kg",
            "kg_marl",
        ):
            result = run_scenario(
                scenario,
                total_packets=total_packets,
                selection_method=method,
                learner=learner,
                training=False,
                seed=42,
            )
            results.append(result)
    return results


def save_results(results):
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
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

    with RESULTS_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 76)
    print("       RelayNet Knowledge Graph + Multi-Agent Q-Learning")
    print("=" * 76)

    config = RLConfig()
    print_parameters(config)
    print("\nTraining independent relay agents...")
    learner, training_metrics = train_agents(
        config=config,
        collect_metrics=True,
    )
    learner.save(MODEL_PATH)
    save_training_artifacts(config, training_metrics)
    results = evaluate(learner)
    save_results(results)

    print(f"Learned Q-table entries: {learner.q_table_size()}")
    print("\nFinal evaluation (same seed and traffic for every method):")
    for result in results:
        print(
            f"{result['scenario']:20s} "
            f"{result['selection_method']:14s} "
            f"PDR={result['pdr']:.2%} "
            f"Loss={result['loss_ratio']:.2%} "
            f"Delay={result['average_delay']:.2f} "
            f"Throughput={result['throughput_kbps']:.3f}kbps "
            f"Energy={result['energy_consumed']:.2f} "
            f"Lifetime={result['network_lifetime_steps']}"
        )

    print(f"\nResults saved to {RESULTS_PATH}")
    print(f"Learned model saved to {MODEL_PATH}")
    print(f"RL parameters saved to {PARAMETERS_PATH}")
    print(f"Training metrics saved to {TRAINING_METRICS_PATH}")
    print(f"Training graph saved to {TRAINING_GRAPH_PATH}")


if __name__ == "__main__":
    main()
