-- ====================================================================
-- Staging: stg_sessions
-- Purpose: Validate session boundaries, durations, and conversion flags
-- Grain: One row per unique user session
-- ====================================================================

WITH deduplicated AS (
    SELECT
        session_id,
        user_id,
        CAST(session_start AS TIMESTAMP) AS session_start,
        CAST(session_end AS TIMESTAMP) AS session_end,
        CAST(duration_seconds AS INTEGER) AS duration_seconds,
        CAST(event_count AS INTEGER) AS event_count,
        device_type,
        country,
        CAST(had_conversion AS BOOLEAN) AS had_conversion,
        ROW_NUMBER() OVER (
            PARTITION BY session_id 
            ORDER BY session_start ASC
        ) AS row_num
    FROM raw_sessions
)
SELECT
    session_id,
    user_id,
    session_start,
    CAST(session_start AS DATE) AS session_date,
    session_end,
    CASE 
        WHEN duration_seconds < 0 THEN 0 
        ELSE duration_seconds 
    END AS duration_seconds,
    ROUND(duration_seconds / 60.0, 2) AS duration_minutes,
    event_count,
    device_type,
    country,
    had_conversion
FROM deduplicated
WHERE row_num = 1;
