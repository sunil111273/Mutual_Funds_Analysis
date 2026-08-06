import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "05_category_inflows_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "category_inflow_heatmap.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading category inflow dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Records Loaded : {len(df)}")
print(f"Categories     : {df['category'].nunique()}")
print(f"Months         : {df['month'].nunique()}")

# ==========================================================
# Pivot Table
# ==========================================================

pivot = df.pivot(
    index="category",
    columns="month",
    values="net_inflow_crore"
)

# Sort categories by total inflow
pivot = pivot.loc[
    pivot.sum(axis=1)
         .sort_values(ascending=False)
         .index
]

# ==========================================================
# Plot
# ==========================================================

sns.set_theme(style="white")

plt.figure(figsize=(15, 8))

ax = sns.heatmap(
    pivot,
    cmap="YlOrRd",
    annot=True,
    fmt=".0f",
    linewidths=0.5,
    linecolor="white",
    cbar_kws={
        "label": "Net Inflow (₹ Crore)"
    }
)

# ==========================================================
# Formatting
# ==========================================================

ax.set_title(
    "Category-wise Net Inflows (Apr 2024 – Mar 2025)",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel(
    "Month",
    fontsize=12
)

ax.set_ylabel(
    "Fund Category",
    fontsize=12
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.yticks(
    rotation=0
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

print("\nCategory inflow heatmap generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")

# ==========================================================
# Validation
# ==========================================================

peak = df.loc[df["net_inflow_crore"].idxmax()]

print("\nHighest Monthly Inflow")
print("----------------------")
print(f"Category : {peak['category']}")
print(f"Month    : {peak['month']}")
print(f"Inflow   : ₹{peak['net_inflow_crore']:,} Cr")

print(f"\nHeatmap Shape : {pivot.shape}")
print(f"Missing Values: {pivot.isna().sum().sum()}")