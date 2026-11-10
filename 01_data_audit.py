"""
Urban Transit Intelligence — Delhi Bus Network
Step 2: GTFS Data Audit + Quality Check

Folder structure expected:
Urban_Transit_Intelligence/
├── data/
│   └── raw/
│       ├── agency.txt
│       ├── calendar.txt
│       ├── routes.txt
│       ├── trips.txt
│       ├── stops.txt
│       ├── stop_times.txt
│       ├── fare_attributes.txt
│       └── fare_rules.txt
├── reports/
└── 01_data_audit.py

Run:
    python 01_data_audit.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 200_000

FILES = [
    "agency.txt",
    "calendar.txt",
    "routes.txt",
    "trips.txt",
    "stops.txt",
    "stop_times.txt",
    "fare_attributes.txt",
    "fare_rules.txt",
]

LARGE_FILES = {"stop_times.txt", "fare_attributes.txt", "fare_rules.txt"}


def require_files():
    missing = [f for f in FILES if not (RAW_DIR / f).exists()]
    if missing:
        print("\nMissing files:")
        for f in missing:
            print(f"  - {f}")
        print(f"\nExpected folder:\n{RAW_DIR}")
        raise FileNotFoundError("Put all 8 GTFS files inside data/raw/ and run again.")


def get_columns(path: Path):
    return list(pd.read_csv(path, nrows=0).columns)


def audit_small_file(path: Path):
    df = pd.read_csv(path)
    result = {
        "file": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
    }

    print(f"\n=== {path.name} ===")
    print(f"Rows: {result['rows']:,}")
    print(f"Columns: {result['columns']}")
    print(f"Duplicate rows: {result['duplicate_rows']:,}")
    print(f"Missing cells: {result['total_missing_cells']:,}")
    print("Columns:", ", ".join(df.columns))

    missing = df.isna().sum()
    missing = missing[missing > 0]
    if len(missing):
        print("Missing by column:")
        print(missing.to_string())
    else:
        print("Missing by column: none")

    print("\nSample:")
    print(df.head(3).to_string(index=False))

    return df, result


def audit_large_file(path: Path):
    columns = get_columns(path)
    row_count = 0
    missing_counts = pd.Series(0, index=columns, dtype="int64")
    duplicate_rows = 0

    # Optional key checks
    key_cols = {
        "stop_times.txt": ["trip_id", "stop_sequence"],
        "fare_attributes.txt": ["fare_id"],
        "fare_rules.txt": ["fare_id", "route_id", "origin_id", "destination_id"],
    }.get(path.name)

    seen_keys = set() if key_cols else None
    bad_key_rows = 0

    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        row_count += len(chunk)
        missing_counts = missing_counts.add(chunk.isna().sum(), fill_value=0).astype("int64")

        # Count exact duplicate rows within each chunk.
        # Cross-chunk exact duplicates are not counted; key checks are used where appropriate.
        duplicate_rows += int(chunk.duplicated().sum())

        if key_cols and all(col in chunk.columns for col in key_cols):
            keys = chunk[key_cols].astype("string").fillna("<NA>").agg("|".join, axis=1)
            for key in keys:
                if key in seen_keys:
                    bad_key_rows += 1
                else:
                    seen_keys.add(key)

    result = {
        "file": path.name,
        "rows": row_count,
        "columns": len(columns),
        "duplicate_rows_within_chunks": duplicate_rows,
        "duplicate_key_rows": bad_key_rows,
        "total_missing_cells": int(missing_counts.sum()),
    }

    print(f"\n=== {path.name} ===")
    print(f"Rows: {row_count:,}")
    print(f"Columns: {len(columns)}")
    print(f"Columns: {', '.join(columns)}")
    print(f"Duplicate rows within chunks: {duplicate_rows:,}")
    if key_cols:
        print(f"Repeated key rows ({', '.join(key_cols)}): {bad_key_rows:,}")
    print(f"Missing cells: {result['total_missing_cells']:,}")

    missing = missing_counts[missing_counts > 0].sort_values(ascending=False)
    if len(missing):
        print("Missing by column:")
        print(missing.to_string())
    else:
        print("Missing by column: none")

    return result


def normalize_keys(series):
    return set(series.astype("string").dropna().astype(str).str.strip())


def referential_integrity(agency, calendar, routes, trips, stops):
    issues = []

    agency_ids = normalize_keys(agency["agency_id"]) if "agency_id" in agency else set()
    service_ids = normalize_keys(calendar["service_id"]) if "service_id" in calendar else set()
    route_ids = normalize_keys(routes["route_id"]) if "route_id" in routes else set()
    trip_ids = normalize_keys(trips["trip_id"]) if "trip_id" in trips else set()
    stop_ids = normalize_keys(stops["stop_id"]) if "stop_id" in stops else set()

    if "agency_id" in routes:
        missing = sorted(normalize_keys(routes["agency_id"]) - agency_ids)
        issues.append(f"routes -> agency missing references: {len(missing)}")
        if missing:
            issues.append(f"  Examples: {missing[:10]}")

    if "route_id" in trips:
        missing = sorted(normalize_keys(trips["route_id"]) - route_ids)
        issues.append(f"trips -> routes missing references: {len(missing)}")
        if missing:
            issues.append(f"  Examples: {missing[:10]}")

    if "service_id" in trips:
        missing = sorted(normalize_keys(trips["service_id"]) - service_ids)
        issues.append(f"trips -> calendar missing references: {len(missing)}")
        if missing:
            issues.append(f"  Examples: {missing[:10]}")

    # Stops in stop_times are checked in a separate streaming pass.
    stop_times_path = RAW_DIR / "stop_times.txt"
    if stop_times_path.exists():
        orphan_trip_ids = set()
        orphan_stop_ids = set()

        for chunk in pd.read_csv(
            stop_times_path,
            usecols=lambda c: c in {"trip_id", "stop_id"},
            chunksize=CHUNK_SIZE,
            dtype="string",
        ):
            chunk_trip_ids = set(chunk["trip_id"].dropna().astype(str).str.strip())
            chunk_stop_ids = set(chunk["stop_id"].dropna().astype(str).str.strip())
            orphan_trip_ids.update(chunk_trip_ids - trip_ids)
            orphan_stop_ids.update(chunk_stop_ids - stop_ids)

        issues.append(f"stop_times -> trips missing references: {len(orphan_trip_ids)}")
        issues.append(f"stop_times -> stops missing references: {len(orphan_stop_ids)}")
        if orphan_trip_ids:
            issues.append(f"  Example orphan trip_ids: {sorted(orphan_trip_ids)[:10]}")
        if orphan_stop_ids:
            issues.append(f"  Example orphan stop_ids: {sorted(orphan_stop_ids)[:10]}")

    return issues


def main():
    require_files()

    print("=" * 70)
    print("URBAN TRANSIT INTELLIGENCE — DELHI BUS GTFS")
    print("STEP 2: DATA AUDIT")
    print("=" * 70)
    print(f"Raw data folder: {RAW_DIR}")

    summaries = []
    loaded = {}

    for filename in FILES:
        path = RAW_DIR / filename
        if filename in LARGE_FILES:
            result = audit_large_file(path)
            summaries.append(result)
        else:
            df, result = audit_small_file(path)
            summaries.append(result)
            loaded[filename] = df

    print("\n=== REFERENTIAL INTEGRITY ===")
    issues = referential_integrity(
        loaded["agency.txt"],
        loaded["calendar.txt"],
        loaded["routes.txt"],
        loaded["trips.txt"],
        loaded["stops.txt"],
    )
    for line in issues:
        print(line)

    # Write summary report
    summary_df = pd.DataFrame(summaries)
    summary_path = REPORT_DIR / "data_audit_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    integrity_path = REPORT_DIR / "referential_integrity.txt"
    integrity_path.write_text("\n".join(issues), encoding="utf-8")

    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)
    print(f"Saved: {summary_path}")
    print(f"Saved: {integrity_path}")
    print("\nNext step: send me the console output (or the two report files).")
    print("Do NOT clean or edit the raw GTFS files yet.")


if __name__ == "__main__":
    main()
