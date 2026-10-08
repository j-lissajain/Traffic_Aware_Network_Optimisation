import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


np.random.seed(42)


# ==========================================
# V2.4.1 GRAPH OUTPUT SETTINGS
# ==========================================

GRAPH_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "Graph"
)

os.makedirs(GRAPH_DIR, exist_ok=True)

# ==========================================
# 1. SIMULATION SETTINGS
# ==========================================

NUM_BASE_STATIONS = 5
SIMULATION_HOURS = 24
MAX_CAPACITY_MBPS = 100
# ==========================================
# ENERGY MODEL
# ==========================================

IDLE_POWER_W = 100
MAX_POWER_W = 200
# ==========================================
# OPERATING LEVELS
# ==========================================

LOW_CAPACITY_MBPS = 40
MEDIUM_CAPACITY_MBPS = 70
HIGH_CAPACITY_MBPS = 100

LOW_POWER_W = 120
MEDIUM_POWER_W = 160
HIGH_POWER_W = 200
# ==========================================
# V2.0 NETWORK RESOURCE MODEL
# ==========================================

OPERATING_LEVELS = {
    "LOW": {
        "capacity": 40,
        "power": 120
    },

    "MEDIUM": {
        "capacity": 70,
        "power": 160
    },

    "HIGH": {
        "capacity": 100,
        "power": 200
    }
}

# ==========================================
# 2. TIME
# ==========================================

hours = np.arange(SIMULATION_HOURS)


# ==========================================
# 3. GENERATE TRAFFIC
# ==========================================

traffic_data = {}

for bs in range(1, NUM_BASE_STATIONS + 1):

    # Different base stations have slightly
    # different traffic patterns.
    base_traffic = (
        40
        + 25 * np.sin((hours - 8) * np.pi / 12)
    )

    random_variation = np.random.normal(
        0, 5, SIMULATION_HOURS
    )

    traffic = base_traffic + random_variation

    # Traffic cannot be negative
    traffic = np.maximum(traffic, 0)

    traffic_data[f"BS{bs}"] = traffic


# ==========================================
# 4. STORE DATA
# ==========================================

df = pd.DataFrame(traffic_data)

df["Hour"] = hours

df = df[
    ["Hour"] +
    [f"BS{i}" for i in range(1, NUM_BASE_STATIONS + 1)]
]


# ==========================================
# 5. DISPLAY TRAFFIC DATA
# ==========================================

print("\nTraffic generated for the network:\n")

print(df.round(2))


# ==========================================
# 6. CALCULATE UTILISATION
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    df[f"BS{bs}_Utilisation"] = (
        df[f"BS{bs}"] / MAX_CAPACITY_MBPS
    ) * 100


# ==========================================
# 7. PLOT TRAFFIC
# ==========================================

plt.figure(figsize=(12, 6))

for bs in range(1, NUM_BASE_STATIONS + 1):

    plt.plot(
        df["Hour"],
        df[f"BS{bs}"],
        marker="o",
        label=f"BS{bs}"
    )

plt.xlabel("Time (Hour)")
plt.ylabel("Traffic Demand (Mbps)")
plt.title("Traffic Demand Across Base Stations")

plt.xticks(range(24))
plt.grid(True)
plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "01_traffic_demand.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ==========================================
# 8. CALCULATE BASELINE POWER CONSUMPTION
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    # Baseline assumption:
    # Every BS remains fully active at maximum power
    df[f"BS{bs}_Power_W"] = MAX_POWER_W
    
# ==========================================
# 9. TOTAL NETWORK POWER
# ==========================================

power_columns = [
    f"BS{i}_Power_W"
    for i in range(1, NUM_BASE_STATIONS + 1)
]

df["Total_Power_W"] = df[power_columns].sum(axis=1)

# ==========================================
# 10. ENERGY CONSUMPTION
# ==========================================

df["Energy_Wh"] = df["Total_Power_W"] * 1

total_energy_Wh = df["Energy_Wh"].sum()

total_energy_kWh = total_energy_Wh / 1000

print("\n==========================================")
print("BASELINE ENERGY RESULTS")
print("==========================================")

print(f"Total energy consumption: {total_energy_kWh:.2f} kWh")
print(
    f"Average network power: "
    f"{df['Total_Power_W'].mean():.2f} W"
)

# ==========================================
# 11. PLOT NETWORK POWER
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    df["Hour"],
    df["Total_Power_W"],
    marker="o"
)

plt.xlabel("Time (Hour)")
plt.ylabel("Network Power (W)")
plt.title("Baseline Network Power Consumption")

plt.xticks(range(24))
plt.grid(True)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "02_baseline_network_power.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ==========================================
# 12. QOS CHECK
# ==========================================

def check_qos(demand, available_capacity):

    if demand <= available_capacity:
        return "Satisfied"
    else:
        return "Violation"

# ==========================================
# 13. TEST QOS CHECK
# ==========================================

print("\n==========================================")
print("QOS TEST")
print("==========================================")

print(
    "Demand: 25 Mbps, Capacity: 40 Mbps →",
    check_qos(25, 40)
)

print(
    "Demand: 60 Mbps, Capacity: 40 Mbps →",
    check_qos(60, 40)
)

print(
    "Demand: 90 Mbps, Capacity: 100 Mbps →",
    check_qos(90, 100)
)

print(
    "Demand: 110 Mbps, Capacity: 100 Mbps →",
    check_qos(110, 100)
)

# ==========================================
# 14. OPERATING LEVEL QOS TEST
# ==========================================

