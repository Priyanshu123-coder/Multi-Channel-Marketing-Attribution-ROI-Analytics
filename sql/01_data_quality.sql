-- ==============================================================================
-- 01_data_quality.sql
-- Grito Labs Marketing Analytics & Attribution Framework
-- Data Quality & Integrity Validation Suite
-- ==============================================================================

-- 1. NULL CHECKS
-- Expected: 0 rows returned for all checks.

SELECT 'users_null_check' AS test_name, COUNT(*) AS failure_count
FROM users
WHERE user_id IS NULL OR signup_date IS NULL OR acquisition_channel IS NULL;

SELECT 'campaigns_null_check' AS test_name, COUNT(*) AS failure_count
FROM campaigns
WHERE campaign_id IS NULL OR channel IS NULL OR name IS NULL;

SELECT 'spend_null_check' AS test_name, COUNT(*) AS failure_count
FROM spend
WHERE campaign_id IS NULL OR date IS NULL OR spend IS NULL;

SELECT 'touchpoints_null_check' AS test_name, COUNT(*) AS failure_count
FROM touchpoints
WHERE touchpoint_id IS NULL OR user_id IS NULL OR timestamp IS NULL OR channel IS NULL OR campaign_id IS NULL;

SELECT 'conversions_null_check' AS test_name, COUNT(*) AS failure_count
FROM conversions
WHERE conversion_id IS NULL OR user_id IS NULL OR timestamp IS NULL OR revenue IS NULL;


-- 2. DUPLICATE PRIMARY KEY CHECKS
-- Expected: 0 duplicates across all entities.

SELECT 'users_duplicate_pk' AS test_name, COUNT(*) AS failure_count
FROM (
    SELECT user_id, COUNT(*) AS cnt
    FROM users
    GROUP BY user_id
    HAVING COUNT(*) > 1
);

SELECT 'campaigns_duplicate_pk' AS test_name, COUNT(*) AS failure_count
FROM (
    SELECT campaign_id, COUNT(*) AS cnt
    FROM campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
);

SELECT 'touchpoints_duplicate_pk' AS test_name, COUNT(*) AS failure_count
FROM (
    SELECT touchpoint_id, COUNT(*) AS cnt
    FROM touchpoints
    GROUP BY touchpoint_id
    HAVING COUNT(*) > 1
);

SELECT 'conversions_duplicate_pk' AS test_name, COUNT(*) AS failure_count
FROM (
    SELECT conversion_id, COUNT(*) AS cnt
    FROM conversions
    GROUP BY conversion_id
    HAVING COUNT(*) > 1
);


-- 3. REFERENTIAL INTEGRITY / ORPHAN RECORD CHECKS
-- Expected: 0 orphan touchpoints, conversions, or spend records.

SELECT 'orphan_touchpoint_users' AS test_name, COUNT(*) AS failure_count
FROM touchpoints t
LEFT JOIN users u ON t.user_id = u.user_id
WHERE u.user_id IS NULL;

SELECT 'orphan_conversion_users' AS test_name, COUNT(*) AS failure_count
FROM conversions c
LEFT JOIN users u ON c.user_id = u.user_id
WHERE u.user_id IS NULL;

SELECT 'orphan_touchpoint_campaigns' AS test_name, COUNT(*) AS failure_count
FROM touchpoints t
LEFT JOIN campaigns c ON t.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL;

SELECT 'orphan_spend_campaigns' AS test_name, COUNT(*) AS failure_count
FROM spend s
LEFT JOIN campaigns c ON s.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL;


-- 4. CHRONOLOGICAL INTEGRITY CHECKS
-- Identify touchpoints that occurred strictly AFTER a conversion event for that user
-- (useful to flag for pre-conversion attribution filtering)

SELECT 'touchpoints_after_conversion' AS test_name, COUNT(*) AS anomaly_count
FROM touchpoints t
JOIN conversions c ON t.user_id = c.user_id
WHERE t.timestamp > c.timestamp;


-- 5. RANGE & METRIC LOGIC CHECKS
-- Check for negative numbers or impossible click-through relationships

SELECT 'negative_spend_or_revenue' AS test_name, COUNT(*) AS failure_count
FROM (
    SELECT spend FROM spend WHERE spend < 0
    UNION ALL
    SELECT revenue FROM conversions WHERE revenue < 0
);

SELECT 'clicks_exceed_impressions' AS test_name, COUNT(*) AS failure_count
FROM spend
WHERE clicks > impressions AND impressions > 0;
