# 🛢️ Strait of Hormuz Crisis 2026 — Maritime Trade Dashboard

Live dashboard tracking daily vessel traffic through critical maritime chokepoints
following the 2026 Iran war and the effective closure of the Strait of Hormuz.

🌐 **[View Live Dashboard](https://data-innovation-for-africa.github.io/hormuz_impact_Africa/)**

---

## How updates work

The pipeline runs automatically in **3 situations**:

### 1. Automatic weekly download ✅
Every **Tuesday at 14:00 UTC**, GitHub Actions:
1. Downloads the latest CSV from IMF PortWatch API
2. Regenerates `dashboard_data.json` + `hormuz_analysis.xlsx`
3. Commits and pushes — dashboard is live within minutes

### 2. You push a new CSV ✅
When you drop a new CSV and push it to the repo, the pipeline triggers **immediately**:

```
Copy new CSV → data/
git add data/Daily_Chokepoint_Transit_Calls_and_Trade_Volume_Estimates.csv
git commit -m "New data"
git push
→ GitHub Action runs automatically → dashboard + Excel updated
```

### 3. Manual trigger ✅
Go to **GitHub → Actions → Update Dashboard → Run workflow**

---

## Repository structure

```
hormuz-dashboard/
├── index.html                    ← Live dashboard (GitHub Pages)
├── data/
│   ├── Daily_Chokepoint_...csv  ← Source data (push here to trigger update)
│   ├── dashboard_data.json      ← Generated — feeds the dashboard
│   └── hormuz_analysis.xlsx     ← Generated — downloadable Excel workbook
├── scripts/
│   ├── download_data.py         ← Downloads CSV from IMF PortWatch API
│   └── process_data.py          ← Generates JSON + Excel from CSV
├── .github/workflows/
│   └── update_data.yml          ← Automation (schedule + push trigger)
├── requirements.txt
└── .gitignore
```

---

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

Then: **Settings → Pages → Deploy from branch → main → / (root) → Save**

---

## Data source

**IMF PortWatch** · Environmental Change Institute, University of Oxford  
AIS satellite vessel tracking · 28 global chokepoints · Updated weekly (Tuesdays)  
Dataset: [Daily Chokepoint Transit Calls and Trade Volume Estimates](https://portwatch.imf.org/datasets/42132aa4e2fc4d41bdaf9a445f688931_0/about)

> ⚠️ Post-February 28, 2026: AIS data partially degraded due to GPS jamming and vessel blackouts in the Hormuz region.
