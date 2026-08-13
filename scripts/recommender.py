import pandas as pd

print("Loading datasets...")

# ============================================================
# 1. LOAD DATA
# ============================================================

fund_master = pd.read_csv(
    "data/processed/01_fund_master_clean.csv"
)

scheme_perf = pd.read_csv(
    "data/processed/07_scheme_performance_clean.csv"
)

print(f"Fund Master Records      : {len(fund_master):,}")
print(f"Performance Records      : {len(scheme_perf):,}")


# ============================================================
# 2. RISK APPETITE MAPPING
#
# Dataset contains 5 risk grades:
# Low, Moderate, Moderately High, High, Very High
#
# User input is simplified into:
# Low, Moderate, High
# ============================================================

RISK_MAP = {
    "Low": [
        "Low",
        "Moderate"
    ],

    "Moderate": [
        "Moderate",
        "Moderately High"
    ],

    "High": [
        "Moderately High",
        "High",
        "Very High"
    ]
}


# ============================================================
# 3. RECOMMENDATION FUNCTION
# ============================================================

def recommend_funds(
    risk_appetite: str,
    top_n: int = 3
) -> pd.DataFrame:

    # Clean user input
    risk_appetite = (
        str(risk_appetite)
        .strip()
        .title()
    )

    # Validate risk appetite
    if risk_appetite not in RISK_MAP:
        raise ValueError(
            "Invalid risk appetite. "
            "Choose: Low, Moderate, or High."
        )

    # Validate number of recommendations
    if top_n <= 0:
        raise ValueError(
            "top_n must be greater than 0."
        )

    # --------------------------------------------------------
    # Get matching risk grades
    # --------------------------------------------------------

    matching_grades = RISK_MAP[risk_appetite]

    # --------------------------------------------------------
    # Filter funds by risk grade
    # --------------------------------------------------------

    candidates = scheme_perf[
        scheme_perf["risk_grade"]
        .isin(matching_grades)
    ].copy()

    # --------------------------------------------------------
    # Remove invalid/anomalous records if available
    # --------------------------------------------------------

    if "anomaly_flag" in candidates.columns:

        candidates = candidates[
            candidates["anomaly_flag"] != True
        ].copy()

    # --------------------------------------------------------
    # Remove records with missing Sharpe ratio
    # --------------------------------------------------------

    candidates = candidates.dropna(
        subset=["sharpe_ratio"]
    )

    # --------------------------------------------------------
    # Rank funds by Sharpe ratio
    # Highest Sharpe = best risk-adjusted performance
    # --------------------------------------------------------

    candidates = candidates.sort_values(
        "sharpe_ratio",
        ascending=False
    )

    # Select top N
    top_funds = candidates.head(top_n).copy()

    # --------------------------------------------------------
    # Add fund master information
    # --------------------------------------------------------

    master_columns = [
        "amfi_code",
        "category",
        "sub_category",
        "plan",
        "expense_ratio_pct"
    ]

    # Only use columns that actually exist
    master_columns = [
        col for col in master_columns
        if col in fund_master.columns
    ]

    result = top_funds.merge(
        fund_master[
            ["amfi_code"] + master_columns
            if "amfi_code" not in master_columns
            else master_columns
        ],
        on="amfi_code",
        how="left",
        suffixes=("", "_master")
    )

    # --------------------------------------------------------
    # Select output columns
    # --------------------------------------------------------

    desired_columns = [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "risk_grade",
        "sharpe_ratio",
        "sortino_ratio",
        "return_3yr_pct",
        "return_5yr_pct",
        "expense_ratio_pct",
        "morningstar_rating"
    ]

    # Keep only columns that exist
    output_columns = [
        col for col in desired_columns
        if col in result.columns
    ]

    result = result[
        output_columns
    ].reset_index(drop=True)

    # Add recommendation rank
    result.insert(
        0,
        "recommendation_rank",
        range(1, len(result) + 1)
    )

    return result


# ============================================================
# 4. PRINT RECOMMENDATIONS
# ============================================================

def print_recommendation(
    risk_appetite: str,
    top_n: int = 3
):

    recommendations = recommend_funds(
        risk_appetite,
        top_n
    )

    print()
    print("=" * 110)
    print(
        f"TOP {top_n} FUND RECOMMENDATIONS"
    )
    print(
        f"Risk Appetite: {risk_appetite}"
    )
    print("=" * 110)

    if recommendations.empty:

        print(
            "No matching funds found."
        )

        return

    # Format display
    display_df = recommendations.copy()

    if "sharpe_ratio" in display_df.columns:
        display_df["sharpe_ratio"] = (
            display_df["sharpe_ratio"]
            .map(lambda x: f"{x:.2f}")
        )

    if "sortino_ratio" in display_df.columns:
        display_df["sortino_ratio"] = (
            display_df["sortino_ratio"]
            .map(lambda x: f"{x:.2f}")
        )

    if "return_3yr_pct" in display_df.columns:
        display_df["return_3yr_pct"] = (
            display_df["return_3yr_pct"]
            .map(lambda x: f"{x:.2f}%")
        )

    if "return_5yr_pct" in display_df.columns:
        display_df["return_5yr_pct"] = (
            display_df["return_5yr_pct"]
            .map(lambda x: f"{x:.2f}%")
        )

    if "expense_ratio_pct" in display_df.columns:
        display_df["expense_ratio_pct"] = (
            display_df["expense_ratio_pct"]
            .map(lambda x: f"{x:.2f}%")
        )

    print(
        display_df.to_string(
            index=False
        )
    )


# ============================================================
# 5. RUN RECOMMENDER FOR ALL RISK APPETITES
# ============================================================

if __name__ == "__main__":

    print("\nFund Recommender")
    print("=" * 110)

    for appetite in [
        "Low",
        "Moderate",
        "High"
    ]:

        print_recommendation(
            appetite,
            top_n=3
        )


# ============================================================
# 6. EXAMPLE OF SINGLE USER INPUT
# ============================================================

# Uncomment the following lines if you want
# the user to enter their own risk appetite.
#
# user_risk = input(
#     "\nEnter risk appetite (Low / Moderate / High): "
# )
#
# print_recommendation(
#     user_risk,
#     top_n=3
# )


print(
    "\nTask 5 (Simple Fund Recommender) completed successfully."
)