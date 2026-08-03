import pandas as pd

df = pd.read_csv("data/raw/07_scheme_performance.csv")

return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
               "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio"]

# validate numeric
for col in return_cols:
    non_numeric = pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()
    if non_numeric.any():
        print(f"Non-numeric values in {col}: {df.loc[non_numeric, col].tolist()}")
    df[col] = pd.to_numeric(df[col], errors="coerce")

# flag anomalies: returns outside a plausible range, e.g. -100% to +200%
df["anomaly_flag"] = False
for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]:
    df.loc[(df[col] < -100) | (df[col] > 200), "anomaly_flag"] = True

# expense ratio range check (0.1% - 2.5%)
df["expense_ratio_valid"] = df["expense_ratio_pct"].between(0.1, 2.5)
out_of_range = (~df["expense_ratio_valid"]).sum()

print(f"Rows flagged as return anomalies: {df['anomaly_flag'].sum()}")
print(f"Rows with expense_ratio outside 0.1%-2.5%: {out_of_range}")

df.to_csv("data/processed/07_scheme_performance_clean.csv", index=False)
print("Saved -> data/processed/07_scheme_performance_clean.csv")