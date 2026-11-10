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


# ==============================
# COUNT TRIPS BY ROUTE
# ==============================

print("\nCalculating scheduled trips by route...")

trip_counts = (
    trips
    .groupby("route_id")
    .size()
    .reset_index(name="scheduled_trips")
)


# ==============================
# JOIN WITH ROUTE INFORMATION
# ==============================

route_analysis = trip_counts.merge(
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
# SORT BY TRIP COUNT
# ==============================

route_analysis = route_analysis.sort_values(
    "scheduled_trips",
    ascending=False
)


# ==============================
# SAVE RESULT
# ==============================

output_file = OUTPUT_DIR / "route_trip_analysis.csv"

route_analysis.to_csv(
    output_file,
    index=False
)


# ==============================
# DISPLAY TOP 20
# ==============================

print("\nTOP 20 ROUTES BY SCHEDULED TRIPS")
print("=" * 60)

print(
    route_analysis[
        [
            "route_id",
            "route_long_name",
            "agency_id",
            "scheduled_trips"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n==============================")
print("ROUTE ANALYSIS COMPLETE")
print("==============================")

print(f"\nTotal routes analyzed: {len(route_analysis):,}")
print(f"Saved to: {output_file}")