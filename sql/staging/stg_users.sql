-- ====================================================================
-- Staging: stg_users
-- Purpose: Deduplicate, typecast, and format user dimensions
-- Grain: One row per unique registered user
-- ====================================================================

WITH deduplicated AS (
    SELECT
        user_id,
        CAST(signup_timestamp AS TIMESTAMP) AS signup_timestamp,
        country,
        acquisition_channel,
        device_type,
        browser,
        initial_plan,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY signup_timestamp ASC
        ) AS row_num
    FROM raw_users
)
SELECT
    user_id,
    signup_timestamp,
    CAST(signup_timestamp AS DATE) AS signup_date,
    DATE_TRUNC('month', signup_timestamp) AS signup_month,
    country,
    acquisition_channel,
    device_type,
    browser,
    initial_plan
FROM deduplicated
WHERE row_num = 1;
