#!/bin/bash
# 💬 PHASE 1: Cloud Function Deployment
# Purpose: Deploys the transform Cloud Function to GCP
#
# Outputs:
#   - Deployed Cloud Function triggered by GCS uploads
#
# Sample Output:
#   ✅ Deployed function: cocktailverse-transform

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
FUNCTION_NAME=${FUNCTION_NAME:-"cocktailverse-transform"}
DATASET_ID=${DATASET_ID:-"cocktailverse"}
TABLE_ID=${TABLE_ID:-"cocktails"}
BUCKET_NAME=${BUCKET_NAME:-"cocktailverse-raw-${PROJECT_ID}"}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID not set"
    echo "   Please set PROJECT_ID in .env file or export it"
    exit 1
fi

echo "🍹 Deploying Cloud Function"
echo "==========================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Function: $FUNCTION_NAME"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com

# Create BigQuery dataset if it doesn't exist
echo "Setting up BigQuery dataset..."
bq show $PROJECT_ID:$DATASET_ID 2>/dev/null || bq mk --dataset --location=US $PROJECT_ID:$DATASET_ID

# Create BigQuery table from schema
echo "Creating BigQuery table..."
bq show $PROJECT_ID:$DATASET_ID.$TABLE_ID 2>/dev/null || \
    bq mk --table \
        --schema=bq/schema.json \
        $PROJECT_ID:$DATASET_ID.$TABLE_ID

# Deploy Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=gcf \
    --entry-point=cloud_function_handler \
    --trigger-bucket=$BUCKET_NAME \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,DATASET_ID=$DATASET_ID,TABLE_ID=$TABLE_ID,BUCKET_NAME=$BUCKET_NAME" \
    --memory=256MB \
    --timeout=540s \
    --min-instances=0 \
    --max-instances=10

echo ""
echo "🎉 Cloud Function deployed successfully!"
echo ""
echo "Function URL:"
gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)" || echo "   (Check console for URL)"
echo ""
echo "Test it:"
echo "  gsutil cp data/raw/sample_data.json gs://$BUCKET_NAME/"

