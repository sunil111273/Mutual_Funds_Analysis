import os
import pandas as pd
from sqlalchemy import create_engine, text

# ----------------------------------------------------
# Database Connection
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "mutual_fund_analytics.db")

print(f"Using database: {DB_PATH}")

engine = create_engine(f"sqlite:///{DB_PATH}")

# ----------------------------------------------------
# Verify Tables
# ----------------------------------------------------
with engine.connect() as conn:
    tables = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table';")
    ).fetchall()

print("Tables found:")
for t in tables:
    print("-", t[0])

# ----------------------------------------------------
# Read Cleaned CSV Files
# ----------------------------------------------------
nav = pd.read_csv(
    "data/processed/02_nav_history_clean.csv",
    parse_dates=["date"]
)

txn = pd.read_csv(
    "data/processed/08_investor_transactions_clean.csv",
    parse_dates=["transaction_date"]
)

aum = pd.read_csv(
    "data/processed/03_aum_by_fund_house_clean.csv",
    parse_dates=["date"]
)

dim_fund = pd.read_csv(
    "data/processed/01_fund_master_clean.csv",
    parse_dates=["launch_date"]
)

fact_perf = pd.read_csv(
    "data/processed/07_scheme_performance_clean.csv"
)

sip_inflows = pd.read_csv(
    "data/processed/04_monthly_sip_inflows_clean.csv"
)

# ----------------------------------------------------
# Build dim_date
# ----------------------------------------------------
all_dates = pd.concat([
    nav["date"],
    txn["transaction_date"],
    aum["date"]
]).dropna().unique()

dim_date = pd.DataFrame({
    "full_date": pd.to_datetime(all_dates)
})

dim_date = (
    dim_date
    .drop_duplicates()
    .sort_values("full_date")
)

dim_date["date_id"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["full_date"].dt.year
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["month_name"] = dim_date["full_date"].dt.month_name()
dim_date["quarter"] = dim_date["full_date"].dt.quarter
dim_date["day_of_week"] = dim_date["full_date"].dt.day_name()

dim_date = dim_date[
    [
        "date_id",
        "full_date",
        "year",
        "month",
        "month_name",
        "quarter",
        "day_of_week",
    ]
]

# ----------------------------------------------------
# Build fact_nav
# ----------------------------------------------------
fact_nav = nav.copy()

fact_nav["date_id"] = (
    fact_nav["date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

fact_nav = fact_nav[
    [
        "amfi_code",
        "date_id",
        "nav",
    ]
]

# ----------------------------------------------------
# Build fact_transactions
# ----------------------------------------------------
fact_txn = txn.copy()

fact_txn["date_id"] = (
    fact_txn["transaction_date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

fact_txn = fact_txn.drop(columns=["transaction_date"])

# ----------------------------------------------------
# Build fact_performance
# ----------------------------------------------------
fact_perf = fact_perf[
    [
        "amfi_code",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade",
    ]
]

# ----------------------------------------------------
# Build fact_aum
# ----------------------------------------------------
fact_aum = aum.copy()

fact_aum["date_id"] = (
    fact_aum["date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

fact_aum = fact_aum[
    [
        "fund_house",
        "date_id",
        "aum_lakh_crore",
        "aum_crore",
        "num_schemes",
    ]
]

# ----------------------------------------------------
# Tables to Load
# ----------------------------------------------------
tables = {
    "dim_date": dim_date,
    "dim_fund": dim_fund,
    "fact_nav": fact_nav,
    "fact_transactions": fact_txn,
    "fact_performance": fact_perf,
    "fact_aum": fact_aum,
    "sip_inflows": sip_inflows,
}

# ----------------------------------------------------
# Clear Existing Data
# ----------------------------------------------------
print("\nClearing old data...")

with engine.begin() as conn:
    conn.execute(text("DELETE FROM fact_transactions"))
    conn.execute(text("DELETE FROM fact_nav"))
    conn.execute(text("DELETE FROM fact_performance"))
    conn.execute(text("DELETE FROM fact_aum"))
    conn.execute(text("DELETE FROM dim_date"))
    conn.execute(text("DELETE FROM dim_fund"))
    conn.execute(text("DELETE FROM sip_inflows"))

print("Old data cleared.")

# ----------------------------------------------------
# Load Data
# ----------------------------------------------------
print("\nLoading tables...\n")

for table_name, df in tables.items():

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
    )

    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count FROM {table_name}",
        engine,
    )["row_count"][0]

    print(f"{table_name}: {count} rows loaded successfully.")

print("\nAll tables loaded successfully!")