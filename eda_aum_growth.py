import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AUM_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "03_aum_by_fund_house_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(REPORT_DIR, "aum_growth_by_fund_house.png")

# ==========================================================
# Load Data
# ==========================================================

print("Loading AUM dataset...")

aum = pd.read_csv(
    AUM_PATH,
    parse_dates=["date"]
)

aum["year"] = aum["date"].dt.year

print(f"Records loaded : {len(aum):,}")

# ==========================================================
# Year-end AUM (last available record of each year)
# ==========================================================

year_end = (
    aum.sort_values("date")
       .groupby(["fund_house", "year"], as_index=False)
       .last()
)

# Keep only required years
year_end = year_end[
    year_end["year"].between(2022, 2025)
]

# ==========================================================
# Plot
# ==========================================================

sns.set_theme(style="whitegrid")

plt.figure(figsize=(15, 8))

ax = sns.barplot(
    data=year_end,
    x="year",
    y="aum_lakh_crore",
    hue="fund_house",
    estimator="mean",
    errorbar=None,
)

# ==========================================================
# Highlight SBI Mutual Fund
# ==========================================================

legend = ax.get_legend()
labels = [t.get_text() for t in legend.texts]

sbi_index = labels.index("SBI Mutual Fund")

num_years = year_end["year"].nunique()

# seaborn creates bars grouped by hue
for i in range(num_years):
    patch = ax.patches[sbi_index * num_years + i]
    patch.set_edgecolor("black")
    patch.set_linewidth(2.5)
    patch.set_alpha(1)

# ==========================================================
# Annotate SBI 2025
# ==========================================================

peak = year_end[
    (year_end["fund_house"] == "SBI Mutual Fund") &
    (year_end["year"] == 2025)
].iloc[0]

# Find the actual SBI-2025 bar
target_patch = ax.patches[sbi_index * num_years + (num_years - 1)]

x = target_patch.get_x() + target_patch.get_width() / 2
y = target_patch.get_height()

ax.annotate(
    f"₹{peak['aum_lakh_crore']:.1f} L Cr\nMarket Leader",
    xy=(x, y),
    xytext=(x + 0.25, y + 1.2),
    fontsize=10,
    fontweight="bold",
    color="red",
    arrowprops=dict(
        arrowstyle="->",
        color="red",
        lw=2
    ),
)

# ==========================================================
# Formatting
# ==========================================================

ax.set_title(
    "AUM Growth by Fund House (Year-End Snapshot, 2022–2025)",
    fontsize=16,
    fontweight="bold"
)

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("AUM (₹ Lakh Crore)", fontsize=12)

ax.legend(
    title="Fund House",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=8
)

plt.tight_layout()

# ==========================================================
# Save & Show
# ==========================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nAUM chart generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")