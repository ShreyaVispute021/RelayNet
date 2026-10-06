# RelayNet --- Adaptive Emergency Mesh Routing Protocol (AEMRP)

**MeshMinds · B.Tech CSE · VIT Vellore**

RelayNet is a semester-level research prototype for adaptive emergency
communication in disaster environments where cellular towers, wired
networks, or normal communication infrastructure may be damaged. It
models ground devices communicating through mobile UAV relay nodes and
evaluates adaptive relay selection using network context, a temporal
Knowledge Graph (KG), and independent multi-agent Q-learning.

> **Scope:** AEMRP/KG+MARL is implemented in Python. NS-3 is used as an
> independent MANET baseline-validation layer for AODV, OLSR, and DSR.
> KG+RL is not implemented natively inside NS-3.

## Repository

https://github.com/ShreyaVispute021/RelayNet

## Architecture

``` text
Dynamic Disaster MANET
        ↓
Network Observations
(RSSI, battery, queue, mobility, stability, hops)
        ↓
Temporal Knowledge Graph
        ↓
Contextual Reasoning
        ↓
Independent Multi-Agent Q-Learning
        ↓
Relay Selection
        ↓
Packet Forwarding
        ↓
Performance Evaluation
```

Independent NS-3 validation:

``` text
NS-3.47
  ├── AODV
  ├── OLSR
  └── DSR
        ↓
5 scenarios × 10 runs/protocol
        ↓
Statistical analysis
```

## Features

### Dynamic MANET

-   Source, destination, and three UAV relays: R1, R2, R3
-   Automatic neighbour discovery
-   3-D wireless-distance calculation
-   Dynamic wireless links
-   Link-cost calculation
-   Dijkstra multi-hop route discovery
-   Relay-failure handling
-   Mobility and link-stability changes
-   MANET topology visualization
-   Routing-log export

### Relay-selection methods

  Method          Description
  --------------- -----------------------------------------
  Static          Fixed/static relay selection
  Baseline        Weighted network-condition score
  Contextual KG   Knowledge-Graph contextual reasoning
  KG + MARL       KG score combined with learned Q-values

Weighted baseline:

-   RSSI: 25%
-   Battery: 20%
-   Queue: 15%
-   Mobility: 10%
-   Link stability: 20%
-   Hop count: 10%

### Temporal Knowledge Graph

The KG uses temporal subject--predicate--object triples stored in CSV.

Predicates include `HAS_RSSI`, `HAS_BATTERY`, `HAS_QUEUE_LENGTH`,
`HAS_MOBILITY`, `HAS_LINK_STABILITY`, `HAS_HOP_COUNT`, `HAS_SCORE`,
`SELECTED`, `AVAILABLE`, and `HAS_CONTEXT`.

Derived facts include `SUFFICIENT_BATTERY`, `LOW_QUEUE`, `STABLE_LINK`,
`LOW_MOBILITY`, and `STRONG_RSSI`.

Verified KG:

-   330 raw temporal triples
-   216 derived contextual triples
-   546 total triples

Relay recommendations are classified as `PREFER`, `CAUTION`, or `AVOID`.

The current KG uses CSV storage and Python visualization. **Neo4j is
future work.**

### Multi-agent Q-learning

Each UAV relay maintains an independent Q-table.

``` text
FinalScore = 0.65 × KGScore + 0.35 × QScore
```

Verified parameters:

  Parameter                   Value
  ------------------------- -------
  Learning rate                0.15
  Discount factor              0.90
  Epsilon start                0.20
  Epsilon decay                0.97
  Epsilon minimum              0.02
  KG weight                    0.65
  Training episodes              60
  Packets / episode             250
  Success reward                4.0
  Failure reward               -1.0
  Stability reward weight       0.4
  Battery reward weight        0.25
  Queue penalty weight          0.5
  Random seed                    42

The verified training run learned 44 Q-table entries.

## Scenarios

1.  `normal`
2.  `high_mobility`
3.  `high_congestion`
4.  `low_battery`
5.  `relay_failure`

## Python Evaluation

The complete evaluation contains:

**5 scenarios × 4 methods × 10 seeds = 200 runs**

Metrics:

-   Packet Delivery Ratio
-   Packet-loss ratio
-   Average delay
-   Throughput
-   Energy consumption
-   Network lifetime

### Selected results

#### Normal

  Method                           PDR
  ------------------- ----------------
  Static                27.81% ± 1.87%
  Weighted Baseline     28.52% ± 1.82%
  Contextual KG         28.35% ± 1.84%
  KG + MARL             28.51% ± 1.91%

#### High Mobility

  Method                               PDR
  ------------------- --------------------
  Static                    19.93% ± 1.50%
  Weighted Baseline         20.43% ± 1.49%
  Contextual KG             20.43% ± 1.47%
  KG + MARL             **20.48% ± 1.44%**

KG + MARL achieves the best PDR and throughput in high mobility, but it
does not win in every scenario. Under low-battery conditions it
currently underperforms simpler methods.

**Conclusion:** KG-assisted multi-agent Q-learning provides adaptive and
competitive relay selection, particularly under high mobility. The
current reward function requires further optimization for low-battery
conditions.

## NS-3.47 Validation

NS-3 independently evaluates AODV, OLSR, and DSR.

**5 scenarios × 3 protocols × 10 runs = 150 runs**

The final NS-3 dataset contains 150 experiment rows.

Average PDR:

  Scenario                   AODV     OLSR      DSR
  ----------------- ------------- -------- --------
  Normal              **10.476%**   7.991%   9.186%
  High mobility        **7.848%**   4.102%   5.056%
  High congestion     **10.307%**   7.923%   8.561%
  Low battery         **10.476%**   7.991%   6.760%
  Relay failure       **10.379%**   7.898%   9.093%

