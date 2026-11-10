import pandas as pd
from pathlib import Path

# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed" / "metro"
REPORT_DIR = BASE_DIR / "reports" / "metro"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# LOAD DATA
# ==============================

trips = pd.read_csv(DATA_DIR / "trips_clean.csv")
stop_times = pd.read_csv(DATA_DIR / "stop_times_clean.csv")

print("Metro service data loaded successfully.")

# ==============================
# SERVICE BY HOUR
# ==============================

# Convert arrival_time to string
stop_times["arrival_time"] = stop_times["arrival_time"].astype(str)

# Extract hour from GTFS time
stop_times["gtfs_hour"] = (
    stop_times["arrival_time"]
    .str.extract(r"^(\d+):")[0]
    .astype(float)
)

# Remove invalid/missing times
stop_times = stop_times.dropna(subset=["gtfs_hour"])

stop_times["gtfs_hour"] = stop_times["gtfs_hour"].astype(int)

# Count scheduled stop activity by hour
service_by_hour = (
    stop_times
    .groupby("gtfs_hour")
    .size()
    .reset_index(name="scheduled_stop_visits")
    .sort_values("gtfs_hour")
)

# ==============================
# PEAK SERVICE
# ==============================

peak_row = service_by_hour.loc[
    service_by_hour["scheduled_stop_visits"].idxmax()
]

peak_hour = int(peak_row["gtfs_hour"])
peak_volume = int(peak_row["scheduled_stop_visits"])

# ==============================
# SERVICE BY ROUTE
# ==============================

stop_route_data = stop_times.merge(
    trips[["trip_id", "route_id"]],
    on="trip_id",
    how="left"
)

service_by_route = (
    stop_route_data
    .groupby("route_id")
    .size()
    .reset_index(name="scheduled_stop_visits")
    .sort_values(
        "scheduled_stop_visits",
        ascending=False
    )
)

# ==============================
# SAVE REPORTS
# ==============================

hourly_output = REPORT_DIR / "metro_service_by_hour.csv"

service_by_hour.to_csv(
    hourly_output,
    index=False
)

route_output = REPORT_DIR / "metro_service_by_route.csv"

service_by_route.to_csv(
    route_output,
    index=False
)

# ==============================
# SUMMARY
# ==============================

print("\nMetro Service Analysis Complete!")
print("----------------------------------")

print(
    f"Peak scheduled service hour: "
    f"{peak_hour:02d}:00"
)

print(
    f"Peak scheduled stop visits: "
    f"{peak_volume:,}"
)

print(
    f"Hours represented in dataset: "
    f"{service_by_hour['gtfs_hour'].min()} "
    f"to "
    f"{service_by_hour['gtfs_hour'].max()}"
)

print("\nScheduled Service by Hour:")
print(service_by_hour.to_string(index=False))

print("\nTop Metro Routes by Scheduled Stop Activity:")
print(service_by_route.head(10).to_string(index=False))

print("\nReports saved to:")
print(hourly_output)
print(route_output)