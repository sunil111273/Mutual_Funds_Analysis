# Day 1 — Data Quality Summary

## Row counts per dataset

| Dataset | Rows | Cols |
|---|---|---|
| fund_master | 40 | 15 |
| nav_history | 46,000 | 3 |
| aum_by_fund_house | 90 | 5 |
| monthly_sip_inflows | 48 | 6 |
| category_inflows | 144 | 3 |
| industry_folio_count | 21 | 6 |
| scheme_performance | 40 | 19 |
| investor_transactions | 32,778 | 13 |
| portfolio_holdings | 322 | 8 |
| macro_factors | 8,050 | 3 |

## Nulls found

Only one dataset has nulls: `monthly_sip_inflows.yoy_growth_pct` — **12 nulls** out of 48 rows.
Likely explanation: YoY growth can't be computed for the first 12 months of the series
(no prior-year base to compare against). Not a data quality defect — expected for a
year-over-year metric at the start of a time series.

All other datasets: 0 nulls.

## AMFI code validation (fund_master vs nav_history)

**Result: PASSED.** All 40/40 AMFI codes in `fund_master` have corresponding NAV history
records in `nav_history`. No missing codes.

## macro_factors long-format note

`macro_factors.csv` is stored in **long format** (`date`, `index_name`, `close_value`) rather
than wide format. It covers 8,050 rows across **7 indices**: NIFTY50, NIFTY100,
NIFTY_MIDCAP150, BSE_SMALLCAP, NIFTY500, CRISIL_LIQUID, CRISIL_GILT.

For time-series analysis (e.g. plotting benchmarks alongside NAV/AUM trends), this needs to
be pivoted to wide format first:

```python
macro_wide = macro_df.pivot(index="date", columns="index_name", values="close_value")
```

## expense_ratio_pct cross-check (bonus finding)

Cross-checked `expense_ratio_pct` between `fund_master` and `scheme_performance` (joined on
`amfi_code`). All 40 schemes matched exactly — no mismatches, no orphan codes in either
direction. Confirms the two datasets are internally consistent on this field.

## Live API fetch confirmation

- [ ] HDFC Top 100 Direct (125497) — fetched, N records
- [ ] SBI Bluechip (119551) — fetched, N records
- [ ] ICICI Bluechip (120503) — fetched, N records
- [ ] Nippon Large Cap (118632) — fetched, N records
- [ ] Axis Bluechip (119092) — fetched, N records
- [ ] Kotak Bluechip (120841) — fetched, N records

*(Fill in record counts once `live_nav_fetch.py` runs successfully — this depends on
internet access to api.mfapi.in from your machine.)*