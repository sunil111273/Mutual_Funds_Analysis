import pandas as pd
import numpy as np

print("Loading datasets...")

# ==================================================
# 1. LOAD DATA
# ==================================================

tx = pd.read_csv(
    "data/processed/08_investor_transactions_clean.csv",
    parse_dates=["transaction_date"]
)

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)[[
    "amfi_code",
    "scheme_name",
    "fund_house",
    "category",
    "sub_category"
]]

print(f"Transactions Loaded : {len(tx):,}")
print(f"Unique Investors    : {tx['investor_id'].nunique():,}")


# ==================================================
# 2. DETERMINE INVESTOR COHORT
# Cohort = year of investor's FIRST transaction
# ==================================================

first_transaction = (
    tx.groupby("investor_id")["transaction_date"]
    .min()
    .reset_index()
)

first_transaction = first_transaction.rename(
    columns={
        "transaction_date": "first_transaction_date"
    }
)

first_transaction["cohort_year"] = (
    first_transaction["first_transaction_date"]
    .dt.year
)

# Add cohort year to every transaction
tx = tx.merge(
    first_transaction[
        ["investor_id", "first_transaction_date", "cohort_year"]
    ],
    on="investor_id",
    how="left"
)

print("\nInvestors by Cohort")
print("-" * 50)

cohort_counts = (
    first_transaction["cohort_year"]
    .value_counts()
    .sort_index()
)

print(cohort_counts.to_string())


# ==================================================
# 3. ADD FUND DETAILS
# ==================================================

tx = tx.merge(
    fund_master,
    on="amfi_code",
    how="left"
)

# Check for unmatched funds
unmatched_funds = tx["scheme_name"].isna().sum()

print(f"\nTransactions with missing fund details: {unmatched_funds:,}")


# ==================================================
# 4. AVERAGE SIP AMOUNT PER COHORT
# Only SIP transactions are considered
# ==================================================

sip_tx = tx[
    tx["transaction_type"].str.upper() == "SIP"
].copy()

avg_sip_amount = (
    sip_tx
    .groupby("cohort_year")["amount_inr"]
    .mean()
    .rename("avg_sip_amount_inr")
)


# ==================================================
# 5. TOTAL INVESTED PER COHORT
#
# Invested capital =
# SIP + Lumpsum
#
# Redemptions are excluded.
# ==================================================

invested_tx = tx[
    tx["transaction_type"].str.upper().isin(
        ["SIP", "LUMPSUM"]
    )
].copy()

total_invested = (
    invested_tx
    .groupby("cohort_year")["amount_inr"]
    .sum()
    .rename("total_invested_inr")
)


# ==================================================
# 6. AVERAGE INVESTMENT PER INVESTOR
# Additional useful metric for advanced insights
# ==================================================

avg_invested_per_investor = (
    invested_tx
    .groupby("cohort_year")
    .agg(
        total_amount=("amount_inr", "sum"),
        investors=("investor_id", "nunique")
    )
)

avg_invested_per_investor[
    "avg_invested_per_investor_inr"
] = (
    avg_invested_per_investor["total_amount"]
    / avg_invested_per_investor["investors"]
)

avg_invested_per_investor = (
    avg_invested_per_investor[
        "avg_invested_per_investor_inr"
    ]
    .rename("avg_invested_per_investor_inr")
)


# ==================================================
# 7. TOP FUND PREFERENCE PER COHORT
#
# Preference is measured using total invested amount
# (SIP + Lumpsum)
# ==================================================

fund_cohort_amount = (
    invested_tx
    .groupby(
        [
            "cohort_year",
            "scheme_name",
            "fund_house"
        ]
    )["amount_inr"]
    .sum()
    .reset_index()
)

# Sort within each cohort
fund_cohort_amount = fund_cohort_amount.sort_values(
    ["cohort_year", "amount_inr"],
    ascending=[True, False]
)

# Select highest-invested fund for each cohort
top_fund = (
    fund_cohort_amount
    .drop_duplicates(
        subset=["cohort_year"],
        keep="first"
    )
    .rename(
        columns={
            "scheme_name": "top_fund_scheme",
            "fund_house": "top_fund_house",
            "amount_inr": "top_fund_invested_inr"
        }
    )
    [[
        "cohort_year",
        "top_fund_scheme",
        "top_fund_house",
        "top_fund_invested_inr"
    ]]
)


# ==================================================
# 8. TOP CATEGORY PREFERENCE
# Additional useful metric
# ==================================================

category_cohort_amount = (
    invested_tx
    .groupby(
        ["cohort_year", "category"]
    )["amount_inr"]
    .sum()
    .reset_index()
)

category_cohort_amount = category_cohort_amount.sort_values(
    ["cohort_year", "amount_inr"],
    ascending=[True, False]
)

