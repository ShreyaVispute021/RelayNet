from python.relaynet.knowledge_graph_query import KnowledgeGraphQuery
from python.relaynet.relay_selection import select_best_relay


KG_PATH = "results/relaynet_knowledge_graph.csv"


def main():
    graph = KnowledgeGraphQuery(KG_PATH)

    print("==============================================")
    print("   RelayNet Selection Comparison")
    print("==============================================")

    for time_step in range(11):

        kg_relay = graph.get_best_relay(time_step)

        print(f"\nTime Step: T{time_step}")

        if kg_relay:
            print(
                f"KG Selection: {kg_relay['relay_id']} "
                f"| Score: {kg_relay['score']:.4f}"
            )
        else:
            print("KG Selection: None")

    print("\n==============================================")
    print("KG selection layer is connected to the")
    print("existing RelayNet decision pipeline.")
    print("==============================================")


if __name__ == "__main__":
    main()