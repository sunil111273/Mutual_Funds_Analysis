"""
live_nav_fetch.py
Bluestock Mutual Fund Analytics Capstone -- Day 1

This script covers two Day 1 tasks from the project brief:

    Task 4 - Fetch live NAV history for HDFC Top 100 Fund (AMFI code 125497)
              from the public mfapi.in API and save it as a raw CSV.
    Task 5 - Fetch live NAV history for 5 more key schemes:
                  SBI Bluechip Fund              (119551)
                  ICICI Prudential Bluechip Fund  (120503)
                  Nippon India Large Cap Fund     (118632)
                  Axis Bluechip Fund              (119092)
                  Kotak Bluechip Fund             (120841)

mfapi.in is a free, public REST API and does not need an API key.

How to run:
    python3 scripts/live_nav_fetch.py

Output:
    One CSV per scheme, saved under data/raw/live_fetched/

Note: this script needs internet access to reach api.mfapi.in. If your
current network blocks it, run this script from your own machine.
"""

import pathlib
import time

import pandas as pd
import requests

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "data" / "raw" / "live_fetched"
API_URL = "https://api.mfapi.in/mf/{code}"

# amfi_code -> a short readable label used in the output filename
SCHEMES = {
    125497: "HDFC_Top_100_Fund",
    119551: "SBI_Bluechip_Fund",
    120503: "ICICI_Prudential_Bluechip_Fund",
    118632: "Nippon_India_Large_Cap_Fund",
    119092: "Axis_Bluechip_Fund",
    120841: "Kotak_Bluechip_Fund",
}


def fetch_scheme_nav(amfi_code):
    """GET the NAV history JSON for one scheme from mfapi.in."""
    url = API_URL.format(code=amfi_code)
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def save_scheme_csv(amfi_code, label, payload):
    """Parse the mfapi.in JSON payload into a simple CSV: amfi_code, date, nav."""
    meta = payload.get("meta", {})
    records = payload.get("data", [])

    df = pd.DataFrame(records)
    df["amfi_code"] = amfi_code
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df = df[["amfi_code", "date", "nav"]].sort_values("date").reset_index(drop=True)

    out_path = OUT_DIR / f"live_nav_{amfi_code}_{label}.csv"
    df.to_csv(out_path, index=False)

    print(f"  scheme_name (from API): {meta.get('scheme_name', 'n/a')}")
    print(f"  fund_house  (from API): {meta.get('fund_house', 'n/a')}")
    print(f"  rows fetched: {len(df)}  ->  saved to {out_path.relative_to(BASE_DIR)}")
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Day 1 - Live NAV fetch from api.mfapi.in")
    print("=" * 70)

    results = []
    for amfi_code, label in SCHEMES.items():
        print(f"\nFetching AMFI code {amfi_code} ({label}) ...")
        try:
            payload = fetch_scheme_nav(amfi_code)
            save_scheme_csv(amfi_code, label, payload)
            results.append((amfi_code, label, "OK"))
        except Exception as e:
            print(f"  ERROR fetching {amfi_code}: {e}")
            results.append((amfi_code, label, f"FAILED: {e}"))
        time.sleep(1)  # be polite to the free public API

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for amfi_code, label, status in results:
        print(f"  {amfi_code:>7}  {label:<32}  {status}")


if __name__ == "__main__":
    main()
