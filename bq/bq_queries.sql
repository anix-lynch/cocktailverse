-- 💬 PHASE 1: BigQuery Analytics Queries
-- Purpose: SQL queries to analyze processed cocktail data
--
-- Outputs:
--   - Cocktail count by ingredient
--   - Cocktails by category
--   - Most common ingredients
--   - Cocktails by alcoholic type
--   - Top cocktails by data source

-- Cocktail count by ingredient
SELECT 
    ingredient,
    COUNT(*) as cocktail_count
FROM (
    SELECT 
        cocktail_id,
        name,
        ingredients,
        ingredient
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`,
    UNNEST(ingredients) as ingredient
)
GROUP BY ingredient
ORDER BY cocktail_count DESC
LIMIT 20;

-- Cocktails by category
SELECT 
    category,
    COUNT(*) as cocktail_count,
    COUNT(DISTINCT name) as unique_cocktails
FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
WHERE category IS NOT NULL
GROUP BY category
ORDER BY cocktail_count DESC;

-- Most common ingredients across all cocktails
SELECT 
    ingredient,
    COUNT(DISTINCT cocktail_id) as cocktail_count,
    COUNT(*) as total_occurrences
FROM (
    SELECT 
        cocktail_id,
        name,
        ingredients
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
),
UNNEST(ingredients) as ingredient
GROUP BY ingredient
ORDER BY cocktail_count DESC
LIMIT 30;

-- Cocktails by alcoholic type
SELECT 
    alcoholic,
    COUNT(*) as cocktail_count,
    COUNT(DISTINCT category) as unique_categories
FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
WHERE alcoholic IS NOT NULL
GROUP BY alcoholic
ORDER BY cocktail_count DESC;

-- Top cocktails by data source
SELECT 
    source,
    COUNT(*) as cocktail_count,
    COUNT(DISTINCT category) as unique_categories
FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
GROUP BY source
ORDER BY cocktail_count DESC;

-- Cocktails with most ingredients (complexity)
SELECT 
    name,
    category,
    ARRAY_LENGTH(ingredients) as ingredient_count,
    ingredients
FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
ORDER BY ingredient_count DESC
LIMIT 20;

