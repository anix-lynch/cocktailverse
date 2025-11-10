#!/usr/bin/env python3
# 💬 PHASE 1: Data Transformation
# Purpose: Cloud Function to transform raw cocktail data from GCS and load into BigQuery
#
# Outputs:
#   - Transformed data loaded into BigQuery table
#
# Sample Output:
#   {"statusCode": 200, "message": "Data transformed successfully", "processed_records": 3}

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from google.cloud import storage
from google.cloud import bigquery

# Initialize GCP clients
storage_client = storage.Client()
bq_client = bigquery.Client()

# Environment variables
PROJECT_ID = os.environ.get('PROJECT_ID', '')
DATASET_ID = os.environ.get('DATASET_ID', 'cocktailverse')
TABLE_ID = os.environ.get('TABLE_ID', 'cocktails')
BUCKET_NAME = os.environ.get('BUCKET_NAME', '')

def transform_cocktail_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform and validate cocktail data
    Normalizes fields, validates required data, adds timestamps
    """
    # Handle both single object and array
    if isinstance(raw_data, dict):
        raw_data = [raw_data]
    
    transformed = []
    for cocktail in raw_data:
        transformed_cocktail = {
            'cocktail_id': validate_field(cocktail.get('cocktail_id'), required=True),
            'name': validate_field(cocktail.get('name'), required=True),
            'category': validate_field(cocktail.get('category')),
            'alcoholic': validate_field(cocktail.get('alcoholic')),
            'glass': validate_field(cocktail.get('glass')),
            'instructions': validate_field(cocktail.get('instructions')),
            'ingredients': normalize_ingredients(cocktail.get('ingredients', [])),
            'image_url': validate_field(cocktail.get('image_url')),
            'tags': normalize_tags(cocktail.get('tags', [])),
            'iba': validate_field(cocktail.get('iba')),
            'video_url': validate_field(cocktail.get('video_url')),
            'source': validate_field(cocktail.get('source'), required=True),
            'fetched_at': normalize_timestamp(cocktail.get('fetched_at')),
            'processed_at': datetime.utcnow().isoformat()
        }
        transformed.append(transformed_cocktail)
    return transformed

def validate_field(field_value: Any, required: bool = False) -> str:
    """Validate and clean field values"""
    if field_value is None:
        if required:
            raise ValueError("Required field is missing")
        return ""
    return str(field_value).strip()


def normalize_ingredients(ingredients: Any) -> List[str]:
    """Normalize ingredients list"""
    if not ingredients:
        return []
    if isinstance(ingredients, str):
        return [ing.strip() for ing in ingredients.split(',')]
    if isinstance(ingredients, list):
        return [str(ing).strip() for ing in ingredients if ing]
    return []

def normalize_tags(tags: Any) -> List[str]:
    """Normalize tags list"""
    if not tags:
        return []
    if isinstance(tags, str):
        return [tag.strip() for tag in tags.split(',')]
    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if tag]
    return []

def normalize_timestamp(timestamp_str: str) -> str:
    """Normalize timestamp format"""
    if not timestamp_str:
        return None
    try:
        # Try parsing ISO format
        parsed = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return parsed.isoformat()
    except (ValueError, AttributeError):
        return timestamp_str

def load_to_bigquery(data: List[Dict[str, Any]]) -> bool:
    """Load transformed data into BigQuery"""
    try:
        dataset_ref = bq_client.dataset(DATASET_ID)
        table_ref = dataset_ref.table(TABLE_ID)
        
        # Insert rows
        errors = bq_client.insert_rows_json(table_ref, data)
        if errors:
            print(f"Errors inserting rows: {errors}")
            return False
        print(f"Successfully loaded {len(data)} records to BigQuery")
        return True
    except Exception as e:
        print(f"Error loading to BigQuery: {e}")
        raise

def main(cloud_event):
    """
    Cloud Function entry point (Gen2)
    Triggered by Cloud Storage events
    """
    try:
        # Extract bucket and file info from Cloud Storage event
        data = cloud_event.data
        bucket_name = data.get('bucket', BUCKET_NAME)
        file_name = data.get('name', '')
        
        if not file_name:
            print("No file name in event data")
            return {'statusCode': 400, 'body': 'No file name provided'}
        
        print(f"Processing file: gs://{bucket_name}/{file_name}")
        
        # Download raw data from GCS
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        raw_data = json.loads(blob.download_as_text())
        
        # Transform data (handles both array and single object internally)
        transformed_data = transform_cocktail_data(raw_data)
        
        # Load to BigQuery
        load_to_bigquery(transformed_data)
        
        print(f"Successfully processed {len(transformed_data)} records")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data transformed successfully',
                'processed_records': len(transformed_data),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

# For local testing
if __name__ == "__main__":
    # Test with sample data
    with open('../data/raw/sample_data.json', 'r') as f:
        test_data = json.load(f)
    
    result = transform_cocktail_data(test_data)
    print("Transformed data:")
    print(json.dumps(result, indent=2))

