import pandas as pd
import os

# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# ============================================================
# Load Files
# ============================================================

cagr = pd.read_csv(
    os.path.join(DATA_DIR, "cagr_comparison_table.csv")
)

sharpe = pd.read_csv(
    os.path.join(DATA_DIR, "sharpe_ratio_ranking.csv")
)

alpha = pd.read_csv(
    os.path.join(DATA_DIR, "alpha_beta.csv")
)

drawdown = pd.read_csv(
    os.path.join(DATA_DIR, "max_drawdown_by_fund.csv")
)

performance = pd.read_csv(
    os.path.join(DATA_DIR, "07_scheme_performance_clean.csv")
)

# ============================================================
# Validation
# ============================================================

print("\nLoading data...\n")

print("CAGR rows      :", len(cagr))
print("Sharpe rows    :", len(sharpe))
print("Alpha rows     :", len(alpha))
print("Drawdown rows  :", len(drawdown))
print("Performance    :", len(performance))

# ============================================================
# Merge
# ============================================================

scorecard = (
    cagr[
        [
            "amfi_code",
            "scheme_name",
            "category",
            "cagr_3yr_pct",
        ]
    ]
    .merge(
        sharpe[
            [
                "amfi_code",
                "sharpe_ratio",
            ]
        ],
        on="amfi_code",
    )
    .merge(
        alpha[
            [
                "amfi_code",
                "alpha_annual",
            ]
        ],
        on="amfi_code",
    )
    .merge(
        drawdown[
            [
                "amfi_code",
                "max_drawdown_pct",
            ]
        ],
        on="amfi_code",
    )
    .merge(
        performance[
            [
                "amfi_code",
                "expense_ratio_pct",
            ]
        ],
        on="amfi_code",
    )
)

# ============================================================
# Missing Values
# ============================================================

print("\nMissing Values\n")
print(scorecard.isna().sum())

# ============================================================
# Ranking
# ============================================================

# Higher CAGR = Better
scorecard["rank_return"] = (
    scorecard["cagr_3yr_pct"]
    .rank(method="average", ascending=False, pct=True)
    * 100
)

# Higher Sharpe = Better
scorecard["rank_sharpe"] = (
    scorecard["sharpe_ratio"]
    .rank(method="average", ascending=False, pct=True)
    * 100
)

# Higher Alpha = Better
scorecard["rank_alpha"] = (
    scorecard["alpha_annual"]
    .rank(method="average", ascending=False, pct=True)
    * 100
)

# Lower Expense Ratio = Better
scorecard["rank_expense"] = (
    scorecard["expense_ratio_pct"]
    .rank(method="average", ascending=True, pct=True)
    * 100
)

# Smaller drawdown (closer to zero) = Better
scorecard["rank_drawdown"] = (
    scorecard["max_drawdown_pct"]
    .rank(method="average", ascending=False, pct=True)
    * 100
)

# ============================================================
# Composite Score (0-100)
# ============================================================

# ============================================================
# Composite Score (Weighted)
# ============================================================

scorecard["weighted_score"] = (
    scorecard["rank_return"] * 0.30
    + scorecard["rank_sharpe"] * 0.25
    + scorecard["rank_alpha"] * 0.20
    + scorecard["rank_expense"] * 0.15
    + scorecard["rank_drawdown"] * 0.10
)

# Normalize to 0-100
min_score = scorecard["weighted_score"].min()
max_score = scorecard["weighted_score"].max()

scorecard["fund_score"] = (
    (scorecard["weighted_score"] - min_score)
    / (max_score - min_score)
    * 100
).round(2)

# Remove intermediate column
scorecard.drop(columns="weighted_score", inplace=True)

# ============================================================
# Final Ranking
# ============================================================

scorecard = scorecard.sort_values(
    "fund_score",
    ascending=False,
).reset_index(drop=True)

scorecard.insert(
    0,
    "rank",
    range(1, len(scorecard) + 1),
)

# ============================================================
# Save
# ============================================================

OUTPUT = os.path.join(
    DATA_DIR,
    "fund_scorecard.csv",
)

scorecard.to_csv(
    OUTPUT,
    index=False,
)

# ============================================================
# Validation
# ============================================================

print("\nValidation")
print("-" * 50)

print("Rows :", len(scorecard))
print("Unique Funds :", scorecard["amfi_code"].nunique())

print(
    "\nFund Score Range :",
    round(scorecard["fund_score"].min(), 2),
    "to",
    round(scorecard["fund_score"].max(), 2),
)

print("\nTop 10 Funds\n")

print(
    scorecard[
        [
            "rank",
            "scheme_name",
            "fund_score",
            "cagr_3yr_pct",
            "sharpe_ratio",
            "alpha_annual",
            "expense_ratio_pct",
            "max_drawdown_pct",
        ]
    ].head(10)
)

print("\nSaved Successfully")
print(OUTPUT)