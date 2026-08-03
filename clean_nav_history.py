import pandas as pd
print("Script started")
df = pd.read_csv("data/raw/02_nav_history.csv", parse_dates=["date"])

before = len(df)

# 1. sort by amfi_code + date
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# 2. remove duplicates (same fund, same date)
dupes = df.duplicated(subset=["amfi_code", "date"]).sum()
df = df.drop_duplicates(subset=["amfi_code", "date"], keep="first")

# 3. forward-fill missing NAV per fund (holidays/weekends -> reindex to daily calendar per fund, then ffill)
filled_frames = []
for code, g in df.groupby("amfi_code"):
    g = g.set_index("date").sort_index()
    full_range = pd.date_range(g.index.min(), g.index.max(), freq="D")
    g = g.reindex(full_range)
    g["amfi_code"] = code
    g["nav"] = g["nav"].ffill()
    g.index.name = "date"
    filled_frames.append(g.reset_index())

df_clean = pd.concat(filled_frames, ignore_index=True)
df_clean = df_clean[["amfi_code", "date", "nav"]]

# 4. validate NAV > 0
invalid = df_clean[df_clean["nav"] <= 0]
df_clean = df_clean[df_clean["nav"] > 0]

print(f"Rows before: {before}, duplicates removed: {dupes}, "
      f"rows after calendar fill: {len(df_clean)}, invalid NAV rows dropped: {len(invalid)}")

df_clean.to_csv("data/processed/02_nav_history_clean.csv", index=False)
print("Saved -> data/processed/02_nav_history_clean.csv")