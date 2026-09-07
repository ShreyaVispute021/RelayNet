# RelayNet Evaluation Summary

## Objective

Evaluate whether dynamic, context-aware and learning-assisted relay selection
is feasible for UAV-supported disaster MANET communication under changing
network conditions.

## Experimental setup

- Three simulated UAV relay agents and one source-destination pair
- 1,000 emergency packets per run
- Five network scenarios
- Four relay-selection methods
- Ten random evaluation seeds
- Independent Q-learning trained for 60 episodes across all scenarios

## Ten-seed mean results

| Scenario | Method | PDR | Delay | Throughput (kbps) | Energy | Lifetime |
|---|---|---:|---:|---:|---:|---:|
| Normal | Static | 27.81% | 8.04 | 1.139 | 183.64 | 1000 |
| Normal | Weighted baseline | 28.52% | 15.56 | 1.168 | 189.17 | 1000 |
| Normal | Contextual KG | 28.35% | 14.77 | 1.161 | 188.93 | 1000 |
| Normal | KG + MARL | 28.51% | 14.67 | 1.168 | 189.14 | 1000 |
| High mobility | Static | 19.93% | 9.36 | 0.816 | 180.80 | 919 |
| High mobility | Weighted baseline | 20.43% | 18.33 | 0.837 | 185.75 | 919 |
| High mobility | Contextual KG | 20.43% | 15.70 | 0.837 | 185.52 | 919 |
| High mobility | KG + MARL | 20.48% | 16.59 | 0.839 | 185.76 | 919 |
| High congestion | Static | 21.29% | 8.65 | 0.872 | 229.45 | 874 |
| High congestion | Weighted baseline | 21.42% | 14.06 | 0.877 | 233.65 | 874 |
| High congestion | Contextual KG | 21.36% | 13.43 | 0.875 | 230.33 | 874 |
| High congestion | KG + MARL | 21.41% | 13.66 | 0.877 | 230.42 | 874 |
| Low battery | Static | 17.75% | 7.05 | 0.727 | 235.00 | 563 |
| Low battery | Weighted baseline | 17.75% | 9.45 | 0.727 | 235.00 | 566 |
| Low battery | Contextual KG | 17.58% | 9.45 | 0.720 | 235.00 | 545 |
| Low battery | KG + MARL | 17.45% | 9.63 | 0.715 | 235.00 | 540 |
| Relay failure | Static | 19.42% | 7.90 | 0.795 | 225.88 | 699 |
| Relay failure | Weighted baseline | 19.93% | 12.26 | 0.816 | 228.99 | 756 |
| Relay failure | Contextual KG | 19.71% | 11.42 | 0.807 | 226.13 | 734 |
| Relay failure | KG + MARL | 19.63% | 11.09 | 0.804 | 228.36 | 712 |

## Findings

- KG + MARL produced the highest mean PDR and throughput under high mobility.
- Contextual KG reduced delay and energy use relative to the weighted baseline
  in several dynamic scenarios.
- The weighted baseline remained competitive because it already uses all six
  network-state features.
- The static method had lower delay because it avoids relay switching, but it
  lacks contextual adaptation and usually provides lower PDR and throughput.
- Low-battery routing is the main weakness: the current agents do not yet
  balance short-term delivery against long-term network survival effectively.

## Conclusion

The prototype validates the complete proposed information flow from UAV-MANET
state collection through Knowledge Graph reasoning and multi-agent learning to
dynamic relay selection. Results demonstrate feasibility and explainable
adaptation, but they do not support a claim that KG + MARL dominates every
metric or scenario. Reward shaping, larger topologies, deeper MARL, and NS-3
validation are the next steps required for stronger performance claims.
