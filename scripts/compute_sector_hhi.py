"""
compute_sector_hhi.py
Day 6 — Sector Concentration Analysis (Herfindahl-Hirschman Index)

HHI = sum(sector_weight_pct^2), computed per fund on the 0–10,000 scale.

Thresholds:
    < 1,500       -> Low (Diversified)
    1,500–2,500   -> Moderate
    > 2,500       -> High (Concentrated)
"""

import pandas as pd

print("Loading datasets...")

# ============================================================
# 1. LOAD DATA
# ============================================================

holdings = pd.read_csv(
    "data/processed/09_portfolio_holdings_clean.csv"
)

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)

print(f"Holdings records loaded : {len(holdings):,}")
print(f"Funds in fund master    : {fund_master['amfi_code'].nunique():,}")


# ============================================================
# 2. FILTER EQUITY FUNDS
# ============================================================

equity_codes = fund_master.loc[
    fund_master["category"] == "Equity",
    "amfi_code"
]

holdings_equity = holdings[
    holdings["amfi_code"].isin(equity_codes)
].copy()

print(
    f"Equity funds with holdings: "
    f"{holdings_equity['amfi_code'].nunique():,}"
)


# ============================================================
# 3. AGGREGATE HOLDINGS BY SECTOR
#
# Multiple stocks belonging to the same sector are combined
# into one sector weight per fund.
# ============================================================

sector_weights = (
    holdings_equity
    .groupby(
        ["amfi_code", "sector"],
        as_index=False
    )["weight_pct"]
    .sum()
)

print(
    f"Fund-sector combinations: "
    f"{len(sector_weights):,}"
)


# ============================================================
# 4. CALCULATE SECTOR HHI
#
# HHI = Σ(weight_i²)
#
# Since weight_pct is expressed as percentage:
#
# Example:
# Sector A = 30%
# Sector B = 20%
# Sector C = 10%
#
# HHI = 30² + 20² + 10² = 1400
# ============================================================

hhi = (
    sector_weights
    .groupby("amfi_code")["weight_pct"]
    .apply(
        lambda weights: (weights ** 2).sum()
    )
    .reset_index()
    .rename(
        columns={
            "weight_pct": "sector_hhi"
        }
    )
)


# ============================================================
# 5. ADD FUND INFORMATION
# ============================================================

hhi = hhi.merge(
    fund_master[
        [
            "amfi_code",
            "scheme_name",
            "fund_house",
            "category",
            "sub_category"
        ]
    ],
    on="amfi_code",
    how="left"
)


# ============================================================
# 6. ENSURE ONLY EQUITY FUNDS
# ============================================================

hhi = hhi[
    hhi["category"] == "Equity"
].copy()


# ============================================================
# 7. CLASSIFY CONCENTRATION LEVEL
# ============================================================

def classify_hhi(hhi_value):

    if hhi_value < 1500:
        return "Low (Diversified)"

    elif hhi_value < 2500:
        return "Moderate"

    else:
        return "High (Concentrated)"


hhi["concentration_level"] = (
    hhi["sector_hhi"]
    .apply(classify_hhi)
)


# ============================================================
# 8. ROUND AND SORT
# ============================================================

hhi["sector_hhi"] = (
    hhi["sector_hhi"]
    .round(2)
)

hhi = (
    hhi
    .sort_values(
        "sector_hhi",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# 9. ADD RANK
# ============================================================

hhi.insert(
    0,
    "concentration_rank",
    range(1, len(hhi) + 1)
)


# ============================================================
# 10. FINAL COLUMN ORDER
# ============================================================

hhi = hhi[
    [
        "concentration_rank",
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "sector_hhi",
        "concentration_level"
    ]
]


# ============================================================
# 11. SAVE OUTPUT
# ============================================================

output_file = (
    "data/processed/sector_hhi.csv"
)

hhi.to_csv(
    output_file,
    index=False
)


# ============================================================
# 12. VALIDATION
# ============================================================

print("\nValidation")
print("-" * 60)

print(
    f"Equity funds analysed : {len(hhi):,}"
)

print(
    f"Unique funds          : "
    f"{hhi['amfi_code'].nunique():,}"
)

print(
    f"Missing HHI values    : "
    f"{hhi['sector_hhi'].isna().sum():,}"
)

print("\nConcentration Level Summary")
print("-" * 60)

print(
    hhi["concentration_level"]
    .value_counts()
    .to_string()
)


# ============================================================
# 13. TOP 10 MOST CONCENTRATED FUNDS
# ============================================================

print("\nTop 10 Most Concentrated Equity Funds")
print("-" * 90)

print(
    hhi[
        [
            "concentration_rank",
            "scheme_name",
            "sector_hhi",
            "concentration_level"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 14. TOP 10 MOST DIVERSIFIED FUNDS
# ============================================================

print("\nTop 10 Most Diversified Equity Funds")
print("-" * 90)

print(
    hhi[
        [
            "concentration_rank",
            "scheme_name",
            "sector_hhi",
            "concentration_level"
        ]
    ]
    .tail(10)
    .sort_values("sector_hhi")
    .to_string(index=False)
)


# ============================================================
# 15. FINAL MESSAGE
# ============================================================

print(
    f"\nSaved successfully -> {output_file}"
)

print(
    "\nTask 6 (Sector HHI Concentration) completed successfully."
)

print("\nDefinition:")
print(
    "HHI = sum of squared sector weights. "
    "Higher HHI indicates greater sector concentration."
)