-- ====================================================================
-- Analytics SQL: Cohort Analysis
-- Purpose: Track monthly signup cohorts and calculate retention percentage
--          across subsequent monthly intervals (Month 0 through Month 6).
-- Advanced SQL: Date truncation, Date arithmetic, Group By, Cross Joins,
--               Conditional Aggregation, Ratio formatting
-- ====================================================================

WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_timestamp) AS cohort_month
    FROM stg_users
),

user_activities AS (
    SELECT DISTINCT
        e.user_id,
        DATE_TRUNC('month', e.event_timestamp) AS activity_month
    FROM stg_events e
),

cohort_activity_periods AS (
    SELECT
        c.user_id,
        c.cohort_month,
        a.activity_month,
        CAST(
            (EXTRACT(year FROM a.activity_month) - EXTRACT(year FROM c.cohort_month)) * 12
            + (EXTRACT(month FROM a.activity_month) - EXTRACT(month FROM c.cohort_month))
            AS INTEGER
        ) AS period_month
    FROM user_cohorts c
    INNER JOIN user_activities a ON c.user_id = a.user_id
    WHERE a.activity_month >= c.cohort_month
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS total_cohort_users
    FROM user_cohorts
    GROUP BY cohort_month
)

SELECT
    STRFTIME(c.cohort_month, '%Y-%m') AS cohort_month,
    s.total_cohort_users AS cohort_size,
    COUNT(DISTINCT CASE WHEN c.period_month = 0 THEN c.user_id END) AS m0_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 0 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m0_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 1 THEN c.user_id END) AS m1_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 1 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m1_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 2 THEN c.user_id END) AS m2_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 2 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m2_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 3 THEN c.user_id END) AS m3_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 3 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m3_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 4 THEN c.user_id END) AS m4_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 4 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m4_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 5 THEN c.user_id END) AS m5_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 5 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m5_retention_pct,
    COUNT(DISTINCT CASE WHEN c.period_month = 6 THEN c.user_id END) AS m6_users,
    ROUND(COUNT(DISTINCT CASE WHEN c.period_month = 6 THEN c.user_id END) * 100.0 / s.total_cohort_users, 1) AS m6_retention_pct
FROM cohort_activity_periods c
INNER JOIN cohort_sizes s ON c.cohort_month = s.cohort_month
GROUP BY c.cohort_month, s.total_cohort_users
ORDER BY c.cohort_month ASC;
