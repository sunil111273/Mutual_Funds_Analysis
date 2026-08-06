import os
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SIP_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "04_monthly_sip_inflows_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "sip_inflow_trend.html"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading SIP inflow dataset...")

sip = pd.read_csv(
    SIP_PATH,
    parse_dates=["month"]
)

sip = sip.sort_values("month")

print(f"Records Loaded : {len(sip)}")
print(
    f"Date Range     : "
    f"{sip['month'].min().strftime('%b %Y')} "
    f"to "
    f"{sip['month'].max().strftime('%b %Y')}"
)

# ==========================================================
# Find All-Time High
# ==========================================================

peak = sip.loc[sip["sip_inflow_crore"].idxmax()]

print(
    f"Peak SIP Inflow: "
    f"₹{peak['sip_inflow_crore']:,} Cr "
    f"({peak['month'].strftime('%b %Y')})"
)

# ==========================================================
# Create Plotly Figure
# ==========================================================

fig = go.Figure()

# Main Trend Line
fig.add_trace(
    go.Scatter(
        x=sip["month"],
        y=sip["sip_inflow_crore"],
        mode="lines+markers",
        name="Monthly SIP Inflow",
        line=dict(
            color="#1f77b4",
            width=3
        ),
        marker=dict(
            size=6
        ),
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>"
            "SIP Inflow: ₹%{y:,} Cr"
            "<extra></extra>"
        ),
    )
)

# Highlight Peak
fig.add_trace(
    go.Scatter(
        x=[peak["month"]],
        y=[peak["sip_inflow_crore"]],
        mode="markers",
        name="All-Time High",
        marker=dict(
            color="crimson",
            size=14,
            symbol="star"
        ),
        hovertemplate=(
            "<b>All-Time High</b><br>"
            "%{x|%b %Y}<br>"
            "₹%{y:,} Cr"
            "<extra></extra>"
        ),
    )
)

# Annotation
fig.add_annotation(
    x=peak["month"],
    y=peak["sip_inflow_crore"],
    text=(
        f"<b>₹{peak['sip_inflow_crore']:,} Cr</b>"
        "<br>All-Time High"
        "<br>Dec 2025"
    ),
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="crimson",
    ax=-80,
    ay=-70,
    bgcolor="white",
    bordercolor="crimson",
    borderwidth=1,
    font=dict(
        size=12,
        color="crimson"
    ),
)

# ==========================================================
# Layout
# ==========================================================

fig.update_layout(
    title=(
        "Monthly SIP Inflow Trend (Jan 2022 – Dec 2025)"
    ),
    xaxis_title="Month",
    yaxis_title="SIP Inflow (₹ Crore)",
    template="plotly_white",
    hovermode="x unified",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    margin=dict(
        l=60,
        r=40,
        t=80,
        b=60
    )
)

# X-axis formatting
fig.update_xaxes(
    tickformat="%b\n%Y",
    dtick="M6",
    showgrid=True
)

# Y-axis formatting
fig.update_yaxes(
    showgrid=True,
    tickprefix="₹",
    ticksuffix=" Cr"
)

# ==========================================================
# Save Report
# ==========================================================

fig.write_html(OUTPUT_FILE)

print(f"\nInteractive report saved to:\n{OUTPUT_FILE}")

# ==========================================================
# Display Figure
# ==========================================================

fig.show()