# Traffic-Aware Energy Optimisation in 5G/6G Networks

A Python-based, **5G/6G-inspired network simulation** investigating how traffic-aware base-station operating levels can reduce energy use while maintaining a simplified, capacity-based quality-of-service (QoS) criterion. The project also evaluates whether neighbouring base stations can serve excess traffic during short-lived demand spikes.

> **Current implemented version: V2.4.1** (`Simulation/main2_41.py`). The simulation uses synthetic traffic and illustrative power/capacity assumptions; results are not measurements or performance guarantees for a deployed 5G/6G network.

## Objectives

- Compare an always-on, maximum-power baseline against traffic-aware operating-level selection.
- Examine energy savings under LOW, NORMAL, HIGH and SPIKE traffic scenarios.
- Measure capacity-based QoS violations, throughput, unmet demand and resource utilisation.
- Evaluate simplified neighbour-assisted traffic coordination during the SPIKE scenario.
- Export plots and summary figures for interpretation.

## Repository structure

```text
Traffic_Aware_Network_Optimisation/
├── Simulation/
│   ├── main.py                 # Earlier development versions
│   ├── ...
│   └── main2_41.py            # Official V2.4.1 simulation
├── Graph/
│   ├── 01_traffic_demand.png
│   ├── ...
│   └── 17_scenario_summary_table.png
├── Documentation/             # Project documents and planning material
└── .gitignore
```

The repository also contains earlier simulation scripts and some additional `Figure_*.png` images. The **17 numbered graphs** are the principal V2.4.1 exports. Documents discussing V3 are planning/reference material and should not be interpreted as an implemented V3 simulation.

## Requirements

- Python 3
- NumPy
- pandas
- Matplotlib

Install dependencies from the repository root:

```bash
python -m pip install numpy pandas matplotlib
```

## Run the simulation

From the repository root:

```bash
python Simulation/main2_41.py
```

The program prints simulation results and writes numbered PNG figures into `Graph/`. It also displays figures using Matplotlib; a graphical environment may be needed for interactive display.

## Simulation configuration

| Parameter | Value |
|---|---:|
| Base stations | 5 |
| Simulation duration | 24 hours |
| Time step | 1 hour |
| Maximum capacity per base station | 100 Mbps |
| Baseline power per base station | 200 W |

The traffic-aware controller selects the **lowest available operating level whose capacity meets the current traffic demand**:

| Operating level | Capacity | Power |
|---|---:|---:|
| LOW | 40 Mbps | 120 W |
| MEDIUM | 70 Mbps | 160 W |
| HIGH | 100 Mbps | 200 W |

If demand exceeds 100 Mbps, the base station remains at HIGH and the excess is recorded as unmet demand. The algorithm is **rule-based**; it does not use machine learning, traffic forecasting or an optimisation solver.

### Traffic generation

Traffic follows a daily sinusoidal pattern with random noise. The four reproducible scenarios differ in their baseline traffic, amplitude and noise; SPIKE also introduces additional demand at selected hours. Scenario-specific random seeds are used in V2.4.1.

### QoS and throughput

QoS is satisfied when offered demand does not exceed allocated capacity. Served throughput is the lesser of demand and capacity. This is a **capacity-based QoS proxy**, not a simulation of latency, jitter, packet loss or radio-channel quality.

### Neighbour-assisted coordination

For the SPIKE scenario, overloaded base stations may redirect excess traffic to predefined neighbouring base stations that have spare capacity. The coordination logic respects the remaining spare capacity of each donor. Neighbour relationships are assumed, not derived from measured radio coverage or geographic positions.

In V2.4.1, coordination is assumed not to change base-station power consumption; signalling, handover and interference costs are not modelled. Consequently, coordination improves the simplified service metrics **without additional modelled energy cost**.

## V2.4.1 results

All values below refer to the configured **24-hour, five-base-station simulation** with the existing scenario seeds. The always-on baseline consumes **24.00 kWh** in each scenario.

| Scenario | Optimised energy | Energy saved | Energy saving | QoS violations before coordination |
|---|---:|---:|---:|---:|
| LOW | 14.48 kWh | 9.52 kWh | 39.67% | 0 |
| NORMAL | 16.80 kWh | 7.20 kWh | 30.00% | 0 |
| HIGH | 21.04 kWh | 2.96 kWh | 12.33% | 0 |
| SPIKE | 17.64 kWh | 6.36 kWh | 26.50% | 4 |

The separate initial traffic experiment reports **16.68 kWh** optimised energy versus **24.00 kWh** baseline energy, equivalent to **30.50% energy savings**, with no capacity-based QoS violations.

### SPIKE coordination results

| Metric | Before coordination | After coordination |
|---|---:|---:|
| Capacity-based QoS violations | 4 | 1 |
| Unmet demand | 10.46 Mbps-hours | 3.54 Mbps-hours |
| Modelled network energy | 17.64 kWh | 17.64 kWh |

Coordination reduced the number of violation events by **75%** and unmet demand by approximately **66%** in this particular synthetic scenario. These are scenario-specific outcomes, not statistical estimates across repeated random trials.

> **Units note:** “Mbps-hours” here denotes a sum of hourly traffic-rate samples multiplied by the one-hour interval. It is not itself a data-volume unit in megabits.

## Graphs

The `Graph/` directory contains the following numbered V2.4.1 outputs:

| Figures | Content |
|---|---|
| 01–03 | Initial traffic, baseline power, and baseline versus optimised power |
| 04–07 | LOW, NORMAL, HIGH and SPIKE traffic patterns |
| 08–09 | Scenario energy savings and pre-coordination QoS violations |
| 10–11 | SPIKE QoS violations and unmet demand before/after coordination |
| 12–16 | SPIKE demand versus allocated capacity for base stations 1–5, before coordination |
| 17 | Scenario summary table |

## Assumptions and limitations

- Traffic is **synthetic**, not drawn from an operator dataset.
- Power and capacity levels are **illustrative assumptions**, not calibrated hardware measurements.
- The baseline assumes all five base stations operate at HIGH power continuously.
- The controller uses current demand with no forecasting, switching delays, hysteresis or transition-energy cost.
- No sleep state is implemented; the declared idle-power parameter is not used to define an active operating level.
- Neighbour relationships are predefined; mobility, handover delay, interference and radio propagation are not modelled.
- Coordination is evaluated only for the SPIKE scenario and carries no additional modelled energy overhead.
- QoS reflects demand-versus-capacity satisfaction, not end-to-end network performance.
- Results come from fixed seeds and do not establish statistical confidence or generalisation to real deployments.

## Proposed future work (not yet implemented)

Potential V2.5 experiments include repeated runs across multiple random seeds, explicit accounting of traffic physically served by donor base stations, and additional traffic-satisfaction metrics. These are **proposals**, not features of V2.4.1.

## Reproducibility

Use `Simulation/main2_41.py` as the reference implementation and retain the current scenario seeds when reproducing the tables and graphs. Changes to traffic generation, power assumptions, or coordination logic may change the reported results.
