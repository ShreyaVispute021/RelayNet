import csv
from pathlib import Path

from python.experiments.scenario_experiment import run_scenario
from python.relaynet.marl_agent import MultiAgentRelayLearner
from python.relaynet.scenarios import SCENARIOS


RESULTS_PATH = Path("results/kg_marl_comparison.csv")
MODEL_PATH = Path("results/marl_q_tables.csv")


def train_agents(episodes=60, packets_per_episode=250):
    learner = MultiAgentRelayLearner()

    for episode in range(episodes):
        for scenario_index, scenario in enumerate(SCENARIOS):
            run_scenario(
                scenario,
                total_packets=packets_per_episode,
                selection_method="kg_marl",
                learner=learner,
                training=True,
                seed=1000 + episode * len(SCENARIOS) + scenario_index,
            )
        learner.decay_exploration()

    return learner


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
    print("Training independent relay agents...")

    learner = train_agents()
    learner.save(MODEL_PATH)
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


if __name__ == "__main__":
    main()
