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

# Drop the first NaN return per scheme (no prior-day NAV to compare to)
returns = nav.dropna(subset=["daily_return"])

CONFIDENCE_LEVEL = 0.95
VAR_PERCENTILE = (1 - CONFIDENCE_LEVEL) * 100   # 5th percentile

print(f"\nConfidence Level : {CONFIDENCE_LEVEL*100:.0f}%")
print(f"VaR Percentile    : {VAR_PERCENTILE:.0f}th percentile of daily returns")
print(f"Total Funds       : {fund_master['amfi_code'].nunique()}")


# --------------------------------------------------
# Historical VaR (95%) & CVaR per fund
# VaR   = 5th percentile of the daily return distribution
# CVaR  = mean of all daily returns at/below the VaR threshold
#         (a.k.a. Expected Shortfall)
# --------------------------------------------------
def var_cvar(group):
    daily_returns = group["daily_return"].dropna()

    var_95 = np.percentile(daily_returns, VAR_PERCENTILE)
    tail_losses = daily_returns[daily_returns <= var_95]
    cvar_95 = tail_losses.mean() if len(tail_losses) > 0 else np.nan

    return pd.Series({
        "observations": len(daily_returns),
        "mean_daily_return": daily_returns.mean(),
        "daily_std_dev": daily_returns.std(),
        "var_95_daily_pct": var_95 * 100,
        "cvar_95_daily_pct": cvar_95 * 100,
        # Scaled to a 1-day 95% VaR/CVaR on a notional Rs. 1,00,000 investment
        "var_95_amt_per_1lakh": var_95 * 100000,
        "cvar_95_amt_per_1lakh": cvar_95 * 100000,
    })


print("\nComputing Historical VaR (95%) and CVaR per fund...")

var_cvar_stats = (
    returns
    .groupby("amfi_code")
    .apply(var_cvar, include_groups=False)
    .reset_index()
)

# Round values
for col in [
    "mean_daily_return",
    "daily_std_dev",
    "var_95_daily_pct",
    "cvar_95_daily_pct"
]:
    var_cvar_stats[col] = var_cvar_stats[col].round(4)

for col in ["var_95_amt_per_1lakh", "cvar_95_amt_per_1lakh"]:
    var_cvar_stats[col] = var_cvar_stats[col].round(0)

# --------------------------------------------------
# Merge Fund Details
# --------------------------------------------------
report = (
    var_cvar_stats
    .merge(fund_master, on="amfi_code", how="left")
)

# Rank funds from riskiest (most negative VaR) to safest
report = report.sort_values(
    "var_95_daily_pct",
    ascending=True
).reset_index(drop=True)

report["risk_rank"] = report.index + 1

report = report[
    [
        "risk_rank",
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "observations",
        "mean_daily_return",
        "daily_std_dev",
        "var_95_daily_pct",
        "cvar_95_daily_pct",
        "var_95_amt_per_1lakh",
        "cvar_95_amt_per_1lakh"
    ]
]

# --------------------------------------------------
# Save Output
# --------------------------------------------------
output_file = "data/processed/var_cvar_report.csv"

report.to_csv(output_file, index=False)

# --------------------------------------------------
# Validation
# --------------------------------------------------
print("\nValidation")
print("-" * 45)

print(f"Funds Analysed          : {len(report)}")
print(f"Unique Funds             : {report['amfi_code'].nunique()}")
print(f"Missing VaR Values      : {report['var_95_daily_pct'].isna().sum()}")
print(f"Missing CVaR Values     : {report['cvar_95_daily_pct'].isna().sum()}")

print("\nTop 10 Highest-Risk Funds (worst 1-day 95% VaR)")
print("-" * 45)

print(
    report[
        [
            "risk_rank",
            "scheme_name",
            "sub_category",
            "var_95_daily_pct",
            "cvar_95_daily_pct"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nTop 10 Lowest-Risk Funds (best 1-day 95% VaR)")
print("-" * 45)

print(
    report[
        [
            "risk_rank",
            "scheme_name",
            "sub_category",
            "var_95_daily_pct",
            "cvar_95_daily_pct"
        ]
    ]
    .tail(10)
    .to_string(index=False)
)

print("\nAverage VaR / CVaR by Sub-Category")
print("-" * 45)

print(
    report
    .groupby("sub_category")[["var_95_daily_pct", "cvar_95_daily_pct"]]
    .mean()
    .round(4)
    .sort_values("var_95_daily_pct")
    .to_string()
)

print(f"\nSaved successfully -> {output_file}")

print("\nNote:")
print("Historical VaR (95%) = 5th percentile of each fund's daily return")
print("distribution — the 1-day loss not expected to be exceeded 95% of the")
print("time, based purely on historical NAV movements (no distributional")
print("assumption).")
print("CVaR (95%), a.k.a. Expected Shortfall, = the average of all daily")
print("returns that fall at or below the VaR threshold — i.e. the expected")
print("loss on the worst 5% of days.")

print("\nDay 6 Task 1 completed successfully.")
