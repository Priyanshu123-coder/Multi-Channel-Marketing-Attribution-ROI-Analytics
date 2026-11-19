-- ==============================================================================
-- 03_kpis.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Executive KPI Summary & Core Business Formulas
-- ==============================================================================

-- KPI Definitions & Mathematical Formulas:
-- 1. Conversion Rate (CR): (Total Conversions / Total Unique Visitors Reached) * 100
-- 2. Click-Through Rate (CTR): (Total Clicks / Total Impressions) * 100
-- 3. Cost Per Click (CPC): Total Ad Spend / Total Clicks
-- 4. Customer Acquisition Cost (CAC): Total Marketing Spend / Total Converted Customers
-- 5. Return on Ad Spend (ROAS): Total Revenue / Total Marketing Spend
-- 6. Average Order Value (AOV): Total Revenue / Total Conversions
-- 7. Customer Lifetime Value (CLV proxy): AOV * 1.25 * 0.75 margin

WITH metrics_summary AS (
    SELECT 
        (SELECT COUNT(DISTINCT user_id) FROM users) AS total_registered_users,
        (SELECT COUNT(DISTINCT user_id) FROM touchpoints) AS total_visitors_reached,
        (SELECT COUNT(*) FROM conversions) AS total_conversions,
        (SELECT COUNT(DISTINCT user_id) FROM conversions) AS unique_converted_customers,
        (SELECT SUM(revenue) FROM conversions) AS total_revenue,
        (SELECT SUM(spend) FROM spend) AS total_spend,
        (SELECT SUM(impressions) FROM spend) AS total_impressions,
        (SELECT SUM(clicks) FROM spend) AS total_clicks
)
SELECT 
    -- Spend & Volume
    ROUND(total_spend, 2) AS total_spend_usd,
    ROUND(total_revenue, 2) AS total_revenue_usd,
    total_conversions,
    unique_converted_customers,
    total_visitors_reached,
    total_impressions,
    total_clicks,
    
    -- Rates & Efficiency
    ROUND((CAST(total_clicks AS FLOAT) / total_impressions) * 100, 2) AS blended_ctr_pct,
    ROUND(total_spend / total_clicks, 2) AS blended_cpc_usd,
    ROUND((CAST(total_conversions AS FLOAT) / total_visitors_reached) * 100, 2) AS visitor_to_conversion_rate_pct,
    ROUND((CAST(unique_converted_customers AS FLOAT) / total_registered_users) * 100, 2) AS user_conversion_rate_pct,
    
    -- Financial ROI & Unit Economics
    ROUND(total_spend / unique_converted_customers, 2) AS blended_cac_usd,
    ROUND(total_revenue / total_conversions, 2) AS average_order_value_usd,
    ROUND(total_revenue / total_spend, 2) AS blended_roas,
    
    -- 12-Month Projected CLV (AOV * 1.25 repeat rate * 75% edtech margin)
    ROUND((total_revenue / total_conversions) * 1.25 * 0.75, 2) AS projected_clv_usd,
    ROUND(((total_revenue / total_conversions) * 1.25 * 0.75) / (total_spend / unique_converted_customers), 2) AS clv_to_cac_ratio
FROM metrics_summary;
