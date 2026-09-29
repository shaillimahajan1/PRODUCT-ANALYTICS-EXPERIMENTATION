-- ====================================================================
-- Staging: stg_conversions
-- Purpose: Deduplicate and cast subscription transactions and revenue
-- Grain: One row per subscription purchase event
-- ====================================================================

WITH deduplicated AS (
    SELECT
        conversion_id,
        user_id,
        session_id,
        CAST(conversion_timestamp AS TIMESTAMP) AS conversion_timestamp,
        plan_name,
        billing_cycle,
        CAST(revenue_usd AS DOUBLE) AS revenue_usd,
        country,
        acquisition_channel,
        ROW_NUMBER() OVER (
            PARTITION BY conversion_id 
            ORDER BY conversion_timestamp ASC
        ) AS row_num
    FROM raw_conversions
)
SELECT
    conversion_id,
    user_id,
    session_id,
    conversion_timestamp,
    CAST(conversion_timestamp AS DATE) AS conversion_date,
    plan_name,
    billing_cycle,
    revenue_usd,
    country,
    acquisition_channel
FROM deduplicated
WHERE row_num = 1;
