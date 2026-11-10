import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw" / "metro"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "metro"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# FILES TO PROCESS
# --------------------------------------------------

FILES = [
    "agency.txt",
    "calendar.txt",
    "routes.txt",
    "shapes.txt",
    "stop_times.txt",
    "stops.txt",
    "trips.txt"
]


# --------------------------------------------------
# CONVERT GTFS TXT → CSV
# --------------------------------------------------

print("=" * 60)
print("METRO GTFS CLEANING & CSV CONVERSION")
print("=" * 60)

for filename in FILES:

    input_file = RAW_DIR / filename

    if not input_file.exists():
        print(f"❌ Missing file: {filename}")
        continue

    print(f"\nProcessing: {filename}")

    try:
        df = pd.read_csv(
            input_file,
            sep=",",
            low_memory=False
        )

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Remove leading/trailing spaces from column names
        df.columns = df.columns.str.strip()

        # Remove leading/trailing spaces from text values
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()

        # Output filename
        output_name = filename.replace(".txt", "_clean.csv")
        output_file = PROCESSED_DIR / output_name

        df.to_csv(
            output_file,
            index=False,
            encoding="utf-8"
        )

        print(f"✅ Saved: {output_name}")
        print(f"   Rows    : {len(df):,}")
        print(f"   Columns : {len(df.columns)}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")


print("\n" + "=" * 60)
print("METRO CONVERSION COMPLETED")
print("=" * 60)