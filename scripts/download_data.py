#!/usr/bin/env python3
"""
download_data.py
────────────────
Downloads the latest "Daily Chokepoint Transit Calls and Trade Volume Estimates"
CSV from IMF PortWatch (ArcGIS Hub) and saves it to data/.

The GitHub Action runs this every Tuesday at 14:00 UTC, one hour after
IMF PortWatch publishes its weekly update (Tuesdays ~9am ET).

Direct CSV URL (no authentication, no API key needed):
  https://opendata.arcgis.com/datasets/42132aa4e2fc4d41bdaf9a445f688931_0.csv

Fallback: paginated ArcGIS REST API query.
"""

import requests
import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR   = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_NAME   = "Daily_Chokepoint_Transit_Calls_and_Trade_Volume_Estimates.csv"
CSV_PATH   = DATA_DIR / CSV_NAME
META_PATH  = DATA_DIR / "download_meta.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HormuzDashboard/1.0; "
        "+https://github.com/data-innovation-for-africa/hormuz_impact_Africa)"
    )
}

# ── Method 1: direct CSV export from ArcGIS Hub ───────────────
DIRECT_URL = (
    "https://opendata.arcgis.com/datasets/"
    "42132aa4e2fc4d41bdaf9a445f688931_0.csv"
)

# ── Method 2: ArcGIS REST API (paginated) ────────────────────
REST_URL = (
    "https://services.arcgis.com/iQ1dY19aHwbSDYIF/arcgis/rest/services/"
    "chokepoints_daily/FeatureServer/0/query"
)


def download_direct():
    """Try to download the full CSV directly."""
    print(f"→ Trying direct CSV download from ArcGIS Hub …")
    r = requests.get(DIRECT_URL, headers=HEADERS, timeout=120, stream=True)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type", "")
    if "text/csv" not in content_type and "text/plain" not in content_type:
        # Could be a redirect to S3 — follow it
        if r.history:
            final_url = r.url
            print(f"  Redirected to: {final_url[:80]}")
    # Write raw bytes
    tmp = CSV_PATH.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
    # Validate: must be a readable CSV with a 'date' column
    df = pd.read_csv(tmp, encoding="utf-8-sig", nrows=5)
    if "date" not in df.columns and "portname" not in df.columns:
        raise ValueError(f"Downloaded file does not look like PortWatch data. Columns: {list(df.columns)}")
    tmp.rename(CSV_PATH)
    return True


def download_via_rest():
    """Paginated fallback using the ArcGIS REST Feature Service."""
    print("→ Trying ArcGIS REST API (paginated) …")
    records   = []
    offset    = 0
    page_size = 2000

    while True:
        params = {
            "where":             "1=1",
            "outFields":         "*",
            "orderByFields":     "date ASC",
            "resultOffset":      offset,
            "resultRecordCount": page_size,
            "f":                 "json",
        }
        r = requests.get(REST_URL, params=params, headers=HEADERS, timeout=60)
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise RuntimeError(f"API error: {data['error']}")

        features = data.get("features", [])
        if not features:
            break

        for feat in features:
            records.append(feat["attributes"])

        print(f"  … {len(records):,} records fetched")

        if not data.get("exceededTransferLimit", False):
            break
        offset += page_size

    if not records:
        raise RuntimeError("REST API returned 0 records.")

    df = pd.DataFrame(records)

    # Convert epoch milliseconds → datetime string
    if "date" in df.columns and pd.api.types.is_numeric_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], unit="ms", utc=True)

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    return True


def main():
    print("=" * 60)
    print("IMF PortWatch — Data Downloader")
    print(f"Target: {CSV_PATH}")
    print("=" * 60)

    success = False

    # Try method 1
    try:
        success = download_direct()
        print("✅ Direct download succeeded.")
    except Exception as e:
        print(f"  ✗ Direct download failed: {e}")

    # Fallback to method 2
    if not success:
        try:
            success = download_via_rest()
            print("✅ REST API download succeeded.")
        except Exception as e:
            print(f"  ✗ REST API download failed: {e}")

    if not success:
        print("\n❌ Both download methods failed.")
        print("   The workflow will keep the existing data/CSV file.")
        sys.exit(0)   # exit 0 so the workflow continues with old data

    # ── Validate and report ───────────────────────────────────
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.tz_localize(None)
    latest     = df["date"].max()
    n_rows     = len(df)
    cps        = sorted(df["portname"].unique().tolist()) if "portname" in df.columns else []

    print(f"\n📊 Downloaded: {n_rows:,} rows — latest date: {latest.date()}")
    print(f"   File size:  {CSV_PATH.stat().st_size // 1024:,} KB")
    print(f"   Chokepoints ({len(cps)}): {', '.join(cps[:5])} …")

    # ── Write metadata ────────────────────────────────────────
    meta = {
        "downloaded_at":    datetime.now(timezone.utc).isoformat(),
        "latest_data_date": str(latest.date()),
        "total_rows":       n_rows,
        "file_size_kb":     CSV_PATH.stat().st_size // 1024,
        "chokepoints":      cps,
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"✅ Metadata written: {META_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
