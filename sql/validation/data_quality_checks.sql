-- ====================================================================
-- Validation SQL: Data Quality and Integrity Checks
-- Purpose: Automated SQL tests checking key integrity constraints,
--          uniqueness, non-nullability, foreign keys, and range limits.
-- ====================================================================

-- 1. Check user uniqueness
SELECT
    'dim_users' AS table_name,
    'user_id_uniqueness' AS check_name,
    COUNT(*) - COUNT(DISTINCT user_id) AS failed_record_count,
    CASE WHEN COUNT(*) = COUNT(DISTINCT user_id) THEN 'PASSED' ELSE 'FAILED' END AS check_status
FROM dim_users

UNION ALL

-- 2. Check event referential integrity
SELECT
    'fct_events' AS table_name,
    'referential_integrity_user_id' AS check_name,
    COUNT(e.event_id) AS failed_record_count,
    CASE WHEN COUNT(e.event_id) = 0 THEN 'PASSED' ELSE 'FAILED' END AS check_status
FROM fct_events e
LEFT JOIN dim_users u ON e.user_id = u.user_id
WHERE u.user_id IS NULL

UNION ALL

-- 3. Check session duration sanity
SELECT
    'fct_sessions' AS table_name,
    'non_negative_duration' AS check_name,
    COUNT(*) AS failed_record_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS check_status
FROM fct_sessions
WHERE duration_seconds < 0

UNION ALL

-- 4. Check experiment assignment uniqueness
SELECT
    'fct_experiments' AS table_name,
    'single_assignment_per_user' AS check_name,
    COUNT(*) - COUNT(DISTINCT experiment_id || '_' || user_id) AS failed_record_count,
    CASE WHEN COUNT(*) = COUNT(DISTINCT experiment_id || '_' || user_id) THEN 'PASSED' ELSE 'FAILED' END AS check_status
FROM fct_experiments;
