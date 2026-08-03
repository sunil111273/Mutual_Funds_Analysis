import pandas as pd

df = pd.read_csv("data/raw/08_investor_transactions.csv")

# fix date format
df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

# standardise transaction_type
print("Raw transaction_type values:", df["transaction_type"].unique())

type_map = {
    "sip": "SIP", "SIP": "SIP",
    "lumpsum": "Lumpsum", "lump sum": "Lumpsum", "Lump Sum": "Lumpsum", "Lumpsum": "Lumpsum",
    "redemption": "Redemption", "redeem": "Redemption", "Redemption": "Redemption",
}
df["transaction_type"] = df["transaction_type"].astype(str).str.strip().map(
    lambda x: type_map.get(x, type_map.get(x.lower(), x.title()))
)

# validate amount > 0
before = len(df)
df = df[df["amount_inr"] > 0]
invalid_amount = before - len(df)

# check KYC status enum
valid_kyc = {"Verified", "Pending", "Not Verified"}   # adjust after seeing actual unique values
print("Raw kyc_status values:", df["kyc_status"].unique())
df["kyc_flag"] = df["kyc_status"].isin(valid_kyc)

# drop rows with unparseable dates
before2 = len(df)
df = df.dropna(subset=["transaction_date"])
bad_dates = before2 - len(df)

print(f"Invalid amount rows dropped: {invalid_amount}, bad date rows dropped: {bad_dates}")
print(f"Transaction types after standardisation: {df['transaction_type'].unique()}")

df.to_csv("data/processed/08_investor_transactions_clean.csv", index=False)
print("Saved -> data/processed/08_investor_transactions_clean.csv")