#!/usr/bin/env python3
# 💬 PHASE 1: Cocktail Fetch Function
# Purpose: Cloud Function to fetch cocktails from TheCocktailDB API and store in GCS
#
# Outputs:
#   - Fetched cocktail data uploaded to GCS raw bucket (triggers transform function)
#
# Sample Output:
#   {"statusCode": 200, "message": "Successfully fetched 3 cocktails", "count": 3}

import json
import os
import requests
from datetime import datetime
from typing import Dict, Any, List
from google.cloud import storage
import functions_framework
from flask import Request

# Initialize GCP clients
storage_client = storage.Client()

# Environment variables
PROJECT_ID = os.environ.get('PROJECT_ID', '')
BUCKET_NAME = os.environ.get('BUCKET_NAME', '')
COCKTAIL_API_BASE = "https://www.thecocktaildb.com/api/json/v1/1"

def fetch_cocktails(fetch_type: str = 'random', limit: int = 10, search_term: str = '') -> List[Dict[str, Any]]:
    """
    Fetch cocktails from TheCocktailDB API
    """
    cocktails = []
    
    try:
        if fetch_type == 'random':
            # Fetch random cocktails
            for _ in range(limit):
                response = requests.get(f"{COCKTAIL_API_BASE}/random.php", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('drinks') and len(data['drinks']) > 0:
                        cocktails.append(data['drinks'][0])
        elif fetch_type == 'mocktails' or fetch_type == 'non_alcoholic':
            # Fetch non-alcoholic drinks (mocktails)
            response = requests.get(f"{COCKTAIL_API_BASE}/filter.php?a=Non_Alcoholic", timeout=10)
            if response.status_code == 200:
                data = response.json()
                drink_list = data.get('drinks', [])[:limit]
                # Get full details for each drink
                for drink in drink_list:
                    detail_response = requests.get(
                        f"{COCKTAIL_API_BASE}/lookup.php?i={drink['idDrink']}",
                        timeout=10
                    )
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('drinks') and len(detail_data['drinks']) > 0:
                            cocktails.append(detail_data['drinks'][0])
        elif fetch_type == 'popular':
            # Fetch popular cocktails
            response = requests.get(f"{COCKTAIL_API_BASE}/popular.php", timeout=10)
            if response.status_code == 200:
                data = response.json()
                cocktails = data.get('drinks', [])[:limit]
        elif fetch_type == 'search':
            # Search by name
            search_term = search_term or 'margarita'
            response = requests.get(f"{COCKTAIL_API_BASE}/search.php?s={search_term}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                cocktails = data.get('drinks', [])[:limit]
    except Exception as e:
        print(f"Error fetching cocktails: {str(e)}")
        raise
    
    return cocktails

def transform_cocktail_to_format(cocktail: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform TheCocktailDB API response to cocktail format
    """
    # Extract ingredients and measures
    ingredients = []
    measures = []
    for i in range(1, 16):
        ingredient = cocktail.get(f'strIngredient{i}')
        measure = cocktail.get(f'strMeasure{i}')
        if ingredient:
            ingredients.append(ingredient.strip())
            if measure:
                measures.append(measure.strip())
    
    # Create ingredients list with measures
    ingredients_list = []
    for i, ing in enumerate(ingredients):
        if i < len(measures):
            ingredients_list.append(f"{measures[i]} {ing}")
        else:
            ingredients_list.append(ing)
    
    # Extract tags
    tags = []
    if cocktail.get('strTags'):
        tags = [tag.strip() for tag in cocktail.get('strTags', '').split(',') if tag.strip()]
    
    transformed = {
        'cocktail_id': cocktail.get('idDrink', 'UNKNOWN'),
        'name': cocktail.get('strDrink', 'Unknown Cocktail'),
        'category': cocktail.get('strCategory'),
        'alcoholic': cocktail.get('strAlcoholic'),
        'glass': cocktail.get('strGlass'),
        'instructions': cocktail.get('strInstructions', ''),
        'ingredients': ingredients_list,
        'image_url': cocktail.get('strDrinkThumb'),
        'tags': tags,
        'iba': cocktail.get('strIBA'),
        'video_url': cocktail.get('strVideo'),
        'source': 'TheCocktailDB',
        'fetched_at': datetime.utcnow().isoformat()
    }
    
    return transformed

@functions_framework.http
def main(request: Request):
    """
    Cloud Function entry point (HTTP trigger)
    Can be called via HTTP request or Cloud Scheduler
    """
    try:
        # Parse request data
        if request.method == 'GET':
            fetch_type = request.args.get('fetch_type', 'random')
            limit = int(request.args.get('limit', 10))
            search_term = request.args.get('search_term', '')
        else:
            request_json = request.get_json(silent=True) or {}
            fetch_type = request_json.get('fetch_type', 'random')
            limit = request_json.get('limit', 10)
            search_term = request_json.get('search_term', '')
        
        print(f"Fetching cocktails: type={fetch_type}, limit={limit}")
        
        # Fetch cocktails from API
        cocktails = fetch_cocktails(fetch_type=fetch_type, limit=limit, search_term=search_term)
        
        if not cocktails:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'No cocktails found',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }, 404
        
        # Transform to cocktail format
        transformed_cocktails = [transform_cocktail_to_format(c) for c in cocktails]
        
        # Upload to GCS (this will trigger the transform function)
        blob_name = None
        if BUCKET_NAME:
            bucket = storage_client.bucket(BUCKET_NAME)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            blob_name = f"cocktails_{timestamp}.json"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(
                json.dumps(transformed_cocktails, indent=2),
                content_type='application/json'
            )
            print(f"Uploaded {len(transformed_cocktails)} cocktails to gs://{BUCKET_NAME}/{blob_name}")
        else:
            print("Warning: BUCKET_NAME not set, skipping GCS upload")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully fetched and uploaded {len(transformed_cocktails)} cocktails',
                'count': len(transformed_cocktails),
                'gcs_path': f"gs://{BUCKET_NAME}/{blob_name}" if BUCKET_NAME and blob_name else None,
                'timestamp': datetime.utcnow().isoformat()
            })
        }, 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }, 500

# For local testing
if __name__ == "__main__":
    from flask import Flask, Request
    
    app = Flask(__name__)
    
    class MockRequest:
        method = 'GET'
        args = {'fetch_type': 'random', 'limit': '3'}
        def get_json(self, silent=True):
            return None
    
    result = main(MockRequest())
    print(json.dumps(json.loads(result[0]['body']), indent=2))

