-- ====================================================================
-- Mart: dim_users
-- Purpose: Conformed user dimension with demographics, activation,
--          lifecycle metrics, and behavioral tier
-- Grain: One row per user
-- ====================================================================

SELECT
    user_id,
    signup_timestamp,
    signup_date,
    signup_month,
    country,
    acquisition_channel,
    device_type,
    browser,
    initial_plan,
    current_plan_name,
    is_activated_7d,
    minutes_to_activation,
    total_events_count,
    total_active_days,
    distinct_features_used,
    total_sessions_count,
    total_duration_seconds,
    avg_session_duration_seconds,
    total_purchases_count,
    total_revenue_usd,
    is_paying_customer,
    -- Behavioral Segmentation
    CASE
        WHEN NOT is_activated_7d THEN 'Unactivated'
        WHEN total_events_count >= 50 AND total_sessions_count >= 15 THEN 'Power User'
        WHEN total_events_count >= 15 THEN 'Regular User'
        ELSE 'Casual User'
    END AS user_behavioral_segment
FROM int_user_lifecycle;
