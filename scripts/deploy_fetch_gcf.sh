#!/bin/bash
# 💬 PHASE 1: Fetch Cocktail Function Deployment
# Purpose: Deploys the fetch cocktails Cloud Function to GCP
#
# Outputs:
#   - Deployed Cloud Function that fetches cocktails from TheCocktailDB API
#
# Sample Output:
#   ✅ Deployed function: cocktailverse-fetch-cocktails

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
FUNCTION_NAME="cocktailverse-fetch-cocktails"  # Fixed name for fetch function
BUCKET_NAME=${BUCKET_NAME:-"cocktailverse-raw-${PROJECT_ID}"}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID not set"
    echo "   Please set PROJECT_ID in .env file or export it"
    exit 1
fi

echo "🍹 Deploying Fetch Cocktails Cloud Function"
echo "==========================================="
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
gcloud services enable storage.googleapis.com

# Deploy Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=gcf \
    --entry-point=main \
    --trigger-http \
    --no-allow-unauthenticated \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME" \
    --memory=256MB \
    --timeout=540s \
    --min-instances=0 \
    --max-instances=10

echo ""
echo "🎉 Fetch Cocktails Function deployed successfully!"
echo ""
echo "Function URL:"
gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)" || echo "   (Check console for URL)"
echo ""
echo "Test it:"
echo "  curl \"\$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format='value(serviceConfig.uri)')\"?fetch_type=random&limit=3"

