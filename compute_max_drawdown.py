import pandas as pd

print("Loading NAV datasets...\n")

# ----------------------------
# Load Data
# ----------------------------
nav = pd.read_csv(
    "data/processed/02_nav_history_clean.csv",
    parse_dates=["date"]
)

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[["amfi_code", "scheme_name", "sub_category"]]

# Sort data
nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)

print(f"Total Schemes : {nav['amfi_code'].nunique()}")
print(f"Latest NAV Date : {nav['date'].max().date()}")

print("\nComputing Maximum Drawdown...\n")

results = []

# ----------------------------
# Compute Drawdown
# ----------------------------
for code, group in nav.groupby("amfi_code"):

    group = group.sort_values("date").reset_index(drop=True)

    # Running maximum NAV
    group["running_max"] = group["nav"].cummax()

    # Drawdown
    group["drawdown"] = (
        group["nav"] /
        group["running_max"]
    ) - 1

    # Worst drawdown
    trough_idx = group["drawdown"].idxmin()

    max_drawdown = group.loc[trough_idx, "drawdown"]
    trough_date = group.loc[trough_idx, "date"]

    # Running max value that produced this drawdown
    peak_nav = group.loc[trough_idx, "running_max"]

    peak_date = (
        group.loc[
            (group["nav"] == peak_nav)
            &
            (group["date"] <= trough_date),
            "date"
        ]
        .max()
    )

    duration_days = (
        trough_date - peak_date
    ).days

    results.append(
        {
            "amfi_code": code,
            "max_drawdown": round(max_drawdown, 6),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "peak_date": peak_date,
            "trough_date": trough_date,
            "drawdown_duration_days": duration_days,
        }
    )

# ----------------------------
# Merge Fund Names
# ----------------------------
dd = (
    pd.DataFrame(results)
    .merge(
        fund_master,
        on="amfi_code",
        how="left"
    )
)

dd = dd[
    [
        "amfi_code",
        "scheme_name",
        "sub_category",
        "max_drawdown",
        "max_drawdown_pct",
        "peak_date",
        "trough_date",
        "drawdown_duration_days",
    ]
]

# Worst drawdown first
dd = dd.sort_values(
    "max_drawdown"
).reset_index(drop=True)

# Ranking
dd["rank"] = dd.index + 1

# ----------------------------
# Validation
# ----------------------------
print("Validation")
print("-" * 40)

print(f"Funds analysed : {len(dd)}")
print(f"Unique funds   : {dd['amfi_code'].nunique()}")

print("\nMissing Values")
print(dd.isna().sum())

print("\nWorst Drawdown")

worst = dd.iloc[0]

print(f"Scheme      : {worst['scheme_name']}")
print(f"Category    : {worst['sub_category']}")
print(f"Drawdown    : {worst['max_drawdown_pct']:.2f}%")
print(f"Peak Date   : {worst['peak_date'].date()}")
print(f"Trough Date : {worst['trough_date'].date()}")
print(f"Duration    : {worst['drawdown_duration_days']} days")

print("\nTop 10 Worst Drawdowns\n")

print(
    dd[
        [
            "rank",
            "scheme_name",
            "sub_category",
            "max_drawdown_pct",
            "peak_date",
            "trough_date",
            "drawdown_duration_days",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

# ----------------------------
# Save
# ----------------------------
output_file = "data/processed/max_drawdown_by_fund.csv"

dd.to_csv(
    output_file,
    index=False
)

print(f"\nSaved successfully -> {output_file}")