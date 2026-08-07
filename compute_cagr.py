import pandas as pd

print("Loading NAV datasets...")

# -----------------------------
# Load Data
# -----------------------------
nav = pd.read_csv(
    "data/processed/02_nav_history_clean.csv",
    parse_dates=["date"]
)

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[["amfi_code", "scheme_name", "category"]]

# -----------------------------
# Prepare Data
# -----------------------------
nav = nav.sort_values(["amfi_code", "date"])

latest_date = nav["date"].max()

print(f"\nLatest NAV Date : {latest_date.date()}")
print(f"Total Schemes   : {nav['amfi_code'].nunique()}")

print("\nComputing CAGR...")

# -----------------------------
# CAGR Function
# -----------------------------
def calculate_cagr(nav_data, years):

    target_date = latest_date - pd.DateOffset(years=years)

    output = []

    for code, group in nav_data.groupby("amfi_code"):

        group = group.sort_values("date")

        nav_end = group.iloc[-1]["nav"]

        start_rows = group[group["date"] <= target_date]

        # Not enough history
        if start_rows.empty:
            output.append([code, None])
            continue

        nav_start = start_rows.iloc[-1]["nav"]

        cagr = ((nav_end / nav_start) ** (1 / years) - 1) * 100

        output.append([code, round(cagr, 2)])

    return pd.DataFrame(
        output,
        columns=["amfi_code", f"cagr_{years}yr_pct"]
    )

# -----------------------------
# Calculate CAGR
# -----------------------------
cagr_1 = calculate_cagr(nav, 1)
cagr_3 = calculate_cagr(nav, 3)
cagr_5 = calculate_cagr(nav, 5)

# -----------------------------
# Build Comparison Table
# -----------------------------
comparison = (
    fund_master
    .merge(cagr_1, on="amfi_code")
    .merge(cagr_3, on="amfi_code")
    .merge(cagr_5, on="amfi_code")
)

comparison = comparison.sort_values(
    by=["cagr_3yr_pct", "cagr_1yr_pct"],
    ascending=False
)

# -----------------------------
# Save Output
# -----------------------------
output_path = "data/processed/cagr_comparison_table.csv"

comparison.to_csv(output_path, index=False)

# -----------------------------
# Validation
# -----------------------------
print("\nValidation")
print("-" * 40)

print(f"Rows in comparison table : {len(comparison)}")
print(f"Unique schemes           : {comparison['amfi_code'].nunique()}")

print("\nMissing CAGR Values")
print(f"1-Year : {comparison['cagr_1yr_pct'].isna().sum()}")
print(f"3-Year : {comparison['cagr_3yr_pct'].isna().sum()}")

missing_5 = comparison["cagr_5yr_pct"].isna().sum()

if missing_5 == len(comparison):
    print("\n5-Year CAGR : Not Available")
    print("Reason: NAV history covers Jan 2022 to May 2026,")
    print("which is less than 5 years of historical data.")
else:
    print(f"5-Year : {missing_5}")

# -----------------------------
# Display Results
# -----------------------------
print("\nTop 10 Funds by 3-Year CAGR")
print("-" * 40)

print(
    comparison[
        [
            "scheme_name",
            "category",
            "cagr_1yr_pct",
            "cagr_3yr_pct",
            "cagr_5yr_pct",
        ]
    ].head(10).to_string(index=False)
)

print(f"\nSaved successfully -> {output_path}")

print("\nTask 2 completed successfully.")