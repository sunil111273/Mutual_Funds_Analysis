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
    "08_investor_transactions_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

BAR_OUTPUT = os.path.join(
    REPORT_DIR,
    "sip_amount_by_state.png"
)

PIE_OUTPUT = os.path.join(
    REPORT_DIR,
    "t30_vs_b30_distribution.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading investor transaction dataset...")

txn = pd.read_csv(DATA_PATH)

# ==========================================================
# SIP Transactions Only
# ==========================================================

sip = txn[
    txn["transaction_type"] == "SIP"
]

print(f"SIP Transactions : {len(sip):,}")

# ==========================================================
# Chart 1 : SIP Amount by State
# ==========================================================

sip_by_state = (
    sip.groupby("state", as_index=False)["amount_inr"]
       .sum()
       .sort_values("amount_inr")
)

sip_by_state["amount_cr"] = (
    sip_by_state["amount_inr"] / 1e7
)

fig, ax = plt.subplots(figsize=(11, 7))

bars = ax.barh(
    sip_by_state["state"],
    sip_by_state["amount_cr"],
    color="#2a7fba"
)

# Highlight highest state

top_bar = bars[-1]
top_bar.set_color("crimson")

for bar in bars:
    width = bar.get_width()

    ax.text(
        width + 0.2,
        bar.get_y() + bar.get_height()/2,
        f"₹{width:.1f} Cr",
        va="center",
        fontsize=9
    )

ax.set_title(
    "SIP Amount by State",
    fontsize=15,
    fontweight="bold"
)

ax.set_xlabel("SIP Amount (₹ Crore)")
ax.set_ylabel("")

plt.tight_layout()

plt.savefig(
    BAR_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================================
# Chart 2 : T30 vs B30
# ==========================================================

tier_totals = (
    sip.groupby("city_tier")["amount_inr"]
       .sum()
)

tier_cr = tier_totals / 1e7

fig, ax = plt.subplots(figsize=(7, 7))

colors = {
    "T30": "#2a7fba",
    "B30": "#f2a900"
}

ax.pie(
    tier_cr.values,
    labels=[
        f"{tier}\n₹{tier_cr[tier]:.1f} Cr"
        for tier in tier_cr.index
    ],
    autopct="%1.1f%%",
    startangle=90,
    colors=[colors[t] for t in tier_cr.index],
    explode=[0.04] * len(tier_cr),
    wedgeprops=dict(
        edgecolor="white",
        linewidth=1.5
    )
)

ax.set_title(
    "SIP Investment Distribution\nT30 vs B30 Cities",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    PIE_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================================
# Summary
# ==========================================================

print("\nState-wise SIP Amount")
print(sip_by_state[["state", "amount_cr"]])

print("\nCity Tier Distribution")
print(tier_cr.round(2))

print("\nCharts saved successfully.")
print(BAR_OUTPUT)
print(PIE_OUTPUT)