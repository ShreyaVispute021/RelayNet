import pandas as pd


DATASET_PATH = "data/relaynet_simulation.csv"


def main():

    df = pd.read_csv(DATASET_PATH)

    print("==============================================")
    print("        RelayNet Dataset Analysis")
    print("==============================================")

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(list(df.columns))

    print("\nFirst 10 rows:")
    print(df.head(10))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nRelay selection count:")

    selected = df[df["selected"] == True]

    print(
        selected["relay_id"]
        .value_counts()
    )

    print("\nAverage relay scores:")

    print(
        df.groupby("relay_id")["score"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\nAverage battery:")

    print(
        df.groupby("relay_id")["battery"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\nAvailable relay counts:")

    print(
        df.groupby("relay_id")["available"]
        .sum()
    )


if __name__ == "__main__":
    main()