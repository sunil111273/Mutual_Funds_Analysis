import requests
import pandas as pd
import json

def fetch_nav(amfi_code, scheme_label):
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    nav_df = pd.DataFrame(data["data"])
    nav_df["amfi_code"] = amfi_code
    nav_df["scheme_label"] = scheme_label
    nav_df["fund_house"] = data["meta"]["fund_house"]
    nav_df["scheme_name"] = data["meta"]["scheme_name"]
    return nav_df

# HDFC Top 100 Direct
hdfc_df = fetch_nav(125497, "HDFC Top 100 Direct")
hdfc_df.to_csv("data/raw/hdfc_top100_direct_live_nav.csv", index=False)
print(f"HDFC Top 100 Direct: {hdfc_df.shape[0]} NAV records fetched")

# 5 key schemes
schemes = {
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

all_navs = []
for code, label in schemes.items():
    df = fetch_nav(code, label)
    all_navs.append(df)
    print(f"{label} ({code}): {df.shape[0]} NAV records fetched")

combined_df = pd.concat(all_navs, ignore_index=True)
combined_df.to_csv("data/raw/five_schemes_live_nav.csv", index=False)
print(f"\nCombined saved: {combined_df.shape}")