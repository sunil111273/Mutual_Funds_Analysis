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
    "08_investor_transactions_clean.csv"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    REPORT_DIR,
    "investor_demographics.png"
)

# ==========================================================
# Load Data
# ==========================================================

print("Loading investor transaction dataset...")

txn = pd.read_csv(DATA_PATH)

print(f"Transactions : {len(txn):,}")
print(f"Unique Investors : {txn['investor_id'].nunique():,}")

# ==========================================================
# Unique Investors (for demographics)
# ==========================================================

investor_age = (
    txn.drop_duplicates("investor_id")
       [["investor_id", "age_group"]]
)

investor_gender = (
    txn.drop_duplicates("investor_id")
       [["investor_id", "gender"]]
)

age_counts = investor_age["age_group"].value_counts()

age_order = [
    "18-25",
    "26-35",
    "36-45",
    "46-55",
    "56+"
]

age_counts = age_counts.reindex(age_order)

gender_counts = investor_gender["gender"].value_counts()

# ==========================================================
# SIP Transactions Only
# ==========================================================

sip_only = txn[
    txn["transaction_type"] == "SIP"
]

# ==========================================================
# Plot
# ==========================================================

sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(
    1,
    3,
    figsize=(20, 6)
)

# ==========================================================
# Age Group Pie Chart
# ==========================================================

axes[0].pie(
    age_counts,
    labels=age_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=sns.color_palette("Set2", len(age_counts)),
    wedgeprops=dict(
        edgecolor="white",
        linewidth=1.5
    )
)

axes[0].set_title(
    "Investor Age Group Distribution",
    fontsize=14,
    fontweight="bold"
)

# ==========================================================
# SIP Box Plot
# ==========================================================

sns.boxplot(
    data=sip_only,
    x="age_group",
    y="amount_inr",
    order=age_order,
    palette="Set2",
    showfliers=False,
    ax=axes[1]
)

axes[1].set_title(
    "SIP Amount Distribution by Age Group",
    fontsize=14,
    fontweight="bold"
)

axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("SIP Amount (₹)")

axes[1].ticklabel_format(
    style="plain",
    axis="y"
)

# ==========================================================
# Gender Pie Chart
# ==========================================================

axes[2].pie(
    gender_counts,
    labels=gender_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#4C72B0", "#DD8452"],
    wedgeprops=dict(
        edgecolor="white",
        linewidth=1.5
    )
)

axes[2].set_title(
    "Investor Gender Distribution",
    fontsize=14,
    fontweight="bold"
)

# ==========================================================
# Save
# ==========================================================

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nInvestor demographics chart generated successfully.")
print(f"Saved to: {OUTPUT_FILE}")

# ==========================================================
# Summary Statistics
# ==========================================================

print("\nAge Group Distribution")
print(age_counts)

print("\nGender Distribution")
print(gender_counts)

print("\nSIP Amount Statistics")
print(
    sip_only["amount_inr"].describe().round(2)
)