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

routes = pd.read_csv(DATA_DIR / "routes_clean.csv")
trips = pd.read_csv(DATA_DIR / "trips_clean.csv")
stop_times = pd.read_csv(DATA_DIR / "stop_times_clean.csv")

print("Metro data loaded successfully.")

# ==============================
# ROUTE ANALYSIS
# ==============================

# Scheduled trips per route
trip_counts = (
    trips.groupby("route_id")["trip_id"]
    .nunique()
    .reset_index(name="scheduled_trips")
)

# Unique stops served by each route
route_stops = (
    stop_times.merge(
        trips[["trip_id", "route_id"]],
        on="trip_id",
        how="left"
    )
    .groupby("route_id")["stop_id"]
    .nunique()
    .reset_index(name="unique_stops")
)

# ==============================
# MERGE RESULTS
# ==============================

route_analysis = routes[
    [
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_type"
    ]
].copy()

route_analysis = route_analysis.merge(
    trip_counts,
    on="route_id",
    how="left"
)

route_analysis = route_analysis.merge(
    route_stops,
    on="route_id",
    how="left"
)

# Fill missing analytical values
route_analysis["scheduled_trips"] = (
    route_analysis["scheduled_trips"]
    .fillna(0)
    .astype(int)
)

route_analysis["unique_stops"] = (
    route_analysis["unique_stops"]
    .fillna(0)
    .astype(int)
)

# Average scheduled trips per stop
route_analysis["trips_per_stop"] = (
    route_analysis["scheduled_trips"]
    / route_analysis["unique_stops"].replace(0, pd.NA)
).round(2)

# ==============================
# SORT
# ==============================

route_analysis = route_analysis.sort_values(
    "scheduled_trips",
    ascending=False
)

# ==============================
# SAVE REPORT
# ==============================

output_file = REPORT_DIR / "metro_route_analysis.csv"

route_analysis.to_csv(
    output_file,
    index=False
)

# ==============================
# SUMMARY
# ==============================

print("\nMetro Route Analysis Complete!")
print("--------------------------------")
print(f"Total routes: {route_analysis['route_id'].nunique()}")
print(f"Total scheduled trips: {route_analysis['scheduled_trips'].sum()}")
print(
    f"Average stops per route: "
    f"{route_analysis['unique_stops'].mean():.2f}"
)

print("\nTop Metro Routes by Scheduled Service:")
print(
    route_analysis[
        [
            "route_id",
            "route_short_name",
            "route_long_name",
            "scheduled_trips",
            "unique_stops"
        ]
    ].head(10).to_string(index=False)
)

print(f"\nReport saved to:")
print(output_file)