import csv
import matplotlib.pyplot as plt


def load_results():
    results = []

    with open("results/scenario_results.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            results.append({
                "scenario": row["scenario"],
                "pdr": float(row["pdr"]) * 100,
                "loss": float(row["loss_ratio"]) * 100,
                "delay": float(row["average_delay"])
            })

    return results


def plot_pdr(results):
    scenarios = [r["scenario"] for r in results]
    pdr = [r["pdr"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, pdr)

    plt.xlabel("Scenario")
    plt.ylabel("Packet Delivery Ratio (%)")
    plt.title("Packet Delivery Ratio Across Scenarios")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig("results/pdr_comparison.png")
    plt.close()


def plot_loss(results):
    scenarios = [r["scenario"] for r in results]
    loss = [r["loss"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, loss)

    plt.xlabel("Scenario")
    plt.ylabel("Packet Loss (%)")
    plt.title("Packet Loss Across Scenarios")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig("results/loss_comparison.png")
    plt.close()


def plot_delay(results):
    scenarios = [r["scenario"] for r in results]
    delay = [r["delay"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.bar(scenarios, delay)

    plt.xlabel("Scenario")
    plt.ylabel("Average Delay")
    plt.title("Average Packet Delay Across Scenarios")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig("results/delay_comparison.png")
    plt.close()


def main():
    results = load_results()

    plot_pdr(results)
    plot_loss(results)
    plot_delay(results)

    print("==============================================")
    print("       RelayNet Evaluation Complete")
    print("==============================================")
    print("Generated:")
    print("results/pdr_comparison.png")
    print("results/loss_comparison.png")
    print("results/delay_comparison.png")


if __name__ == "__main__":
    main()