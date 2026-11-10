import pandas as pd
from pathlib import Path

# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# 1. CLEAN ROUTES
# ==============================

print("\nCleaning routes.txt...")

routes = pd.read_csv(RAW_DIR / "routes.txt")

# Remove completely empty rows
routes = routes.dropna(how="all")

# Convert ID columns to string
routes["agency_id"] = routes["agency_id"].astype(str).str.strip()
routes["route_id"] = routes["route_id"].astype(str).str.strip()

# Clean route name
routes["route_long_name"] = (
    routes["route_long_name"]
    .astype(str)
    .str.strip()
)

# Remove unnecessary whitespace from column names
routes.columns = routes.columns.str.strip()

# Save cleaned routes
routes.to_csv(
    PROCESSED_DIR / "routes_clean.csv",
    index=False
)

print(f"Routes saved: {len(routes):,} rows")


# ==============================
# 2. CLEAN STOPS
# ==============================

print("\nCleaning stops.txt...")

stops = pd.read_csv(RAW_DIR / "stops.txt")

# Remove completely empty rows
stops = stops.dropna(how="all")

# Clean ID columns
stops["stop_id"] = stops["stop_id"].astype(str).str.strip()
stops["stop_code"] = stops["stop_code"].astype(str).str.strip()

# Clean stop names
stops["stop_name"] = (
    stops["stop_name"]
    .astype(str)
    .str.strip()
)

# Make coordinates numeric
stops["stop_lat"] = pd.to_numeric(
    stops["stop_lat"],
    errors="coerce"
)

stops["stop_lon"] = pd.to_numeric(
    stops["stop_lon"],
    errors="coerce"
)

# Remove duplicate stop IDs
stops = stops.drop_duplicates(
    subset=["stop_id"]
)

# Save cleaned stops
stops.to_csv(
    PROCESSED_DIR / "stops_clean.csv",
    index=False
)

print(f"Stops saved: {len(stops):,} rows")


# ==============================
# COMPLETE
# ==============================

print("\n==============================")
print("INITIAL CLEANING COMPLETE")
print("==============================")

print("\nProcessed files:")
print("- routes_clean.csv")
print("- stops_clean.csv")

# ==============================
# 3. CLEAN CALENDAR
# ==============================

print("\nCleaning calendar.txt...")

calendar = pd.read_csv(RAW_DIR / "calendar.txt")

calendar = calendar.dropna(how="all")

# Normalize service_id
calendar["service_id"] = (
    calendar["service_id"]
    .astype(str)
    .str.strip()
)

# Convert dates to proper datetime
calendar["start_date"] = pd.to_datetime(
    calendar["start_date"].astype(str),
    format="%Y%m%d"
)

calendar["end_date"] = pd.to_datetime(
    calendar["end_date"].astype(str),
    format="%Y%m%d"
)

calendar.to_csv(
    PROCESSED_DIR / "calendar_clean.csv",
    index=False
)

print(f"Calendar saved: {len(calendar):,} rows")


# ==============================
# 4. CLEAN TRIPS
# ==============================

print("\nCleaning trips.txt...")

trips = pd.read_csv(RAW_DIR / "trips.txt")

trips = trips.dropna(how="all")

# Normalize IDs
trips["route_id"] = (
    trips["route_id"]
    .astype(str)
    .str.strip()
)

trips["service_id"] = (
    trips["service_id"]
    .astype(str)
    .str.strip()
)

trips["trip_id"] = (
    trips["trip_id"]
    .astype(str)
    .str.strip()
)

# Remove duplicate trip IDs if any
trips = trips.drop_duplicates(
    subset=["trip_id"]
)

trips.to_csv(
    PROCESSED_DIR / "trips_clean.csv",
    index=False
)

print(f"Trips saved: {len(trips):,} rows")


# ==============================
# COMPLETE
# ==============================

print("\n==============================")
print("CLEANING STAGE 2 COMPLETE")
print("==============================")

print("\nProcessed files:")
print("- routes_clean.csv")
print("- stops_clean.csv")
print("- calendar_clean.csv")
print("- trips_clean.csv")
# ==============================
# 5. CLEAN STOP_TIMES
# ==============================

print("\nCleaning stop_times.txt...")
print("This may take a few minutes...")

stop_times_file = RAW_DIR / "stop_times.txt"
output_file = PROCESSED_DIR / "stop_times_clean.csv"

# Process the large file in chunks
chunk_size = 200_000

first_chunk = True
total_rows = 0

for chunk in pd.read_csv(
    stop_times_file,
    chunksize=chunk_size,
    dtype={
        "trip_id": str,
        "arrival_time": str,
        "departure_time": str,
        "stop_id": str,
        "stop_sequence": str
    }
):

    # Remove completely empty rows
    chunk = chunk.dropna(how="all")

    # Clean IDs
    chunk["trip_id"] = (
        chunk["trip_id"]
        .astype(str)
        .str.strip()
    )

    chunk["stop_id"] = (
        chunk["stop_id"]
        .astype(str)
        .str.strip()
    )

    # Clean time fields
    chunk["arrival_time"] = (
        chunk["arrival_time"]
        .astype(str)
        .str.strip()
    )

    chunk["departure_time"] = (
        chunk["departure_time"]
        .astype(str)
        .str.strip()
    )

    # Convert stop sequence to numeric
    chunk["stop_sequence"] = pd.to_numeric(
        chunk["stop_sequence"],
        errors="coerce"
    )

    # Remove rows where essential IDs are missing
    chunk = chunk.dropna(
        subset=["trip_id", "stop_id"]
    )

    # Append to output file
    chunk.to_csv(
        output_file,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False
    )

    first_chunk = False
    total_rows += len(chunk)

    print(f"Processed: {total_rows:,} rows")


print(f"\nStop times saved: {total_rows:,} rows")


# ==============================
# COMPLETE
# ==============================

print("\n==============================")
print("STOP_TIMES CLEANING COMPLETE")
print("==============================")

print("\nProcessed file:")
print("- stop_times_clean.csv")