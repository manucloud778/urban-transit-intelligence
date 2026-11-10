# Urban Transit Intelligence

**Data-Driven Decision Support for Urban Public Transport**

Urban Transit Intelligence is a Power BI analytics project that studies the **scheduled Delhi bus network** using GTFS data. It turns raw transit schedules into network-level insight on routes, stops, connectivity and service patterns, to support transport planners, analysts and researchers.

> **Scope note:** All metrics describe *scheduled* GTFS activity. The project does not measure passenger demand, actual delays, cancellations, crowding or bus utilization, and it does not make official transport recommendations.

---

## Key Results

| Metric | Value |
|---|---|
| Routes | 2,403 |
| Stops | 10,559 |
| Scheduled trips | 89,393 |
| Agencies | 2 (DTC, DIMTS) |
| Scheduled trips: DTC / DIMTS | ≈ 46.5K / ≈ 42.9K |
| High-service routes | 1,205 (median-based classification) |
| High-connectivity stops (50+ routes) | 90 |
| Average routes per stop | 9.34 |
| Maximum routes at one stop | 102 |
| Peak scheduled service hour | 09:00 |
| Peak scheduled stop visits | 241,004 |

*Scheduled stop visits are timetable events, not passenger counts.*

**Top routes by scheduled trips:** 623 DOWN (318), 623A DOWN (318), 628 STL DOWN (313), 628 STL UP (311), 623 UP (272).

**Stops with the most connected routes:** NajafGarh Delhi Gate (102), Jahangir Puri Metro Station (101), Health Centre (99), Police Station NajafGarh (95), Adarsh Nagar / Bharola Village (86).

---

## Dashboard Pages

1. **Home**
2. **Bus Overview**: network scale and agency structure
3. **Route Intelligence**: scheduled service by route
4. **Stop Intelligence**: stop connectivity
5. **Service Pattern**: scheduled activity across the day
6. **Bus Executive Overview**: one-page network summary
7. **Methodology**

Metro and city-level analysis are planned as future modules.

---

## Tech Stack

- **Data:** Delhi GTFS (static feed)
- **Processing and analysis:** Python (pandas) and SQL
- **Visualization:** Power BI Desktop
- **Design system:** dark urban-intelligence theme (`#0B1220` background, `#22D3EE` and `#14B8A6` accents)

---

## Repository Structure

```text
Urban_Transit_Intelligence/
├── data/
│   ├── raw/            # original GTFS files (not tracked, see below)
│   └── processed/      # cleaned tables (not tracked, see below)
├── notebooks/          # analysis and cleaning notebooks
├── sql/                # SQL queries
├── dashboard/          # Power BI report (.pbix) and screenshots
└── README.md
```

*Adjust this tree to match your actual folders.*

---

## Getting the Data

The data files are large and are **not stored in this repository** (GitHub's file size limit is 100 MB).

1. Download the Delhi GTFS static feed from the Delhi Open Transit Data portal: <https://otd.delhi.gov.in>
2. Place the raw `.txt` files in `data/raw/`.
3. Run the cleaning notebook(s) to generate the files in `data/processed/`.

---

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/manucloud778/urban-transit-intelligence.git
cd urban-transit-intelligence

# 2. Install dependencies
pip install pandas

# 3. Add the GTFS data as described above, then run the notebooks in order
```

Open the Power BI report in `dashboard/` with Power BI Desktop and refresh it after pointing the data source at your local `data/processed/` folder.

---

## Methodology Notes

- **High Service routes** are defined with a median-based classification of scheduled trips.
- **High-connectivity stops** are stops connected to 50 or more routes.
- **Connected routes** measure route connectivity, not passenger footfall.

---

## Limitations

- GTFS is a schedule, so results show planned service, not real-world operations.
- Findings are network-level patterns and candidates for further review, not proof that a route is inefficient or that any area needs more service.

---

## Author

**manucloud778**: <https://github.com/manucloud778>

## License

Add a license of your choice (for example MIT). Check the terms of use of the Delhi Open Transit Data portal before redistributing any data.
