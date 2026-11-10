import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# URBAN TRANSIT INTELLIGENCE
# Representative Complete-Trip Sampling
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

STOP_TIMES_FILE = BASE_DIR / "data" / "processed" / "stop_times_clean.csv"
TRIPS_FILE = BASE_DIR / "data" / "processed" / "trips_clean.csv"
ROUTES_FILE = BASE_DIR / "data" / "processed" / "routes_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "sampled"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "stop_times_sampled.csv"

# Target size
TARGET_ROWS = 350_000

# Fixed random seed = reproducible sampling
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)

print("=" * 60)
print("REPRESENTATIVE TRANSIT DATA SAMPLING")
print("=" * 60)


# ============================================================
# STEP 1 — LOAD TRIP AND ROUTE INFORMATION
# ============================================================

print("\n[1/6] Loading trip and route information...")

trips = pd.read_csv(
    TRIPS_FILE,
    usecols=["trip_id", "route_id", "service_id"]
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

print(f"Total trips: {len(trip_info):,}")
print(f"Total routes: {trip_info['route_id'].nunique():,}")

print("\nAgency distribution:")
print(trip_info["agency_id"].value_counts())


# ============================================================
# STEP 2 — READ STOP_TIMES AND CALCULATE TRIP INFORMATION
# ============================================================

print("\n[2/6] Reading stop_times to determine trip characteristics...")
print("This may take a few minutes...")

trip_stop_counts = {}
trip_start_hour = {}

chunksize = 200_000

for chunk_number, chunk in enumerate(
    pd.read_csv(
        STOP_TIMES_FILE,
        usecols=[
            "trip_id",
            "arrival_time",
            "stop_id",
            "stop_sequence"
        ],
        chunksize=chunksize
    ),
    start=1
):

    # --------------------------------------------------------
    # Number of stops per trip
    # --------------------------------------------------------

    counts = chunk.groupby("trip_id")["stop_id"].nunique()

    for trip_id, count in counts.items():
        trip_stop_counts[trip_id] = (
            trip_stop_counts.get(trip_id, 0) + count
        )

    # --------------------------------------------------------
    # First stop / starting time of each trip
    # --------------------------------------------------------

    chunk["hour"] = (
        chunk["arrival_time"]
        .astype(str)
        .str.split(":")
        .str[0]
        .astype(int)
    )

    first_times = (
        chunk.sort_values(
            ["trip_id", "stop_sequence"]
        )
        .drop_duplicates("trip_id")
        [["trip_id", "hour"]]
    )

    for row in first_times.itertuples(index=False):
        trip_start_hour[row.trip_id] = row.hour

    if chunk_number % 5 == 0:
        print(
            f"   Processed approximately "
            f"{chunk_number * chunksize:,} rows..."
        )


# Convert dictionaries to DataFrames

stop_count_df = pd.DataFrame(
    list(trip_stop_counts.items()),
    columns=["trip_id", "stop_count"]
)

start_hour_df = pd.DataFrame(
    list(trip_start_hour.items()),
    columns=["trip_id", "start_hour"]
)

trip_info = trip_info.merge(
    stop_count_df,
    on="trip_id",
    how="left"
)

trip_info = trip_info.merge(
    start_hour_df,
    on="trip_id",
    how="left"
)

print(f"\nTrips with stop information: {len(trip_info):,}")


# ============================================================
# STEP 3 — CLASSIFY TRIPS
# ============================================================

print("\n[3/6] Classifying trips...")

# ------------------------------------------------------------
# Trip length
# ------------------------------------------------------------

def length_category(stops):

    if stops <= 10:
        return "Short"

    elif stops <= 30:
        return "Medium"

    else:
        return "Long"


trip_info["length_group"] = (
    trip_info["stop_count"]
    .apply(length_category)
)


# ------------------------------------------------------------
# Time period
# ------------------------------------------------------------

def time_period(hour):

    # GTFS extended hours are allowed
    hour = int(hour)

    if 5 <= hour < 10:
        return "Morning"

    elif 10 <= hour < 15:
        return "Midday"

    elif 15 <= hour < 20:
        return "Evening"

    else:
        return "Late"


trip_info["time_period"] = (
    trip_info["start_hour"]
    .apply(time_period)
)


print("\nTrip length distribution:")
print(
    trip_info["length_group"]
    .value_counts()
)

print("\nTime-period distribution:")
print(
    trip_info["time_period"]
    .value_counts()
)


# ============================================================
# STEP 4 — CALCULATE HOW MANY TRIPS TO SELECT PER ROUTE
# ============================================================

print("\n[4/6] Creating route-level sampling quotas...")

# Total rows represented by all trips
total_rows = trip_info["stop_count"].sum()

print(f"Estimated total stop rows: {total_rows:,}")

# ------------------------------------------------------------
# Initial route quota:
# proportionally represent route size
# ------------------------------------------------------------

route_stats = (
    trip_info
    .groupby(["agency_id", "route_id"])
    .agg(
        total_trips=("trip_id", "count"),
        total_stops=("stop_count", "sum")
    )
    .reset_index()
)

route_stats["target_rows"] = (
    route_stats["total_stops"]
    / total_rows
    * TARGET_ROWS
)

# Estimate number of trips required
route_stats["avg_stops"] = (
    route_stats["total_stops"]
    / route_stats["total_trips"]
)

route_stats["trips_to_select"] = (
    route_stats["target_rows"]
    / route_stats["avg_stops"]
).round().astype(int)

# ------------------------------------------------------------
# VERY IMPORTANT:
# Every route gets at least one complete trip
# ------------------------------------------------------------

route_stats["trips_to_select"] = (
    route_stats["trips_to_select"]
    .clip(lower=1)
)

# Never select more trips than actually exist
route_stats["trips_to_select"] = np.minimum(
    route_stats["trips_to_select"],
    route_stats["total_trips"]
)

print(
    f"\nRoutes represented: "
    f"{len(route_stats):,}"
)

print(
    f"Minimum trips selected per route: "
    f"{route_stats['trips_to_select'].min()}"
)

print(
    f"Maximum trips selected for a route: "
    f"{route_stats['trips_to_select'].max()}"
)


# ============================================================
# STEP 5 — SELECT COMPLETE TRIPS
# ============================================================

print("\n[5/6] Selecting representative complete trips...")

selected_trip_ids = []

# Process route by route
for _, route in route_stats.iterrows():

    route_id = route["route_id"]
    n_select = int(route["trips_to_select"])

    candidates = trip_info[
        trip_info["route_id"] == route_id
    ].copy()

    # --------------------------------------------------------
    # Create a randomized ranking inside each
    # time + length group.
    # --------------------------------------------------------

    candidates["random"] = np.random.random(
        len(candidates)
    )

    # Sort by time period + length + random value.
    # This spreads selection across different characteristics.
    candidates = candidates.sort_values(
        [
            "time_period",
            "length_group",
            "random"
        ]
    )

    # --------------------------------------------------------
    # Take evenly distributed candidates rather than
    # simply taking the first N rows.
    # --------------------------------------------------------

    if len(candidates) <= n_select:

        chosen = candidates

    else:

        positions = np.linspace(
            0,
            len(candidates) - 1,
            n_select,
            dtype=int
        )

        chosen = candidates.iloc[positions]

    selected_trip_ids.extend(
        chosen["trip_id"].tolist()
    )


selected_trip_ids = list(
    dict.fromkeys(selected_trip_ids)
)

print(
    f"\nSelected complete trips: "
    f"{len(selected_trip_ids):,}"
)


# ============================================================
# STEP 6 — EXTRACT ALL STOP_TIMES FOR SELECTED TRIPS
# ============================================================

print("\n[6/6] Extracting complete stop sequences...")
print("Only selected trips will be written to the sample.")

selected_set = set(selected_trip_ids)

sample_chunks = []

for chunk_number, chunk in enumerate(
    pd.read_csv(
        STOP_TIMES_FILE,
        usecols=[
            "trip_id",
            "arrival_time",
            "departure_time",
            "stop_id",
            "stop_sequence"
        ],
        chunksize=chunksize
    ),
    start=1
):

    selected_chunk = chunk[
        chunk["trip_id"].isin(selected_set)
    ]

    if not selected_chunk.empty:

        sample_chunks.append(
            selected_chunk
        )

    if chunk_number % 5 == 0:
        print(
            f"   Scanned approximately "
            f"{chunk_number * chunksize:,} rows..."
        )


sample = pd.concat(
    sample_chunks,
    ignore_index=True
)

# Sort properly
sample = sample.sort_values(
    ["trip_id", "stop_sequence"]
)

# Save
sample.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("SAMPLING COMPLETE")
print("=" * 60)

print(
    f"\nOriginal rows:      {total_rows:,}"
)

print(
    f"Sample rows:        {len(sample):,}"
)

print(
    f"Reduction:          "
    f"{(1 - len(sample) / total_rows) * 100:.2f}%"
)

print(
    f"Selected trips:     {sample['trip_id'].nunique():,}"
)

print(
    f"Selected stops:     {sample['stop_id'].nunique():,}"
)

print(
    f"Selected routes:    "
    f"{trip_info[
        trip_info['trip_id'].isin(selected_set)
    ]['route_id'].nunique():,}"
)

print("\nColumns:")
print(list(sample.columns))

print("\nSample agency distribution:")

selected_info = trip_info[
    trip_info["trip_id"].isin(selected_set)
]

print(
    selected_info["agency_id"].value_counts()
)

print("\nSample length distribution:")

print(
    selected_info["length_group"].value_counts()
)

print("\nSample time-period distribution:")

print(
    selected_info["time_period"].value_counts()
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nIMPORTANT:")
print("Original stop_times_clean.csv was NOT modified.")