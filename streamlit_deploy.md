# 🚀 Deploy to Streamlit Cloud

## Quick Deploy (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Streamlit dashboard"
git push origin main
```

### 2. Connect Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repo
4. Select branch: `main`
5. Main file path: `dashboard/app.py`

### 3. Configure Environment Variables
In Streamlit Cloud settings, add:
```
PROJECT_ID=maps-platform-20251011-140544
DATASET_ID=cocktailverse
TABLE_ID=cocktails
```

### 4. Add GCP Credentials
**Option A: Service Account (Recommended)**
1. Create service account in GCP Console
2. Grant `BigQuery Data Viewer` role
3. Download JSON key
4. In Streamlit Cloud → Settings → Secrets, add:
```toml
[gcp]
service_account_key = """
{
  "type": "service_account",
  ...
}
"""
```

**Option B: Application Default Credentials**
If using `gcloud auth application-default login`, credentials are in:
`~/.config/gcloud/application_default_credentials.json`

Copy to Streamlit Cloud secrets as above.

### 5. Deploy!
Click "Deploy" - your dashboard will be live in ~30 seconds!

---

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROJECT_ID=maps-platform-20251011-140544
export DATASET_ID=cocktailverse
export TABLE_ID=cocktails

# Run Streamlit
streamlit run dashboard/app.py
```

Visit: http://localhost:8501

---

## Troubleshooting

**"Failed to connect to BigQuery"**
- Make sure GCP credentials are configured
- Check PROJECT_ID is correct
- Verify BigQuery API is enabled

**"No cocktail data found"**
- Run fetch function: `gcloud functions call cocktailverse-fetch-cocktails`
- Check BigQuery table exists: `bq ls cocktailverse`

**"Permission denied"**
- Grant service account `BigQuery Data Viewer` role
- Or use application default credentials

---

**Cost: $0/month** (Streamlit Cloud free tier)

