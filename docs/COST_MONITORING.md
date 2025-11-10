# 💰 Cost Monitoring & Free Tier Management

## 🎯 Goal: Stay Within $300 Free Tier

This project is designed to use **GCP Free Tier** services. Here's how to monitor and control costs.

---

## 📊 Free Tier Limits (What We're Using)

| Service | Free Tier | Our Usage | Cost |
|---------|-----------|-----------|------|
| **Cloud Functions (Gen2)** | 2M invocations/month<br>400K GB-seconds/month<br>200K GHz-seconds/month | ~10-100 invocations | ✅ $0 |
| **Cloud Storage** | 5 GB/month<br>5K Class A ops/month<br>50K Class B ops/month | < 1 MB | ✅ $0 |
| **BigQuery** | 10 GB storage/month<br>1 TB queries/month | < 1 MB | ✅ $0 |
| **Cloud Build** | 120 build-minutes/day | ~2-5 minutes per deploy | ✅ $0 |

**Estimated Monthly Cost: $0.00** ✅

---

## 🚨 Cost Alerts Setup

### Option 1: GCP Console Budget Alerts
1. Go to: **Billing → Budgets & alerts**
2. Create budget: **$10/month** (safety buffer)
3. Set alert at: **50% ($5)** and **90% ($9)**

### Option 2: Command Line
```bash
# Check current month's cost
gcloud billing accounts list
gcloud billing projects describe maps-platform-20251011-140544

# Set up budget alert (requires billing account ID)
# gcloud billing budgets create --billing-account=BILLING_ACCOUNT_ID \
#   --display-name="Cocktailverse Budget" \
#   --budget-amount=10USD \
#   --threshold-rule=percent=50 \
#   --threshold-rule=percent=90
```

---

## 📈 Cost Monitoring Commands

### Check Current Usage
```bash
# Cloud Functions invocations
gcloud functions list --format="table(name,status,updateTime)"

# Cloud Storage usage
gsutil du -sh gs://cocktailverse-raw-maps-platform-20251011-140544

# BigQuery storage
bq show --format=prettyjson maps-platform-20251011-140544:cocktailverse

# Check billing (if enabled)
gcloud billing accounts list
```

### Monitor Function Invocations
```bash
# View function logs (shows invocation count)
gcloud functions logs read cocktailverse-transform --limit=50 --gen2

# Check function metrics
gcloud monitoring time-series list \
  --filter='resource.type="cloud_function" AND metric.type="cloudfunctions.googleapis.com/function/execution_count"'
```

---

## 💡 Cost Optimization Tips

### 1. **Cloud Functions**
- ✅ Using Gen2 (more efficient)
- ✅ Memory: 256MB (minimum, keeps costs low)
- ✅ Timeout: 540s (max, but functions finish in <1s)
- ✅ Max instances: 10 (prevents runaway scaling)

### 2. **Cloud Storage**
- ✅ Standard storage class (cheapest)
- ✅ Small files only (< 1MB each)
- ✅ No versioning enabled
- ✅ No lifecycle policies needed (data is small)

### 3. **BigQuery**
- ✅ Small dataset (< 1MB)
- ✅ Queries are simple (no complex joins)
- ✅ Using streaming inserts (free tier)
- ✅ No partitioning needed (small data)

### 4. **Cloud Build**
- ✅ Only runs on deployment (not continuous)
- ✅ Uses minimal build time
- ✅ No custom images needed

---

## 🛡️ Safety Measures

### Automatic Cleanup (Optional)
If you want to prevent data accumulation:

```bash
# Delete old BigQuery data (if needed)
bq query --use_legacy_sql=false \
  "DELETE FROM \`maps-platform-20251011-140544.cocktailverse.jobs_clean\` \
   WHERE processed_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)"

# Delete old GCS files (if needed)
gsutil -m rm gs://cocktailverse-raw-maps-platform-20251011-140544/cocktails_*.json
```

### Disable Functions (Emergency Stop)
```bash
# Stop all functions if needed
gcloud functions delete cocktailverse-transform --gen2 --region=us-central1 --quiet
gcloud functions delete cocktailverse-fetch-cocktails --gen2 --region=us-central1 --quiet
```

---

## 📊 Expected Monthly Costs

**Normal Usage (Testing/Development):**
- Cloud Functions: 50 invocations × $0.00 = **$0.00**
- Cloud Storage: 0.01 GB × $0.00 = **$0.00**
- BigQuery: 0.001 GB × $0.00 = **$0.00**
- Cloud Build: 10 minutes × $0.00 = **$0.00**

**Total: $0.00/month** ✅

**Heavy Usage (1000+ records/day):**
- Cloud Functions: 30K invocations × $0.00 = **$0.00** (still free)
- Cloud Storage: 0.1 GB × $0.00 = **$0.00**
- BigQuery: 0.01 GB × $0.00 = **$0.00**

**Total: $0.00/month** ✅

---

## 🚨 If You Exceed Free Tier

**Cloud Functions (after 2M invocations):**
- $0.40 per 1M invocations
- **Our usage: ~$0.00** (way under limit)

**Cloud Storage (after 5 GB):**
- $0.020 per GB/month
- **Our usage: ~$0.00** (way under limit)

**BigQuery (after 10 GB storage):**
- $0.020 per GB/month
- **Our usage: ~$0.00** (way under limit)

**BigQuery Queries (after 1 TB):**
- $5.00 per TB
- **Our usage: ~$0.00** (queries are tiny)

---

## ✅ Cost Checklist

Before deploying:
- [x] Using free tier services only
- [x] Small data volumes (< 1MB)
- [x] Minimal function invocations
- [x] No expensive operations (no ML, no video processing)
- [x] Standard storage class
- [x] No data transfer out of GCP

**You're safe!** This project is designed to stay at **$0/month** indefinitely.

---

## 📞 Quick Cost Check

Run this monthly to verify:
```bash
# Quick cost check script
echo "=== Cost Check ==="
echo "Functions:"
gcloud functions list --format="table(name,status)" 2>/dev/null || echo "No functions"
echo ""
echo "Storage:"
gsutil du -sh gs://cocktailverse-raw-maps-platform-20251011-140544 2>/dev/null || echo "No bucket"
echo ""
echo "BigQuery:"
bq show maps-platform-20251011-140544:cocktailverse 2>/dev/null | grep "Total" || echo "No dataset"
```

---

**Last Updated:** 2025-01-20  
**Status:** ✅ All services within free tier  
**Estimated Cost:** $0.00/month

