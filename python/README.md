# RelayNet

RelayNet is a simulation-based prototype for Knowledge Graph-assisted,
multi-agent reinforcement learning (MARL) relay selection in UAV-supported
mobile ad hoc networks for disaster communication.

## Implemented pipeline

1. Simulated ground source and destination nodes with three UAV relay agents.
2. Dynamic state collection: RSSI, battery, queue length, mobility, link
   stability, hop count, platform, and altitude.
3. Temporal Knowledge Graph construction and querying.
4. Explainable contextual recommendations: `PREFER`, `CAUTION`, and `AVOID`.
5. Independent Q-learning agents with one Q-table per UAV relay.
6. Dynamic relay selection using learned values and KG contextual scores.
7. Evaluation in normal, high-mobility, high-congestion, low-battery, and
   relay-failure scenarios.

## Compared methods

- `static`: fixed hop-count selection without context or learning.
- `baseline`: adaptive weighted scoring.
- `contextual_kg`: KG-derived contextual rule reasoning.
- `kg_marl`: contextual KG score combined with independent Q-learning.

## Metrics

- Packet Delivery Ratio (PDR)
- Packet loss ratio
- Average end-to-end delay
- Throughput (kbps)
- UAV energy consumption
- Network lifetime

## Run

Run all commands from the repository root:

```bash
python -m python.experiments.dynamic_scenario
python -m python.relaynet.knowledge_graph
python -m python.experiments.kg_contextual_reasoning
python -m python.experiments.kg_marl_experiment
python -m python.experiments.multi_seed_evaluation
```

Generated datasets, Q-tables, summaries, and charts are stored in `results/`.

## Prototype scope

The current implementation uses a custom Python simulator, CSV-based temporal
Knowledge Graph, software-simulated UAVs, and independent tabular Q-learning.
NS-3, Neo4j, AirSim, real UAV deployment, and deep MARL algorithms such as
MADDPG remain future extensions.
