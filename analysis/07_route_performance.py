import pandas as pd
from pathlib import Path

# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# LOAD PREVIOUS ANALYSES
# ==============================

print("Loading route trip analysis...")

trip_analysis = pd.read_csv(
    REPORTS_DIR / "route_trip_analysis.csv",
    dtype={"route_id": str}
)

print("Loading route stop analysis...")

stop_analysis = pd.read_csv(
    REPORTS_DIR / "route_stop_analysis.csv",
    dtype={"route_id": str}
)


# ==============================
# SELECT REQUIRED COLUMNS
# ==============================

trip_analysis = trip_analysis[
    [
        "route_id",
        "route_long_name",
        "agency_id",
        "scheduled_trips"
    ]
]

stop_analysis = stop_analysis[
    [
        "route_id",
        "unique_stops"
    ]
]


# ==============================
# COMBINE ROUTE METRICS
# ==============================

print("\nCombining route metrics...")

route_performance = trip_analysis.merge(
    stop_analysis,
    on="route_id",
    how="left"
)


# ==============================
# CALCULATE TRIPS PER STOP
# ==============================

route_performance["trips_per_stop"] = (
    route_performance["scheduled_trips"]
    / route_performance["unique_stops"]
)


# ==============================
# CLASSIFY ROUTES
# ==============================

median_trips = route_performance["scheduled_trips"].median()
median_stops = route_performance["unique_stops"].median()

print(f"\nMedian scheduled trips: {median_trips:.0f}")
print(f"Median unique stops: {median_stops:.0f}")


def classify_route(row):

    high_trips = row["scheduled_trips"] >= median_trips
    high_stops = row["unique_stops"] >= median_stops

    if high_trips and high_stops:
        return "High Service + High Coverage"

    elif high_trips and not high_stops:
        return "High Service + Lower Coverage"

    elif not high_trips and high_stops:
        return "Lower Service + High Coverage"

    else:
        return "Lower Service + Lower Coverage"


route_performance["route_category"] = (
    route_performance.apply(
        classify_route,
        axis=1
    )
)


# ==============================
# SORT BY SCHEDULED TRIPS
# ==============================

route_performance = route_performance.sort_values(
    "scheduled_trips",
    ascending=False
)


# ==============================
# SAVE RESULT
# ==============================

output_file = OUTPUT_DIR / "route_performance_analysis.csv"

route_performance.to_csv(
    output_file,
    index=False
)


# ==============================
# DISPLAY SUMMARY
# ==============================

print("\nROUTE PERFORMANCE SUMMARY")
print("=" * 70)

print(
    route_performance[
        [
            "route_id",
            "route_long_name",
            "agency_id",
            "scheduled_trips",
            "unique_stops",
            "trips_per_stop",
            "route_category"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ==============================
# CATEGORY COUNTS
# ==============================

print("\nROUTE CATEGORY COUNTS")
print("=" * 50)

category_counts = (
    route_performance["route_category"]
    .value_counts()
)

print(category_counts.to_string())


# ==============================
# COMPLETE
# ==============================

print("\n==============================")
print("ROUTE PERFORMANCE COMPLETE")
print("==============================")

print(f"\nTotal routes analyzed: {len(route_performance):,}")
print(f"Saved to: {output_file}")