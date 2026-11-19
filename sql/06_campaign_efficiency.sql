-- ==============================================================================
-- 06_campaign_efficiency.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Campaign-Level Efficiency Ranking, ROAS, CAC, and Performance Tiers
-- ==============================================================================

WITH campaign_spend_summary AS (
    SELECT 
        s.campaign_id,
        c.name AS campaign_name,
        c.channel,
        c.objective,
        ROUND(SUM(s.spend), 2) AS total_spend,
        SUM(s.impressions) AS total_impressions,
        SUM(s.clicks) AS total_clicks,
        ROUND(CASE WHEN SUM(s.impressions) > 0 
                   THEN (CAST(SUM(s.clicks) AS FLOAT) / SUM(s.impressions)) * 100 
                   ELSE 0 END, 2) AS ctr_pct,
        ROUND(CASE WHEN SUM(s.clicks) > 0 
                   THEN SUM(s.spend) / SUM(s.clicks) 
                   ELSE 0 END, 2) AS cpc
    FROM spend s
    JOIN campaigns c ON s.campaign_id = c.campaign_id
    GROUP BY s.campaign_id, c.name, c.channel, c.objective
),
pre_conversion_touches AS (
    SELECT 
        c.conversion_id,
        c.revenue,
        t.campaign_id,
        ROW_NUMBER() OVER (PARTITION BY c.conversion_id ORDER BY t.timestamp DESC) AS touch_rank_desc,
        COUNT(*) OVER (PARTITION BY c.conversion_id) AS total_touches
    FROM conversions c
    JOIN touchpoints t ON c.user_id = t.user_id AND t.timestamp <= c.timestamp
),
campaign_attribution AS (
    SELECT 
        campaign_id,
        -- Last-touch attribution
        SUM(CASE WHEN touch_rank_desc = 1 THEN 1.0 ELSE 0.0 END) AS last_touch_conversions,
        SUM(CASE WHEN touch_rank_desc = 1 THEN revenue ELSE 0.0 END) AS last_touch_revenue,
        -- Linear attribution
        SUM(1.0 / total_touches) AS linear_conversions,
        SUM((1.0 / total_touches) * revenue) AS linear_revenue
    FROM pre_conversion_touches
    GROUP BY campaign_id
)
SELECT 
    cs.campaign_id,
    cs.campaign_name,
    cs.channel,
    cs.objective,
    cs.total_spend,
    cs.total_clicks,
    cs.cpc,
    ROUND(COALESCE(ca.linear_conversions, 0), 1) AS attributed_conversions,
    ROUND(COALESCE(ca.linear_revenue, 0), 2) AS attributed_revenue,
    
    -- Linear ROAS & CAC
    ROUND(CASE WHEN cs.total_spend > 0 
               THEN COALESCE(ca.linear_revenue, 0) / cs.total_spend 
               ELSE 999.0 END, 2) AS roas,
               
    ROUND(CASE WHEN COALESCE(ca.linear_conversions, 0) > 0 
               THEN cs.total_spend / ca.linear_conversions 
               ELSE 0.0 END, 2) AS cac,
               
    -- Performance Tier Classification
    CASE 
        WHEN cs.total_spend == 0 THEN 'Tier 1 - Organic Star (Zero Spend)'
        WHEN (COALESCE(ca.linear_revenue, 0) / cs.total_spend) >= 3.0 AND (cs.total_spend / ca.linear_conversions) <= 200 THEN 'Tier 1 - High Performer (Scale Up)'
        WHEN (COALESCE(ca.linear_revenue, 0) / cs.total_spend) >= 1.5 THEN 'Tier 2 - Moderate (Maintain / Optimize)'
        ELSE 'Tier 3 - Underperformer (Reduce / Reallocate)'
    END AS performance_tier
FROM campaign_spend_summary cs
LEFT JOIN campaign_attribution ca ON cs.campaign_id = ca.campaign_id
ORDER BY roas DESC;
