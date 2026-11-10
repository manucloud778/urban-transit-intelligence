import pandas as pd
from pathlib import Path

# ============================================================
# VALIDATE REPRESENTATIVE SAMPLE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

STOP_TIMES_FILE = BASE_DIR / "data" / "processed" / "stop_times_clean.csv"
SAMPLE_FILE = BASE_DIR / "data" / "sampled" / "stop_times_sampled.csv"
TRIPS_FILE = BASE_DIR / "data" / "processed" / "trips_clean.csv"
ROUTES_FILE = BASE_DIR / "data" / "processed" / "routes_clean.csv"

print("=" * 60)
print("REPRESENTATIVE SAMPLE VALIDATION")
print("=" * 60)


# ============================================================
# 1. LOAD TRIP + ROUTE INFORMATION
# ============================================================

print("\n[1/7] Loading trip and route information...")

trips = pd.read_csv(
    TRIPS_FILE,
    usecols=["trip_id", "route_id"]
)

routes = pd.read_csv(
    ROUTES_FILE,
    usecols=["route_id", "agency_id"]
)

trip_info = trips.merge(
    routes,
    on="route_id",
    how="left"
)


# ============================================================
# 2. LOAD SAMPLE
# ============================================================

print("\n[2/7] Loading sampled dataset...")

sample = pd.read_csv(SAMPLE_FILE)

print(f"Sample rows: {len(sample):,}")
print(f"Sample trips: {sample['trip_id'].nunique():,}")
print(f"Sample stops: {sample['stop_id'].nunique():,}")

print("\nColumns:")
print(list(sample.columns))


# ============================================================
# 3. ROUTE + AGENCY COVERAGE
# ============================================================

print("\n[3/7] Checking route and agency coverage...")

sample_trip_info = trip_info[
    trip_info["trip_id"].isin(
        sample["trip_id"].unique()
    )
].copy()

sample_routes = sample_trip_info["route_id"].nunique()
total_routes = trip_info["route_id"].nunique()

print(
    f"Routes represented: "
    f"{sample_routes:,} / {total_routes:,}"
)

print("\nAgency distribution:")
print(
    sample_trip_info["agency_id"].value_counts()
)

print("\nAgency percentage:")
print(
    sample_trip_info["agency_id"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 4. COMPLETE TRIP CHECK
# ============================================================

print("\n[4/7] Checking complete trips...")

# Count rows in original for selected trips
selected_trips = set(
    sample["trip_id"].unique()
)

original_counts = {}

for chunk in pd.read_csv(
    STOP_TIMES_FILE,
    usecols=["trip_id"],
    chunksize=200_000
):

    selected = chunk[
        chunk["trip_id"].isin(selected_trips)
    ]

    counts = selected["trip_id"].value_counts()

    for trip_id, count in counts.items():
        original_counts[trip_id] = (
            original_counts.get(trip_id, 0) + count
        )


sample_counts = (
    sample["trip_id"]
    .value_counts()
    .to_dict()
)

incomplete_trips = []

for trip_id in selected_trips:

    original_count = original_counts.get(
        trip_id,
        0
    )

    sample_count = sample_counts.get(
        trip_id,
        0
    )

    if original_count != sample_count:
        incomplete_trips.append(
            (
                trip_id,
                original_count,
                sample_count
            )
        )

print(
    f"Complete trips: "
    f"{len(selected_trips) - len(incomplete_trips):,}"
)

print(
    f"Incomplete trips: "
    f"{len(incomplete_trips):,}"
)

if len(incomplete_trips) == 0:
    print("PASS: Every selected trip is complete.")
else:
    print("WARNING: Some trips are incomplete.")


# ============================================================
# 5. STOP COVERAGE
# ============================================================

print("\n[5/7] Checking stop coverage...")

# Full dataset stop IDs
full_stops = set()

for chunk in pd.read_csv(
    STOP_TIMES_FILE,
    usecols=["stop_id"],
    chunksize=200_000
):

    full_stops.update(
        chunk["stop_id"].unique()
    )

sample_stops = set(
    sample["stop_id"].unique()
)

covered_stops = len(
    full_stops.intersection(sample_stops)
)

print(
    f"Stops represented: "
    f"{covered_stops:,} / {len(full_stops):,}"
)

print(
    f"Stop coverage: "
    f"{covered_stops / len(full_stops) * 100:.2f}%"
)


# ============================================================
# 6. TRIP LENGTH DISTRIBUTION
# ============================================================

print("\n[6/7] Checking trip-length distribution...")

sample_stop_counts = (
    sample.groupby("trip_id")["stop_id"]
    .nunique()
)

def classify_length(x):

    if x <= 10:
        return "Short"
    elif x <= 30:
        return "Medium"
    else:
        return "Long"


sample_length = (
    sample_stop_counts
    .apply(classify_length)
)

print("\nSample trip-length distribution:")

print(
    sample_length
    .value_counts()
)

print("\nSample trip-length percentage:")

print(
    sample_length
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 7. TIME PERIOD DISTRIBUTION
# ============================================================

print("\n[7/7] Checking time-period distribution...")

# First arrival time of each selected trip
first_times = (
    sample
    .sort_values(
        ["trip_id", "stop_sequence"]
    )
    .drop_duplicates("trip_id")
    [["trip_id", "arrival_time"]]
)

first_times["start_hour"] = (
    first_times["arrival_time"]
    .astype(str)
    .str.split(":")
    .str[0]
    .astype(int)
)


def classify_time(hour):

    if 5 <= hour < 10:
        return "Morning"

    elif 10 <= hour < 15:
        return "Midday"

    elif 15 <= hour < 20:
        return "Evening"

    else:
        return "Late"


first_times["time_period"] = (
    first_times["start_hour"]
    .apply(classify_time)
)

print("\nSample time-period distribution:")

print(
    first_times["time_period"]
    .value_counts()
)

print("\nSample time-period percentage:")

print(
    first_times["time_period"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

print("\nIMPORTANT CHECKS:")

print(
    f"Route coverage: "
    f"{sample_routes:,}/{total_routes:,}"
)

print(
    f"Stop coverage: "
    f"{covered_stops:,}/{len(full_stops):,}"
)

print(
    f"Incomplete trips: "
    f"{len(incomplete_trips):,}"
)

if (
    sample_routes == total_routes
    and len(incomplete_trips) == 0
):

    print(
        "\nCORE VALIDATION: PASS"
    )

else:

    print(
        "\nCORE VALIDATION: NEEDS REVIEW"
    )

print("\nDo NOT import into MySQL yet.")