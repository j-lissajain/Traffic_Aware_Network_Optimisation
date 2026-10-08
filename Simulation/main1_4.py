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
# 15. TRAFFIC-AWARE OPTIMISATION
# ==========================================

def select_operating_level(demand):

    if demand <= LOW_CAPACITY_MBPS:
        return "LOW"

    elif demand <= MEDIUM_CAPACITY_MBPS:
        return "MEDIUM"

    elif demand <= HIGH_CAPACITY_MBPS:
        return "HIGH"

    else:
        return "OVERLOAD"

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
# 18. CALCULATE OPTIMISED POWER
# ==========================================

def get_power(level):

    if level == "LOW":
        return LOW_POWER_W

    elif level == "MEDIUM":
        return MEDIUM_POWER_W

    elif level == "HIGH":
        return HIGH_POWER_W

    else:
        return MAX_POWER_W

for bs in range(1, NUM_BASE_STATIONS + 1):

    df[f"BS{bs}_Optimised_Power_W"] = (
        df[f"BS{bs}_Level"].apply(get_power)
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
# 21. QOS CHECK FOR OPTIMISED NETWORK
# ==========================================

total_qos_violations = 0

for bs in range(1, NUM_BASE_STATIONS + 1):

    for i in range(len(df)):

        demand = df.loc[i, f"BS{bs}"]

        level = df.loc[i, f"BS{bs}_Level"]

        if level == "LOW":
            capacity = LOW_CAPACITY_MBPS

        elif level == "MEDIUM":
            capacity = MEDIUM_CAPACITY_MBPS

        elif level == "HIGH":
            capacity = HIGH_CAPACITY_MBPS

        else:
            capacity = HIGH_CAPACITY_MBPS

        qos = check_qos(demand, capacity)

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