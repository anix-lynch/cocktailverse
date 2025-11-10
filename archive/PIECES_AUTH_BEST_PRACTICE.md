# 🔐 Google Cloud Auth - Smooth Setup (Pieces Snippet)

**Tags:** `gcp` `authentication` `gcloud` `service-account` `best-practice` `cocktailverse`

## Why This Works So Smooth

This is the **Service Account OAuth2 pattern** (enterprise/backend) - perfect for Cloud Functions, BigQuery, and GCS. It's smooth because:
- ✅ Auto-detects credentials (no manual key management)
- ✅ Works seamlessly with `google-cloud-*` Python SDKs
- ✅ Credentials stored securely in `~/.config/gcloud/`
- ✅ One-time setup, works forever (until tokens expire)

## The Smooth 3-Step Process

### Step 1: User Authentication
```bash
gcloud auth login
```
- Opens browser automatically
- Select your Google account
- Done in 30 seconds

### Step 2: Application Default Credentials
```bash
gcloud auth application-default login --quiet
```
- Opens browser again (one more click)
- Saves to `~/.config/gcloud/application_default_credentials.json`
- Python SDKs auto-detect this file
- `--quiet` flag for non-interactive use

### Step 3: Enable Required APIs (One Command)
```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  --project=YOUR_PROJECT_ID
```

## Code Pattern (Auto-Detection)

```python
from google.cloud import storage
from google.cloud import bigquery

# These automatically use ~/.config/gcloud/application_default_credentials.json
storage_client = storage.Client()
bq_client = bigquery.Client()

# No credentials needed in code!
bucket = storage_client.bucket(BUCKET_NAME)
```

## Free Tier APIs Enabled

All these are **FREE** within limits:
- **Cloud Functions**: 2M invocations/month
- **Cloud Build**: 120 build-minutes/day  
- **BigQuery**: 1 TB queries/month, 10 GB storage
- **Cloud Storage**: 5 GB/month

## Verification

```bash
# Check auth status
gcloud auth list

# Check project
gcloud config get-value project

# Verify APIs enabled
gcloud services list --enabled \
  --filter="name:cloudfunctions.googleapis.com OR name:bigquery.googleapis.com OR name:storage.googleapis.com"
```

## When to Use This Pattern

✅ **Use this (Service Account OAuth2) for:**
- Backend services
- Cloud Functions
- BigQuery operations
- GCS operations
- Server-to-server communication

❌ **Don't use this for:**
- Frontend/client-side (use API key pattern instead)
- Public web apps (use API key with restrictions)

## Project Context

**Project:** Cocktailverse  
**Pattern:** Service Account OAuth2 (backend)  
**Setup Time:** ~2 minutes (including browser clicks)  
**Complexity:** ⭐⭐ (Simple once you know the steps)

## Related Files

- `.cursorrules` - Documents this pattern for Cursor AI
- `AUTH_SETUP.md` - Detailed setup guide
- `gcf/fetch_cocktails.py` - Example usage
- `gcf/transform.py` - Example usage

---

**Last Updated:** 2025-01-XX  
**Status:** ✅ Tested and working smoothly

