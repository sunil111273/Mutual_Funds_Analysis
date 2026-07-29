# Bluestock MF Capstone — Day 1: Project Setup + Data Ingestion (ETL)

Individual capstone project for Bluestock Fintech — Mutual Fund Analytics Platform.
This repo currently contains **Day 1 work only**. Later days (data cleaning, SQL
database, EDA, performance metrics, dashboard, final report) will be added on top
of this in separate commits.

## Setup

```bash
pip install -r requirements.txt
```

## What's in this repo so far

```
mutual_fund_analytics/
├── data/
│   ├── raw/                  10 provided source CSVs
│   │   └── live_fetched/     live NAV CSVs fetched from api.mfapi.in (Day 1 Tasks 4-5)
│   └── processed/            empty for now — used from Day 2 onward
├── notebooks/                empty for now — used from Day 2 onward
├── scripts/
│   ├── data_ingestion.py     Day 1 Tasks 3, 6, 7
│   └── live_nav_fetch.py     Day 1 Tasks 4, 5
├── sql/                      empty for now — used from Day 2 onward
├── dashboard/                empty for now — used from Day 5 onward
├── reports/
│   └── data_quality_report.txt
├── requirements.txt
└── README.md
```

## How to run Day 1

```bash
# Task 3, 6, 7 - load all datasets, explore fund_master, validate AMFI codes
python3 scripts/data_ingestion.py

# Task 4, 5 - fetch live NAV data from api.mfapi.in (needs internet access)
python3 scripts/live_nav_fetch.py
```

`data_ingestion.py` prints everything to the console and also saves a summary
to `reports/data_quality_report.txt`.

`live_nav_fetch.py` saves one CSV per scheme to `data/raw/live_fetched/` for:

| AMFI Code | Scheme |
|---|---|
| 125497 | HDFC Top 100 Fund |
| 119551 | SBI Bluechip Fund |
| 120503 | ICICI Prudential Bluechip Fund |
| 118632 | Nippon India Large Cap Fund |
| 119092 | Axis Bluechip Fund |
| 120841 | Kotak Bluechip Fund |

## Day 1 checklist

- [x] Project folder structure created, Git repo initialised
- [x] `requirements.txt` created
- [x] All 10 raw CSVs loaded — shape / dtypes / head printed, nulls & duplicates checked
- [x] Live NAV fetched for HDFC Top 100 (125497)
- [x] Live NAV fetched for 5 more key schemes
- [x] fund_master explored — unique fund houses, categories, sub-categories, risk grades
- [x] AMFI codes validated: every code in fund_master exists in nav_history — **PASS**
- [x] Git commit: "Day 1: Data ingestion complete"

## Data quality summary (from `reports/data_quality_report.txt`)

- 10 fund houses, 2 categories (Equity/Debt), 12 sub-categories, 5 risk grades
- 40 unique AMFI codes in `fund_master`, all 40 present in `nav_history` — **PASS**
- No nulls or duplicate rows found in any of the 10 raw datasets

## Note on `live_fetched/`

`live_nav_fetch.py` calls the public `api.mfapi.in` API, so it needs an internet
connection to that domain to run. Run it locally — the fetched CSVs will appear
in `data/raw/live_fetched/`.
