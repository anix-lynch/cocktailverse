#!/bin/bash
# Remove BigQuery table to recreate with new schema (without salary columns)

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${PROJECT_ID:-"maps-platform-20251011-140544"}
DATASET_ID=${DATASET_ID:-"cocktailverse"}
TABLE_ID=${TABLE_ID:-"jobs_clean"}

echo "🗑️  Removing BigQuery table to recreate with clean schema"
echo "========================================================"
echo "Project ID: $PROJECT_ID"
echo "Dataset: $DATASET_ID"
echo "Table: $TABLE_ID"
echo ""

# Check if table exists
if bq show $PROJECT_ID:$DATASET_ID.$TABLE_ID 2>/dev/null; then
    echo "✅ Table exists, removing..."
    bq rm -f -t $PROJECT_ID:$DATASET_ID.$TABLE_ID
    echo "✅ Table removed successfully!"
else
    echo "ℹ️  Table does not exist (nothing to remove)"
fi

echo ""
echo "Next step: Run ./scripts/deploy_gcf.sh to recreate table with new schema"

