-- ============================================================
-- VENDOR COMPARISON SYSTEM - DATABASE MIGRATION
-- ============================================================
-- Run this SQL on Railway PostgreSQL Database
-- ============================================================

-- 1. UPDATE EXISTING products TABLE
-- Add new comparison fields to products table

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS freshness_level VARCHAR(20) DEFAULT 'TODAY',
ADD COLUMN IF NOT EXISTS quality_tier VARCHAR(20) DEFAULT 'GOOD',
ADD COLUMN IF NOT EXISTS certification VARCHAR(255),
ADD COLUMN IF NOT EXISTS stock_quantity FLOAT DEFAULT 0;

-- Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_products_freshness ON products(freshness_level);
CREATE INDEX IF NOT EXISTS idx_products_quality_tier ON products(quality_tier);

-- ============================================================

-- 2. CREATE vendor_ratings_cache TABLE
-- Stores aggregated vendor ratings for fast comparison

CREATE TABLE IF NOT EXISTS vendor_ratings_cache (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Rating components (aggregated from product_reviews)
    avg_quality_rating FLOAT DEFAULT 0.0,
    avg_punctuality_rating FLOAT DEFAULT 0.0,
    avg_communication_rating FLOAT DEFAULT 0.0,
    overall_rating FLOAT DEFAULT 0.0,
    
    -- Performance metrics
    total_reviews INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    on_time_rate FLOAT DEFAULT 0.0,
    repeat_customer_rate FLOAT DEFAULT 0.0,
    
    -- Timestamps
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_vendor_ratings_vendor ON vendor_ratings_cache(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_ratings_overall ON vendor_ratings_cache(overall_rating);

-- ============================================================

-- 3. CREATE vendor_delivery_metrics TABLE
-- Tracks delivery performance for each vendor

CREATE TABLE IF NOT EXISTS vendor_delivery_metrics (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Delivery time metrics (in minutes)
    avg_delivery_time INTEGER DEFAULT 0,
    min_delivery_time INTEGER DEFAULT 0,
    max_delivery_time INTEGER DEFAULT 0,
    
    -- Delivery performance counts
    delivery_on_time_count INTEGER DEFAULT 0,
    delivery_late_count INTEGER DEFAULT 0,
    total_deliveries INTEGER DEFAULT 0,
    
    -- Timestamps
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast lookup
CREATE INDEX IF NOT EXISTS idx_vendor_delivery_vendor ON vendor_delivery_metrics(vendor_id);

-- ============================================================

-- 4. CREATE product_comparison TABLE
-- Logs retailer comparison actions for analytics and ML

CREATE TABLE IF NOT EXISTS product_comparison (
    id SERIAL PRIMARY KEY,
    comparison_id VARCHAR(36) NOT NULL UNIQUE,  -- UUID
    
    retailer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_name VARCHAR(100) NOT NULL,
    
    -- Comparison data (stored as JSON)
    vendors_compared TEXT NOT NULL,  -- JSON array: [123, 456, 789]
    selected_vendor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Metadata
    sort_preference VARCHAR(50),  -- price, rating, delivery, value
    filters_applied TEXT,  -- JSON: {"min_price": 30, "max_price": 50}
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_product_comparison_retailer ON product_comparison(retailer_id);
CREATE INDEX IF NOT EXISTS idx_product_comparison_product ON product_comparison(product_name);
CREATE INDEX IF NOT EXISTS idx_product_comparison_id ON product_comparison(comparison_id);
CREATE INDEX IF NOT EXISTS idx_product_comparison_created ON product_comparison(created_at);

-- ============================================================

-- 5. SEED INITIAL DATA for vendor_ratings_cache
-- Create default rating cache for all existing vendors

INSERT INTO vendor_ratings_cache (vendor_id, avg_quality_rating, avg_punctuality_rating, avg_communication_rating, overall_rating, success_rate, on_time_rate)
SELECT 
    u.id,
    4.0,  -- Default quality rating
    4.0,  -- Default punctuality rating
    4.0,  -- Default communication rating
    4.0,  -- Default overall rating
    95.0, -- Default success rate (95%)
    90.0  -- Default on-time rate (90%)
FROM users u
WHERE u.user_type = 'vendor'
ON CONFLICT (vendor_id) DO NOTHING;

-- ============================================================

-- 6. SEED INITIAL DATA for vendor_delivery_metrics
-- Create default delivery metrics for all existing vendors

INSERT INTO vendor_delivery_metrics (vendor_id, avg_delivery_time, min_delivery_time, max_delivery_time)
SELECT 
    u.id,
    240,  -- Default avg: 4 hours (240 minutes)
    120,  -- Default min: 2 hours (120 minutes)
    360   -- Default max: 6 hours (360 minutes)
FROM users u
WHERE u.user_type = 'vendor'
ON CONFLICT (vendor_id) DO NOTHING;

-- ============================================================

-- 7. UPDATE EXISTING PRODUCTS with default values
-- Set default values for new comparison fields

UPDATE products 
SET 
    freshness_level = 'TODAY',
    quality_tier = 'GOOD',
    stock_quantity = quantity
WHERE freshness_level IS NULL OR stock_quantity IS NULL;

-- ============================================================

-- 8. VERIFICATION QUERIES
-- Run these to verify tables were created successfully

-- Check vendor_ratings_cache
SELECT COUNT(*) as vendor_cache_count FROM vendor_ratings_cache;

-- Check vendor_delivery_metrics
SELECT COUNT(*) as delivery_metrics_count FROM vendor_delivery_metrics;

-- Check product_comparison table exists
SELECT COUNT(*) as comparison_log_count FROM product_comparison;

-- Check products table updated
SELECT 
    product_name, 
    freshness_level, 
    quality_tier, 
    stock_quantity 
FROM products 
LIMIT 5;

-- ============================================================
-- MIGRATION COMPLETE!
-- ============================================================

-- Summary:
-- ✅ products table updated with 4 new columns
-- ✅ vendor_ratings_cache table created
-- ✅ vendor_delivery_metrics table created  
-- ✅ product_comparison table created
-- ✅ All indexes created
-- ✅ Initial data seeded for existing vendors
-- ============================================================
