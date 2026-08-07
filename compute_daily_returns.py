import pandas as pd

# ==========================================================
# Task 1: Compute Daily Returns for All 40 Mutual Fund Schemes
# Formula:
# Daily Return = (NAV_t / NAV_t-1) - 1
# ==========================================================

print("=" * 60)
print("Loading datasets...")
print("=" * 60)

# Load NAV history
nav = pd.read_csv(
    "data/processed/02_nav_history_clean.csv",
    parse_dates=["date"]
)

# Load fund information
fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[["amfi_code", "scheme_name", "sub_category"]]

# ----------------------------------------------------------
# Sort data
# ----------------------------------------------------------
nav = (
    nav.sort_values(["amfi_code", "date"])
       .reset_index(drop=True)
)

# ----------------------------------------------------------
# Compute Daily Returns
# ----------------------------------------------------------
nav["daily_return"] = (
    nav.groupby("amfi_code")["nav"]
       .pct_change()
)

# ----------------------------------------------------------
# Merge fund information
# ----------------------------------------------------------
nav = nav.merge(
    fund_master,
    on="amfi_code",
    how="left",
    validate="many_to_one"
)

# ==========================================================
# VALIDATION
# ==========================================================

print("\nVALIDATION")
print("-" * 60)

# Number of funds
num_funds = nav["amfi_code"].nunique()

# Null values
null_returns = nav["daily_return"].isna().sum()

print(f"Total Funds                : {num_funds}")
print(f"Null Daily Returns         : {null_returns}")

if null_returns == num_funds:
    print("PASS - Exactly one null return per fund.")
else:
    print("WARNING - Unexpected null values detected.")

# ----------------------------------------------------------
# Extreme daily moves
# ----------------------------------------------------------
extreme_moves = nav[nav["daily_return"].abs() > 0.20]

print(f"\nExtreme Daily Moves (>20%) : {len(extreme_moves)}")

if len(extreme_moves) == 0:
    print("PASS - No unrealistic NAV jumps found.")
else:
    print("WARNING - Extreme daily movements detected.")

# ----------------------------------------------------------
# Return Distribution
# ----------------------------------------------------------
print("\nDaily Return Distribution")
print("-" * 60)
print(nav["daily_return"].describe())

# ----------------------------------------------------------
# Volatility by Sub Category
# ----------------------------------------------------------
print("\nDaily Return Volatility by Sub-category")
print("-" * 60)

volatility = (
    nav.groupby("sub_category")["daily_return"]
       .std()
       .sort_values()
)

print(volatility)

# ==========================================================
# Save Output
# ==========================================================

output_path = "data/processed/02_nav_history_with_returns.csv"

nav.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("Daily returns computed successfully.")
print(f"Output saved to: {output_path}")
print("=" * 60)