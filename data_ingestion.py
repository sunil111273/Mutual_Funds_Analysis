import pandas as pd
import os

DATA_DIR = "data/raw"  # adjust if your CSVs live elsewhere

files = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "macro_factors": "10_macro_factors.csv",
}

# Columns that should be parsed as dates, per dataset
date_columns = {
    "fund_master": ["launch_date"],
    "nav_history": ["date"],
    "aum_by_fund_house": ["date"],
    "investor_transactions": ["transaction_date"],
    "portfolio_holdings": ["portfolio_date"],
    "macro_factors": ["date"],
}

dataframes = {}

# ------------------------------------------------------------------
# STEP 1: Load all datasets, parsing dates where relevant
# ------------------------------------------------------------------
for name, filename in files.items():
    path = os.path.join(DATA_DIR, filename)
    parse_dates = date_columns.get(name)
    df = pd.read_csv(path, parse_dates=parse_dates)
    dataframes[name] = df

    print(f"\n{'='*60}")
    print(f"DATASET: {name}  ({filename})")
    print(f"{'='*60}")
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nHead:\n{df.head()}")

# ------------------------------------------------------------------
# STEP 2: Anomaly check — confirm date columns parsed correctly
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("ANOMALY CHECK 1: Date column parsing")
print(f"{'='*60}")

for name, cols in date_columns.items():
    df = dataframes[name]
    for col in cols:
        dtype = df[col].dtype
        is_datetime = pd.api.types.is_datetime64_any_dtype(df[col])
        status = "OK" if is_datetime else "FAILED - still object/string"
        print(f"{name}.{col}: dtype={dtype} -> {status}")
        if is_datetime:
            print(f"   Range: {df[col].min()} to {df[col].max()}")

# ------------------------------------------------------------------
# STEP 3: Anomaly check — null values per dataset
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("ANOMALY CHECK 2: Null values per dataset")
print(f"{'='*60}")

for name, df in dataframes.items():
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    print(f"\n{name}: {total_nulls} total nulls")
    if total_nulls > 0:
        print(null_counts[null_counts > 0])
    else:
        print("  No nulls found.")

# ------------------------------------------------------------------
# STEP 4: Anomaly check — macro_factors is long-format
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("ANOMALY CHECK 3: macro_factors long-format structure")
print(f"{'='*60}")

macro_df = dataframes["macro_factors"]
unique_indices = macro_df["index_name"].unique()
print(f"macro_factors is in LONG format: {macro_df.shape[0]} rows, "
      f"{len(unique_indices)} unique index_name values")
print(f"Unique indices: {unique_indices}")
print("NOTE: This will need to be pivoted to wide format for time-series "
      "analysis, e.g.:")
print("  macro_wide = macro_df.pivot(index='date', columns='index_name', "
      "values='close_value')")

# ------------------------------------------------------------------
# STEP 5: Anomaly check — expense_ratio_pct consistency
# between fund_master and scheme_performance
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("ANOMALY CHECK 4: expense_ratio_pct — fund_master vs scheme_performance")
print(f"{'='*60}")

fm = dataframes["fund_master"][["amfi_code", "scheme_name", "expense_ratio_pct"]]
sp = dataframes["scheme_performance"][["amfi_code", "scheme_name", "expense_ratio_pct"]]

merged = fm.merge(
    sp,
    on="amfi_code",
    suffixes=("_fund_master", "_scheme_performance"),
    how="inner"
)

merged["expense_ratio_diff"] = (
    merged["expense_ratio_pct_fund_master"] - merged["expense_ratio_pct_scheme_performance"]
).round(4)

mismatches = merged[merged["expense_ratio_diff"] != 0]

print(f"Matched on amfi_code: {merged.shape[0]} schemes")
print(f"Schemes with matching expense_ratio_pct: {merged.shape[0] - mismatches.shape[0]}")
print(f"Schemes with MISMATCHED expense_ratio_pct: {mismatches.shape[0]}")

if not mismatches.empty:
    print("\nMismatched rows:")
    print(mismatches[[
        "amfi_code", "scheme_name_fund_master",
        "expense_ratio_pct_fund_master",
        "expense_ratio_pct_scheme_performance",
        "expense_ratio_diff"
    ]].to_string(index=False))
else:
    print("All expense ratios match exactly between the two datasets.")

# Also flag amfi_codes present in one dataset but not the other
fm_codes = set(dataframes["fund_master"]["amfi_code"])
sp_codes = set(dataframes["scheme_performance"]["amfi_code"])
print(f"\nAMFI codes in fund_master but not scheme_performance: {fm_codes - sp_codes}")
print(f"AMFI codes in scheme_performance but not fund_master: {sp_codes - fm_codes}")

print(f"\n{'='*60}")
print("DATA INGESTION + ANOMALY CHECKS COMPLETE")
print(f"{'='*60}")

# ------------------------------------------------------------------
# STEP 6: Explore fund_master — unique values
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("EXPLORATION: fund_master unique values")
print(f"{'='*60}")

fund_master = dataframes["fund_master"]

print("\nUnique fund houses:")
print(fund_master["fund_house"].unique())

print("\nUnique categories:")
print(fund_master["category"].unique())

print("\nUnique sub-categories:")
print(fund_master["sub_category"].unique())

print("\nUnique risk categories:")
print(fund_master["risk_category"].unique())

print("\nSEBI category codes:")
print(fund_master["sebi_category_code"].unique())

# ------------------------------------------------------------------
# STEP 6: Validate AMFI codes — fund_master vs nav_history
# ------------------------------------------------------------------
print(f"\n{'='*60}")
print("VALIDATION: AMFI codes — fund_master vs nav_history")
print(f"{'='*60}")

master_codes = set(dataframes["fund_master"]["amfi_code"].unique())
nav_codes = set(dataframes["nav_history"]["amfi_code"].unique())
missing = master_codes - nav_codes

print(f"Fund master AMFI codes: {len(master_codes)}")
print(f"NAV history AMFI codes: {len(nav_codes)}")
print(f"Codes in fund_master but missing from nav_history: {missing}")
print(f"Validation {'PASSED' if not missing else 'FAILED'}: "
      f"{len(master_codes - missing)}/{len(master_codes)} codes have NAV history")