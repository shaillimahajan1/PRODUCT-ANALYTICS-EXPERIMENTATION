-- ====================================================================
-- Mart: fct_sessions
-- Purpose: Conformed fact table containing user session details
-- Grain: One row per session
-- ====================================================================

SELECT
    s.session_id,
    s.user_id,
    s.session_start,
    s.session_date,
    s.session_end,
    s.duration_seconds,
    s.duration_minutes,
    s.event_count,
    s.device_type,
    s.country,
    s.had_conversion,
    s.session_sequence_number,
    s.is_first_session,
    s.days_since_previous_session,
    u.acquisition_channel,
    u.signup_date
FROM int_session_metrics s
INNER JOIN stg_users u ON s.user_id = u.user_id;
