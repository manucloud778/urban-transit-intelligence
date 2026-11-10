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

print("Loading stops...")

stops = pd.read_csv(
    PROCESSED_DIR / "stops_clean.csv",
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


stop_route = stop_times.merge(
    trip_route,
    on="trip_id",
    how="left"
)


# ==============================
# COUNT UNIQUE ROUTES PER STOP
# ==============================

print("Calculating routes serving each stop...")

stop_route_counts = (
    stop_route
    .groupby("stop_id")["route_id"]
    .nunique()
    .reset_index(name="unique_routes")
)


# ==============================
# ADD STOP INFORMATION
# ==============================

stop_analysis = stop_route_counts.merge(
    stops[
        [
            "stop_id",
            "stop_code",
            "stop_name",
            "stop_lat",
            "stop_lon",
            "zone_id"
        ]
    ],
    on="stop_id",
    how="left"
)


# ==============================
# SORT BY NUMBER OF ROUTES
# ==============================

stop_analysis = stop_analysis.sort_values(
    "unique_routes",
    ascending=False
)


# ==============================
# SAVE RESULT
# ==============================

output_file = OUTPUT_DIR / "stop_route_analysis.csv"

stop_analysis.to_csv(
    output_file,
    index=False
)


# ==============================
# DISPLAY TOP 20
# ==============================

print("\nTOP 20 STOPS BY NUMBER OF UNIQUE ROUTES")
print("=" * 75)

print(
    stop_analysis[
        [
            "stop_id",
            "stop_name",
            "zone_id",
            "unique_routes"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n==============================")
print("STOP ANALYSIS COMPLETE")
print("==============================")

print(f"\nTotal stops analyzed: {len(stop_analysis):,}")
print(f"Saved to: {output_file}")