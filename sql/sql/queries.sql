-- 1. Top 5 funds by AUM
SELECT scheme_name, aum_crore
FROM fact_performance fp JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY aum_crore DESC LIMIT 5;

-- 2. Average NAV per month, per fund
SELECT amfi_code, dd.year, dd.month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav fn JOIN dim_date dd ON fn.date_id = dd.date_id
GROUP BY amfi_code, dd.year, dd.month
ORDER BY amfi_code, dd.year, dd.month;

-- 3. SIP YoY growth (from monthly_sip_inflows_clean, loaded separately or referenced from CSV/staging table)
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM sip_inflows
ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) AS num_txns, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense_ratio < 1%
SELECT scheme_name, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- 6. Top 5 funds by 3-year return
SELECT df.scheme_name, fp.return_3yr_pct
FROM fact_performance fp JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY fp.return_3yr_pct DESC LIMIT 5;

-- 7. Transaction type breakdown by city tier
SELECT city_tier, transaction_type, COUNT(*) AS n, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY city_tier, transaction_type
ORDER BY city_tier, total_amount DESC;

-- 8. Average sharpe ratio by category
SELECT df.category, ROUND(AVG(fp.sharpe_ratio), 3) AS avg_sharpe
FROM fact_performance fp JOIN dim_fund df ON fp.amfi_code = df.amfi_code
GROUP BY df.category
ORDER BY avg_sharpe DESC;

-- 9. Monthly AUM trend by fund house
SELECT fund_house, dd.year, dd.month, aum_crore
FROM fact_aum fa JOIN dim_date dd ON fa.date_id = dd.date_id
ORDER BY fund_house, dd.year, dd.month;

-- 10. Investors with highest total investment amount (top 10)
SELECT investor_id, SUM(amount_inr) AS total_invested, COUNT(*) AS num_txns
FROM fact_transactions
WHERE transaction_type != 'Redemption'
GROUP BY investor_id
ORDER BY total_invested DESC LIMIT 10;