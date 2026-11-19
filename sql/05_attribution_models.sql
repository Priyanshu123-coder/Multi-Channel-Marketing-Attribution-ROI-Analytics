-- ==============================================================================
-- 05_attribution_models.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Comparative Attribution Models in Pure SQL
-- (First-Touch, Last-Touch, Linear, Position-Based U-Shaped, Time-Decay)
-- ==============================================================================

WITH pre_conversion_touches AS (
    SELECT 
        c.conversion_id,
        c.user_id,
        c.revenue,
        c.timestamp AS conversion_time,
        t.channel,
        t.timestamp AS touch_time,
        -- Julian day difference (conversion_time - touch_time)
        MAX(0, julianday(c.timestamp) - julianday(t.timestamp)) AS days_before_conversion,
        ROW_NUMBER() OVER (PARTITION BY c.conversion_id ORDER BY t.timestamp ASC) AS touch_rank_asc,
        ROW_NUMBER() OVER (PARTITION BY c.conversion_id ORDER BY t.timestamp DESC) AS touch_rank_desc,
        COUNT(*) OVER (PARTITION BY c.conversion_id) AS total_touches
    FROM conversions c
    JOIN touchpoints t ON c.user_id = t.user_id AND t.timestamp <= c.timestamp
),
touchpoint_weights AS (
    SELECT 
        conversion_id,
        channel,
        revenue,
        touch_rank_asc,
        touch_rank_desc,
        total_touches,
        
        -- 1. First-Touch Weight
        CASE WHEN touch_rank_asc = 1 THEN 1.0 ELSE 0.0 END AS weight_first_touch,
        
        -- 2. Last-Touch Weight
        CASE WHEN touch_rank_desc = 1 THEN 1.0 ELSE 0.0 END AS weight_last_touch,
        
        -- 3. Linear Weight
        1.0 / total_touches AS weight_linear,
        
        -- 4. Position-Based (U-Shaped: 40% First, 40% Last, 20% Middle)
        CASE 
            WHEN total_touches = 1 THEN 1.0
            WHEN total_touches = 2 THEN 0.5
            WHEN touch_rank_asc = 1 THEN 0.40
            WHEN touch_rank_desc = 1 THEN 0.40
            ELSE 0.20 / (total_touches - 2)
        END AS weight_position_based,
        
        -- 5. Time-Decay Raw Exponential Weight (7-day half-life: 2^(-days/7) = exp(-0.099021 * days))
        -- Using SQLite exp() or power()
        POWER(2.0, - (days_before_conversion / 7.0)) AS raw_decay_weight
    FROM pre_conversion_touches
),
normalized_weights AS (
    SELECT 
        conversion_id,
        channel,
        revenue,
        weight_first_touch,
        weight_last_touch,
        weight_linear,
        weight_position_based,
        raw_decay_weight / (SUM(raw_decay_weight) OVER (PARTITION BY conversion_id)) AS weight_time_decay
    FROM touchpoint_weights
)
SELECT 
    channel,
    -- First Touch
    ROUND(SUM(weight_first_touch), 2) AS first_touch_conversions,
    ROUND(SUM(weight_first_touch * revenue), 2) AS first_touch_revenue,
    
    -- Last Touch
    ROUND(SUM(weight_last_touch), 2) AS last_touch_conversions,
    ROUND(SUM(weight_last_touch * revenue), 2) AS last_touch_revenue,
    
    -- Linear
    ROUND(SUM(weight_linear), 2) AS linear_conversions,
    ROUND(SUM(weight_linear * revenue), 2) AS linear_revenue,
    
    -- Position-Based (U-Shaped)
    ROUND(SUM(weight_position_based), 2) AS position_based_conversions,
    ROUND(SUM(weight_position_based * revenue), 2) AS position_based_revenue,
    
    -- Time-Decay
    ROUND(SUM(weight_time_decay), 2) AS time_decay_conversions,
    ROUND(SUM(weight_time_decay * revenue), 2) AS time_decay_revenue
FROM normalized_weights
GROUP BY channel
ORDER BY linear_revenue DESC;
