#!/usr/bin/env python3
"""
🍹 Cocktailverse Dashboard
Streamlit app to visualize cocktail data from BigQuery
"""

import streamlit as st
import pandas as pd
from google.cloud import bigquery
import os
from typing import Optional

# Page config
st.set_page_config(
    page_title="Cocktailverse Dashboard",
    page_icon="🍹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize BigQuery client
@st.cache_resource
def init_bigquery_client():
    """Initialize BigQuery client with cached connection"""
    project_id = os.getenv('PROJECT_ID', 'maps-platform-20251011-140544')
    
    # Try to get credentials from Streamlit secrets (for Streamlit Cloud)
    credentials = None
    try:
        import json
        from google.oauth2 import service_account
        
        # Check if secrets are available (avoid "No secrets files found" warning)
        if hasattr(st, 'secrets') and st.secrets is not None:
            try:
                gcp_secrets = st.secrets.get('gcp', {})
                if gcp_secrets and 'service_account_key' in gcp_secrets:
                    service_account_info = json.loads(gcp_secrets['service_account_key'])
                    credentials = service_account.Credentials.from_service_account_info(
                        service_account_info
                    )
            except (AttributeError, KeyError, TypeError):
                # Secrets not configured, use default credentials
                pass
    except Exception:
        # Silently fall back to default credentials (for Cloud Run / local dev)
        pass
    
    try:
        if credentials:
            client = bigquery.Client(project=project_id, credentials=credentials)
        else:
            # Try default credentials (for local development)
            client = bigquery.Client(project=project_id)
        return client, project_id
    except Exception as e:
        st.error(f"Failed to connect to BigQuery: {e}")
        st.info("""
        **For Streamlit Cloud:**
        1. Go to Settings → Secrets
        2. Add your GCP service account JSON:
        ```toml
        [gcp]
        service_account_key = \"\"\"
        {paste your service account JSON here}
        \"\"\"
        ```
        
        **For local development:**
        Run: `gcloud auth application-default login`
        """)
        return None, project_id

# Get client
bq_client, PROJECT_ID = init_bigquery_client()
DATASET_ID = os.getenv('DATASET_ID', 'cocktailverse')
TABLE_ID = os.getenv('TABLE_ID', 'cocktails')

# Header with ATS keywords
st.title("🍹 Cocktailverse: GCP BigQuery ETL Pipeline Dashboard")
st.markdown("**Real-time Analytics | Python • BigQuery • Cloud Run • ETL • API Integration**")

if not bq_client:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Add cost estimate sidebar (mocktailverse pattern)
st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 GCP Cost Estimate")
st.sidebar.caption("**Cloud Run**: $0.05/month (Free tier)")
st.sidebar.caption("**BigQuery Storage**: $0.10/month (Free tier)")
st.sidebar.caption("**BigQuery Queries**: $0.01/month (Free tier)")
st.sidebar.caption("**Total Estimated**: **$0.16/month**")
st.sidebar.markdown("*Based on typical usage with GCP Free Tier*")

# Query cocktails
@st.cache_data(ttl=300)  # Cache for 5 minutes
def query_cocktails(limit: int = 1000):
    """Query all cocktails from BigQuery"""
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
        source,
        fetched_at,
        processed_at
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY processed_at DESC
    LIMIT {limit}
    """
    try:
        df = bq_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

# Get data
df = query_cocktails()

if df.empty:
    st.warning("No cocktail data found. Make sure data has been loaded to BigQuery.")
    st.info("Run the fetch function to load cocktails: `gcloud functions call cocktailverse-fetch-cocktails`")
    st.stop()

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cocktails", len(df))
col2.metric("Categories", df['category'].nunique() if 'category' in df.columns else 0)
col3.metric("Alcoholic Types", df['alcoholic'].nunique() if 'alcoholic' in df.columns else 0)
col4.metric("Data Source", df['source'].iloc[0] if 'source' in df.columns and len(df) > 0 else "N/A")

st.divider()

# Filters
category_filter = st.sidebar.multiselect(
    "Category",
    options=sorted(df['category'].dropna().unique()) if 'category' in df.columns else [],
    default=[]
)

alcoholic_filter = st.sidebar.multiselect(
    "Alcoholic Type",
    options=sorted(df['alcoholic'].dropna().unique()) if 'alcoholic' in df.columns else [],
    default=[]
)

# Apply filters
filtered_df = df.copy()
if category_filter:
    filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
if alcoholic_filter:
    filtered_df = filtered_df[filtered_df['alcoholic'].isin(alcoholic_filter)]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🍸 Cocktails", "📈 Analytics", "🔍 Search"])

with tab1:
    st.header("Overview")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'category' in filtered_df.columns:
            category_counts = filtered_df['category'].value_counts().head(10)
            st.subheader("Top Categories")
            st.bar_chart(category_counts)
    
    with col2:
        if 'alcoholic' in filtered_df.columns:
            alcoholic_counts = filtered_df['alcoholic'].value_counts()
            st.subheader("Alcoholic Distribution")
            st.bar_chart(alcoholic_counts)
    
    # Ingredients analysis
    st.subheader("Most Common Ingredients")
    if 'ingredients' in filtered_df.columns:
        all_ingredients = []
        for ingredients_list in filtered_df['ingredients'].dropna():
            if isinstance(ingredients_list, list):
                all_ingredients.extend(ingredients_list)
            elif isinstance(ingredients_list, str):
                all_ingredients.append(ingredients_list)
        
        if all_ingredients:
            ingredient_df = pd.DataFrame({'ingredient': all_ingredients})
            top_ingredients = ingredient_df['ingredient'].value_counts().head(15)
            st.bar_chart(top_ingredients)

with tab2:
    st.header("Cocktail List")
    
    # Display cocktails
    for idx, row in filtered_df.head(50).iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(row.get('image_url')):
                    st.image(row['image_url'], width=150)
                else:
                    st.write("🍹")
            
            with col2:
                st.subheader(row.get('name', 'Unknown'))
                
                cols = st.columns(4)
                if 'category' in row and pd.notna(row['category']):
                    cols[0].write(f"**Category:** {row['category']}")
                if 'alcoholic' in row and pd.notna(row['alcoholic']):
                    cols[1].write(f"**Type:** {row['alcoholic']}")
                if 'glass' in row and pd.notna(row['glass']):
                    cols[2].write(f"**Glass:** {row['glass']}")
                if 'iba' in row and pd.notna(row['iba']):
                    cols[3].write(f"**IBA:** {row['iba']}")
                
                # Check ingredients - extract first, then check type
                if 'ingredients' in row:
                    try:
                        ingredients = row['ingredients']
                        if isinstance(ingredients, list) and len(ingredients) > 0:
                            st.write(f"**Ingredients:** {', '.join(str(i) for i in ingredients[:5])}")
                        elif ingredients is not None and str(ingredients).strip():
                            st.write(f"**Ingredients:** {str(ingredients)}")
                    except (ValueError, TypeError):
                        pass  # Skip if ingredients is problematic
                
                if 'instructions' in row and pd.notna(row['instructions']):
                    with st.expander("Instructions"):
                        st.write(row['instructions'])
            
            st.divider()

with tab3:
    st.header("Analytics")
    
    # Category breakdown
    if 'category' in filtered_df.columns:
        st.subheader("Cocktails by Category")
        category_stats = filtered_df.groupby('category').agg({
            'cocktail_id': 'count',
            'name': 'nunique'
        }).rename(columns={'cocktail_id': 'count', 'name': 'unique'})
        st.dataframe(category_stats, use_container_width=True)
    
    # Glass types
    if 'glass' in filtered_df.columns:
        st.subheader("Glass Types")
        glass_counts = filtered_df['glass'].value_counts().head(10)
        st.bar_chart(glass_counts)
    
    # IBA cocktails
    if 'iba' in filtered_df.columns:
        iba_cocktails = filtered_df[filtered_df['iba'].notna()]
        if len(iba_cocktails) > 0:
            st.subheader(f"IBA Cocktails ({len(iba_cocktails)})")
            iba_df = iba_cocktails[['name', 'category', 'iba']].drop_duplicates()
            st.dataframe(iba_df, use_container_width=True)

with tab4:
    st.header("Search Cocktails")
    
    search_term = st.text_input("Search by name, ingredient, or category")
    
    if search_term:
        search_lower = search_term.lower()
        search_results = filtered_df[
            filtered_df['name'].str.contains(search_lower, case=False, na=False) |
            filtered_df['category'].str.contains(search_lower, case=False, na=False) |
            filtered_df['ingredients'].astype(str).str.contains(search_lower, case=False, na=False)
        ]
        
        st.write(f"Found {len(search_results)} results")
        
        for idx, row in search_results.iterrows():
            st.write(f"**{row.get('name', 'Unknown')}** - {row.get('category', 'N/A')}")
            # Check ingredients - extract first, then check type
            if 'ingredients' in row:
                try:
                    ingredients = row['ingredients']
                    if isinstance(ingredients, list) and len(ingredients) > 0:
                        st.write(f"Ingredients: {', '.join(str(i) for i in ingredients)}")
                    elif ingredients is not None and str(ingredients).strip():
                        st.write(f"Ingredients: {str(ingredients)}")
                except (ValueError, TypeError):
                    pass  # Skip if ingredients is problematic
            st.divider()

# Footer
st.divider()
st.markdown(f"**Data Source:** {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
st.caption(f"Last updated: {filtered_df['processed_at'].max() if 'processed_at' in filtered_df.columns else 'N/A'}")

