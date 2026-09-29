-- ====================================================================
-- Mart: fct_events
-- Purpose: Conformed fact table containing all user product events
-- Grain: One row per event
-- ====================================================================

SELECT
    e.event_id,
    e.event_timestamp,
    e.event_date,
    e.user_id,
    e.session_id,
    e.event_name,
    e.feature_name,
    e.page_path,
    e.device_type,
    e.country,
    u.acquisition_channel,
    u.signup_date,
    DATE_DIFF('day', u.signup_date, e.event_date) AS days_since_signup
FROM stg_events e
INNER JOIN stg_users u ON e.user_id = u.user_id;
