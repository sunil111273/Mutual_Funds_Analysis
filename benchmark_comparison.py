import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go

# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORT_DIR, exist_ok=True)

# ============================================================
# Load Data
# ============================================================

print("=" * 60)
print("Loading datasets...")
print("=" * 60)

nav = pd.read_csv(
    os.path.join(DATA_DIR, "02_nav_history_clean.csv"),
    parse_dates=["date"]
)

macro = pd.read_csv(
    os.path.join(DATA_DIR, "10_macro_factors_clean.csv"),
    parse_dates=["date"]
)

fund_master = pd.read_csv(
    os.path.join(DATA_DIR, "01_fund_master_clean.csv")
)

scorecard = pd.read_csv(
    os.path.join(DATA_DIR, "fund_scorecard.csv")
)

# ============================================================
# Validation
# ============================================================

print("\nValidation")
print("-" * 50)

print("NAV rows            :", len(nav))
print("Macro rows          :", len(macro))
print("Fund Master rows    :", len(fund_master))
print("Scorecard rows      :", len(scorecard))

print("\nUnique NAV Schemes  :", nav["amfi_code"].nunique())
print("Unique Scorecard    :", scorecard["amfi_code"].nunique())

# ============================================================
# Keep only Equity Funds
# ============================================================

equity_codes = fund_master.loc[
    fund_master["category"] == "Equity",
    "amfi_code"
]

scorecard_equity = (
    scorecard[
        scorecard["amfi_code"].isin(equity_codes)
    ]
    .sort_values("fund_score", ascending=False)
    .reset_index(drop=True)
)

# ============================================================
# Select Top 5 Funds
# ============================================================

top5 = scorecard_equity.head(5)

top5_codes = top5["amfi_code"].tolist()

print("\nTop 5 Equity Funds")
print("-" * 50)

print(
    top5[
        [
            "rank",
            "scheme_name",
            "fund_score",
        ]
    ]
)

# ============================================================
# Restrict NAV to Top 5 Funds
# ============================================================

nav = nav[
    nav["amfi_code"].isin(top5_codes)
].copy()

# ============================================================
# Restrict to Last 3 Years
# ============================================================

latest_date = nav["date"].max()

start_date = latest_date - pd.DateOffset(years=3)

nav = nav[
    nav["date"] >= start_date
].copy()

macro = macro[
    (macro["date"] >= start_date)
    &
    (
        macro["index_name"].isin(
            [
                "NIFTY50",
                "NIFTY100",
            ]
        )
    )
].copy()

print("\nAnalysis Window")
print("-" * 50)

print("Start Date :", start_date.date())
print("End Date   :", latest_date.date())

print("\nNAV Rows After Filter :", len(nav))
print("Macro Rows            :", len(macro))

# ============================================================
# Create Mapping
# ============================================================

scheme_map = dict(
    zip(
        fund_master["amfi_code"],
        fund_master["scheme_name"]
    )
)

print("\nData Loaded Successfully.")
print("=" * 60)

# ============================================================
# Part 1B: Rebase Data and Create Benchmark Comparison Chart
# ============================================================

print("\nCreating benchmark comparison chart...")
print("=" * 60)


# ============================================================
# Rebase Function
# ============================================================

def rebase_to_100(df, group_col, value_col):
    """
    Converts values into indexed performance starting from 100.
    Formula:
    Current Value / First Value * 100
    """

    df = df.sort_values(
        [group_col, "date"]
    ).copy()

    first_value = (
        df.groupby(group_col)[value_col]
        .transform("first")
    )

    df["rebased_value"] = (
        df[value_col] / first_value
    ) * 100

    return df


# ============================================================
# Rebase NAV Data
# ============================================================

nav_chart = rebase_to_100(
    nav,
    "amfi_code",
    "nav"
)


# ============================================================
# Rebase Benchmark Data
# ============================================================

macro_chart = rebase_to_100(
    macro,
    "index_name",
    "close_value"
)


# ============================================================
# Create Plotly Chart
# ============================================================

fig = go.Figure()


# ------------------------------------------------------------
# Add Top 5 Funds
# ------------------------------------------------------------

for code in top5_codes:

    fund_data = nav_chart[
        nav_chart["amfi_code"] == code
    ]

    fig.add_trace(
        go.Scatter(
            x=fund_data["date"],
            y=fund_data["rebased_value"],
            mode="lines",
            name=scheme_map.get(
                code,
                str(code)
            )
        )
    )


# ------------------------------------------------------------
# Add Nifty 50
# ------------------------------------------------------------

for benchmark in [
    "NIFTY50",
    "NIFTY100"
]:

    benchmark_data = macro_chart[
        macro_chart["index_name"] == benchmark
    ]

    fig.add_trace(
        go.Scatter(
            x=benchmark_data["date"],
            y=benchmark_data["rebased_value"],
            mode="lines",
            name=benchmark,
            line=dict(
                dash="dash",
                width=3
            )
        )
    )


# ============================================================
# Chart Layout
# ============================================================

fig.update_layout(

    title=(
        "Top 5 Mutual Funds vs NIFTY50 & NIFTY100 "
        "Performance Comparison (3 Years)"
    ),

    xaxis_title="Date",

    yaxis_title=(
        "Indexed Value "
        "(Starting Value = 100)"
    ),

    height=650,

    width=1100,

    template="plotly_white",

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.35,
        xanchor="center",
        x=0.5
    )

)


