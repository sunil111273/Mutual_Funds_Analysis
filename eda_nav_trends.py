import os
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NAV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "02_nav_history_clean.csv"
)

FUND_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "01_fund_master_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(REPORT_DIR, "eda_nav_trends.html")

# ==========================================================
# Load Data
# ==========================================================

print("Loading datasets...")

nav = pd.read_csv(
    NAV_PATH,
    parse_dates=["date"]
)

funds = pd.read_csv(
    FUND_PATH,
    usecols=["amfi_code", "scheme_name"]
)

print(f"NAV records : {len(nav):,}")
print(f"Funds       : {len(funds)}")

# ==========================================================
# Merge Scheme Names
# ==========================================================

nav = nav.merge(
    funds,
    on="amfi_code",
    how="left"
)

# ==========================================================
# Sort Data
# ==========================================================

nav = nav.sort_values(
    ["amfi_code", "date"]
)

# ==========================================================
# Indexed NAV (Base = 100)
# ==========================================================

nav["nav_indexed"] = (
    nav.groupby("amfi_code")["nav"]
    .transform(lambda s: (s / s.iloc[0]) * 100)
)

# ==========================================================
# Create Interactive Plot
# ==========================================================

fig = go.Figure()

for code, group in nav.groupby("amfi_code"):

    scheme = group["scheme_name"].iloc[0]

    fig.add_trace(
        go.Scatter(
            x=group["date"],
            y=group["nav_indexed"],
            mode="lines",
            name=scheme,
            line=dict(width=1),
            opacity=0.6,
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Date: %{x|%d-%b-%Y}<br>"
                "Indexed NAV: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

# ==========================================================
# Highlight Market Phases
# ==========================================================

fig.add_vrect(
    x0="2023-01-01",
    x1="2023-12-31",
    fillcolor="green",
    opacity=0.08,
    line_width=0,
    annotation_text="2023 Bull Run",
    annotation_position="top left",
)

fig.add_vrect(
    x0="2024-01-01",
    x1="2024-12-31",
    fillcolor="red",
    opacity=0.08,
    line_width=0,
    annotation_text="2024 Correction",
    annotation_position="top left",
)

# ==========================================================
# Layout
# ==========================================================

fig.update_layout(
    title="NAV Trend Analysis (2022–2026)<br><sup>All 40 Mutual Fund Schemes Indexed to Base = 100</sup>",
    xaxis_title="Date",
    yaxis_title="Indexed NAV (Base = 100)",
    template="plotly_white",
    height=750,
    hovermode="x unified",
    legend=dict(
        font=dict(size=8),
        itemsizing="constant"
    ),
    margin=dict(
        l=60,
        r=20,
        t=80,
        b=50
    )
)

fig.update_xaxes(showgrid=True)

fig.update_yaxes(showgrid=True)

# ==========================================================
# Save Report
# ==========================================================

fig.write_html(OUTPUT_FILE)

print("\nEDA Report Generated Successfully")
print(f"Location : {OUTPUT_FILE}")
print(f"Schemes  : {nav['amfi_code'].nunique()}")
print(f"Date Range : {nav['date'].min().date()} -> {nav['date'].max().date()}")