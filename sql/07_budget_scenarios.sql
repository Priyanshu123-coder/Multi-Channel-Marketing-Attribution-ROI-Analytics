-- ==============================================================================
-- 07_budget_scenarios.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Quantitative Budget Reallocation Scenarios & Projected Impact
-- ==============================================================================

WITH channel_baseline AS (
    SELECT 
        c.channel,
        ROUND(SUM(s.spend), 2) AS current_spend,
        ROUND(SUM(la.linear_revenue), 2) AS current_revenue,
        ROUND(SUM(la.linear_revenue) / SUM(s.spend), 2) AS baseline_roas
    FROM campaigns c
    JOIN (
        SELECT campaign_id, SUM(spend) AS spend FROM spend GROUP BY campaign_id
    ) s ON c.campaign_id = s.campaign_id
    LEFT JOIN (
        SELECT 
            t.campaign_id,
            SUM((1.0 / pt.total_touches) * conv.revenue) AS linear_revenue
        FROM conversions conv
        JOIN (
            SELECT conversion_id, user_id, timestamp,
                   COUNT(*) OVER (PARTITION BY conversion_id) AS total_touches
            FROM (
                SELECT c2.conversion_id, c2.user_id, c2.timestamp
                FROM conversions c2
            )
        ) pt ON conv.conversion_id = pt.conversion_id
        JOIN touchpoints t ON conv.user_id = t.user_id AND t.timestamp <= conv.timestamp
        GROUP BY t.campaign_id
    ) la ON c.campaign_id = la.campaign_id
    WHERE s.spend > 0
    GROUP BY c.channel
),
budget_shift_rules AS (
    -- Shift 20% budget away from lowest-ROAS channels (Display, Paid Social)
    -- and reallocate into highest-ROAS channels (Email, Referral, Paid Search)
    SELECT 
        channel,
        current_spend,
        current_revenue,
        baseline_roas,
        CASE 
            WHEN channel = 'Display' THEN -0.30
            WHEN channel = 'Paid Social' THEN -0.15
            WHEN channel = 'Email' THEN +0.40
            WHEN channel = 'Referral' THEN +0.25
            WHEN channel = 'Paid Search' THEN +0.10
            ELSE 0.0
        END AS reallocation_pct
    FROM channel_baseline
),
scenario_projections AS (
    SELECT 
        channel,
        current_spend,
        current_revenue,
        baseline_roas,
        reallocation_pct,
        ROUND(current_spend * (1 + reallocation_pct), 2) AS new_spend,
        ROUND(current_spend * reallocation_pct, 2) AS spend_delta,
        
        -- Conservative Case: 85% marginal efficiency on expanded budget, 100% loss on cut budget
        ROUND(
            current_revenue + 
            CASE 
                WHEN reallocation_pct > 0 THEN (current_spend * reallocation_pct * baseline_roas * 0.85)
                ELSE (current_spend * reallocation_pct * baseline_roas)
            END
        , 2) AS projected_revenue_conservative,
        
        -- Optimistic Case: 100% marginal efficiency on expanded budget
        ROUND(
            current_revenue + (current_spend * reallocation_pct * baseline_roas)
        , 2) AS projected_revenue_optimistic
    FROM budget_shift_rules
)
SELECT 
    channel,
    current_spend,
    new_spend,
    spend_delta,
    baseline_roas,
    current_revenue,
    projected_revenue_conservative,
    ROUND(projected_revenue_conservative - current_revenue, 2) AS conservative_revenue_lift,
    projected_revenue_optimistic,
    ROUND(projected_revenue_optimistic - current_revenue, 2) AS optimistic_revenue_lift,
    ROUND(projected_revenue_conservative / new_spend, 2) AS projected_conservative_roas,
    ROUND(projected_revenue_optimistic / new_spend, 2) AS projected_optimistic_roas
FROM scenario_projections
ORDER BY current_spend DESC;
