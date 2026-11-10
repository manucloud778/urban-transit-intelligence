import pandas as pd
from pathlib import Path

# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed" / "metro"
REPORT_DIR = BASE_DIR / "reports" / "metro"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# LOAD DATA
# ==============================

stops = pd.read_csv(DATA_DIR / "stops_clean.csv")
trips = pd.read_csv(DATA_DIR / "trips_clean.csv")
stop_times = pd.read_csv(DATA_DIR / "stop_times_clean.csv")

print("Metro station data loaded successfully.")

# ==============================
# ROUTES CONNECTED TO EACH STOP
# ==============================

# Attach route_id to every stop-time record
stop_route_data = stop_times.merge(
    trips[["trip_id", "route_id"]],
    on="trip_id",
    how="left"
)

# Count distinct routes serving each station
station_connectivity = (
    stop_route_data
    .groupby("stop_id")["route_id"]
    .nunique()
    .reset_index(name="connected_routes")
)

# ==============================
# MERGE WITH STATION DETAILS
# ==============================

station_analysis = stops[
    [
        "stop_id",
        "stop_code",
        "stop_name",
        "stop_lat",
        "stop_lon"
    ]
].copy()

station_analysis = station_analysis.merge(
    station_connectivity,
    on="stop_id",
    how="left"
)

station_analysis["connected_routes"] = (
    station_analysis["connected_routes"]
    .fillna(0)
    .astype(int)
)

# ==============================
# SORT BY CONNECTIVITY
# ==============================

station_analysis = station_analysis.sort_values(
    "connected_routes",
    ascending=False
)

# ==============================
# SAVE REPORT
# ==============================

output_file = REPORT_DIR / "metro_station_analysis.csv"

station_analysis.to_csv(
    output_file,
    index=False
)

# ==============================
# SUMMARY
# ==============================

print("\nMetro Station Analysis Complete!")
print("----------------------------------")

print(
    f"Total stations: "
    f"{station_analysis['stop_id'].nunique()}"
)

print(
    f"Average routes per station: "
    f"{station_analysis['connected_routes'].mean():.2f}"
)

print(
    f"Maximum route connectivity: "
    f"{station_analysis['connected_routes'].max()}"
)

print("\nTop Metro Stations by Route Connectivity:")

print(
    station_analysis[
        [
            "stop_id",
            "stop_name",
            "connected_routes"
        ]
    ].head(15).to_string(index=False)
)

print("\nReport saved to:")
print(output_file)