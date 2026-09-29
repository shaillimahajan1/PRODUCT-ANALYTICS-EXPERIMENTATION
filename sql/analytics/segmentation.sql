-- ====================================================================
-- Analytics SQL: Behavioral Segmentation
-- Purpose: Classify users into Power, Regular, Casual, At-Risk, and
--          Unactivated segments using activity percentiles and lifecycle rules.
-- Advanced SQL: NTILE, PERCENT_RANK, Window Functions, Multi-tier CASE
-- ====================================================================

WITH user_activity_ranks AS (
    SELECT
        u.user_id,
        u.signup_date,
        u.is_activated_7d,
        u.total_events_count,
        u.total_sessions_count,
        u.total_revenue_usd,
        u.is_paying_customer,
        u.total_active_days,
        -- Percentile ranks among activated users
        PERCENT_RANK() OVER (ORDER BY u.total_events_count ASC) AS event_percentile,
        PERCENT_RANK() OVER (ORDER BY u.total_sessions_count ASC) AS session_percentile
    FROM dim_users u
),

segmented_users AS (
    SELECT
        user_id,
        signup_date,
        is_activated_7d,
        total_events_count,
        total_sessions_count,
        total_revenue_usd,
        is_paying_customer,
        event_percentile,
        session_percentile,
        CASE
            WHEN NOT is_activated_7d THEN 'Unactivated'
            WHEN event_percentile >= 0.85 AND session_percentile >= 0.85 THEN 'Power User'
            WHEN event_percentile >= 0.45 THEN 'Regular User'
            ELSE 'Casual User'
        END AS behavioral_segment
    FROM user_activity_ranks
)

SELECT
    behavioral_segment,
    COUNT(user_id) AS total_users,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM segmented_users), 2) AS segment_share_pct,
    ROUND(AVG(total_events_count), 1) AS avg_events_per_user,
    ROUND(AVG(total_sessions_count), 1) AS avg_sessions_per_user,
    ROUND(AVG(total_revenue_usd), 2) AS avg_revenue_per_user,
    COUNT(CASE WHEN is_paying_customer THEN user_id END) AS paying_customers_count,
    ROUND(COUNT(CASE WHEN is_paying_customer THEN user_id END) * 100.0 / COUNT(user_id), 2) AS payer_conversion_rate_pct
FROM segmented_users
GROUP BY behavioral_segment
ORDER BY avg_events_per_user DESC;
