import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

scorecard = pd.read_csv(
    "data/processed/fund_scorecard.csv"
)

# --------------------------------------------------
# Select Top 5 Key Equity Funds
# Same set used in Day 4 benchmark comparison
# --------------------------------------------------
equity_codes = fund_master.loc[
    fund_master["category"] == "Equity",
    "amfi_code"
]

scorecard_equity = scorecard[
    scorecard["amfi_code"].isin(equity_codes)
].copy()

top5 = scorecard_equity.head(5)

top5_codes = top5["amfi_code"].tolist()

print("\nTop 5 Key Equity Funds Selected")
print("-" * 60)

print(
    top5[
        ["rank", "amfi_code", "scheme_name", "fund_score"]
    ].to_string(index=False)
)

# --------------------------------------------------
# Rolling Sharpe Parameters
# --------------------------------------------------
WINDOW = 90
ANNUALIZATION_FACTOR = np.sqrt(252)

# --------------------------------------------------
# Filter NAV data for selected funds
# --------------------------------------------------
nav_top5 = nav[
    nav["amfi_code"].isin(top5_codes)
].sort_values(
    ["amfi_code", "date"]
).copy()

# --------------------------------------------------
# Compute Rolling 90-Day Sharpe Ratio
#
# Assignment formula:
#
# Rolling Sharpe =
# rolling mean of returns
# -----------------------
# rolling std of returns
# × √252
# --------------------------------------------------

rolling_frames = []

for code, group in nav_top5.groupby("amfi_code"):

    group = group.sort_values("date").copy()

    # 90-day rolling mean
    rolling_mean = (
        group["daily_return"]
        .rolling(WINDOW)
        .mean()
    )

    # 90-day rolling standard deviation
    rolling_std = (
        group["daily_return"]
        .rolling(WINDOW)
        .std()
    )

    # Rolling 90-day annualised Sharpe ratio
    group["rolling_sharpe"] = (
        rolling_mean / rolling_std
    ) * ANNUALIZATION_FACTOR

    rolling_frames.append(
        group[
            [
                "amfi_code",
                "date",
                "rolling_sharpe"
            ]
        ]
    )

# --------------------------------------------------
# Combine all 5 funds
# --------------------------------------------------
rolling_sharpe_df = pd.concat(
    rolling_frames,
    ignore_index=True
)

# Add scheme names
rolling_sharpe_df = rolling_sharpe_df.merge(
    fund_master[
        ["amfi_code", "scheme_name"]
    ],
    on="amfi_code",
    how="left"
)

# Sort output
rolling_sharpe_df = rolling_sharpe_df.sort_values(
    ["amfi_code", "date"]
).reset_index(drop=True)

# --------------------------------------------------
# Save Calculated Results
# --------------------------------------------------
output_file = "data/processed/rolling_sharpe_top5.csv"

rolling_sharpe_df.to_csv(
    output_file,
    index=False
)

print(f"\nSaved successfully -> {output_file}")

print(
    f"Rows written: {len(rolling_sharpe_df)}"
)

print(
    f"NaN rolling_sharpe "
    f"(first {WINDOW - 1} observations per fund): "
    f"{rolling_sharpe_df['rolling_sharpe'].isna().sum()}"
)

# --------------------------------------------------
# Validation
# --------------------------------------------------
print("\nValidation")
print("-" * 60)

print(
    f"Funds analysed       : "
    f"{rolling_sharpe_df['amfi_code'].nunique()}"
)

print(
    f"Expected funds       : 5"
)

print(
    f"Missing Sharpe values: "
    f"{rolling_sharpe_df['rolling_sharpe'].isna().sum()}"
)

# --------------------------------------------------
# Plot Rolling 90-Day Sharpe Ratio
# --------------------------------------------------
plt.figure(figsize=(14, 7))

for code in top5_codes:

    fund_data = rolling_sharpe_df[
        rolling_sharpe_df["amfi_code"] == code
    ].copy()

    if fund_data.empty:
        continue

    label = fund_data[
        "scheme_name"
    ].iloc[0]

    plt.plot(
        fund_data["date"],
        fund_data["rolling_sharpe"],
        label=label,
        linewidth=1.3
    )

# Zero reference line
plt.axhline(
    0,
    linestyle="--",
    linewidth=0.8
)

plt.title(
    "Rolling 90-Day Sharpe Ratio — 5 Key Equity Funds",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Date")

plt.ylabel(
    "Rolling Sharpe Ratio (Annualised)"
)

plt.legend(
    loc="upper left",
    fontsize=9
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# --------------------------------------------------
# Save Chart
# --------------------------------------------------
chart_file = "reports/rolling_sharpe_chart.png"

plt.savefig(
    chart_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(
    f"\nChart saved -> {chart_file}"
)

print("\nTask 2 (Day 6) completed successfully.")