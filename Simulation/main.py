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