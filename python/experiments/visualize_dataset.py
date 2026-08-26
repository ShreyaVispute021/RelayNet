import pandas as pd
import matplotlib.pyplot as plt


DATASET_PATH = "data/relaynet_simulation.csv"


def main():

    df = pd.read_csv(DATASET_PATH)

    plt.figure(figsize=(10, 6))

    for relay_id in df["relay_id"].unique():

        relay_data = df[df["relay_id"] == relay_id]

        plt.plot(
            relay_data["time_step"],
            relay_data["score"],
            marker="o",
            label=relay_id
        )

    # Mark selected relays
    selected = df[df["selected"] == True]

    for _, row in selected.iterrows():

        plt.scatter(
            row["time_step"],
            row["score"],
            s=100,
            marker="*"
        )

    plt.title("RelayNet: Relay Score Over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Relay Score")

    plt.xticks(
        sorted(df["time_step"].unique())
    )

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    output_path = "results/relay_scores.png"

    plt.savefig(output_path)

    print(f"Graph saved to: {output_path}")

    plt.show()


if __name__ == "__main__":
    main()