import pandas as pd
import numpy as np
from scipy import stats

print("Loading datasets...")

# NAV history
nav = pd.read_csv(
    "data/processed/02_nav_history_clean.csv",
    parse_dates=["date"]
)

# Fund master
fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[["amfi_code", "scheme_name", "category"]]

# Benchmark
macro = pd.read_csv(
    "data/processed/10_macro_factors_clean.csv",
    parse_dates=["date"]
)

print("Datasets loaded successfully.")

print("\nPreparing daily returns...")

nav = nav.sort_values(["amfi_code", "date"])

nav["daily_return"] = (
    nav.groupby("amfi_code")["nav"]
       .pct_change()
)

# Benchmark returns
benchmark = (
    macro[macro["index_name"] == "NIFTY100"]
    .sort_values("date")
)

benchmark["benchmark_return"] = (
    benchmark["close_value"]
    .pct_change()
)

benchmark = benchmark[
    ["date", "benchmark_return"]
].dropna()

print("Daily returns created.")

print("\nComputing Alpha & Beta...")

results = []

for code, group in nav.groupby("amfi_code"):

    merged = (
        group.merge(
            benchmark,
            on="date",
            how="inner"
        )
        .dropna()
    )

    if len(merged) < 30:
        continue

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        merged["benchmark_return"],
        merged["daily_return"]
    )

    results.append({
        "amfi_code": code,
        "beta": slope,
        "alpha_daily": intercept,
        "alpha_annual": intercept * 252,
        "r_squared": r_value ** 2,
        "p_value": p_value,
        "observations": len(merged)
    })

alpha_beta = pd.DataFrame(results)

print(alpha_beta.head())

alpha_beta = (
    alpha_beta.merge(
        fund_master,
        on="amfi_code",
        how="left"
    )
)

alpha_beta = alpha_beta[
    [
        "amfi_code",
        "scheme_name",
        "category",
        "beta",
        "alpha_annual",
        "r_squared",
        "p_value",
        "observations"
    ]
]

print(alpha_beta.head())

print("\nValidation")

print("-" * 40)

print("Funds analysed :", len(alpha_beta))

print("Missing values")
print(alpha_beta.isna().sum())

print()

print("Beta summary")
print(alpha_beta["beta"].describe())

print()

print("R² summary")
print(alpha_beta["r_squared"].describe())

alpha_beta = alpha_beta.sort_values(
    "alpha_annual",
    ascending=False
).reset_index(drop=True)

alpha_beta["rank"] = alpha_beta.index + 1

print("\nTop 10 by Alpha")

print(
    alpha_beta[
        [
            "rank",
            "scheme_name",
            "alpha_annual",
            "beta"
        ]
    ].head(10)
)

alpha_beta.to_csv(
    "data/processed/alpha_beta.csv",
    index=False
)

print("\nSaved successfully")
print("data/processed/alpha_beta.csv")