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
# 8. CALCULATE POWER CONSUMPTION
# ==========================================

for bs in range(1, NUM_BASE_STATIONS + 1):

    utilisation = df[f"BS{bs}_Utilisation"] / 100

    df[f"BS{bs}_Power_W"] = (
        IDLE_POWER_W
        + (MAX_POWER_W - IDLE_POWER_W) * utilisation
    )

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