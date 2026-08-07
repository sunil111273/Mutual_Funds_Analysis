import numpy as np
import pandas as pd

print("Loading datasets...")

# --------------------------------------------------
# Load Data
# --------------------------------------------------
nav = pd.read_csv(
    "data/processed/02_nav_history_with_returns.csv",
    parse_dates=["date"]
)

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[[
    "amfi_code",
    "scheme_name",
    "fund_house",
    "category",
    "sub_category"
]]

# --------------------------------------------------
# Risk-Free Rate
# --------------------------------------------------
RF_ANNUAL = 0.065
RF_DAILY = RF_ANNUAL / 252

print(f"\nRisk-Free Rate : {RF_ANNUAL*100:.2f}%")
print(f"Total Funds    : {fund_master['amfi_code'].nunique()}")

# --------------------------------------------------
# Compute Mean & Std Daily Returns
# --------------------------------------------------
stats = (
    nav
    .groupby("amfi_code")["daily_return"]
    .agg(
        average_daily_return="mean",
        daily_std_dev="std",
        observations="count"
    )
    .reset_index()
)

# --------------------------------------------------
# Sharpe Ratio
# Sharpe = (Rp - Rf) / Std × √252
# --------------------------------------------------
stats["sharpe_ratio"] = np.where(
    stats["daily_std_dev"] > 0,
    ((stats["average_daily_return"] - RF_DAILY)
     / stats["daily_std_dev"]) * np.sqrt(252),
    np.nan
)

# Round values
stats["average_daily_return"] = stats["average_daily_return"].round(6)
stats["daily_std_dev"] = stats["daily_std_dev"].round(6)
stats["sharpe_ratio"] = stats["sharpe_ratio"].round(3)

# --------------------------------------------------
# Merge Fund Details
# --------------------------------------------------
ranking = (
    stats.merge(
        fund_master,
        on="amfi_code",
        how="left"
    )
)

ranking = ranking.sort_values(
    "sharpe_ratio",
    ascending=False
).reset_index(drop=True)

ranking["rank"] = ranking.index + 1

ranking = ranking[
    [
        "rank",
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "average_daily_return",
        "daily_std_dev",
        "sharpe_ratio"
    ]
]

# --------------------------------------------------
# Save Output
# --------------------------------------------------
output_file = "data/processed/sharpe_ratio_ranking.csv"

ranking.to_csv(output_file, index=False)

# --------------------------------------------------
# Validation
# --------------------------------------------------
print("\nValidation")
print("-" * 45)

print(f"Funds Ranked            : {len(ranking)}")
print(f"Unique Funds            : {ranking['amfi_code'].nunique()}")
print(f"Missing Sharpe Values   : {ranking['sharpe_ratio'].isna().sum()}")

print("\nTop 10 Funds by Sharpe Ratio")
print("-" * 45)

print(
    ranking[
        [
            "rank",
            "scheme_name",
            "sub_category",
            "sharpe_ratio"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nBottom 10 Funds by Sharpe Ratio")
print("-" * 45)

print(
    ranking[
        [
            "rank",
            "scheme_name",
            "sub_category",
            "sharpe_ratio"
        ]
    ]
    .tail(10)
    .to_string(index=False)
)

print(f"\nSaved successfully -> {output_file}")

print("\nNote:")
print("Sharpe Ratio was computed using:")
print("Sharpe = (Average Daily Return − Daily Risk-Free Rate)")
print("         / Daily Return Standard Deviation × √252")

print("\nRisk-Free Rate Assumption : 6.5% annually")

print("\nTask 3 completed successfully.")