operating_levels = {
    "LOW": LOW_CAPACITY_MBPS,
    "MEDIUM": MEDIUM_CAPACITY_MBPS,
    "HIGH": HIGH_CAPACITY_MBPS
}

test_demand = 60

print("\n==========================================")
print("OPERATING LEVEL TEST")
print("==========================================")

print(f"Traffic demand = {test_demand} Mbps\n")

for level, capacity in operating_levels.items():

    qos = check_qos(test_demand, capacity)

    print(
        f"{level}: "
        f"Capacity = {capacity} Mbps → "
        f"QoS = {qos}"
    )

# ==========================================
# 15. TRAFFIC-AWARE RESOURCE ALLOCATION
# ==========================================

def select_operating_level(demand):
    """
    Select the lowest-power operating level
    that can satisfy the traffic demand.
    """

    for level, settings in OPERATING_LEVELS.items():

        if demand <= settings["capacity"]:
            return level

    return "OVERLOAD"


def get_resource_configuration(level):
    """
    Return capacity and power
    for the selected operating level.
    """

    if level == "OVERLOAD":

        return {
            "capacity": OPERATING_LEVELS["HIGH"]["capacity"],
            "power": OPERATING_LEVELS["HIGH"]["power"]
        }

    return OPERATING_LEVELS[level]


def calculate_throughput(demand, capacity):
    """
    Throughput is limited by available capacity.
    """

    return min(demand, capacity)

# ==========================================
# 16. TEST OPTIMISATION
# ==========================================

test_demands = [25, 55, 85, 110]

print("\n==========================================")
print("TRAFFIC-AWARE OPTIMISATION TEST")
print("==========================================")

for demand in test_demands:

    level = select_operating_level(demand)

    print(
        f"Demand = {demand} Mbps "
        f"→ Selected Level = {level}"
    )

# ==========================================
# 17. APPLY OPTIMISATION TO ALL BSs
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    df[f"BS{bs}_Level"] = df[f"BS{bs}"].apply(
        select_operating_level
    )

# ==========================================
# 18. APPLY V2.0 RESOURCE CONFIGURATION
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    # Store selected capacity
    df[f"BS{bs}_Available_Capacity_Mbps"] = (
        df[f"BS{bs}_Level"].apply(
            lambda level:
            get_resource_configuration(level)["capacity"]
        )
    )

    # Store selected power
    df[f"BS{bs}_Optimised_Power_W"] = (
        df[f"BS{bs}_Level"].apply(
            lambda level:
            get_resource_configuration(level)["power"]
        )
    )

    # Calculate actual throughput
    df[f"BS{bs}_Throughput_Mbps"] = df.apply(
        lambda row:
        calculate_throughput(
            row[f"BS{bs}"],
            row[f"BS{bs}_Available_Capacity_Mbps"]
        ),
        axis=1
    )

# ==========================================
# 19. TOTAL OPTIMISED POWER
# ==========================================

optimised_power_columns = [
    f"BS{i}_Optimised_Power_W"
    for i in range(1, NUM_BASE_STATIONS + 1)
]

df["Optimised_Total_Power_W"] = (
    df[optimised_power_columns].sum(axis=1)
)

df["Optimised_Energy_Wh"] = (
    df["Optimised_Total_Power_W"] * 1
)

optimised_energy_Wh = df["Optimised_Energy_Wh"].sum()

optimised_energy_kWh = optimised_energy_Wh / 1000

# ==========================================
# 20. COMPARE BASELINE AND OPTIMISATION
# ==========================================

energy_saving_kWh = (
    total_energy_kWh - optimised_energy_kWh
)

energy_saving_percent = (
    energy_saving_kWh / total_energy_kWh
) * 100


print("\n==========================================")
print("BASELINE vs OPTIMISED")
print("==========================================")

print(
    f"Baseline energy: "
    f"{total_energy_kWh:.2f} kWh"
)

print(
    f"Optimised energy: "
    f"{optimised_energy_kWh:.2f} kWh"
)

print(
    f"Energy saved: "
    f"{energy_saving_kWh:.2f} kWh"
)

print(
    f"Energy saving: "
    f"{energy_saving_percent:.2f}%"
)

# ==========================================
# 21. QOS AND THROUGHPUT CHECK
# ==========================================

total_qos_violations = 0

for bs in range(1, NUM_BASE_STATIONS + 1):

    for i in range(len(df)):

        demand = df.loc[i, f"BS{bs}"]

        level = df.loc[i, f"BS{bs}_Level"]

        # Get capacity from V2.0 resource model
        config = get_resource_configuration(level)

        capacity = config["capacity"]

        # Calculate throughput
        throughput = calculate_throughput(
            demand,
            capacity
        )

        # Store throughput
        df.loc[
            i,
            f"BS{bs}_Throughput_Mbps"
        ] = throughput

        # Check QoS
        qos = check_qos(
            demand,
            capacity
        )

        # Store QoS status
        df.loc[
            i,
            f"BS{bs}_QoS"
        ] = qos

        if qos == "Violation":
            total_qos_violations += 1


print(
    f"Total QoS violations: "
    f"{total_qos_violations}"
)

# ==========================================
# 22. BASELINE vs OPTIMISED POWER
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    df["Hour"],
    df["Total_Power_W"],
    marker="o",
    label="Baseline"
)

plt.plot(
    df["Hour"],
    df["Optimised_Total_Power_W"],
    marker="o",
    label="Traffic-Aware Optimisation"
)

