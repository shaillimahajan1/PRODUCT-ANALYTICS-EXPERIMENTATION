-- ====================================================================
-- Analytics SQL: Retention Analysis
-- Purpose: Calculate N-Day (Day 1, Day 3, Day 7, Day 14, Day 30) exact and
--          rolling retention rates, segmented by acquisition channel.
-- Advanced SQL: CTEs, Date Diff in seconds/days, Conditional Aggregations
-- ====================================================================

WITH user_signups AS (
    SELECT
        user_id,
        signup_timestamp,
        acquisition_channel,
        device_type
    FROM stg_users
),

user_event_delays AS (
    SELECT
        e.user_id,
        u.acquisition_channel,
        u.device_type,
        -- Exact days elapsed between signup and event
        DATE_DIFF('second', u.signup_timestamp, e.event_timestamp) / 86400.0 AS days_since_signup
    FROM stg_events e
    INNER JOIN user_signups u ON e.user_id = u.user_id
    WHERE e.event_timestamp > u.signup_timestamp
),

channel_cohort_sizes AS (
    SELECT
        acquisition_channel,
        COUNT(DISTINCT user_id) AS total_users
    FROM user_signups
    GROUP BY acquisition_channel
)

SELECT
    s.acquisition_channel,
    c.total_users,
    -- Day 1 Retention (24h to 48h)
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 1.0 AND s.days_since_signup < 2.0 THEN s.user_id END) AS day1_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 1.0 AND s.days_since_signup < 2.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS day1_retention_pct,
    -- Day 3 Retention
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 3.0 AND s.days_since_signup < 4.0 THEN s.user_id END) AS day3_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 3.0 AND s.days_since_signup < 4.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS day3_retention_pct,
    -- Day 7 Retention
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 7.0 AND s.days_since_signup < 8.0 THEN s.user_id END) AS day7_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 7.0 AND s.days_since_signup < 8.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS day7_retention_pct,
    -- Day 14 Retention
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 14.0 AND s.days_since_signup < 15.0 THEN s.user_id END) AS day14_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 14.0 AND s.days_since_signup < 15.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS day14_retention_pct,
    -- Day 30 Retention
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 30.0 AND s.days_since_signup < 31.0 THEN s.user_id END) AS day30_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 30.0 AND s.days_since_signup < 31.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS day30_retention_pct,
    -- Rolling 30-Day Retention (at least one activity on or after Day 30)
    COUNT(DISTINCT CASE WHEN s.days_since_signup >= 30.0 THEN s.user_id END) AS rolling_day30_retained,
    ROUND(COUNT(DISTINCT CASE WHEN s.days_since_signup >= 30.0 THEN s.user_id END) * 100.0 / c.total_users, 2) AS rolling_day30_retention_pct
FROM user_event_delays s
INNER JOIN channel_cohort_sizes c ON s.acquisition_channel = c.acquisition_channel
GROUP BY s.acquisition_channel, c.total_users
ORDER BY day7_retention_pct DESC;
