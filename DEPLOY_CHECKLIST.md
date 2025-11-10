# ✅ Streamlit Deployment Checklist

## Pre-Deployment

- [x] Streamlit app created (`dashboard/app.py`)
- [x] Requirements updated (Streamlit added)
- [x] Config file created (`.streamlit/config.toml`)
- [ ] **Git repository initialized** (if not already)
- [ ] **Cocktail data in BigQuery** (fetch if needed)

## Deployment Steps

### 1. Initialize Git (if needed)
```bash
cd /Users/anixlynch/dev/northstar/03_cocktailverse
git init
git add .
git commit -m "Add Streamlit dashboard for Cocktailverse"
```

### 2. Push to GitHub
```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/cocktailverse.git
git branch -M main
git push -u origin main
```

### 3. Fetch Cocktail Data (if BigQuery is empty)
```bash
gcloud functions call cocktailverse-fetch-cocktails \
  --region=us-central1 \
  --data '{"fetch_type":"random","limit":20}'
```

Wait ~30 seconds for transform function to process, then verify:
```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`maps-platform-20251011-140544.cocktailverse.cocktails\`"
```

### 4. Deploy to Streamlit Cloud

1. **Go to:** https://share.streamlit.io
2. **Click:** "New app"
3. **Connect:** Your GitHub repo
4. **Settings:**
   - Branch: `main`
   - Main file: `dashboard/app.py`
5. **Environment Variables:**
   ```
   PROJECT_ID=maps-platform-20251011-140544
   DATASET_ID=cocktailverse
   TABLE_ID=cocktails
   ```
6. **Secrets** (GCP Credentials):
   - Option A: Service Account JSON (recommended)
   - Option B: Application Default Credentials JSON
   
   Add to Streamlit Cloud → Settings → Secrets:
   ```toml
   [gcp]
   service_account_key = """
   {paste your service account JSON here}
   """
   ```

7. **Deploy!** Click "Deploy"

---

## Quick Commands

**Check if data exists:**
```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as count FROM \`maps-platform-20251011-140544.cocktailverse.cocktails\`"
```

**Fetch cocktails:**
```bash
gcloud functions call cocktailverse-fetch-cocktails \
  --region=us-central1 \
  --data '{"fetch_type":"random","limit":20}'
```

**Test locally (optional):**
```bash
pip install streamlit pandas
export PROJECT_ID=maps-platform-20251011-140544
export DATASET_ID=cocktailverse
export TABLE_ID=cocktails
streamlit run dashboard/app.py
```

---

**Status:** ✅ Ready to deploy!
**Cost:** $0/month (Streamlit Cloud free tier)