top_category = (
    category_cohort_amount
    .drop_duplicates(
        subset=["cohort_year"],
        keep="first"
    )
    .rename(
        columns={
            "category": "top_category",
            "amount_inr": "top_category_invested_inr"
        }
    )
    [[
        "cohort_year",
        "top_category",
        "top_category_invested_inr"
    ]]
)


# ==================================================
# 9. COHORT SIZE
# ==================================================

cohort_size = (
    first_transaction
    .groupby("cohort_year")["investor_id"]
    .nunique()
    .rename("cohort_investors")
)


# ==================================================
# 10. TRANSACTION COUNT
# Additional context metric
# ==================================================

transaction_count = (
    tx
    .groupby("cohort_year")
    .size()
    .rename("total_transactions")
)


# ==================================================
# 11. SIP TRANSACTION COUNT
# Additional useful metric
# ==================================================

sip_transaction_count = (
    sip_tx
    .groupby("cohort_year")
    .size()
    .rename("total_sip_transactions")
)


# ==================================================
# 12. COMBINE ALL COHORT METRICS
# ==================================================

cohort_analysis = pd.concat(
    [
        cohort_size,
        transaction_count,
        sip_transaction_count,
        avg_sip_amount,
        total_invested,
        avg_invested_per_investor
    ],
    axis=1
).reset_index()


# Add top fund information
cohort_analysis = cohort_analysis.merge(
    top_fund,
    on="cohort_year",
    how="left"
)

# Add top category information
cohort_analysis = cohort_analysis.merge(
    top_category,
    on="cohort_year",
    how="left"
)


# ==================================================
# 13. CLEAN / ROUND NUMERIC VALUES
# ==================================================

numeric_columns = [
    "avg_sip_amount_inr",
    "total_invested_inr",
    "avg_invested_per_investor_inr",
    "top_fund_invested_inr",
    "top_category_invested_inr"
]

for column in numeric_columns:
    cohort_analysis[column] = (
        cohort_analysis[column]
        .round(2)
    )


cohort_analysis = (
    cohort_analysis
    .sort_values("cohort_year")
    .reset_index(drop=True)
)


# ==================================================
# 14. SAVE OUTPUT
# ==================================================

output_file = (
    "data/processed/cohort_analysis.csv"
)

cohort_analysis.to_csv(
    output_file,
    index=False
)


# ==================================================
# 15. VALIDATION
# ==================================================

print("\nValidation")
print("-" * 50)

print(
    f"Cohorts Identified       : "
    f"{len(cohort_analysis)}"
)

print(
    f"Total Investors Covered : "
    f"{cohort_analysis['cohort_investors'].sum():,}"
)

print(
    f"Unique Investors Check   : "
    f"{tx['investor_id'].nunique():,}"
)

print(
    f"Total SIP Transactions   : "
    f"{len(sip_tx):,}"
)

print(
    f"Total Invested           : "
    f"₹{invested_tx['amount_inr'].sum():,.2f}"
)


# ==================================================
# 16. DISPLAY FINAL COHORT ANALYSIS
# ==================================================

print("\nInvestor Cohort Analysis")
print("=" * 100)

display_columns = [
    "cohort_year",
    "cohort_investors",
    "avg_sip_amount_inr",
    "total_invested_inr",
    "avg_invested_per_investor_inr",
    "top_category",
    "top_fund_scheme"
]

print(
    cohort_analysis[
        display_columns
    ].to_string(index=False)
)


# ==================================================
# 17. FINDINGS FOR TASK 7
# ==================================================

largest_cohort = cohort_analysis.loc[
    cohort_analysis["cohort_investors"].idxmax()
]

highest_invested_cohort = cohort_analysis.loc[
    cohort_analysis["total_invested_inr"].idxmax()
]

highest_avg_sip_cohort = cohort_analysis.loc[
    cohort_analysis["avg_sip_amount_inr"].idxmax()
]

print("\nKey Cohort Findings")
print("=" * 50)

print(
    f"Largest cohort: "
    f"{int(largest_cohort['cohort_year'])} "
    f"({int(largest_cohort['cohort_investors']):,} investors)"
)

print(
    f"Highest total investment cohort: "
    f"{int(highest_invested_cohort['cohort_year'])} "
    f"(₹{highest_invested_cohort['total_invested_inr']:,.2f})"
)

print(
    f"Highest average SIP cohort: "
    f"{int(highest_avg_sip_cohort['cohort_year'])} "
    f"(₹{highest_avg_sip_cohort['avg_sip_amount_inr']:,.2f})"
)


# ==================================================
# 18. FINAL MESSAGE
# ==================================================

print(
    f"\nSaved successfully -> {output_file}"
)

print("\nTask 3 (Investor Cohort Analysis) completed successfully.")

print("\nDefinitions:")
print(
    "Cohort = calendar year of an investor's first transaction."
)
print(
    "Average SIP amount = mean amount of SIP transactions."
)
print(
    "Total invested = SIP + Lumpsum; Redemptions excluded."
)
print(
    "Top fund preference = fund with highest invested amount "
    "within each cohort."
)