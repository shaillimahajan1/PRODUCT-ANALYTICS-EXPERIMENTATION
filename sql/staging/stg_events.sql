-- ====================================================================
-- Staging: stg_events
-- Purpose: Deduplicate, cast timestamps, and clean raw events
-- Grain: One row per unique user event
-- ====================================================================

WITH deduplicated AS (
    SELECT
        event_id,
        CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
        user_id,
        session_id,
        event_name,
        COALESCE(feature_name, 'none') AS feature_name,
        page_path,
        device_type,
        country,
        ROW_NUMBER() OVER (
            PARTITION BY event_id 
            ORDER BY event_timestamp ASC
        ) AS row_num
    FROM raw_events
)
SELECT
    event_id,
    event_timestamp,
    CAST(event_timestamp AS DATE) AS event_date,
    user_id,
    session_id,
    event_name,
    feature_name,
    page_path,
    device_type,
    country
FROM deduplicated
WHERE row_num = 1;
