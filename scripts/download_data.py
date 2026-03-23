#!/usr/bin/env python3
"""
download_data.py
Fetches the latest chokepoints CSV from IMF PortWatch ArcGIS API
and saves it to data/ replacing the previous file.
"""
import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone
import sys

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# IMF PortWatch ArcGIS Feature Service
# Dataset: Daily Chokepoint Transit Calls and Trade Volume Estimates
BASE_URL = (
    "https://services.arcgis.com/iQ1dY19aHwbSDYIF/arcgis/rest/services/"
    "chokepoints_daily/FeatureServer/0/query"
)

CHOKEPOINTS_FILTER = (
    "portname='Strait of Hormuz' OR "
    "portname='Cape of Good Hope' OR "
    "portname='Suez Canal' OR "
    "portname='Panama Canal' OR "
    "portname='Bab el-Mandeb Strait'"
)

def fetch_all_records():
    """Paginate through the API to get all records."""
    records = []
    offset  = 0
    page_size = 1000

    print("Fetching data from IMF PortWatch API...")
    while True:
        params = {
            "where":           "1=1",          # all records
            "outFields":       "*",
            "orderByFields":   "date ASC",
            "resultOffset":    offset,
            "resultRecordCount": page_size,
            "f":               "json",
        }
        try:
            r = requests.get(BASE_URL, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"  API error at offset {offset}: {e}")
            break

        features = data.get("features", [])
        if not features:
            break

        for feat in features:
            records.append(feat["attributes"])

        print(f"  Fetched {len(records):,} records...")

        if not data.get("exceededTransferLimit", False):
            break
        offset += page_size

    return records

def main():
    records = fetch_all_records()
    if not records:
        print("ERROR: No records fetched. Keeping existing data.")
        sys.exit(0)

    df = pd.DataFrame(records)

    # Convert epoch ms → datetime
    if 'date' in df.columns and df['date'].dtype in ['int64','float64']:
        df['date'] = pd.to_datetime(df['date'], unit='ms', utc=True)

    latest = pd.to_datetime(df['date']).max()
    print(f"✅ Fetched {len(df):,} rows — latest date: {latest.date()}")

    # Save CSV
    out_path = DATA_DIR / "Daily_Chokepoint_Transit_Calls_and_Trade_Volume_Estimates.csv"
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"✅ Saved → {out_path}  ({out_path.stat().st_size // 1024} KB)")

    # Save a metadata file
    meta = {
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "latest_data_date": str(latest.date()),
        "total_rows": len(df),
        "chokepoints": sorted(df['portname'].unique().tolist())
                       if 'portname' in df.columns else [],
    }
    with open(DATA_DIR / "download_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"✅ Metadata saved.")

if __name__ == "__main__":
    main()
