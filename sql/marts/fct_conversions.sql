-- ====================================================================
-- Mart: fct_conversions
-- Purpose: Conformed fact table containing subscription purchases
-- Grain: One row per transaction
-- ====================================================================

SELECT
    c.conversion_id,
    c.user_id,
    c.session_id,
    c.conversion_timestamp,
    c.conversion_date,
    c.plan_name,
    c.billing_cycle,
    c.revenue_usd,
    c.country,
    c.acquisition_channel,
    u.signup_date,
    DATE_DIFF('day', u.signup_date, c.conversion_date) AS days_to_conversion
FROM stg_conversions c
INNER JOIN stg_users u ON c.user_id = u.user_id;
