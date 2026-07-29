# Mutual Funds Analysis

A data analysis project that ingests, processes, and analyzes mutual fund NAV data — combining historical datasets with live data from the AMFI/mfapi.in API to evaluate fund performance across schemes and categories.

## 📊 Overview

This project builds an end-to-end pipeline for mutual fund analysis: from raw data ingestion and validation, through processing, to analysis and reporting/dashboards.

## 📁 Project Structure

```
Mutual_Funds_Analysis/
├── data/
│   ├── raw/            # Raw ingested data (CSV datasets, live API pulls)
│   └── processed/       # Cleaned and validated data
├── notebooks/            # Jupyter notebooks for exploration and analysis
├── sql/                  # SQL scripts/queries
├── dashboard/            # Dashboard files (Power BI / other)
├── reports/              # Written reports and summaries
├── data_ingestion.py      # Loads and validates the 10 provided CSV datasets
├── live_nav_fetch.py      # Fetches live NAV data from mfapi.in
├── requirements.txt       # Project dependencies
└── README.md
```

## 🛠️ Tools & Dependencies

- Python
- pandas, numpy
- matplotlib, seaborn, plotly
- sqlalchemy
- requests
- scipy
- jupyter

Install everything with:
```bash
pip install -r requirements.txt
```

## 🔄 Data Sources

- **Provided datasets:** 10 CSV files covering fund master and NAV history data
- **Live NAV data:** Fetched via the [mfapi.in](https://www.mfapi.in/) API, e.g. `GET https://api.mfapi.in/mf/125497` for HDFC Top 100 Direct

**Key schemes tracked:**
| Scheme | AMFI Code |
|---|---|
| SBI Bluechip | 119551 |
| ICICI Bluechip | 120503 |
| Nippon Large Cap | 118632 |
| Axis Bluechip | 119092 |
| Kotak Bluechip | 120841 |

## 🚀 Project Progress

### Day 1 — Project Setup + Data Ingestion (ETL) ✅
- Set up project folder structure and initialized Git/GitHub repo
- Installed all dependencies (see `requirements.txt`)
- Loaded all 10 provided CSV datasets with pandas; reviewed shape, dtypes, and sample rows for anomalies
- Fetched live NAV data from mfapi.in for HDFC Top 100 Direct and 5 key bluechip schemes
- Explored fund master data — unique fund houses, categories, sub-categories, and risk grades
- Validated that all AMFI scheme codes in `fund_master` exist in `nav_history`
- Documented a short data quality summary

**Day 1 Deliverables:** `data_ingestion.py`, `live_nav_fetch.py`, `requirements.txt`, GitHub repo with Day 1 commit

## 👤 Contributors

- Bijjam Sunil Reddy
- sikderranadip
- codexmohan

## 📄 License

This project is open source and available under the [MIT License](LICENSE).