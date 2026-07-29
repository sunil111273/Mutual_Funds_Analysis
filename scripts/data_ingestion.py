"""
data_ingestion.py
Bluestock Mutual Fund Analytics Capstone -- Day 1

This script covers three Day 1 tasks from the project brief:

    Task 3 - Load all 10 raw CSVs, print shape / dtypes / head() for each,
              and note any basic anomalies (nulls, duplicate rows).
    Task 6 - Explore fund_master: print unique fund houses, categories,
              sub-categories and risk grades. Look at how an AMFI code
              identifies a scheme.
    Task 7 - Validate that every AMFI code in fund_master also exists in
              nav_history, and write a short data quality summary.

How to run:
    python3 scripts/data_ingestion.py

Output:
    Everything is printed to the console, and a short summary is also
    saved to reports/data_quality_report.txt
"""

import pathlib
import pandas as pd

# project_root/scripts/data_ingestion.py -> project_root
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
REPORT_PATH = BASE_DIR / "reports" / "data_quality_report.txt"

# The 10 raw files provided for this project
RAW_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "macro_factors": "10_macro_factors.csv",
}


def load_all_datasets():
    """Task 3: load every raw CSV, print a quick sanity check for each one."""
    datasets = {}

    print("=" * 70)
    print("TASK 3 - Loading all 10 raw datasets")
    print("=" * 70)

    for name, filename in RAW_FILES.items():
        path = RAW_DIR / filename
        df = pd.read_csv(path)
        datasets[name] = df

        print(f"\n--- {filename}  ->  '{name}' ---")
        print(f"shape: {df.shape}")
        print("dtypes:")
        print(df.dtypes)
        print("head:")
        print(df.head(3))

        # Basic anomaly checks: missing values and duplicate rows.
        null_counts = df.isnull().sum()
        nulls_found = null_counts[null_counts > 0]
        duplicate_rows = df.duplicated().sum()

        if len(nulls_found) > 0:
            print(f"anomaly check: null values found ->\n{nulls_found}")
        else:
            print("anomaly check: no null values found")

        if duplicate_rows > 0:
            print(f"anomaly check: {duplicate_rows} duplicate rows found")
        else:
            print("anomaly check: no duplicate rows found")

    return datasets


def summarise_fund_master(fund_master):
    """Task 6: unique fund houses, categories, sub-categories, risk grades."""
    lines = []
    lines.append("=" * 70)
    lines.append("TASK 6 - Fund Master Summary")
    lines.append("=" * 70)

    lines.append(f"Unique fund houses ({fund_master['fund_house'].nunique()}):")
    lines.append(f"  {sorted(fund_master['fund_house'].unique().tolist())}")

    lines.append(f"Unique categories ({fund_master['category'].nunique()}):")
    lines.append(f"  {sorted(fund_master['category'].unique().tolist())}")

    lines.append(f"Unique sub-categories ({fund_master['sub_category'].nunique()}):")
    lines.append(f"  {sorted(fund_master['sub_category'].unique().tolist())}")

    lines.append(f"Unique risk categories ({fund_master['risk_category'].nunique()}):")
    lines.append(f"  {sorted(fund_master['risk_category'].unique().tolist())}")

    # A quick look at the AMFI scheme code structure: each row's amfi_code
    # is simply a unique numeric ID that AMFI assigns to one specific scheme.
    lines.append("\nAMFI scheme code structure (sample of 3 rows):")
    sample = fund_master[["amfi_code", "scheme_name", "fund_house"]].head(3)
    lines.append(sample.to_string(index=False))
    lines.append("Each amfi_code is a unique numeric ID assigned by AMFI to one scheme.")

    text = "\n".join(lines)
    print("\n" + text)
    return text


def validate_amfi_codes(fund_master, nav_history):
    """Task 7: confirm every AMFI code in fund_master exists in nav_history."""
    lines = []
    lines.append("=" * 70)
    lines.append("TASK 7 - AMFI Code Validation (fund_master vs nav_history)")
    lines.append("=" * 70)

    master_codes = set(fund_master["amfi_code"].unique())
    nav_codes = set(nav_history["amfi_code"].unique())
    missing_codes = master_codes - nav_codes

    lines.append(f"fund_master has {len(master_codes)} unique AMFI codes.")
    lines.append(f"nav_history has {len(nav_codes)} unique AMFI codes.")

    if not missing_codes:
        lines.append("RESULT: PASS - every AMFI code in fund_master exists in nav_history.")
    else:
        lines.append(f"RESULT: FAIL - {len(missing_codes)} codes are missing from nav_history:")
        lines.append(f"  {sorted(missing_codes)}")

    text = "\n".join(lines)
    print("\n" + text)
    return text


def main():
    datasets = load_all_datasets()
    fund_summary = summarise_fund_master(datasets["fund_master"])
    validation_report = validate_amfi_codes(datasets["fund_master"], datasets["nav_history"])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("BLUESTOCK MF CAPSTONE - DAY 1 DATA QUALITY REPORT\n")
        f.write("Generated by scripts/data_ingestion.py\n\n")
        f.write(fund_summary + "\n\n")
        f.write(validation_report + "\n")

    print(f"\nData quality report saved to: {REPORT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
