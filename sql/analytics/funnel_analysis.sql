-- ====================================================================
-- Analytics SQL: Funnel Analysis
-- Purpose: Calculate stage-to-stage conversion rates, cumulative conversion,
--          drop-off rates, and time between steps across product lifecycle.
-- Advanced SQL: CTEs, Conditional Aggregation, Window Functions, LAG
-- ====================================================================

WITH stage_events AS (
    SELECT
        user_id,
        device_type,
        country,
        MIN(CASE WHEN event_name = 'signup' THEN event_timestamp END) AS t_signup,
        MIN(CASE WHEN event_name = 'onboarding_completed' THEN event_timestamp END) AS t_activation,
        MIN(CASE WHEN event_name = 'feature_used' THEN event_timestamp END) AS t_feature_adoption,
        MIN(CASE WHEN event_name = 'intent_action' THEN event_timestamp END) AS t_intent,
        MIN(CASE WHEN event_name = 'purchase' THEN event_timestamp END) AS t_conversion
    FROM stg_events
    GROUP BY user_id, device_type, country
),

funnel_counts AS (
    SELECT
        COUNT(DISTINCT user_id) AS step1_signup_users,
        COUNT(DISTINCT CASE WHEN t_activation IS NOT NULL AND t_activation >= t_signup THEN user_id END) AS step2_activation_users,
        COUNT(DISTINCT CASE WHEN t_feature_adoption IS NOT NULL AND t_feature_adoption >= t_signup THEN user_id END) AS step3_feature_users,
        COUNT(DISTINCT CASE WHEN t_intent IS NOT NULL AND t_intent >= t_signup THEN user_id END) AS step4_intent_users,
        COUNT(DISTINCT CASE WHEN t_conversion IS NOT NULL AND t_conversion >= t_signup THEN user_id END) AS step5_conversion_users
    FROM stage_events
),

unpivoted_stages AS (
    SELECT 1 AS stage_order, '1. Signup' AS stage_name, step1_signup_users AS users_reached FROM funnel_counts
    UNION ALL
    SELECT 2 AS stage_order, '2. Activation' AS stage_name, step2_activation_users AS users_reached FROM funnel_counts
    UNION ALL
    SELECT 3 AS stage_order, '3. Feature Adoption' AS stage_name, step3_feature_users AS users_reached FROM funnel_counts
    UNION ALL
    SELECT 4 AS stage_order, '4. Intent Action' AS stage_name, step4_intent_users AS users_reached FROM funnel_counts
    UNION ALL
    SELECT 5 AS stage_order, '5. Conversion' AS stage_name, step5_conversion_users AS users_reached FROM funnel_counts
),

funnel_metrics AS (
    SELECT
        stage_order,
        stage_name,
        users_reached,
        LAG(users_reached, 1) OVER (ORDER BY stage_order) AS prev_stage_users,
        FIRST_VALUE(users_reached) OVER (ORDER BY stage_order) AS top_of_funnel_users
    FROM unpivoted_stages
)

SELECT
    stage_order,
    stage_name,
    users_reached,
    -- Stage-to-stage conversion rate
    CASE 
        WHEN prev_stage_users IS NULL THEN 1.0000
        WHEN prev_stage_users = 0 THEN 0.0000
        ELSE ROUND(CAST(users_reached AS DOUBLE) / prev_stage_users, 4)
    END AS stage_conversion_rate,
    -- Cumulative conversion rate from top of funnel
    ROUND(CAST(users_reached AS DOUBLE) / top_of_funnel_users, 4) AS cumulative_conversion_rate,
    -- Drop-off rate at this stage
    CASE 
        WHEN prev_stage_users IS NULL THEN 0.0000
        WHEN prev_stage_users = 0 THEN 0.0000
        ELSE ROUND(1.0 - (CAST(users_reached AS DOUBLE) / prev_stage_users), 4)
    END AS drop_off_rate
FROM funnel_metrics
ORDER BY stage_order ASC;