AODV produced the highest average PDR in all five NS-3 scenarios. High
mobility was the most difficult scenario.

> **Important:** NS-3 percentages must not be directly compared with
> Python percentages because the two implementations use different
> topology, traffic, radio, mobility, and packet models. NS-3 is
> independent MANET baseline validation.

## Streamlit Dashboard

Launch from the repository root:

``` bash
python -m streamlit run dashboard/app.py
```

Dashboard tabs:

-   **Overview** --- scenario comparison and KPIs
-   **MANET** --- topology and routing log
-   **Knowledge Graph** --- KG visualization and triple explorer
-   **Q-Learning** --- parameters, training progress, and Q-table
-   **Performance** --- Python multi-seed charts
-   **NS-3 Validation** --- scenario selection, AODV/OLSR/DSR
    comparison, rankings, KPIs, and all seven NS-3 graphs
-   **Simulation Lab** --- run verified Python experiments

## Project Structure

``` text
RelayNet/
├── dashboard/
│   └── app.py
├── python/
│   ├── relaynet/
│   │   ├── manet.py
│   │   ├── knowledge_graph.py
│   │   ├── knowledge_graph_query.py
│   │   ├── marl_agent.py
│   │   └── rl_config.py
│   └── experiments/
│       ├── scenario_experiment.py
│       ├── manet_simulation.py
│       ├── visualize_knowledge_graph.py
│       ├── kg_contextual_reasoning.py
│       ├── kg_marl_experiment.py
│       ├── multi_seed_evaluation.py
│       └── analyze_ns3_results.py
├── ns3/
│   └── relaynet-manet.cc
├── results/
│   └── ns3_analysis/
└── README.md
```

## Requirements

Python 3.14.2 was used for the project.

Install dependencies:

``` bash
python -m pip install matplotlib pandas streamlit
```

A `requirements.txt` file is intentionally not maintained.

NS-3:

-   NS-3.47
-   WSL Ubuntu

The custom NS-3 source is stored at:

``` text
ns3/relaynet-manet.cc
```

For execution it is copied to:

``` text
/home/shree/ns-3.47/scratch/relaynet-manet.cc
```

## Running the Experiments

### MANET

``` bash
python -m python.experiments.manet_simulation
```

Outputs:

``` text
results/manet_routing_log.csv
results/manet_topology.png
```

### Knowledge Graph

``` bash
python -m python.relaynet.knowledge_graph
python -m python.experiments.visualize_knowledge_graph
python -m python.experiments.kg_contextual_reasoning
```

### KG + MARL

``` bash
python -m python.experiments.kg_marl_experiment
```

Outputs include:

``` text
results/rl_parameters.json
results/rl_training_metrics.csv
results/rl_training_progress.png
results/marl_q_tables.csv
results/kg_marl_comparison.csv
```

### Python multi-seed evaluation

``` bash
python -m python.experiments.multi_seed_evaluation
```

### NS-3 analysis

``` bash
python -m python.experiments.analyze_ns3_results
```

Outputs:

``` text
results/ns3_analysis/ns3_multiseed_summary.csv
results/ns3_analysis/ns3_protocol_rankings.csv
results/ns3_analysis/*.png
```

## Running NS-3

Run NS-3 from WSL:

``` bash
cd ~/ns-3.47
```

Example:

``` bash
./ns3 run "scratch/relaynet-manet --protocol=AODV --scenario=normal --output=/mnt/d/RelayNet/results/ns3_results.csv --seed=42 --run=1"
```

Path conventions:

  Environment   Path
  ------------- -------------------
  Git Bash      `/d/RelayNet`
  WSL           `/mnt/d/RelayNet`

## Reproducibility

Python:

-   10 seeds per scenario/method
-   RL random seed: 42

NS-3:

-   10 runs per protocol/scenario
-   Seed and run controls are exposed by the simulation

Total evaluated runs:

``` text
Python: 200
NS-3:   150
Total:  350
```

## Limitations

This is a semester-level simulation and research prototype, not a
production emergency communication system.

Not currently implemented:

-   AEMRP natively inside NS-3
-   KG directly connected to NS-3 during simulation
-   Q-learning directly connected to NS-3 during simulation
-   Neo4j
-   Deep MARL such as MADDPG
-   Physical UAV deployment
-   Real mobile-device communication
-   Wi-Fi Direct deployment
-   Bluetooth Mesh deployment
-   Production emergency application infrastructure

The current reward function also has a known limitation under
low-battery conditions.

## Future Work

-   Connect AEMRP directly to NS-3.
-   Integrate a persistent graph database such as Neo4j.
-   Improve battery-aware reward shaping.
-   Explore advanced MARL algorithms such as MADDPG.
-   Add more realistic UAV mobility and wireless-channel models.
-   Evaluate larger and more heterogeneous disaster topologies.
-   Validate on real UAV/mobile hardware.
-   Model more realistic emergency traffic.
-   Evaluate simultaneous multi-relay failures.
-   Explore real-time adaptive routing.

## Key Takeaway

RelayNet demonstrates a complete research prototype:

``` text
Network State
    ↓
Dynamic MANET
    ↓
Temporal Knowledge Graph
    ↓
Contextual Reasoning
    ↓
Multi-Agent Q-Learning
    ↓
Adaptive Relay Selection
    ↓
Packet Forwarding
    ↓
Performance Evaluation
```

The Python evaluation demonstrates adaptive and competitive KG-assisted
relay selection, particularly under high mobility. Independent NS-3
validation provides additional evidence using established MANET
protocols AODV, OLSR, and DSR.
