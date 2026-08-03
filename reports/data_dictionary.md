# Data Dictionary — Bluestock MF Capstone

## dim_fund (source: 01_fund_master.csv)
| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | Unique AMFI scheme identifier, primary key |
| fund_house | TEXT | AMC operating the scheme |
| scheme_name | TEXT | Full scheme name |
| category | TEXT | Broad category (Equity/Debt/Hybrid) |
| ...