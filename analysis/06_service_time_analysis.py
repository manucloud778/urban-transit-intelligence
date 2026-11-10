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
# FUNCTION TO EXTRACT GTFS HOUR
# ==============================

def get_gtfs_hour(time_series):
    """
    Extract the hour from GTFS time values.

    GTFS allows hours greater than 23:
    24:30:00, 25:15:00, etc.

    We preserve those hours instead of
    converting them to normal clock time.
    """
    return pd.to_numeric(
        time_series.astype(str).str.split(":").str[0],
        errors="coerce"
    )


# ==============================
# PROCESS STOP TIMES IN CHUNKS
# ==============================

print("Analyzing service times...")
print("This may take a few minutes...")

stop_times_file = PROCESSED_DIR / "stop_times_clean.csv"

chunk_size = 200_000

hourly_counts = {}
first_hour = None
last_hour = None
total_rows = 0

for chunk in pd.read_csv(
    stop_times_file,
    chunksize=chunk_size,
    usecols=[
        "trip_id",
        "arrival_time",
        "departure_time",
        "stop_id"
    ],
    dtype={
        "trip_id": str,
        "arrival_time": str,
        "departure_time": str,
        "stop_id": str
    }
):

    # Extract hour from departure time
    hours = get_gtfs_hour(chunk["departure_time"])

    # Remove invalid time values
    hours = hours.dropna().astype(int)

    # Count scheduled stop visits by hour
    counts = hours.value_counts()

    for hour, count in counts.items():
        hourly_counts[hour] = (
            hourly_counts.get(hour, 0) + int(count)
        )

    # Track earliest and latest scheduled hour
    if len(hours) > 0:
        chunk_min = int(hours.min())
        chunk_max = int(hours.max())

        if first_hour is None or chunk_min < first_hour:
            first_hour = chunk_min

        if last_hour is None or chunk_max > last_hour:
            last_hour = chunk_max

    total_rows += len(chunk)

    print(f"Processed: {total_rows:,} rows")


# ==============================
# CREATE HOURLY RESULT
# ==============================

hourly_analysis = pd.DataFrame(
    list(hourly_counts.items()),
    columns=["gtfs_hour", "scheduled_stop_visits"]
)

hourly_analysis = hourly_analysis.sort_values(
    "gtfs_hour"
)


# ==============================
# SAVE HOURLY ANALYSIS
# ==============================

hourly_output = OUTPUT_DIR / "service_by_hour.csv"

hourly_analysis.to_csv(
    hourly_output,
    index=False
)


# ==============================
# DISPLAY RESULTS
# ==============================

print("\nSCHEDULED SERVICE BY HOUR")
print("=" * 55)

print(
    hourly_analysis.to_string(index=False)
)


# ==============================
# PEAK SCHEDULED ACTIVITY
# ==============================

peak_row = hourly_analysis.loc[
    hourly_analysis["scheduled_stop_visits"].idxmax()
]

print("\nPEAK SCHEDULED ACTIVITY")
print("=" * 55)

print(
    f"GTFS hour: {int(peak_row['gtfs_hour']):02d}:00"
)

print(
    f"Scheduled stop visits: "
    f"{int(peak_row['scheduled_stop_visits']):,}"
)


# ==============================
# OPERATING RANGE
# ==============================

print("\nSCHEDULED OPERATING RANGE")
print("=" * 55)

print(f"Earliest GTFS hour: {first_hour:02d}:00")
print(f"Latest GTFS hour:   {last_hour:02d}:00")


# ==============================
# COMPLETE
# ==============================

print("\n==============================")
print("SERVICE TIME ANALYSIS COMPLETE")
print("==============================")

print(f"\nSaved to: {hourly_output}")