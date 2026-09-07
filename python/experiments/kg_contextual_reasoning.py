from python.relaynet.kg_relay_selector import KGRRelaySelector


def main():

    print("==============================================")
    print("     RelayNet KG Contextual Reasoning")
    print("==============================================")

    kg_path = (
        "results/relaynet_knowledge_graph.csv"
    )

    selector = KGRRelaySelector(
        kg_path
    )

    for time_step in [0, 5, 10]:

        print()
        print(f"Time Step: T{time_step}")
        print("----------------------------------------------")

        ranking = selector.get_ranking(
            time_step
        )

        if not ranking:
            print("No relay states available.")
            continue

        for index, relay in enumerate(
            ranking,
            start=1
        ):

            print(
                f"{index}. "
                f"{relay['relay_id']} | "
                f"Recommendation: "
                f"{relay['recommendation']} | "
                f"Context Score: "
                f"{relay['contextual_score']:.4f}"
            )

            print(
                f"   Reason: "
                f"{relay['explanation']}"
            )

        relay_id, score = selector.select_relay(
            time_step
        )

        print()
        print(
            f"Selected Relay: {relay_id} | "
            f"Context Score: {score:.4f}"
        )


if __name__ == "__main__":
    main()