import pandas as pd
from pathlib import Path

# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

STOP_TIMES = BASE_DIR / "data" / "processed" / "stop_times_clean.csv"
TRIPS = BASE_DIR / "data" / "processed" / "trips_clean.csv"
ROUTES = BASE_DIR / "data" / "processed" / "routes_clean.csv"

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# ==============================
# 1. BASIC STOP_TIME ANALYSIS
# ==============================

print("\n==============================")
print("STOP_TIME DATASET ANALYSIS")
print("==============================")

total_rows = 0
unique_trips = set()
unique_stops = set()

hour_counts = {}

for chunk in pd.read_csv(STOP_TIMES, chunksize=200_000):

    total_rows += len(chunk)

    unique_trips.update(chunk["trip_id"].unique())
    unique_stops.update(chunk["stop_id"].unique())

    # Extract hour from arrival time
    hours = (
        chunk["arrival_time"]
        .astype(str)
        .str.split(":")
        .str[0]
        .astype(int)
    )

    counts = hours.value_counts()

    for hour, count in counts.items():
        hour_counts[hour] = hour_counts.get(hour, 0) + count


print(f"\nTotal stop_time rows: {total_rows:,}")
print(f"Unique trips: {len(unique_trips):,}")
print(f"Unique stops: {len(unique_stops):,}")

# ==============================
# 2. HOURLY DISTRIBUTION
# ==============================

hour_df = pd.DataFrame(
    list(hour_counts.items()),
    columns=["hour", "stop_time_count"]
).sort_values("hour")

hour_df.to_csv(
    REPORT_DIR / "sampling_hour_distribution.csv",
    index=False
)

print("\nHourly distribution:")
print(hour_df.to_string(index=False))

# ==============================
# 3. TRIP LENGTH ANALYSIS
# ==============================

print("\n==============================")
print("TRIP LENGTH ANALYSIS")
print("==============================")

trip_lengths = []

for chunk in pd.read_csv(
    STOP_TIMES,
    usecols=["trip_id", "stop_id"],
    chunksize=200_000
):

    counts = chunk.groupby("trip_id")["stop_id"].nunique()

    trip_lengths.append(counts)

trip_lengths = pd.concat(trip_lengths)

print("\nTrip length statistics:")
print(trip_lengths.describe())

trip_length_report = pd.DataFrame({
    "trip_id": trip_lengths.index,
    "stop_count": trip_lengths.values
})

trip_length_report.to_csv(
    REPORT_DIR / "trip_length_distribution.csv",
    index=False
)

# ==============================
# 4. TRIP → ROUTE → AGENCY
# ==============================

print("\n==============================")
print("ROUTE / AGENCY ANALYSIS")
print("==============================")

trips = pd.read_csv(TRIPS)
routes = pd.read_csv(ROUTES)

mapping = trips[
    ["trip_id", "route_id", "service_id"]
].merge(
    routes[
        ["route_id", "agency_id"]
    ],
    on="route_id",
    how="left"
)

mapping = mapping.merge(
    trip_length_report,
    on="trip_id",
    how="left"
)

print(f"\nTrips in mapping: {len(mapping):,}")
print(f"Unique routes: {mapping['route_id'].nunique():,}")
print(f"Agencies:")
print(mapping["agency_id"].value_counts())

# ==============================
# 5. ROUTE COVERAGE
# ==============================

route_summary = (
    mapping
    .groupby(["agency_id", "route_id"])
    .agg(
        trips=("trip_id", "nunique"),
        avg_stops_per_trip=("stop_count", "mean")
    )
    .reset_index()
)

route_summary.to_csv(
    REPORT_DIR / "sampling_route_distribution.csv",
    index=False
)

print("\nRoute distribution summary:")
print(route_summary.describe())

# ==============================
# 6. TRIP LENGTH GROUPS
# ==============================

def classify_trip_length(x):

    if x <= 10:
        return "Short"

    elif x <= 30:
        return "Medium"

    else:
        return "Long"


mapping["trip_length_group"] = mapping["stop_count"].apply(
    classify_trip_length
)

print("\nTrip length groups:")
print(
    mapping["trip_length_group"]
    .value_counts()
)

# ==============================
# 7. SAVE SAMPLING FRAME
# ==============================

mapping.to_csv(
    REPORT_DIR / "sampling_frame.csv",
    index=False
)

print("\n==============================")
print("ANALYSIS COMPLETE")
print("==============================")

print("\nReports created:")
print("1. sampling_hour_distribution.csv")
print("2. trip_length_distribution.csv")
print("3. sampling_route_distribution.csv")
print("4. sampling_frame.csv")

print("\nNext step:")
print("Use these distributions to create a representative sample.")