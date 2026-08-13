import pandas as pd

print("Loading investor transactions...")

# ==================================================
# 1. LOAD DATA
# ==================================================

df = pd.read_csv(
    "data/processed/08_investor_transactions_clean.csv",
    parse_dates=["transaction_date"]
)

print(f"Total transactions loaded : {len(df):,}")
print(f"Unique investors          : {df['investor_id'].nunique():,}")


# ==================================================
# 2. KEEP ONLY SIP TRANSACTIONS
# ==================================================

sip_df = df[
    df["transaction_type"].str.upper() == "SIP"
].copy()

print(f"SIP transactions           : {len(sip_df):,}")


# ==================================================
# 3. SORT BY INVESTOR AND DATE
# ==================================================

sip_df = sip_df.sort_values(
    ["investor_id", "transaction_date"]
).copy()


# ==================================================
# 4. IDENTIFY INVESTORS WITH 6+ SIP TRANSACTIONS
# ==================================================

sip_counts = (
    sip_df
    .groupby("investor_id")
    .size()
)

eligible_investors = sip_counts[
    sip_counts >= 6
].index

sip_df = sip_df[
    sip_df["investor_id"].isin(eligible_investors)
].copy()

print(
    f"Investors with 6+ SIP transactions : "
    f"{len(eligible_investors):,}"
)


# ==================================================
# 5. CALCULATE GAP BETWEEN CONSECUTIVE SIP DATES
# ==================================================

sip_df["gap_days"] = (
    sip_df
    .groupby("investor_id")["transaction_date"]
    .diff()
    .dt.days
)


# ==================================================
# 6. AGGREGATE SIP CONTINUITY METRICS
# ==================================================

sip_continuity = (
    sip_df
    .groupby("investor_id")
    .agg(
        sip_txn_count=("transaction_date", "count"),

        avg_gap_days=("gap_days", "mean"),

        max_gap_days=("gap_days", "max"),

        first_sip_date=("transaction_date", "min"),

        last_sip_date=("transaction_date", "max")
    )
    .reset_index()
)


# ==================================================
# 7. FLAG AT-RISK INVESTORS
#
# Primary assignment interpretation:
# Any individual SIP gap > 35 days
# ==================================================

sip_continuity["at_risk"] = (
    sip_continuity["max_gap_days"] > 35
)


# Also provide average-gap flag for analysis
sip_continuity["avg_gap_at_risk"] = (
    sip_continuity["avg_gap_days"] > 35
)


# ==================================================
# 8. ROUND VALUES
# ==================================================

sip_continuity["avg_gap_days"] = (
    sip_continuity["avg_gap_days"]
    .round(1)
)


sip_continuity["max_gap_days"] = (
    sip_continuity["max_gap_days"]
    .round(1)
)


# ==================================================
# 9. CALCULATE SUMMARY METRICS
# ==================================================

total_eligible = len(sip_continuity)

at_risk_count = (
    sip_continuity["at_risk"].sum()
)

at_risk_percentage = (
    at_risk_count / total_eligible * 100
    if total_eligible > 0
    else 0
)

avg_gap_overall = (
    sip_continuity["avg_gap_days"].mean()
    if total_eligible > 0
    else 0
)


# ==================================================
# 10. PRINT VALIDATION
# ==================================================

print("\nSIP Continuity Validation")
print("-" * 55)

print(
    f"Investors with 6+ SIPs : "
    f"{total_eligible:,}"
)

print(
    f"At-risk investors      : "
    f"{at_risk_count:,}"
)

print(
    f"At-risk percentage     : "
    f"{at_risk_percentage:.1f}%"
)

print(
    f"Average SIP gap        : "
    f"{avg_gap_overall:.1f} days"
)


# ==================================================
# 11. TOP 10 MOST AT-RISK INVESTORS
# ==================================================

print("\nTop 10 Investors by Maximum SIP Gap")
print("-" * 75)

print(
    sip_continuity
    .sort_values(
        "max_gap_days",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ==================================================
# 12. TOP 10 BY AVERAGE GAP
# ==================================================

print("\nTop 10 Investors by Average SIP Gap")
print("-" * 75)

print(
    sip_continuity
    .sort_values(
        "avg_gap_days",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ==================================================
# 13. SAVE OUTPUT
# ==================================================

output_file = (
    "data/processed/sip_continuity.csv"
)

sip_continuity.to_csv(
    output_file,
    index=False
)

print(
    f"\nSaved successfully -> {output_file}"
)


# ==================================================
# 14. TASK COMPLETION
# ==================================================

print("\nTask 4 (SIP Continuity Analysis) completed successfully.")

print("\nDefinitions:")
print(
    "Eligible investor = investor with at least 6 SIP transactions."
)

print(
    "Average gap = mean number of days between consecutive SIP transactions."
)

print(
    "Maximum gap = longest number of days between consecutive SIP transactions."
)

print(
    "At-risk = investor with at least one SIP gap greater than 35 days."
)