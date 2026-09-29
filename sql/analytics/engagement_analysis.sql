-- ====================================================================
-- Analytics SQL: Engagement & Stickiness Analysis
-- Purpose: Calculate DAU, rolling 7-day WAU, rolling 30-day MAU,
--          DAU/MAU stickiness ratio, and session intensity.
-- Advanced SQL: Daily date spine, subqueries, self-joins on rolling intervals,
--               Window functions, Conditional Aggregation
-- ====================================================================

WITH daily_active_users AS (
    SELECT
        CAST(event_timestamp AS DATE) AS activity_date,
        COUNT(DISTINCT user_id) AS dau,
        COUNT(event_id) AS total_events,
        COUNT(DISTINCT session_id) AS total_sessions
    FROM stg_events
    GROUP BY CAST(event_timestamp AS DATE)
),

rolling_active_metrics AS (
    SELECT
        d1.activity_date,
        d1.dau,
        d1.total_events,
        d1.total_sessions,
        -- Rolling 7-day unique users (WAU)
        (
            SELECT COUNT(DISTINCT e.user_id)
            FROM stg_events e
            WHERE CAST(e.event_timestamp AS DATE) BETWEEN d1.activity_date - INTERVAL '6 days' AND d1.activity_date
        ) AS wau,
        -- Rolling 30-day unique users (MAU)
        (
            SELECT COUNT(DISTINCT e.user_id)
            FROM stg_events e
            WHERE CAST(e.event_timestamp AS DATE) BETWEEN d1.activity_date - INTERVAL '29 days' AND d1.activity_date
        ) AS mau
    FROM daily_active_users d1
)

SELECT
    activity_date,
    dau,
    wau,
    mau,
    -- DAU/MAU Stickiness Ratio
    CASE 
        WHEN mau > 0 THEN ROUND(CAST(dau AS DOUBLE) / mau, 4)
        ELSE 0.0000 
    END AS dau_mau_stickiness_ratio,
    total_events,
    total_sessions,
    -- Intensity metrics
    CASE 
        WHEN dau > 0 THEN ROUND(CAST(total_events AS DOUBLE) / dau, 2)
        ELSE 0.00 
    END AS events_per_dau,
    CASE 
        WHEN dau > 0 THEN ROUND(CAST(total_sessions AS DOUBLE) / dau, 2)
        ELSE 0.00 
    END AS sessions_per_dau
FROM rolling_active_metrics
ORDER BY activity_date ASC;