# ============================================================
# Save Chart
# ============================================================

html_path = os.path.join(
    REPORT_DIR,
    "benchmark_comparison.html"
)

# Save interactive HTML chart
# Save interactive HTML chart

fig.write_html(
    html_path
)

print("\nInteractive chart saved successfully")
print(html_path)


# Save PNG chart (optional static output)

png_path = os.path.join(
    REPORT_DIR,
    "benchmark_comparison.png"
)

try:
    fig.write_image(
        png_path,
        scale=2
    )

    print("\nPNG chart saved successfully")
    print(png_path)

except Exception as e:
    print("\nPNG export skipped")
    print(e)


fig.show()


# ============================================================
# Validation
# ============================================================

print("\nChart Validation")
print("-" * 50)

print(
    "Funds plotted :",
    len(top5_codes)
)

print(
    "Benchmarks plotted :",
    macro_chart["index_name"].nunique()
)

print(
    "Chart Start Date :",
    nav_chart["date"].min().date()
)

print(
    "Chart End Date   :",
    nav_chart["date"].max().date()
)


print("\nSaved Files")
print("-" * 50)

print(html_path)

if os.path.exists(png_path):
    print(png_path)

print("\nPart 1 Completed Successfully")

# ============================================================
# Load Required Data
# ============================================================

nav = pd.read_csv(
    os.path.join(DATA_DIR, "02_nav_history_clean.csv"),
    parse_dates=["date"]
)

macro = pd.read_csv(
    os.path.join(DATA_DIR, "10_macro_factors_clean.csv"),
    parse_dates=["date"]
)


scorecard = pd.read_csv(
    os.path.join(DATA_DIR, "fund_scorecard.csv")
)


fund_master = pd.read_csv(
    os.path.join(DATA_DIR, "01_fund_master_clean.csv")
)


print("Data Loaded Successfully")


# ============================================================
# Select Top 5 Equity Funds
# ============================================================

equity_codes = fund_master[
    fund_master["category"] == "Equity"
]["amfi_code"]


top5 = (
    scorecard[
        scorecard["amfi_code"].isin(equity_codes)
    ]
    .sort_values(
        "fund_score",
        ascending=False
    )
    .head(5)
)


top5_codes = top5["amfi_code"].tolist()


print("\nTop 5 Funds Selected")
print(
    top5[
        [
            "rank",
            "scheme_name",
            "fund_score"
        ]
    ]
)


# ============================================================
# Filter Last 3 Years Data
# ============================================================

end_date = nav["date"].max()

start_date = (
    end_date -
    pd.DateOffset(years=3)
)


nav_3y = nav[
    (nav["amfi_code"].isin(top5_codes))
    &
    (nav["date"] >= start_date)
].copy()


benchmark = macro[
    (macro["index_name"].isin(
        [
            "NIFTY50",
            "NIFTY100"
        ]
    ))
    &
    (macro["date"] >= start_date)
].copy()



# ============================================================
# Calculate Daily Returns
# ============================================================


nav_3y = nav_3y.sort_values(
    [
        "amfi_code",
        "date"
    ]
)


nav_3y["fund_return"] = (
    nav_3y
    .groupby("amfi_code")["nav"]
    .pct_change()
)



benchmark = benchmark.sort_values(
    [
        "index_name",
        "date"
    ]
)


benchmark["benchmark_return"] = (
    benchmark
    .groupby("index_name")["close_value"]
    .pct_change()
)



# ============================================================
# Tracking Error Calculation
#
# TE = std(Fund Return - Benchmark Return) * sqrt(252)
# ============================================================


results = []


for fund in top5_codes:


    fund_data = nav_3y[
        nav_3y["amfi_code"] == fund
    ][
        [
            "date",
            "fund_return"
        ]
    ]


    for index in [
        "NIFTY50",
        "NIFTY100"
    ]:


        bench_data = benchmark[
            benchmark["index_name"] == index
        ][
            [
                "date",
                "benchmark_return"
            ]
        ]


        merged = fund_data.merge(
            bench_data,
            on="date",
            how="inner"
        )


        merged = merged.dropna()


        tracking_error = (
            (
                merged["fund_return"]
                -
                merged["benchmark_return"]
            )
            .std()
            *
            np.sqrt(252)
            *
            100
        )


        scheme_name = (
            fund_master[
                fund_master["amfi_code"] == fund
            ]
            ["scheme_name"]
            .iloc[0]
        )


        results.append(
            {
                "amfi_code": fund,
                "scheme_name": scheme_name,
                "benchmark": index,
                "tracking_error_pct": round(
                    tracking_error,
                    2
                ),
                "observations": len(merged)
            }
        )


# ============================================================
# Save Output
# ============================================================


tracking_error_df = pd.DataFrame(results)


OUTPUT = os.path.join(
REPORT_DIR,
"tracking_error_top5.csv"
)


tracking_error_df.to_csv(
    OUTPUT,
    index=False
)



# ============================================================
# Validation
# ============================================================

print("\nValidation")
print("-"*50)

print(
    "Rows:",
    len(tracking_error_df)
)

print(
    "Funds:",
    tracking_error_df["amfi_code"].nunique()
)


print("\nTracking Error Results")

print(
    tracking_error_df
    .to_string(index=False)
)


print(
    "\nSaved:",
    OUTPUT
)