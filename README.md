# Mutual Funds Analysis

An end-to-end data analysis project that ingests, cleans, and analyzes Indian mutual fund data — combining historical AMFI-style datasets with live NAV data from the mfapi.in API — to evaluate fund performance, AUM trends, and investor behavior across schemes and categories.

## Overview

The project moves through four stages: raw data ingestion and validation, cleaning and SQL database design, exploratory data analysis, and (upcoming) reporting/dashboards. Each stage builds directly on the outputs of the previous one.

## Project Structure

## Tools & Dependencies

- **Language:** Python
- **Data processing:** pandas, numpy
- **Visualization:** matplotlib, seaborn, plotly
- **Database:** SQLAlchemy, SQLite
- **Other:** requests, scipy, Jupyter

Install everything with:
```bash
pip install -r requirements.txt
```

## Data Sources

- **Provided datasets:** 10 CSV files covering fund master data, NAV history, AUM, SIP inflows, category inflows, folio counts, scheme performance, portfolio holdings, investor transactions, and macro factors.
- **Live NAV data:** Fetched via the [mfapi.in](https://www.mfapi.in/) API, e.g. `GET https://api.mfapi.in/mf/125497` for HDFC Top 100 Direct.

**Key schemes tracked:**

| Scheme | AMFI Code |
|---|---|
| SBI Bluechip | 119551 |
| ICICI Bluechip | 120503 |
| Nippon Large Cap | 118632 |
| Axis Bluechip | 119092 |
| Kotak Bluechip | 120841 |

---

## Project Progress

### Day 1 — Project Setup + Data Ingestion (ETL) ✅

- Set up the project folder structure and initialized the Git/GitHub repository
- Installed all dependencies (see `requirements.txt`)
- Loaded all 10 provided CSV datasets with pandas; reviewed shape, dtypes, and sample rows for anomalies
- Fetched live NAV data from mfapi.in for HDFC Top 100 Direct and 5 key bluechip schemes
- Explored fund master data — unique fund houses, categories, sub-categories, and risk grades
- Validated that all AMFI scheme codes in `fund_master` exist in `nav_history`
- Documented a short data quality summary

**Deliverables:** `data_ingestion.py`, `live_nav_fetch.py`, `requirements.txt`, GitHub repo with Day 1 commit

### Day 2 — Data Cleaning + SQL Database Design ✅

- Cleaned `nav_history`, `investor_transactions`, and `scheme_performance`; applied lighter validation (deduplication, date parsing) to the remaining 7 datasets — all 10 outputs saved to `data/processed/`
- Designed a SQLite star schema: `dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`
- Loaded all datasets into `bluestock_mf.db` via SQLAlchemy; verified row counts match source CSVs
- Wrote 10 analytical SQL queries (`sql/queries.sql`)
- Documented all columns, data types, and business definitions in `reports/data_dictionary.md`

**Deliverables:** `data/processed/*.csv`, `bluestock_mf.db`, `sql/schema.sql`, `sql/queries.sql`, `reports/data_dictionary.md`

### Day 3 — Exploratory Data Analysis (EDA) ✅

Performed comprehensive exploratory data analysis on the processed datasets using Python visualization libraries.

**Visualizations created:**
- NAV trend analysis (2022–2026) for all 40 schemes, using Plotly
- AUM growth by fund house (2022–2025), using Seaborn
- Monthly SIP inflow trend (Jan 2022–Dec 2025), with all-time-high annotation
- Category-wise net inflow heatmap
- Investor demographics: age group distribution, SIP amount box plot, gender split
- Geographic distribution: SIP amount by state, T30 vs B30 city split
- Industry folio count growth
- NAV return correlation matrix for selected mutual funds
- Sector allocation donut chart across equity fund holdings

**Key insights:**
- NAV growth across all 40 schemes, compared on an indexed basis, shows a clear 2023 bull run
- SBI Mutual Fund is the largest AMC by AUM, reaching ₹12.5L Cr by 2025
- SIP inflows grew consistently, reaching ₹31,002 Cr in December 2025 (up from ₹11,517 Cr in January 2022)
- Active SIP accounts and total industry folios both nearly doubled over the same period (folios: 13.26 Cr → 26.12 Cr)
- Portfolio holdings are concentrated in Banking, IT, and Pharma across equity schemes
- Investor transaction value remains concentrated in T30 cities relative to B30
- Large-cap fund NAV returns show unexpectedly low correlation with each other and with Nifty50 — flagged as a limitation of the synthetic dataset rather than a genuine market pattern

**Technologies used:** pandas, matplotlib, seaborn, plotly, Jupyter Notebook

**Deliverables:**
- `EDA_Analysis.ipynb`
- `eda_nav_trends.py`
- `eda_aum_growth.py`
- `eda_sip_inflow_trend.py`
- `eda_category_inflow_heatmap.py`
- `eda_investor_demographics.py`
- `eda_geographic_distribution.py`
- `eda_folio_count_growth.py`
- `eda_nav_return_correlation.py`
- `eda_sector_allocation.py`
- Exported charts in `reports/`

---

## Contributors

- Bijjam Sunil Reddy
- sikderranadip
- codexmohan

## License

This project is open source and available under the [MIT License](LICENSE).
