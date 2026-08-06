import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PORTFOLIO_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "09_portfolio_holdings_clean.csv"
)

FUND_MASTER_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "01_fund_master_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "sector_allocation_donut.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading portfolio holdings...")

ph = pd.read_csv(PORTFOLIO_PATH)
fund_master = pd.read_csv(FUND_MASTER_PATH)

# ==========================================================
# Keep Equity Funds Only
# ==========================================================

ph = ph.merge(
    fund_master[
        ["amfi_code", "category"]
    ],
    on="amfi_code",
    how="left"
)

ph = ph[
    ph["category"] == "Equity"
]

print(f"Equity Funds : {ph['amfi_code'].nunique()}")
print(f"Holdings     : {len(ph)}")

# ==========================================================
# Aggregate Sector Allocation
# ==========================================================

sector_value = (
    ph.groupby("sector")["market_value_cr"]
      .sum()
      .sort_values(ascending=False)
)

sector_pct = (
    sector_value /
    sector_value.sum() * 100
).round(2)

# ==========================================================
# Plot Donut Chart
# ==========================================================

plt.figure(figsize=(9, 9))

colors = plt.cm.tab20.colors[:len(sector_pct)]

wedges, texts, autotexts = plt.pie(
    sector_pct,
    labels=sector_pct.index,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.82,
    colors=colors,
    wedgeprops=dict(
        width=0.4,
        edgecolor="white"
    )
)

for text in texts:
    text.set_fontsize(9)

for text in autotexts:
    text.set_fontsize(8)

# Center Label

plt.text(
    0,
    0,
    "Sector\nMix",
    ha="center",
    va="center",
    fontsize=15,
    fontweight="bold"
)

plt.title(
    f"Sector Allocation Across {ph['amfi_code'].nunique()} Equity Funds\n"
    f"Portfolio Date: {ph['portfolio_date'].iloc[0]}",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

# ==========================================================
# Save
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

print("\nSector allocation chart generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")

print("\nTop 5 Sectors")
print(sector_pct.head())

print(f"\nTotal Market Value : ₹{sector_value.sum():,.0f} Cr")