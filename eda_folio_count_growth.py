import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "06_industry_folio_count_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "folio_count_growth.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading folio count dataset...")

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["month"]
)

df = df.sort_values("month")

print(f"Records Loaded : {len(df)}")

# ==========================================================
# Start / End Values
# ==========================================================

start = df.iloc[0]
end = df.iloc[-1]

growth_pct = (
    (end["total_folios_crore"] / start["total_folios_crore"] - 1)
    * 100
)

# ==========================================================
# Plot
# ==========================================================

plt.figure(figsize=(13, 6))

plt.plot(
    df["month"],
    df["total_folios_crore"],
    marker="o",
    markersize=5,
    linewidth=2.5,
    color="#1f77b4",
    label="Total Folios"
)

# ==========================================================
# Milestones
# ==========================================================

milestones = [15, 20, 25]

for milestone in milestones:

    crossing = df[
        df["total_folios_crore"] >= milestone
    ].iloc[0]

    plt.scatter(
        crossing["month"],
        crossing["total_folios_crore"],
        color="crimson",
        s=90,
        zorder=5
    )

    plt.annotate(
        f"{milestone} Cr\n{crossing['month'].strftime('%b %Y')}",
        xy=(
            crossing["month"],
            crossing["total_folios_crore"]
        ),
        xytext=(10, 15),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        color="crimson",
        arrowprops=dict(
            arrowstyle="->",
            color="crimson",
            lw=1.5
        )
    )

# ==========================================================
# Start / End Labels
# ==========================================================

plt.annotate(
    f"{start['total_folios_crore']:.2f} Cr\nJan 2022",
    xy=(
        start["month"],
        start["total_folios_crore"]
    ),
    xytext=(-20, -35),
    textcoords="offset points",
    fontsize=9,
    fontweight="bold",
    ha="right"
)

plt.annotate(
    f"{end['total_folios_crore']:.2f} Cr\nDec 2025",
    xy=(
        end["month"],
        end["total_folios_crore"]
    ),
    xytext=(-10, 15),
    textcoords="offset points",
    fontsize=9,
    fontweight="bold",
    color="#1f77b4",
    ha="right"
)

# ==========================================================
# Formatting
# ==========================================================

plt.title(
    f"Industry Folio Count Growth (Jan 2022 – Dec 2025)\n"
    f"Overall Growth: {growth_pct:.0f}%",
    fontsize=15,
    fontweight="bold"
)

plt.xlabel("Month")
plt.ylabel("Total Folios (Crore)")

plt.grid(alpha=0.3)

plt.legend()

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

print("\nFolio count growth chart generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")

print("\nGrowth Summary")
print("----------------")
print(
    f"Start : {start['total_folios_crore']:.2f} Cr "
    f"({start['month'].strftime('%b %Y')})"
)

print(
    f"End   : {end['total_folios_crore']:.2f} Cr "
    f"({end['month'].strftime('%b %Y')})"
)

print(f"Growth: {growth_pct:.1f}%")