#!/bin/bash
# 💬 PHASE 1: GCS Bucket Setup
# Purpose: Creates Google Cloud Storage buckets for raw data storage
#
# Outputs:
#   - GCS bucket for raw data (cocktailverse-raw-{PROJECT_ID})
#
# Sample Output:
#   ✅ Created bucket: gs://cocktailverse-raw-{PROJECT_ID}

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
RAW_BUCKET=${BUCKET_NAME:-"cocktailverse-raw-${PROJECT_ID}"}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID not set"
    echo "   Please set PROJECT_ID in .env file or export it"
    exit 1
fi

echo "🍹 Setting up GCS buckets for Cocktailverse"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Raw Bucket: $RAW_BUCKET"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Create raw data bucket
echo "Creating raw data bucket..."
if gsutil ls -b gs://$RAW_BUCKET 2>/dev/null; then
    echo "✅ Bucket '$RAW_BUCKET' already exists"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$RAW_BUCKET
    echo "✅ Created bucket: gs://$RAW_BUCKET"
fi

# Set bucket permissions (make it readable)
gsutil iam ch allUsers:objectViewer gs://$RAW_BUCKET 2>/dev/null || true

echo ""
echo "🎉 GCS setup complete!"
echo ""
echo "Next steps:"
echo "1. Upload data: gsutil cp data/raw/sample_data.json gs://$RAW_BUCKET/"
echo "2. Deploy Cloud Function: ./deploy_gcf.sh"

