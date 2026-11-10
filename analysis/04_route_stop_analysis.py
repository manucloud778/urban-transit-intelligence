import pandas as pd
from pathlib import Path

# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# LOAD DATA
# ==============================

print("Loading routes...")
routes = pd.read_csv(
    PROCESSED_DIR / "routes_clean.csv",
    dtype=str
)

print("Loading trips...")
trips = pd.read_csv(
    PROCESSED_DIR / "trips_clean.csv",
    dtype=str
)

print("Loading stop times...")
stop_times = pd.read_csv(
    PROCESSED_DIR / "stop_times_clean.csv",
    dtype={
        "trip_id": str,
        "stop_id": str
    },
    usecols=["trip_id", "stop_id"]
)


# ==============================
# CONNECT TRIPS TO ROUTES
# ==============================

print("\nConnecting trips to routes...")

trip_route = trips[
    ["trip_id", "route_id"]
].drop_duplicates()


stop_times_route = stop_times.merge(
    trip_route,
    on="trip_id",
    how="left"
)


# ==============================
# COUNT UNIQUE STOPS PER ROUTE
# ==============================

print("Calculating unique stops per route...")

route_stop_counts = (
    stop_times_route
    .groupby("route_id")["stop_id"]
    .nunique()
    .reset_index(name="unique_stops")
)


# ==============================
# ADD ROUTE INFORMATION
# ==============================

route_analysis = route_stop_counts.merge(
    routes[
        [
            "route_id",
            "route_long_name",
            "agency_id"
        ]
    ],
    on="route_id",
    how="left"
)


# ==============================
# SORT
# ==============================

route_analysis = route_analysis.sort_values(
    "unique_stops",
    ascending=False
)


# ==============================
# SAVE RESULT
# ==============================

output_file = OUTPUT_DIR / "route_stop_analysis.csv"

route_analysis.to_csv(
    output_file,
    index=False
)


# ==============================
# DISPLAY TOP 20
# ==============================

print("\nTOP 20 ROUTES BY UNIQUE STOPS")
print("=" * 65)

print(
    route_analysis[
        [
            "route_id",
            "route_long_name",
            "agency_id",
            "unique_stops"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n==============================")
print("ROUTE-STOP ANALYSIS COMPLETE")
print("==============================")

print(f"\nTotal routes analyzed: {len(route_analysis):,}")
print(f"Saved to: {output_file}")