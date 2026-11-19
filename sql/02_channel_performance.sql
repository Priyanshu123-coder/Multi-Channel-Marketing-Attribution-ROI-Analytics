-- ==============================================================================
-- 02_channel_performance.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Channel-Level Reach, Engagement, Spend, and Direct Metrics
-- ==============================================================================

WITH channel_spend AS (
    SELECT 
        c.channel,
        COUNT(DISTINCT s.campaign_id) AS active_campaigns,
        SUM(s.spend) AS total_spend,
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
    GROUP BY c.channel
),
channel_touchpoints AS (
    SELECT 
        channel,
        COUNT(touchpoint_id) AS total_touchpoints,
        COUNT(DISTINCT user_id) AS unique_users_reached,
        SUM(CASE WHEN interaction_type = 'impression' THEN 1 ELSE 0 END) AS logged_impressions,
        SUM(CASE WHEN interaction_type = 'click' THEN 1 ELSE 0 END) AS logged_clicks,
        SUM(CASE WHEN interaction_type = 'visit' THEN 1 ELSE 0 END) AS logged_visits
    FROM touchpoints
    GROUP BY channel
),
channels_dim AS (
    SELECT DISTINCT channel FROM campaigns
    UNION
    SELECT DISTINCT channel FROM touchpoints
)
SELECT 
    cd.channel,
    COALESCE(cs.active_campaigns, 0) AS active_campaigns,
    ROUND(COALESCE(cs.total_spend, 0), 2) AS total_spend,
    COALESCE(cs.total_impressions, 0) AS total_impressions,
    COALESCE(cs.total_clicks, 0) AS total_clicks,
    COALESCE(cs.ctr_pct, 0) AS ctr_pct,
    COALESCE(cs.cpc, 0) AS cpc,
    COALESCE(ct.total_touchpoints, 0) AS total_touchpoints,
    COALESCE(ct.unique_users_reached, 0) AS unique_users_reached,
    ROUND(CASE WHEN (SELECT SUM(spend) FROM spend) > 0 
               THEN (COALESCE(cs.total_spend, 0) / (SELECT SUM(spend) FROM spend)) * 100 
               ELSE 0 END, 2) AS spend_share_pct
FROM channels_dim cd
LEFT JOIN channel_spend cs ON cd.channel = cs.channel
LEFT JOIN channel_touchpoints ct ON cd.channel = ct.channel
ORDER BY total_spend DESC;
