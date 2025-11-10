# 🍹 Cocktailverse – GCP ETL Pipeline

![GCP](https://img.shields.io/badge/GCP-Serverless-blue?logo=google-cloud)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Ready-green)
![License](https://img.shields.io/badge/License-MIT-blue)

> **Northstar Project #3: Serverless GCP ETL pipeline showcasing end-to-end data processing**

---

## 🎯 What This Does

**Fetch cocktails from TheCocktailDB API → Transform → Production-ready BigQuery warehouse in < 1 second**

- ✅ **100% Serverless** - GCS, Cloud Functions, BigQuery (zero infrastructure)
- ✅ **Event-Driven** - GCS uploads trigger automatic transformation
- ✅ **Creative Schema Reuse** - Cocktails stored in job listing format (fun mapping!)
- ✅ **Production-Ready** - Error handling, validation, monitoring
- ✅ **Cost-Effective** - GCP Free Tier friendly
- ✅ **Scalable** - Handles growth automatically

---

## 🏗️ Architecture

```
┌─────────────┐
│  Raw Data   │
│  (JSON)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  GCS Bucket │  ← Raw layer (storage)
│  (raw/)     │
└──────┬──────┘
       │
       │ (triggers)
       ▼
┌─────────────┐
│  Cloud      │  ← Transform layer (processing)
│  Function   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  BigQuery   │  ← Refined layer (warehouse)
│  (jobs_clean)│  (cocktails stored in job format schema)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │  ← Query layer (local simulator)
│  Test Harness│
└─────────────┘
```

**Three-Layer Serverless Architecture:**
- **Storage:** Google Cloud Storage (raw data)
- **Processing:** Cloud Functions (event-driven transformation)
- **Warehouse:** BigQuery (analytics-ready data)
- **Query:** FastAPI (local testing)

---

## 📊 Data Flow

### Input (Raw Cocktail from TheCocktailDB API)
```json
{
  "idDrink": "11007",
  "strDrink": "Margarita",
  "strCategory": "Ordinary Drink",
  "strAlcoholic": "Alcoholic",
  "strGlass": "Cocktail glass",
  "strInstructions": "Rub the rim of the glass with the lime slice...",
  "strIngredient1": "Tequila",
  "strMeasure1": "1 1/2 oz",
  "strIngredient2": "Triple sec",
  "strMeasure2": "1/2 oz",
  "strIngredient3": "Lime juice",
  "strMeasure3": "1 oz"
}
```

### Output (Transformed to Job Format - Creative Mapping! 🍹)
```json
{
  "job_id": "cocktail_11007",
  "title": "Margarita",
  "company": "TheCocktailDB",
  "location": "Ordinary Drink",
  "salary_min": null,
  "salary_max": null,
  "salary_currency": "USD",
  "remote": true,
  "posted_date": "2025-11-07T12:00:00Z",
  "description": "Rub the rim of the glass with the lime slice...",
  "requirements": ["1 1/2 oz Tequila", "1/2 oz Triple sec", "1 oz Lime juice"],
  "contact_email": "api@thecocktaildb.com",
  "processed_at": "2025-11-07T12:00:00Z",
  "data_source": "cocktailverse_ingest"
}
```

**Transformation includes:**
- ✅ Cocktail → Job format mapping (creative reuse of schema!)
- ✅ Ingredient extraction and formatting
- ✅ Field validation and normalization
- ✅ Case normalization (title, category)
- ✅ Timestamp enrichment
- ✅ Source tracking

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- GCP Account (Free Tier)
- `gcloud` CLI installed and configured
- Python 3.11+

### Installation

```bash
# 1. Clone and setup
cd /Users/anixlynch/dev/northstar/03_cocktailverse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure GCP
cp .env.example .env
# Edit .env with your PROJECT_ID

# 3. Deploy infrastructure
chmod +x scripts/*.sh
./scripts/gcs_setup.sh
./scripts/deploy_gcf.sh

# 4. Test it!
# Option A: Upload sample data
gsutil cp data/raw/sample_data.json gs://cocktailverse-raw-${PROJECT_ID}/

# Option B: Fetch fresh cocktails from API
gcloud functions call cocktailverse-fetch-cocktails --region=us-central1 --data '{"fetch_type":"random","limit":3}'
```

### Verify

```bash
# Check BigQuery
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`${PROJECT_ID}.cocktailverse.jobs_clean\`"

# Run local API
python api/test_harness.py
# Visit http://localhost:8000/jobs
```

---

## 📁 Project Structure

```
03_cocktailverse/
├── README.md                 → You are here
├── cocktailverse.yaml         → Project specification
├── requirements.txt          → Python dependencies
│
├── gcf/                      → Cloud Functions
│   ├── fetch_cocktails.py    → Fetches from TheCocktailDB API
│   ├── transform.py          → Data transformation logic
│   └── main.py               → Entry point wrapper
│
├── bq/                       → BigQuery
│   ├── schema.json           → Table schema
│   └── bq_queries.sql        → Analytics queries
│
├── api/                      → FastAPI application
│   └── test_harness.py       → Local query simulator
│
├── scripts/                  → Deployment scripts
│   ├── gcs_setup.sh          → Create GCS buckets
│   ├── deploy_gcf.sh         → Deploy transform function
│   └── deploy_fetch_gcf.sh   → Deploy fetch function
│
└── docs/                     → Documentation
    ├── ARCHITECTURE_MAPS.md  → Architecture visualizations
    ├── COST_MONITORING.md    → Cost tracking guide
    └── SETUP_CREDENTIALS.md  → Setup instructions
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
PROJECT_ID=your-gcp-project-id
REGION=us-central1
DATASET_ID=cocktailverse
TABLE_ID=jobs_clean
BUCKET_NAME=cocktailverse-raw-${PROJECT_ID}
FUNCTION_NAME=cocktailverse-transform
```

---

## 📊 Analytics Queries

See `bq/bq_queries.sql` for example queries:

- Cocktail count by category
- Popular ingredients analysis
- Alcoholic vs non-alcoholic distribution
- Top cocktail types

Run queries:
```bash
bq query --use_legacy_sql=false < bq/bq_queries.sql
```

---

## 💰 Cost Analysis

**GCP Free Tier Coverage:**

| Service | Free Tier | Current Usage | Status |
|---------|-----------|--------------|--------|
| Cloud Functions | 2M invocations/month | ~10 invocations | ✅ 0.0005% |
| Cloud Storage | 5 GB/month | ~0.01 MB | ✅ 0.0002% |
| BigQuery | 10 GB storage, 1 TB queries/month | < 1 MB | ✅ < 0.01% |

**Estimated Monthly Cost: $0.00** (within Free Tier)

---

## 🎓 What This Demonstrates

- ✅ **Serverless Architecture** - Building production systems without servers
- ✅ **Event-Driven Design** - GCS triggers Cloud Functions automatically
- ✅ **GCP Best Practices** - Cloud Functions, BigQuery, GCS integration
- ✅ **Data Quality** - Validation, normalization, enrichment
- ✅ **ETL Pipeline** - Extract → Transform → Load pattern
- ✅ **Cost Optimization** - Maximizing GCP Free Tier

---

## 🔮 Future Enhancements

- [ ] Cloud Workflows for orchestration
- [ ] Cloud Scheduler for scheduled jobs
- [ ] Cloud Monitoring dashboards
- [ ] Data validation rules
- [ ] Multi-source data ingestion
- [ ] Real-time streaming with Pub/Sub

---

## 📚 Documentation

- **Project Spec:** `cocktailverse.yaml` - Complete project specification
- **Architecture:** `docs/ARCHITECTURE_MAPS.md` - Visual architecture maps
- **Setup Guide:** `docs/SETUP_CREDENTIALS.md` - Authentication & deployment
- **Cost Monitoring:** `docs/COST_MONITORING.md` - Free tier tracking
- **Schema:** `bq/schema.json` - BigQuery table structure
- **Queries:** `bq/bq_queries.sql` - Analytics queries
- **API Docs:** Run server and visit `http://localhost:8000/docs`

---

## 🤝 Contributing

This is a portfolio project demonstrating GCP serverless ETL capabilities. Feel free to:
- Fork and experiment
- Suggest improvements
- Use as a learning resource

---

## 📝 License

MIT License - Feel free to use this as a template for your own projects!

---

**Built with ❤️ using Google Cloud Platform**

*Last Updated: 2025-01-20 | Status: Ready | Cost: $0/month (Free Tier)*

