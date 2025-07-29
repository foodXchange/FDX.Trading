-- FoodXchange AI Product Analysis Tables
-- Run this script to create only the necessary tables for AI features

-- Drop existing tables if needed (uncomment to use)
-- DROP TABLE IF EXISTS product_analyses CASCADE;
-- DROP TABLE IF EXISTS product_briefs CASCADE;
-- DROP TABLE IF EXISTS product_images CASCADE;
-- DROP TABLE IF EXISTS ai_insights CASCADE;

-- Product Images table
CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    azure_blob_url TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Analyses table (Computer Vision results)
CREATE TABLE IF NOT EXISTS product_analyses (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES product_images(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50), -- 'ocr', 'object_detection', 'description'
    raw_response JSONB,
    extracted_text TEXT,
    detected_brands TEXT[],
    detected_categories TEXT[],
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Briefs table (GPT-4 generated)
CREATE TABLE IF NOT EXISTS product_briefs (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES product_images(id) ON DELETE CASCADE,
    title VARCHAR(255),
    description TEXT,
    specifications JSONB,
    suggested_categories TEXT[],
    target_market TEXT,
    pricing_insights TEXT,
    sustainability_info TEXT,
    created_by_model VARCHAR(50), -- 'gpt-4', 'gpt-3.5-turbo'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Insights table (market analysis, trends)
CREATE TABLE IF NOT EXISTS ai_insights (
    id SERIAL PRIMARY KEY,
    product_brief_id INTEGER REFERENCES product_briefs(id) ON DELETE CASCADE,
    insight_type VARCHAR(50), -- 'market_trend', 'competitor_analysis', 'demand_forecast'
    insight_data JSONB,
    confidence_level VARCHAR(20), -- 'high', 'medium', 'low'
    valid_until DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_product_images_uploaded_by ON product_images(uploaded_by);
CREATE INDEX idx_product_analyses_image_id ON product_analyses(image_id);
CREATE INDEX idx_product_briefs_image_id ON product_briefs(image_id);
CREATE INDEX idx_ai_insights_brief_id ON ai_insights(product_brief_id);

-- Sample view for easy querying
CREATE OR REPLACE VIEW product_analysis_summary AS
SELECT 
    pi.id as image_id,
    pi.file_name,
    pi.azure_blob_url,
    pb.title as product_title,
    pb.description as product_description,
    pb.suggested_categories,
    pa.detected_brands,
    pa.confidence_score,
    pb.created_at as analysis_date
FROM product_images pi
LEFT JOIN product_briefs pb ON pi.id = pb.image_id
LEFT JOIN product_analyses pa ON pi.id = pa.image_id
ORDER BY pi.created_at DESC;