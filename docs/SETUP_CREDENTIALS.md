# 🍹 Cocktailverse - Setup & Credentials Guide

## What I've Built

✅ **Core Infrastructure:**
- Cloud Function for data transformation (GCS → BigQuery)
- Cloud Function for fetching cocktails from TheCocktailDB API
- FastAPI test harness for local querying
- Deployment scripts for GCS and Cloud Functions
- BigQuery schema and analytics queries

✅ **New Features Added:**
- `gcf/fetch_cocktails.py` - Fetches cocktails from TheCocktailDB API
- `scripts/deploy_fetch_gcf.sh` - Deployment script for fetch function
- Updated `requirements.txt` with `requests` library

---

## 🔑 Required Credentials & Configuration

### 1. **Google Cloud Platform (GCP) Credentials**

You need one of the following:

#### Option A: Service Account Key (Recommended for Local Development)
1. Create a service account in GCP Console:
   - Go to: IAM & Admin → Service Accounts
   - Create new service account with roles:
     - `Storage Admin` (for GCS)
     - `BigQuery Data Editor` (for BigQuery)
     - `Cloud Functions Developer` (for deployment)

2. Download JSON key:
   - Click on service account → Keys → Add Key → JSON
   - Save as `service-account-key.json` in project root

3. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="./service-account-key.json"
   ```

#### Option B: gcloud CLI Authentication (Recommended for Deployment)

Quick setup (3 steps):
```bash
# Step 1: User authentication
gcloud auth login

# Step 2: Application default credentials (use --quiet for non-interactive)
gcloud auth application-default login --quiet

# Step 3: Enable required APIs
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  --project=YOUR_PROJECT_ID
```

### 2. **Environment Variables (.env file)**

Create `.env` file in project root:

```bash
# Google Cloud Platform Configuration
PROJECT_ID=your-gcp-project-id
REGION=us-central1
DATASET_ID=cocktailverse
TABLE_ID=jobs_clean
BUCKET_NAME=cocktailverse-raw-${PROJECT_ID}
FUNCTION_NAME=cocktailverse-transform

# Optional: Service Account Key Path (for local development)
# GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

**Note:** The `.env` file is gitignored, so create it manually.

---

## 🔌 MCP Servers Needed

**None required!** 

This project uses:
- ✅ **filesystem** (already available) - for reading/writing project files
- ✅ **No GCP-specific MCP servers needed** - all GCP interactions use:
  - `gcloud` CLI for deployment
  - `google-cloud-*` Python libraries for runtime operations
  - Service account credentials for authentication

---

## 🌐 External APIs Used

### TheCocktailDB API (Free, No Key Required)
- **Base URL:** `https://www.thecocktaildb.com/api/json/v1/1`
- **Status:** ✅ Free, no authentication needed
- **Rate Limits:** None specified (be reasonable)
- **Used by:** `gcf/fetch_cocktails.py`

**Endpoints Used:**
- `/random.php` - Get random cocktails
- `/filter.php?a=Non_Alcoholic` - Get mocktails
- `/popular.php` - Get popular cocktails
- `/search.php?s={term}` - Search cocktails
- `/lookup.php?i={id}` - Get cocktail details

---

## 🚀 Quick Setup Steps

### 1. Install Dependencies
```bash
cd /Users/anixlynch/dev/northstar/03_cocktailverse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure GCP
```bash
# Option A: Using gcloud CLI (Recommended)
gcloud auth login
gcloud auth application-default login --quiet
gcloud services enable cloudfunctions.googleapis.com cloudbuild.googleapis.com bigquery.googleapis.com storage.googleapis.com --project=YOUR_PROJECT_ID

# Option B: Using service account
# Download service account key and set:
export GOOGLE_APPLICATION_CREDENTIALS="./service-account-key.json"
```

### 3. Create .env File
```bash
# Copy this template and fill in your PROJECT_ID
cat > .env << EOF
PROJECT_ID=your-gcp-project-id
REGION=us-central1
DATASET_ID=cocktailverse
TABLE_ID=jobs_clean
BUCKET_NAME=cocktailverse-raw-${PROJECT_ID}
FUNCTION_NAME=cocktailverse-transform
EOF
```

### 4. Deploy Infrastructure
```bash
# Make scripts executable (already done)
chmod +x scripts/*.sh

# Setup GCS bucket
./scripts/gcs_setup.sh

# Deploy transform function
./scripts/deploy_gcf.sh

# Deploy fetch function (optional)
./scripts/deploy_fetch_gcf.sh
```

### 5. Test It!
```bash
# Test with sample data
gsutil cp data/raw/sample_data.json gs://cocktailverse-raw-${PROJECT_ID}/

# Or fetch cocktails via API
curl "https://YOUR-FUNCTION-URL?fetch_type=random&limit=3"

# Query results
python api/test_harness.py
# Visit http://localhost:8000/jobs
```

---

## 📋 GCP APIs That Need to be Enabled

The deployment scripts automatically enable these, but you can also enable manually:

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

---

## ✅ Verification Checklist

After authentication, verify everything is set up correctly:

```bash
# Check active account
gcloud auth list

# Check project
gcloud config get-value project

# Verify APIs enabled
gcloud services list --enabled \
  --filter="name:cloudfunctions.googleapis.com OR name:bigquery.googleapis.com OR name:storage.googleapis.com"

# Test authentication
gcloud projects describe YOUR_PROJECT_ID
```

**Checklist:**
- [ ] `gcloud auth list` shows your account as ACTIVE
- [ ] `gcloud config get-value project` shows correct PROJECT_ID
- [ ] APIs are enabled (cloudfunctions, bigquery, storage, cloudbuild)
- [ ] `.env` file exists with correct PROJECT_ID

---

## 🔍 Where to Find Old Credentials

If you mentioned the old cocktailverse might have credentials, check:
- `~/.config/gcloud/` - gcloud CLI credentials
- `~/.google-cloud/` - Application default credentials
- Any `service-account-*.json` files in the project directory
- Environment variables: `echo $GOOGLE_APPLICATION_CREDENTIALS`

---

## ✅ Summary

**MCP Servers:** None needed (filesystem already available)

**APIs:**
- TheCocktailDB API: ✅ Free, no key needed
- GCP APIs: Enabled via deployment scripts

**Credentials:**
- GCP Service Account Key OR gcloud CLI authentication
- `.env` file with `PROJECT_ID` and other config

**Next Steps:**
1. Get GCP credentials (service account key or gcloud auth)
2. Create `.env` file with your `PROJECT_ID`
3. Run deployment scripts
4. Test with sample data or fetch cocktails!

