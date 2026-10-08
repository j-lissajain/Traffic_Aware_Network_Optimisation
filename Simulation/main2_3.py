import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

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

plt.show()

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

plt.show()

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

plt.show()

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
# 24. V2.3 TRAFFIC SCENARIO EXPERIMENTS
# ==========================================

print("\n")
print("==========================================")
print("V2.3 TRAFFIC SCENARIO EXPERIMENTS")
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

    throughput_columns = [
        f"BS{i}_Throughput_Mbps"
        for i in range(
            1,
            NUM_BASE_STATIONS + 1
        )
    ]

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
print("V2.3 SCENARIO RESULTS")
print("==========================================")


for scenario in scenarios:

    (
        scenario_df,
        baseline_energy,
        optimised_energy,
        energy_saved,
        energy_saving_percent,
        qos_violations,
        utilisation,
        throughput
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
        f"{utilisation:.2f}%"
    )

    print(
        f"Average throughput: "
        f"{throughput:.2f} Mbps"
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

    plt.show()


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

plt.show()


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

plt.show()