plt.xlabel("Time (Hour)")
plt.ylabel("Network Power (W)")

plt.title(
    "Baseline vs Traffic-Aware Network Power"
)

plt.xticks(range(24))

plt.grid(True)
plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "03_baseline_vs_optimised_power.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ==========================================
# 23. V2.1 RESOURCE UTILISATION ANALYSIS
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    # Calculate unused capacity
    df[f"BS{bs}_Unused_Capacity_Mbps"] = (
        df[f"BS{bs}_Available_Capacity_Mbps"]
        - df[f"BS{bs}_Throughput_Mbps"]
    )

    # Calculate resource utilisation percentage
    df[f"BS{bs}_Resource_Utilisation_Percent"] = np.where(
        df[f"BS{bs}_Available_Capacity_Mbps"] > 0,

        (
            df[f"BS{bs}_Throughput_Mbps"]
            / df[f"BS{bs}_Available_Capacity_Mbps"]
        ) * 100,

        0
    )


print("\n==========================================")
print("V2.1 RESOURCE UTILISATION ANALYSIS")
print("==========================================")

for bs in range(1, NUM_BASE_STATIONS + 1):

    average_utilisation = (
        df[f"BS{bs}_Resource_Utilisation_Percent"].mean()
    )

    average_unused_capacity = (
        df[f"BS{bs}_Unused_Capacity_Mbps"].mean()
    )

    print(
        f"BS{bs}: "
        f"Average Resource Utilisation = "
        f"{average_utilisation:.2f}% | "
        f"Average Unused Capacity = "
        f"{average_unused_capacity:.2f} Mbps"
    )

# ==========================================
# 24. V2.3.1 TRAFFIC SCENARIO EXPERIMENTS
# ==========================================

print("\n")
print("==========================================")
print("V2.3.1 TRAFFIC SCENARIO EXPERIMENTS")
print("==========================================")

# Scenario-specific random seeds
# This ensures every scenario is reproducible.
SCENARIO_SEEDS = {
    "LOW": 101,
    "NORMAL": 102,
    "HIGH": 103,
    "SPIKE": 104
}

# ------------------------------------------
# FUNCTION TO GENERATE TRAFFIC SCENARIOS
# ------------------------------------------

def generate_scenario_traffic(scenario, seed):

    scenario_hours = np.arange(SIMULATION_HOURS)

    rng = np.random.default_rng(seed)

    if scenario == "LOW":

        # Mostly low traffic
        base_traffic = (
            25
            + 12 * np.sin(
                (scenario_hours - 8) * np.pi / 12
            )
        )

        random_variation = rng.normal(
            0, 3, SIMULATION_HOURS
        )

        traffic = base_traffic + random_variation


    elif scenario == "NORMAL":

        # Same traffic pattern used in the
        # original V2.1 experiment
        base_traffic = (
            40
            + 25 * np.sin(
                (scenario_hours - 8) * np.pi / 12
            )
        )

        random_variation = rng.normal(
            0, 5, SIMULATION_HOURS
        )

        traffic = base_traffic + random_variation


    elif scenario == "HIGH":

        # Higher overall traffic
        base_traffic = (
            65
            + 20 * np.sin(
                (scenario_hours - 8) * np.pi / 12
            )
        )

        random_variation = rng.normal(
            0, 4, SIMULATION_HOURS
        )

        traffic = base_traffic + random_variation


    elif scenario == "SPIKE":

        # Start with normal traffic
        base_traffic = (
            40
            + 25 * np.sin(
                (scenario_hours - 8) * np.pi / 12
            )
        )

        random_variation = rng.normal(
            0, 5, SIMULATION_HOURS
        )

        traffic = base_traffic + random_variation

        # Introduce sudden traffic spikes
        spike_hours = [9, 12, 15, 18]

        for hour in spike_hours:
            traffic[hour] += 35


    else:
        raise ValueError(
            "Unknown traffic scenario"
        )


    # Traffic cannot be negative
    traffic = np.maximum(
        traffic,
        0
    )

    return traffic


# ------------------------------------------
# FUNCTION TO RUN ONE SCENARIO
# ------------------------------------------

