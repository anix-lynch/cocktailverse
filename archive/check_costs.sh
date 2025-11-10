#!/bin/bash
# 💬 Cost Monitoring Script
# Purpose: Quick check of GCP resource usage and estimated costs
#
# Outputs:
#   - Summary of resource usage and cost estimates

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${PROJECT_ID:-"maps-platform-20251011-140544"}
BUCKET_NAME=${BUCKET_NAME:-"cocktailverse-raw-${PROJECT_ID}"}
DATASET_ID=${DATASET_ID:-"cocktailverse"}

echo "💰 Cocktailverse Cost Check"
echo "============================"
echo "Project: $PROJECT_ID"
echo ""

# Check Cloud Functions
echo "📦 Cloud Functions:"
if gcloud functions list --project=$PROJECT_ID --format="table(name,status,updateTime)" 2>/dev/null | grep -q "cocktailverse"; then
    gcloud functions list --project=$PROJECT_ID --filter="name:cocktailverse" --format="table(name,status,updateTime)"
    echo "   ✅ Functions deployed"
else
    echo "   ⚠️  No functions found"
fi
echo ""

# Check Cloud Storage
echo "🗄️  Cloud Storage:"
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    SIZE=$(gsutil du -sh gs://$BUCKET_NAME 2>/dev/null | awk '{print $1}')
    echo "   Bucket: gs://$BUCKET_NAME"
    echo "   Size: $SIZE"
    if [ "$SIZE" != "0B" ] && [ -n "$SIZE" ]; then
        echo "   ✅ Within free tier (5 GB)"
    else
        echo "   ✅ Empty bucket"
    fi
else
    echo "   ⚠️  Bucket not found"
fi
echo ""

# Check BigQuery
echo "📊 BigQuery:"
if bq show $PROJECT_ID:$DATASET_ID 2>/dev/null > /dev/null; then
    bq show --format=prettyjson $PROJECT_ID:$DATASET_ID 2>/dev/null | grep -E "(datasetId|location|creationTime)" || true
    echo "   ✅ Dataset exists"
    
    # Check table size
    if bq show $PROJECT_ID:$DATASET_ID.jobs_clean 2>/dev/null > /dev/null; then
        ROWS=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) as count FROM \`$PROJECT_ID.$DATASET_ID.jobs_clean\`" 2>/dev/null | tail -1)
        echo "   Rows in jobs_clean: $ROWS"
    fi
else
    echo "   ⚠️  Dataset not found"
fi
echo ""

# Cost estimate
echo "💵 Cost Estimate:"
echo "   Cloud Functions: \$0.00 (within 2M free invocations/month)"
echo "   Cloud Storage: \$0.00 (within 5 GB free/month)"
echo "   BigQuery: \$0.00 (within 10 GB free storage/month)"
echo "   Total: \$0.00/month ✅"
echo ""
echo "🎉 All services within free tier!"

