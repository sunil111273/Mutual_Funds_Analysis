-- dim_fund: one row per scheme
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- dim_date: calendar dimension, generated once and reused by all fact tables
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,   -- YYYYMMDD as integer
    full_date DATE,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    day_of_week TEXT
);

-- fact_nav: daily NAV per fund
CREATE TABLE fact_nav (
    amfi_code INTEGER,
    date_id INTEGER,
    nav REAL,
    PRIMARY KEY (amfi_code, date_id),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

-- fact_transactions: investor-level transactions
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT,
    date_id INTEGER,
    amfi_code INTEGER,
    transaction_type TEXT,
    amount_inr INTEGER,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

ALTER TABLE fact_transactions
ADD COLUMN kyc_flag INTEGER; -- to add a new column


-- fact_performance: latest return/risk metrics per fund
CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore INTEGER,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_aum: fund-house level AUM by month
CREATE TABLE fact_aum (
    fund_house TEXT,
    date_id INTEGER,
    aum_lakh_crore REAL,
    aum_crore INTEGER,
    num_schemes INTEGER,
    PRIMARY KEY (fund_house, date_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);
SELECT name
FROM sqlite_master
WHERE type = 'table'; --to check the tables created or not


--to check the data loaded or not
SELECT COUNT(*) FROM dim_fund;
SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM fact_nav;
SELECT COUNT(*) FROM fact_transactions;
SELECT COUNT(*) FROM fact_performance;
SELECT COUNT(*) FROM fact_aum;

--to create a new table
CREATE TABLE sip_inflows (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    yoy_growth_pct REAL
);

--to create new columns in sip_inflows
ALTER TABLE sip_inflows
ADD COLUMN new_sip_accounts_lakh REAL;

ALTER TABLE sip_inflows
ADD COLUMN sip_aum_lakh_crore REAL;