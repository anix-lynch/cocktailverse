#!/usr/bin/env python3
# 💬 PHASE 1: API Test Harness
# Purpose: Local FastAPI server to query BigQuery cocktail data
#
# Outputs:
#   - REST API endpoints for querying processed cocktail data
#
# Sample Output:
#   {"jobs": [...], "total_count": 3, "timestamp": "2025-01-20T..."}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
from google.cloud import bigquery

# Initialize FastAPI app
app = FastAPI(
    title="Cocktailverse Test Harness",
    description="Local FastAPI endpoint to query BigQuery data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Cocktail(BaseModel):
    cocktail_id: str
    name: str
    category: Optional[str] = None
    alcoholic: Optional[str] = None
    glass: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: List[str] = []
    image_url: Optional[str] = None
    tags: List[str] = []
    iba: Optional[str] = None
    video_url: Optional[str] = None
    source: Optional[str] = None
    fetched_at: Optional[str] = None
    processed_at: Optional[str] = None

class ResultsResponse(BaseModel):
    cocktails: List[Cocktail]
    total_count: int
    timestamp: str

# GCP Configuration
PROJECT_ID = os.getenv('PROJECT_ID', '')
DATASET_ID = os.getenv('DATASET_ID', 'cocktailverse')
TABLE_ID = os.getenv('TABLE_ID', 'cocktails')

# Initialize BigQuery client
bq_client = None
if PROJECT_ID:
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        print(f"✅ Connected to BigQuery: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to BigQuery: {e}")
        print("   Running in mock mode - will return empty results")

def query_bigquery(limit: int = 100) -> List[Dict[str, Any]]:
    """Query BigQuery for cocktail data"""
    if not bq_client:
        return []
    
    try:
        query = f"""
        SELECT 
            cocktail_id,
            name,
            category,
            alcoholic,
            glass,
            instructions,
            ingredients,
            image_url,
            tags,
            iba,
            video_url,
            source,
            fetched_at,
            processed_at
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        ORDER BY processed_at DESC
        LIMIT {limit}
        """
        
        query_job = bq_client.query(query)
        results = query_job.result()
        
        cocktails = []
        for row in results:
            cocktail = {
                'cocktail_id': row.cocktail_id,
                'name': row.name,
                'category': row.category,
                'alcoholic': row.alcoholic,
                'glass': row.glass,
                'instructions': row.instructions,
                'ingredients': list(row.ingredients) if row.ingredients else [],
                'image_url': row.image_url,
                'tags': list(row.tags) if row.tags else [],
                'iba': row.iba,
                'video_url': row.video_url,
                'source': row.source,
                'fetched_at': row.fetched_at.isoformat() if row.fetched_at else None,
                'processed_at': row.processed_at.isoformat() if row.processed_at else None
            }
            cocktails.append(cocktail)
        
        return cocktails
    except Exception as e:
        print(f"Error querying BigQuery: {e}")
        return []

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cocktailverse Test Harness",
        "version": "1.0.0",
        "endpoints": {
            "cocktails": "GET /cocktails - Query processed cocktail data from BigQuery",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "bigquery_configured": bq_client is not None,
        "project": PROJECT_ID,
        "dataset": DATASET_ID,
        "table": TABLE_ID
    }

@app.get("/cocktails", response_model=ResultsResponse)
async def get_cocktails(limit: int = 100):
    """Retrieve processed cocktail data from BigQuery"""
    cocktails_data = query_bigquery(limit=limit)
    
    return ResultsResponse(
        cocktails=[Cocktail(**cocktail) for cocktail in cocktails_data],
        total_count=len(cocktails_data),
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "bigquery_configured": bq_client is not None,
        "project": PROJECT_ID
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

