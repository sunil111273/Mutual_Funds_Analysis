import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "nav_return_correlation.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading NAV datasets...")

nav = pd.read_csv(
    NAV_PATH,
    parse_dates=["date"]
)

fund_master = pd.read_csv(FUND_PATH)

# ==========================================================
# Selected Funds (One flagship equity fund per AMC)
# ==========================================================

selected_codes = [
    119551,  # SBI Bluechip Fund
    100016,  # HDFC Top 100 Fund
    120503,  # ICICI Prudential Bluechip Fund
    118632,  # Nippon India Large Cap Fund
    120841,  # Kotak Bluechip Fund
    119092,  # Axis Bluechip Fund
    101206,  # Aditya Birla Sun Life Frontline Equity Fund
    102885,  # UTI Nifty 50 Index Fund
    148567,  # Mirae Asset Large Cap Fund
    149322,  # DSP Top 100 Equity Fund
]

# ==========================================================
# Merge Fund Information
# ==========================================================

nav = nav[
    nav["amfi_code"].isin(selected_codes)
]

nav = nav.merge(
    fund_master[
        ["amfi_code", "fund_house"]
    ],
    on="amfi_code",
    how="left"
)

# Short labels for heatmap

nav["label"] = (
    nav["fund_house"]
    .str.replace(" Mutual Fund", "", regex=False)
    .str.replace(" MF", "", regex=False)
)

# ==========================================================
# Pivot NAV Data
# ==========================================================

nav_wide = (
    nav.pivot(
        index="date",
        columns="label",
        values="nav"
    )
    .sort_index()
    .ffill()
)

# ==========================================================
# Compute Daily Returns
# ==========================================================

returns = (
    nav_wide
    .pct_change()
    .dropna()
)

# ==========================================================
# Correlation Matrix
# ==========================================================

corr = returns.corr()

# ==========================================================
# Plot Heatmap
# ==========================================================

sns.set_theme(style="white")

plt.figure(figsize=(10, 8))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="RdYlGn",
    center=0,
    vmin=-1,
    vmax=1,
    square=True,
    linewidths=0.5,
    cbar_kws={
        "label": "Correlation of Daily Returns"
    }
)

plt.title(
    "NAV Return Correlation Matrix (10 Selected Funds)",
    fontsize=15,
    fontweight="bold"
)

plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)

plt.tight_layout()

# ==========================================================
# Save Chart
# ==========================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================================
# Summary
# ==========================================================

print("\nNAV return correlation matrix generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")