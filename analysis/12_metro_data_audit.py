import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed" / "metro"
REPORT_DIR = BASE_DIR / "reports" / "metro"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("METRO GTFS DATA AUDIT")
print("=" * 65)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

files = {
    "agency": "agency_clean.csv",
    "calendar": "calendar_clean.csv",
    "routes": "routes_clean.csv",
    "shapes": "shapes_clean.csv",
    "stop_times": "stop_times_clean.csv",
    "stops": "stops_clean.csv",
    "trips": "trips_clean.csv"
}

data = {}

for name, filename in files.items():

    path = DATA_DIR / filename

    if not path.exists():
        print(f"❌ Missing file: {filename}")
        continue

    df = pd.read_csv(path, low_memory=False)
    data[name] = df

    print(f"\n{name.upper()}")
    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")


# --------------------------------------------------
# DATA QUALITY AUDIT
# --------------------------------------------------

print("\n" + "=" * 65)
print("DATA QUALITY CHECK")
print("=" * 65)

audit_results = []

for name, df in data.items():

    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    audit_results.append({
        "table": name,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": missing,
        "duplicate_rows": duplicates
    })

    print(f"\n{name}")
    print(f"Missing values : {missing:,}")
    print(f"Duplicate rows : {duplicates:,}")


audit_df = pd.DataFrame(audit_results)

audit_df.to_csv(
    REPORT_DIR / "metro_data_quality_audit.csv",
    index=False
)


# --------------------------------------------------
# REFERENTIAL INTEGRITY
# --------------------------------------------------

print("\n" + "=" * 65)
print("REFERENTIAL INTEGRITY CHECK")
print("=" * 65)


# Trips → Routes
if "trips" in data and "routes" in data:

    trips_routes = set(data["trips"]["route_id"].dropna())
    route_ids = set(data["routes"]["route_id"].dropna())

    missing_routes = trips_routes - route_ids

    print(
        f"\nTrips → Routes missing references: "
        f"{len(missing_routes)}"
    )


# Trips → Service Calendar
if "trips" in data and "calendar" in data:

    trip_services = set(data["trips"]["service_id"].dropna())
    calendar_services = set(data["calendar"]["service_id"].dropna())

    missing_services = trip_services - calendar_services

    print(
        f"Trips → Calendar missing references: "
        f"{len(missing_services)}"
    )


# Stop Times → Trips
if "stop_times" in data and "trips" in data:

    stop_time_trips = set(data["stop_times"]["trip_id"].dropna())
    trip_ids = set(data["trips"]["trip_id"].dropna())

    missing_trips = stop_time_trips - trip_ids

    print(
        f"Stop Times → Trips missing references: "
        f"{len(missing_trips)}"
    )


# Stop Times → Stops
if "stop_times" in data and "stops" in data:

    stop_time_stops = set(data["stop_times"]["stop_id"].dropna())
    stop_ids = set(data["stops"]["stop_id"].dropna())

    missing_stops = stop_time_stops - stop_ids

    print(
        f"Stop Times → Stops missing references: "
        f"{len(missing_stops)}"
    )


# Trips → Shapes
if "trips" in data and "shapes" in data:

    if "shape_id" in data["trips"].columns and "shape_id" in data["shapes"].columns:

        trip_shapes = set(
            data["trips"]["shape_id"].dropna()
        )

        shape_ids = set(
            data["shapes"]["shape_id"].dropna()
        )

        missing_shapes = trip_shapes - shape_ids

        print(
            f"Trips → Shapes missing references: "
            f"{len(missing_shapes)}"
        )


# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------

print("\n" + "=" * 65)
print("METRO NETWORK SUMMARY")
print("=" * 65)

summary = {}

if "routes" in data:
    summary["total_routes"] = data["routes"]["route_id"].nunique()

if "stops" in data:
    summary["total_stops"] = data["stops"]["stop_id"].nunique()

if "trips" in data:
    summary["total_trips"] = data["trips"]["trip_id"].nunique()

if "agency" in data:
    summary["total_agencies"] = data["agency"]["agency_id"].nunique()

if "shapes" in data:
    summary["shape_points"] = len(data["shapes"])

if "stop_times" in data:
    summary["stop_time_records"] = len(data["stop_times"])


for key, value in summary.items():
    print(f"{key.replace('_', ' ').title():25}: {value:,}")


summary_df = pd.DataFrame(
    list(summary.items()),
    columns=["metric", "value"]
)

summary_df.to_csv(
    REPORT_DIR / "metro_network_summary.csv",
    index=False
)


# --------------------------------------------------
# ROUTE DISTRIBUTION
# --------------------------------------------------

if "routes" in data:

    route_summary = data["routes"].copy()

    route_summary.to_csv(
        REPORT_DIR / "metro_routes_audit.csv",
        index=False
    )


# --------------------------------------------------
# STOP DISTRIBUTION
# --------------------------------------------------

if "stops" in data:

    stop_summary = data["stops"].copy()

    stop_summary.to_csv(
        REPORT_DIR / "metro_stops_audit.csv",
        index=False
    )


# --------------------------------------------------
# FINAL
# --------------------------------------------------

print("\n" + "=" * 65)
print("METRO DATA AUDIT COMPLETED")
print("=" * 65)

print("\nReports saved in:")
print(REPORT_DIR)