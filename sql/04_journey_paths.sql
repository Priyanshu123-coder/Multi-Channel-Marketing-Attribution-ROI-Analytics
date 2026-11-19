-- ==============================================================================
-- 04_journey_paths.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Customer Journey Paths, Path Lengths, and Conversion Lags
-- ==============================================================================

-- 1. Detailed Journey Path Mapping per Converting User
WITH pre_conversion_touches AS (
    SELECT 
        c.conversion_id,
        c.user_id,
        c.timestamp AS conversion_time,
        c.revenue,
        t.channel,
        t.timestamp AS touch_time,
        ROW_NUMBER() OVER (PARTITION BY c.conversion_id ORDER BY t.timestamp ASC) AS touch_step,
        COUNT(*) OVER (PARTITION BY c.conversion_id) AS total_path_length,
        MIN(t.timestamp) OVER (PARTITION BY c.conversion_id) AS first_touch_time
    FROM conversions c
    JOIN touchpoints t ON c.user_id = t.user_id AND t.timestamp <= c.timestamp
),
user_journey_summary AS (
    SELECT 
        conversion_id,
        user_id,
        revenue,
        total_path_length,
        GROUP_CONCAT(channel, ' > ') AS journey_path,
        first_touch_time,
        conversion_time,
        -- Julian day difference in SQLite
        ROUND((julianday(conversion_time) - julianday(first_touch_time)), 2) AS lag_days
    FROM (
        SELECT * FROM pre_conversion_touches ORDER BY conversion_id, touch_step
    )
    GROUP BY conversion_id, user_id, revenue, total_path_length, first_touch_time, conversion_time
)

-- Top Converting Customer Journey Paths
SELECT 
    journey_path || ' > Conversion' AS full_conversion_path,
    total_path_length AS path_touchpoints,
    COUNT(conversion_id) AS conversion_count,
    ROUND(SUM(revenue), 2) AS total_revenue_generated,
    ROUND(AVG(lag_days), 1) AS avg_conversion_lag_days,
    ROUND((CAST(COUNT(conversion_id) AS FLOAT) / (SELECT COUNT(*) FROM conversions)) * 100, 2) AS pct_of_total_conversions
FROM user_journey_summary
GROUP BY journey_path, total_path_length
ORDER BY conversion_count DESC
LIMIT 15;
