# 🛢️ Strait of Hormuz Crisis 2026 — Maritime Trade Dashboard

Live dashboard tracking daily vessel traffic through critical maritime chokepoints
following the 2026 Iran war and the effective closure of the Strait of Hormuz.

🌐 **[View Live Dashboard](https://YOUR-USERNAME.github.io/hormuz-dashboard/)**

---

## What it shows

- **Daily ship count** transiting Hormuz, Cape of Good Hope, and Suez Canal
- **7-day moving average** for trend analysis
- **KPI cards** — pre-war vs post-war averages and % change for each chokepoint
- **War event marker** (Feb 28, 2026) on all charts
- **Downloadable Excel file** — 4 sheets, 2 native charts, live formulas

## Repository structure

```
hormuz-dashboard/
├── index.html                   ← Dashboard page (served by GitHub Pages)
├── data/
│   ├── dashboard_data.json      ← Processed data read by the dashboard
│   └── hormuz_analysis.xlsx     ← Downloadable Excel workbook
├── scripts/
│   ├── download_data.py         ← Downloads latest CSV from IMF PortWatch API
│   └── process_data.py          ← Generates JSON + Excel from CSV
├── .github/workflows/
│   └── update_data.yml          ← Auto-updates every Tuesday at 14:00 UTC
├── requirements.txt
└── .gitignore
```

> **Note:** The raw CSV is excluded from Git (see `.gitignore`).
> The GitHub Action downloads it automatically from the IMF PortWatch API each week.

## Deploy to GitHub Pages in 3 steps

```bash
# 1. Create a new GitHub repo and push
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/hormuz-dashboard.git
git push -u origin main

# 2. Enable GitHub Pages
# GitHub repo → Settings → Pages → Deploy from branch → main → / (root) → Save

# 3. Dashboard is live at:
# https://YOUR-USERNAME.github.io/hormuz-dashboard/
```

## Automatic weekly updates

The GitHub Action in `.github/workflows/update_data.yml` runs **every Tuesday at 14:00 UTC**
(one hour after IMF PortWatch publishes its weekly update):

1. Downloads the latest CSV from the IMF PortWatch ArcGIS API
2. Runs `process_data.py` → regenerates `dashboard_data.json` and `hormuz_analysis.xlsx`
3. Commits and pushes the updated files automatically

You can also trigger a manual update anytime:
→ **GitHub → Actions → Update Dashboard Data → Run workflow**

## Manual update with a new CSV

```bash
# Place your CSV in data/ then run:
python3 scripts/process_data.py

# Or download latest from the API and process:
python3 scripts/download_data.py
python3 scripts/process_data.py
```

## Dependencies

```
pip install pandas numpy openpyxl requests
```

## Data source

**IMF PortWatch** · Environmental Change Institute, University of Oxford
- AIS (Automatic Identification System) satellite vessel tracking
- 27 major global chokepoints · Updated weekly every Tuesday
- Dataset: [Daily Chokepoint Transit Calls and Trade Volume Estimates](https://portwatch.imf.org/datasets/42132aa4e2fc4d41bdaf9a445f688931_0/about)

> ⚠️ **Data quality note (post-Feb 28, 2026):** AIS data quality is reduced in the Hormuz
> region due to GPS jamming, AIS spoofing, and vessels going dark.
> Use post-war Hormuz data with caution (per IMF PortWatch advisory).
