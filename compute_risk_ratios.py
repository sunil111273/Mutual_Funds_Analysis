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
# Calculate Sortino Ratio
# --------------------------------------------------
results = []

for code, group in nav.groupby("amfi_code"):

    returns = group["daily_return"].dropna()

    avg_return = returns.mean()

    downside_returns = returns[returns < 0]

    downside_std = downside_returns.std()

    if downside_std == 0 or np.isnan(downside_std):
        sortino = np.nan
    else:
        sortino = (
            (avg_return - RF_DAILY)
            / downside_std
        ) * np.sqrt(252)

    results.append({
        "amfi_code": code,
        "average_daily_return": round(avg_return, 6),
        "downside_std_dev": round(downside_std, 6),
        "negative_return_days": len(downside_returns),
        "total_return_days": len(returns),
        "sortino_ratio": round(sortino, 3) if pd.notna(sortino) else np.nan
    })

results = pd.DataFrame(results)

# --------------------------------------------------
# Merge Fund Information
# --------------------------------------------------
ranking = (
    results.merge(
        fund_master,
        on="amfi_code",
        how="left"
    )
)

ranking = ranking.sort_values(
    "sortino_ratio",
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
        "downside_std_dev",
        "negative_return_days",
        "total_return_days",
        "sortino_ratio"
    ]
]

# --------------------------------------------------
# Save Output
# --------------------------------------------------
output_file = "data/processed/sortino_ratio_ranking.csv"

ranking.to_csv(output_file, index=False)

# --------------------------------------------------
# Validation
# --------------------------------------------------
print("\nValidation")
print("-" * 50)

print(f"Funds Ranked              : {len(ranking)}")
print(f"Unique Funds              : {ranking['amfi_code'].nunique()}")
print(f"Missing Sortino Ratios    : {ranking['sortino_ratio'].isna().sum()}")

print("\nTop 10 Funds by Sortino Ratio")
print("-" * 50)

print(
    ranking[
        [
            "rank",
            "scheme_name",
            "sub_category",
            "sortino_ratio"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nBottom 10 Funds by Sortino Ratio")
print("-" * 50)

print(
    ranking[
        [
            "rank",
            "scheme_name",
            "sub_category",
            "sortino_ratio"
        ]
    ]
    .tail(10)
    .to_string(index=False)
)

print(f"\nSaved successfully -> {output_file}")

print("\nFormula Used")
print("--------------------------------")
print("Sortino Ratio =")
print("(Average Daily Return − Daily Risk-Free Rate)")
print("/ Downside Standard Deviation × √252")

print("\nRisk-Free Rate Assumption : 6.5% annually")
print("Trading Days Per Year     : 252")

print("\nTask 4 completed successfully.")