def run_scenario(scenario):

    scenario_data = {}

    # Generate traffic independently for
    # every base station
    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        # Give every BS a different but reproducible seed
        bs_seed = SCENARIO_SEEDS[scenario] + bs

        scenario_data[f"BS{bs}"] = (
            generate_scenario_traffic(
                scenario,
                bs_seed
            )
        )

    scenario_df = pd.DataFrame(
        scenario_data
    )

    scenario_df["Hour"] = np.arange(
        SIMULATION_HOURS
    )

    scenario_df = scenario_df[
        ["Hour"] +
        [
            f"BS{i}"
            for i in range(
                1,
                NUM_BASE_STATIONS + 1
            )
        ]
    ]


    # --------------------------------------
    # BASELINE POWER
    # --------------------------------------

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        scenario_df[
            f"BS{bs}_Baseline_Power_W"
        ] = MAX_POWER_W


    # --------------------------------------
    # APPLY OPTIMISATION
    # --------------------------------------

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        # Select operating level
        scenario_df[
            f"BS{bs}_Level"
        ] = scenario_df[
            f"BS{bs}"
        ].apply(
            select_operating_level
        )


        # Available capacity
        scenario_df[
            f"BS{bs}_Available_Capacity_Mbps"
        ] = scenario_df[
            f"BS{bs}_Level"
        ].apply(
            lambda level:
            get_resource_configuration(
                level
            )["capacity"]
        )


        # Optimised power
        scenario_df[
            f"BS{bs}_Optimised_Power_W"
        ] = scenario_df[
            f"BS{bs}_Level"
        ].apply(
            lambda level:
            get_resource_configuration(
                level
            )["power"]
        )


        # Throughput
        scenario_df[
            f"BS{bs}_Throughput_Mbps"
        ] = scenario_df.apply(
            lambda row:
            calculate_throughput(
                row[f"BS{bs}"],
                row[
                    f"BS{bs}_Available_Capacity_Mbps"
                ]
            ),
            axis=1
        )

        # UNMET DEMAND

        scenario_df[
            f"BS{bs}_Unmet_Demand_Mbps"
        ] = (
            scenario_df[f"BS{bs}"]
            - scenario_df[f"BS{bs}_Throughput_Mbps"]
        )


        # QoS
        scenario_df[
            f"BS{bs}_QoS"
        ] = scenario_df.apply(
            lambda row:
            check_qos(
                row[f"BS{bs}"],
                row[
                    f"BS{bs}_Available_Capacity_Mbps"
                ]
            ),
            axis=1
        )


        # Unused capacity
        scenario_df[
            f"BS{bs}_Unused_Capacity_Mbps"
        ] = (
            scenario_df[
                f"BS{bs}_Available_Capacity_Mbps"
            ]
            -
            scenario_df[
                f"BS{bs}_Throughput_Mbps"
            ]
        )


        # Resource utilisation
        scenario_df[
            f"BS{bs}_Resource_Utilisation_Percent"
        ] = np.where(

            scenario_df[
                f"BS{bs}_Available_Capacity_Mbps"
            ] > 0,

            (
                scenario_df[
                    f"BS{bs}_Throughput_Mbps"
                ]
                /
                scenario_df[
                    f"BS{bs}_Available_Capacity_Mbps"
                ]
            ) * 100,

            0
        )


    # --------------------------------------
    # TOTAL BASELINE POWER
    # --------------------------------------

    baseline_power_columns = [
        f"BS{i}_Baseline_Power_W"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    scenario_df[
        "Baseline_Total_Power_W"
    ] = scenario_df[
        baseline_power_columns
    ].sum(axis=1)


    # --------------------------------------
    # TOTAL OPTIMISED POWER
    # --------------------------------------

    optimised_power_columns = [
        f"BS{i}_Optimised_Power_W"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    scenario_df[
        "Optimised_Total_Power_W"
    ] = scenario_df[
        optimised_power_columns
    ].sum(axis=1)


    # --------------------------------------
    # ENERGY CALCULATION
    # --------------------------------------

    baseline_energy_kWh = (
        scenario_df[
            "Baseline_Total_Power_W"
        ].sum()
        / 1000
    )

    optimised_energy_kWh = (
        scenario_df[
            "Optimised_Total_Power_W"
        ].sum()
        / 1000
    )

    energy_saved_kWh = (
        baseline_energy_kWh
        - optimised_energy_kWh
    )

    energy_saving_percent = (
        energy_saved_kWh
        / baseline_energy_kWh
    ) * 100


    # --------------------------------------
    # QOS VIOLATIONS
    # --------------------------------------

    total_qos_violations = 0

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        total_qos_violations += (
            scenario_df[
                f"BS{bs}_QoS"
            ]
            .eq("Violation")
            .sum()
        )

    # --------------------------------------
    # TOTAL UNMET DEMAND
    # --------------------------------------

    unmet_demand_columns = [
        f"BS{i}_Unmet_Demand_Mbps"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    total_unmet_demand = (
        scenario_df[
            unmet_demand_columns
        ].sum().sum()
    )

    # --------------------------------------
    # QOS VIOLATION RATE
    # --------------------------------------

    total_possible_qos_checks = (
        NUM_BASE_STATIONS
        * SIMULATION_HOURS
    )

    qos_violation_rate = (
        total_qos_violations
        / total_possible_qos_checks
    ) * 100

    # --------------------------------------
    # PEAK DEMAND
    # --------------------------------------

    traffic_columns = [
        f"BS{i}"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    peak_demand = (
        scenario_df[
            traffic_columns
        ].max().max()
    )

    # --------------------------------------
    # PEAK AVAILABLE CAPACITY
    # --------------------------------------

    capacity_columns = [
        f"BS{i}_Available_Capacity_Mbps"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    peak_capacity = (
        scenario_df[
            capacity_columns
        ].max().max()
    )   

    # --------------------------------------
    # TOTAL OFFERED TRAFFIC
    # --------------------------------------

    total_offered_traffic = (
        scenario_df[
            traffic_columns
        ].sum().sum()
    )

    throughput_columns = [
        f"BS{i}_Throughput_Mbps"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    # --------------------------------------
    # TOTAL THROUGHPUT
    # --------------------------------------

    total_throughput = (
        scenario_df[
            throughput_columns
        ].sum().sum()
    )

    # --------------------------------------
    # RESOURCE UTILISATION
    # --------------------------------------

    utilisation_columns = [
        f"BS{i}_Resource_Utilisation_Percent"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

    average_resource_utilisation = (
        scenario_df[
            utilisation_columns
        ].mean().mean()
    )


    # --------------------------------------
    # AVERAGE THROUGHPUT
    # --------------------------------------

    average_throughput = (
        scenario_df[
            throughput_columns
        ].mean().mean()
    )


    return (
        scenario_df,
        baseline_energy_kWh,
        optimised_energy_kWh,
        energy_saved_kWh,
        energy_saving_percent,
        total_qos_violations,
        qos_violation_rate,
        total_unmet_demand,
        peak_demand,
        peak_capacity,
        total_offered_traffic,
        total_throughput,
        average_resource_utilisation,
        average_throughput
    )


# ==========================================
# 25. RUN ALL TRAFFIC SCENARIOS
# ==========================================

scenarios = [
    "LOW",
    "NORMAL",
    "HIGH",
    "SPIKE"
]

scenario_results = {}

for scenario in scenarios:

    print("\n")
    print("------------------------------------------")
    print(f"Running {scenario} TRAFFIC scenario")
    print("------------------------------------------")

    result = run_scenario(
        scenario
    )

    scenario_results[
        scenario
    ] = result


# ==========================================
# 26. DISPLAY SCENARIO RESULTS
# ==========================================

print("\n")
print("==========================================")
print("V2.3.1 SCENARIO RESULTS")
print("==========================================")


for scenario in scenarios:

    (
        scenario_df,
        baseline_energy,
        optimised_energy,
        energy_saved,
        energy_saving_percent,
        qos_violations,
        qos_violation_rate,
        total_unmet_demand,
        peak_demand,
        peak_capacity,
        total_offered_traffic,
        total_throughput,
        average_resource_utilisation,
        average_throughput
    ) = scenario_results[
        scenario
]

    print(
        f"\n{scenario} TRAFFIC"
    )

    print(
        f"Baseline energy: "
        f"{baseline_energy:.2f} kWh"
    )

    print(
        f"Optimised energy: "
        f"{optimised_energy:.2f} kWh"
    )

    print(
        f"Energy saved: "
        f"{energy_saved:.2f} kWh"
    )

    print(
        f"Energy saving: "
        f"{energy_saving_percent:.2f}%"
    )

    print(
        f"QoS violations: "
        f"{qos_violations}"
    )

    print(
        f"Average resource utilisation: "
        f"{average_resource_utilisation:.2f}%"
    )

    print(
        f"Average throughput: "
        f"{average_throughput:.2f} Mbps"
    )

    print(
        f"QoS violation rate: "
        f"{qos_violation_rate:.2f}%"
    )

    print(
        f"Total unmet demand: "
        f"{total_unmet_demand:.2f} Mbps-hours"
    )

    print(
        f"Peak demand: "
        f"{peak_demand:.2f} Mbps"
    )

    print(
        f"Peak available capacity: "
        f"{peak_capacity:.2f} Mbps"
    )

    print(
        f"Total offered traffic: "
        f"{total_offered_traffic:.2f} Mbps-hours"
    )

    print(
        f"Total throughput: "
        f"{total_throughput:.2f} Mbps-hours"
    )


# ==========================================
# 26.1. V2.3.2 SPIKE QOS VIOLATION ANALYSIS
# ==========================================

print("\n")
print("==========================================")
print("V2.3.2 SPIKE QoS VIOLATION ANALYSIS")
print("==========================================")

spike_df = scenario_results["SPIKE"][0]

violation_count = 0

for bs in range(1, NUM_BASE_STATIONS + 1):

    for i in range(len(spike_df)):

        qos_status = spike_df.loc[
            i,
            f"BS{bs}_QoS"
        ]

        if qos_status == "Violation":

            violation_count += 1

            hour = spike_df.loc[i, "Hour"]
            demand = spike_df.loc[
                i,
                f"BS{bs}"
            ]

            level = spike_df.loc[
                i,
                f"BS{bs}_Level"
            ]

            capacity = spike_df.loc[
                i,
                f"BS{bs}_Available_Capacity_Mbps"
            ]

            throughput = spike_df.loc[
                i,
                f"BS{bs}_Throughput_Mbps"
            ]

            unmet_demand = spike_df.loc[
                i,
                f"BS{bs}_Unmet_Demand_Mbps"
            ]

            print(
                f"Violation {violation_count}: "
                f"Hour = {hour} | "
                f"BS = BS{bs} | "
                f"Demand = {demand:.2f} Mbps | "
                f"Level = {level} | "
                f"Capacity = {capacity:.2f} Mbps | "
                f"Throughput = {throughput:.2f} Mbps | "
                f"Unmet Demand = {unmet_demand:.2f} Mbps"
            )

print("\nTotal SPIKE QoS violations:", violation_count)

# ==========================================
# 26.2. V2.4 TRAFFIC COORDINATION
# ==========================================

print("\n")
print("==========================================")
print("V2.4 TRAFFIC COORDINATION")
print("==========================================")

# --------------------------------------------------
# BS OVERLAP / COORDINATION ASSUMPTION
# --------------------------------------------------
#
# These relationships represent neighboring or
# overlapping coverage areas in our simulation.
#
# A BS can receive temporary excess traffic from
# another BS only if it has spare capacity after
# serving its own traffic.
#
# This is a simulation assumption, not a measured
# physical deployment topology.
# --------------------------------------------------

BS_NEIGHBORS = {
    1: [3, 4, 5],
    2: [3, 4, 5],
    3: [1, 2, 5],
    4: [1, 2, 5],
    5: [1, 2, 3, 4]
}


# --------------------------------------------------
# COPY SPIKE SCENARIO
# --------------------------------------------------

coord_df = scenario_results["SPIKE"][0].copy()


# --------------------------------------------------
# CREATE COORDINATION COLUMNS
# --------------------------------------------------

for bs in range(
    1,
    NUM_BASE_STATIONS + 1
):

    # Traffic received from other BSs
    coord_df[
        f"BS{bs}_Offloaded_In_Mbps"
    ] = 0.0

    # Traffic sent to other BSs
    coord_df[
        f"BS{bs}_Offloaded_Out_Mbps"
    ] = 0.0

    # Remaining spare capacity after
    # coordination
    coord_df[
        f"BS{bs}_Remaining_Spare_Mbps"
    ] = 0.0

    # Traffic of this BS's users that
    # is successfully served
    coord_df[
        f"BS{bs}_Coordinated_Throughput_Mbps"
    ] = 0.0

    # Remaining unmet demand after
    # coordination
    coord_df[
        f"BS{bs}_Coordinated_Unmet_Demand_Mbps"
    ] = 0.0


# --------------------------------------------------
# PROCESS EACH HOUR
# --------------------------------------------------

for i in range(
    len(coord_df)
):

    # ----------------------------------------------
    # STEP 1:
    # Calculate spare capacity of every BS
    # after serving its own traffic.
    # ----------------------------------------------

    remaining_spare = {}

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        demand = coord_df.loc[
            i,
            f"BS{bs}"
        ]

        capacity = coord_df.loc[
            i,
            f"BS{bs}_Available_Capacity_Mbps"
        ]

        # Spare capacity available for
        # neighboring traffic
        spare = max(
            capacity - demand,
            0
        )

        remaining_spare[bs] = spare

        coord_df.loc[
            i,
            f"BS{bs}_Remaining_Spare_Mbps"
        ] = spare


    # ----------------------------------------------
    # STEP 2:
    # Find overloaded BSs
    # ----------------------------------------------

    overloaded_bs = []

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        demand = coord_df.loc[
            i,
            f"BS{bs}"
        ]

        capacity = coord_df.loc[
            i,
            f"BS{bs}_Available_Capacity_Mbps"
        ]

        if demand > capacity:

            overloaded_bs.append(bs)


    # ----------------------------------------------
    # STEP 3:
    # Try to serve excess demand using
    # neighboring BS spare capacity.
    # ----------------------------------------------

    for receiver_bs in overloaded_bs:

        demand = coord_df.loc[
            i,
            f"BS{receiver_bs}"
        ]

        capacity = coord_df.loc[
            i,
            f"BS{receiver_bs}_Available_Capacity_Mbps"
        ]

        unmet_demand = max(
            demand - capacity,
            0
        )

        # Check neighboring BSs.
        # Prefer the neighbor with the
        # largest remaining spare capacity.
        possible_donors = sorted(
            BS_NEIGHBORS[receiver_bs],
            key=lambda donor:
                remaining_spare[donor],
            reverse=True
        )


        for donor_bs in possible_donors:

            # Stop if all excess demand
            # has already been served.
            if unmet_demand <= 0:
                break

            donor_spare = remaining_spare[
                donor_bs
            ]

            # Ignore donors with no spare capacity.
            if donor_spare <= 0:
                continue

            # Amount that this donor can provide.
            transferred = min(
                unmet_demand,
                donor_spare
            )

            # Receiver gets additional service.
            coord_df.loc[
                i,
                f"BS{receiver_bs}_Offloaded_In_Mbps"
            ] += transferred

            # Donor serves traffic for receiver.
            coord_df.loc[
                i,
                f"BS{donor_bs}_Offloaded_Out_Mbps"
            ] += transferred

            # Reduce donor's remaining spare capacity.
            remaining_spare[donor_bs] -= transferred

            coord_df.loc[
                i,
                f"BS{donor_bs}_Remaining_Spare_Mbps"
            ] = remaining_spare[donor_bs]

            # Reduce receiver's unmet demand.
            unmet_demand -= transferred


        # Store final unmet demand.
        coord_df.loc[
            i,
            f"BS{receiver_bs}_Coordinated_Unmet_Demand_Mbps"
        ] = unmet_demand


    # ----------------------------------------------
    # STEP 4:
    # Calculate coordinated throughput
    # for each BS's own traffic.
    # ----------------------------------------------

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        demand = coord_df.loc[
            i,
            f"BS{bs}"
        ]

        original_capacity = coord_df.loc[
            i,
            f"BS{bs}_Available_Capacity_Mbps"
        ]

        unmet = coord_df.loc[
            i,
            f"BS{bs}_Coordinated_Unmet_Demand_Mbps"
        ]

        coordinated_throughput = (
            demand - unmet
        )

        coord_df.loc[
            i,
            f"BS{bs}_Coordinated_Throughput_Mbps"
        ] = coordinated_throughput


# --------------------------------------------------
# 4. NETWORK-LEVEL COORDINATION METRICS
# --------------------------------------------------

coordinated_unmet_columns = [
    f"BS{i}_Coordinated_Unmet_Demand_Mbps"
    for i in range(
        1,
        NUM_BASE_STATIONS + 1
    )
]

coordinated_throughput_columns = [
    f"BS{i}_Coordinated_Throughput_Mbps"
    for i in range(
        1,
        NUM_BASE_STATIONS + 1
    )
]


total_coordinated_unmet_demand = (
    coord_df[
        coordinated_unmet_columns
    ].sum().sum()
)


total_coordinated_throughput = (
    coord_df[
        coordinated_throughput_columns
    ].sum().sum()
)


total_offered_traffic = (
    coord_df[
        [
            f"BS{i}"
            for i in range(
                1,
                NUM_BASE_STATIONS + 1
            )
        ]
    ].sum().sum()
)


# --------------------------------------------------
# 5. COUNT REMAINING QOS VIOLATIONS
# --------------------------------------------------

coordinated_qos_violations = 0

for bs in range(
    1,
    NUM_BASE_STATIONS + 1
):

    coordinated_qos_violations += (
        coord_df[
            f"BS{bs}_Coordinated_Unmet_Demand_Mbps"
        ]
        .gt(0)
        .sum()
    )


total_possible_checks = (
    NUM_BASE_STATIONS
    * SIMULATION_HOURS
)


coordinated_qos_violation_rate = (
    coordinated_qos_violations
    / total_possible_checks
) * 100


# --------------------------------------------------
# 6. ENERGY REMAINS UNCHANGED
# --------------------------------------------------
#
# Coordination uses already available spare
# capacity. Therefore no additional BS power
# is introduced by this mechanism.
# --------------------------------------------------

coordination_energy_kWh = (
    coord_df[
        "Optimised_Total_Power_W"
    ].sum()
    / 1000
)


# --------------------------------------------------
# 7. ENERGY SAVING
# --------------------------------------------------

coordination_energy_saved_kWh = (
    coord_df[
        "Baseline_Total_Power_W"
    ].sum()
    / 1000
) - coordination_energy_kWh


coordination_energy_saving_percent = (
    coordination_energy_saved_kWh
    /
    (
        coord_df[
            "Baseline_Total_Power_W"
        ].sum()
        / 1000
    )
) * 100

# --------------------------------------------------
# ORIGINAL SPIKE QOS COUNT
# --------------------------------------------------

original_spike_qos_violations = 0

for bs in range(
    1,
    NUM_BASE_STATIONS + 1
):

    original_spike_qos_violations += (
        spike_df[
            f"BS{bs}_QoS"
        ]
        .eq("Violation")
        .sum()
    )

# --------------------------------------------------
# 8. DISPLAY V2.4 RESULTS
# --------------------------------------------------

print("\n")
print("==========================================")
print("V2.4 COORDINATION RESULTS")
print("==========================================")

print(
    f"Original SPIKE QoS violations: "
    f"{original_spike_qos_violations}"
)

print(
    f"Coordinated QoS violations: "
    f"{coordinated_qos_violations}"
)

print(
    f"Original unmet demand: "
    f"{total_unmet_demand:.2f} Mbps-hours"
)

print(
    f"Coordinated unmet demand: "
    f"{total_coordinated_unmet_demand:.2f} Mbps-hours"
)

print(
    f"Total offered traffic: "
    f"{total_offered_traffic:.2f} Mbps-hours"
)

print(
    f"Coordinated throughput: "
    f"{total_coordinated_throughput:.2f} Mbps-hours"
)

print(
    f"Energy consumption: "
    f"{coordination_energy_kWh:.2f} kWh"
)

print(
    f"Energy saving: "
    f"{coordination_energy_saving_percent:.2f}%"
)


# --------------------------------------------------
# 9. IMPROVEMENT DUE TO COORDINATION
# --------------------------------------------------

qos_violations_reduced = (
    original_spike_qos_violations
    - coordinated_qos_violations
)


unmet_demand_reduced = (
    total_unmet_demand
    - total_coordinated_unmet_demand
)


print("\n")
print("==========================================")
print("V2.4 IMPROVEMENT")
print("==========================================")

print(
    f"QoS violations reduced: "
    f"{qos_violations_reduced}"
)

print(
    f"Unmet demand reduced: "
    f"{unmet_demand_reduced:.2f} Mbps-hours"
)


# --------------------------------------------------
# 10. DISPLAY ACTUAL COORDINATION EVENTS
# --------------------------------------------------

print("\n")
print("==========================================")
print("V2.4 COORDINATION EVENTS")
print("==========================================")

coordination_event_count = 0

for i in range(
    len(coord_df)
):

    for receiver_bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        received = coord_df.loc[
            i,
            f"BS{receiver_bs}_Offloaded_In_Mbps"
        ]

        if received > 0:

            coordination_event_count += 1

            print(
                f"Hour = "
                f"{coord_df.loc[i, 'Hour']} | "
                f"BS{receiver_bs} received "
                f"{received:.2f} Mbps "
                f"from neighboring BS(s)"
            )


print(
    f"\nTotal coordination events: "
    f"{coordination_event_count}"
)

# ==========================================
# 27. TRAFFIC GRAPHS FOR ALL SCENARIOS
# ==========================================

for scenario in scenarios:

    scenario_df = scenario_results[
        scenario
    ][0]

    plt.figure(
        figsize=(12, 6)
    )

    for bs in range(
        1,
        NUM_BASE_STATIONS + 1
    ):

        plt.plot(
            scenario_df["Hour"],
            scenario_df[
                f"BS{bs}"
            ],
            marker="o",
            label=f"BS{bs}"
        )

    plt.xlabel(
        "Time (Hour)"
    )

    plt.ylabel(
        "Traffic Demand (Mbps)"
    )

    plt.title(
        f"{scenario} Traffic Scenario"
    )

    plt.xticks(
        range(24)
    )

    plt.grid(
        True
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            GRAPH_DIR,
            f"{scenarios.index(scenario) + 4:02d}_"
            f"{scenario.lower()}_traffic.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# ==========================================
# 28. ENERGY SAVING COMPARISON
# ==========================================

energy_savings = []

for scenario in scenarios:

    energy_savings.append(
        scenario_results[
            scenario
        ][4]
    )


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    scenarios,
    energy_savings
)

plt.xlabel(
    "Traffic Scenario"
)

plt.ylabel(
    "Energy Saving (%)"
)

plt.title(
    "Energy Saving Across Traffic Scenarios"
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "08_energy_saving_comparison.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ==========================================
# 29. QOS VIOLATION COMPARISON
# ==========================================

qos_results = []

for scenario in scenarios:

    qos_results.append(
        scenario_results[
            scenario
        ][5]
    )


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    scenarios,
    qos_results
)

plt.xlabel(
    "Traffic Scenario"
)

plt.ylabel(
    "Number of QoS Violations"
)

plt.title(
    "QoS Violations Across Traffic Scenarios"
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "09_qos_violation_comparison.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# SECTION 30: V2.4 BEFORE vs AFTER COORDINATION - QoS
# ============================================================

print("\n==========================================")
print("V2.4 BEFORE vs AFTER COORDINATION - QoS")
print("==========================================")

qos_before = original_spike_qos_violations
qos_after = coordinated_qos_violations

print(f"Before coordination: {qos_before} violations")
print(f"After coordination:  {qos_after} violations")

plt.figure(figsize=(8, 5))

plt.bar(
    ["Before Coordination", "After Coordination"],
    [qos_before, qos_after]
)

plt.ylabel("Number of QoS Violations")
plt.title("SPIKE Traffic: QoS Violations Before vs After Coordination")

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "10_qos_violations_before_after_coordination.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# SECTION 31: V2.4 BEFORE vs AFTER COORDINATION - UNMET DEMAND
# ============================================================

print("\n==========================================")
print("V2.4 BEFORE vs AFTER COORDINATION - UNMET DEMAND")
print("==========================================")

unmet_before = total_unmet_demand
unmet_after = total_coordinated_unmet_demand

print(f"Before coordination: {unmet_before:.2f} Mbps-hours")
print(f"After coordination:  {unmet_after:.2f} Mbps-hours")

plt.figure(figsize=(8, 5))

plt.bar(
    ["Before Coordination", "After Coordination"],
    [unmet_before, unmet_after]
)

plt.ylabel("Unmet Demand (Mbps-hours)")
plt.title("SPIKE Traffic: Unmet Demand Before vs After Coordination")

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "11_unmet_demand_before_after_coordination.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# SECTION 32: SPIKE TRAFFIC - DEMAND vs AVAILABLE CAPACITY
# ============================================================

print("\n==========================================")
print("V2.4 SPIKE TRAFFIC - DEMAND vs AVAILABLE CAPACITY")
print("==========================================")

# Use the existing SPIKE scenario DataFrame
spike_df = scenario_results["SPIKE"][0]

# Plot demand and available capacity for each BS
for bs in range(1, NUM_BASE_STATIONS + 1):

    demand_column = f"BS{bs}"
    capacity_column = f"BS{bs}_Available_Capacity_Mbps"

    plt.figure(figsize=(10, 5))

    plt.plot(
        spike_df["Hour"],
        spike_df[demand_column],
        marker="o",
        label="Traffic Demand"
    )

    plt.plot(
        spike_df["Hour"],
        spike_df[capacity_column],
        marker="s",
        linestyle="--",
        label="Available Capacity"
    )

    plt.xlabel("Hour")
    plt.ylabel("Mbps")
    plt.title(
        f"SPIKE Traffic: BS{bs} Demand vs Available Capacity"
    )

    plt.xticks(spike_df["Hour"])
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            GRAPH_DIR,
            f"{bs + 11:02d}_bs{bs}_demand_vs_capacity.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

# ============================================================
# SECTION 33: TRAFFIC SCENARIO SUMMARY TABLE
# ============================================================

print("\n==========================================")
print("SECTION 33: TRAFFIC SCENARIO SUMMARY")
print("==========================================")

summary_data = []

for scenario in scenarios:

    (
        scenario_df,
        baseline_energy,
        optimised_energy,
        energy_saved,
        energy_saving_percent,
        qos_violations,
        qos_violation_rate,
        total_unmet_demand,
        peak_demand,
        peak_capacity,
        total_offered_traffic,
        total_throughput,
        average_resource_utilisation,
        average_throughput
    ) = scenario_results[scenario]

    summary_data.append({
        "Scenario": scenario,
        "Optimised Energy (kWh)": optimised_energy,
        "Energy Saving (%)": energy_saving_percent,
        "QoS Violations": qos_violations,
        "QoS Violation Rate (%)": qos_violation_rate,
        "Unmet Demand (Mbps-hours)": total_unmet_demand,
        "Avg Utilisation (%)": average_resource_utilisation,
        "Peak Demand (Mbps)": peak_demand
    })


summary_df = pd.DataFrame(summary_data)


print("\n")
print(summary_df.to_string(index=False))


# ============================================================
# VISUAL SUMMARY TABLE
# ============================================================

fig, ax = plt.subplots(figsize=(14, 4.5))

ax.axis("off")

table = ax.table(
    cellText=summary_df.round(2).values,
    colLabels=summary_df.columns,
    cellLoc="center",
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

plt.title(
    "Traffic Scenario Summary: Energy, QoS and Resource Utilisation",
    pad=20
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        GRAPH_DIR,
        "17_scenario_summary_table.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# V2.4.1 GRAPH EXPORT COMPLETE
# ============================================================

print("\n==========================================")
print("V2.4.1 GRAPH EXPORT")
print("==========================================")

print(f"All project graphs have been saved to:")
print(os.path.abspath(GRAPH_DIR))