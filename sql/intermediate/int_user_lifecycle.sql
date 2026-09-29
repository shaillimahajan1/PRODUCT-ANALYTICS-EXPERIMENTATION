-- ====================================================================
-- Intermediate: int_user_lifecycle
-- Purpose: Consolidate user onboarding milestones, activation times,
--          first feature events, session counts, and cumulative spend
-- Grain: One row per user
-- ====================================================================

WITH user_base AS (
    SELECT * FROM stg_users
),

user_milestones AS (
    SELECT
        user_id,
        MIN(CASE WHEN event_name = 'onboarding_started' THEN event_timestamp END) AS onboarding_started_at,
        MIN(CASE WHEN event_name = 'onboarding_completed' THEN event_timestamp END) AS onboarding_completed_at,
        MIN(CASE WHEN event_name = 'feature_used' THEN event_timestamp END) AS first_feature_used_at,
        MIN(CASE WHEN event_name = 'intent_action' THEN event_timestamp END) AS first_intent_action_at,
        MIN(CASE WHEN event_name = 'purchase' THEN event_timestamp END) AS first_purchase_at,
        MAX(event_timestamp) AS last_active_at,
        COUNT(event_id) AS total_events_count,
        COUNT(DISTINCT CAST(event_timestamp AS DATE)) AS total_active_days,
        COUNT(DISTINCT CASE WHEN event_name = 'feature_used' THEN feature_name END) AS distinct_features_used
    FROM stg_events
    GROUP BY user_id
),

session_aggregates AS (
    SELECT
        user_id,
        COUNT(session_id) AS total_sessions_count,
        SUM(duration_seconds) AS total_duration_seconds,
        AVG(duration_seconds) AS avg_session_duration_seconds
    FROM stg_sessions
    GROUP BY user_id
),

conversion_aggregates AS (
    SELECT
        user_id,
        COUNT(conversion_id) AS total_purchases_count,
        SUM(revenue_usd) AS total_revenue_usd,
        MAX(plan_name) AS current_plan_name
    FROM stg_conversions
    GROUP BY user_id
)

SELECT
    u.user_id,
    u.signup_timestamp,
    u.signup_date,
    DATE_TRUNC('month', u.signup_timestamp) AS signup_month,
    u.country,
    u.acquisition_channel,
    u.device_type,
    u.browser,
    u.initial_plan,
    m.onboarding_started_at,
    m.onboarding_completed_at,
    m.first_feature_used_at,
    m.first_intent_action_at,
    m.first_purchase_at,
    m.last_active_at,
    -- Activation flag: completed onboarding within 7 days of signup
    CASE 
        WHEN m.onboarding_completed_at IS NOT NULL 
         AND m.onboarding_completed_at <= u.signup_timestamp + INTERVAL '7 days'
        THEN TRUE 
        ELSE FALSE 
    END AS is_activated_7d,
    -- Time to activate in minutes
    ROUND(DATE_DIFF('second', u.signup_timestamp, m.onboarding_completed_at) / 60.0, 2) AS minutes_to_activation,
    COALESCE(m.total_events_count, 0) AS total_events_count,
    COALESCE(m.total_active_days, 0) AS total_active_days,
    COALESCE(m.distinct_features_used, 0) AS distinct_features_used,
    COALESCE(s.total_sessions_count, 0) AS total_sessions_count,
    COALESCE(s.total_duration_seconds, 0) AS total_duration_seconds,
    ROUND(COALESCE(s.avg_session_duration_seconds, 0), 1) AS avg_session_duration_seconds,
    COALESCE(c.total_purchases_count, 0) AS total_purchases_count,
    COALESCE(c.total_revenue_usd, 0.0) AS total_revenue_usd,
    COALESCE(c.current_plan_name, u.initial_plan) AS current_plan_name,
    CASE WHEN COALESCE(c.total_purchases_count, 0) > 0 THEN TRUE ELSE FALSE END AS is_paying_customer
FROM user_base u
LEFT JOIN user_milestones m ON u.user_id = m.user_id
LEFT JOIN session_aggregates s ON u.user_id = s.user_id
LEFT JOIN conversion_aggregates c ON u.user_id = c.user_id;
