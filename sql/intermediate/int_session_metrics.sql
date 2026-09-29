-- ====================================================================
-- Intermediate: int_session_metrics
-- Purpose: Window functions tracking session sequence, time gaps,
--          and prior session recency per user
-- Grain: One row per user session
-- ====================================================================

WITH session_windowed AS (
    SELECT
        session_id,
        user_id,
        session_start,
        session_date,
        session_end,
        duration_seconds,
        duration_minutes,
        event_count,
        device_type,
        country,
        had_conversion,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY session_start ASC
        ) AS session_sequence_number,
        LAG(session_end) OVER (
            PARTITION BY user_id 
            ORDER BY session_start ASC
        ) AS previous_session_end,
        LEAD(session_start) OVER (
            PARTITION BY user_id 
            ORDER BY session_start ASC
        ) AS next_session_start
    FROM stg_sessions
)
SELECT
    session_id,
    user_id,
    session_start,
    session_date,
    session_end,
    duration_seconds,
    duration_minutes,
    event_count,
    device_type,
    country,
    had_conversion,
    session_sequence_number,
    CASE 
        WHEN session_sequence_number = 1 THEN TRUE 
        ELSE FALSE 
    END AS is_first_session,
    ROUND(
        DATE_DIFF('second', previous_session_end, session_start) / 86400.0, 
        2
    ) AS days_since_previous_session
FROM session_windowed;
