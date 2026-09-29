-- ====================================================================
-- Mart: fct_experiments
-- Purpose: Experiment assignments enriched with user outcomes:
--          activation, feature adoption, conversion, and support tickets
-- Grain: One row per user per experiment
-- ====================================================================

WITH assignments AS (
    SELECT * FROM stg_experiment_assignments
),

user_outcomes AS (
    SELECT
        user_id,
        is_activated_7d,
        total_active_days,
        total_events_count,
        total_sessions_count,
        total_revenue_usd,
        is_paying_customer
    FROM int_user_lifecycle
),

support_tickets AS (
    SELECT
        user_id,
        COUNT(event_id) AS support_tickets_count
    FROM stg_events
    WHERE event_name = 'support_interaction'
    GROUP BY user_id
)

SELECT
    a.assignment_id,
    a.experiment_id,
    a.user_id,
    a.variant,
    a.assigned_timestamp,
    CAST(a.assigned_timestamp AS DATE) AS assigned_date,
    a.pre_experiment_segment,
    u.country,
    u.device_type,
    u.acquisition_channel,
    COALESCE(o.is_activated_7d, FALSE) AS is_activated_7d,
    COALESCE(o.is_paying_customer, FALSE) AS has_converted,
    COALESCE(o.total_revenue_usd, 0.0) AS total_revenue_usd,
    COALESCE(o.total_events_count, 0) AS total_events_count,
    COALESCE(o.total_sessions_count, 0) AS total_sessions_count,
    COALESCE(o.total_active_days, 0) AS total_active_days,
    CASE 
        WHEN COALESCE(s.support_tickets_count, 0) > 0 THEN TRUE 
        ELSE FALSE 
    END AS had_support_ticket
FROM assignments a
INNER JOIN stg_users u ON a.user_id = u.user_id
LEFT JOIN user_outcomes o ON a.user_id = o.user_id
LEFT JOIN support_tickets s ON a.user_id = s.user_id;
