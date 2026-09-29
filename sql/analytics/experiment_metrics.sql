-- ====================================================================
-- Analytics SQL: Experiment Metrics
-- Purpose: Aggregate primary, secondary, and guardrail metrics by
--          experiment and variant, calculating observed absolute and relative lifts.
-- Advanced SQL: Conditional Aggregation, Pivot logic, Self-Joins, Window Functions
-- ====================================================================

WITH variant_metrics AS (
    SELECT
        experiment_id,
        variant,
        COUNT(DISTINCT user_id) AS total_assigned_users,
        -- Primary / Secondary: Activation
        COUNT(DISTINCT CASE WHEN is_activated_7d THEN user_id END) AS activated_users,
        ROUND(COUNT(DISTINCT CASE WHEN is_activated_7d THEN user_id END) * 1.0 / COUNT(DISTINCT user_id), 4) AS activation_rate,
        -- Secondary: Conversion
        COUNT(DISTINCT CASE WHEN has_converted THEN user_id END) AS converted_users,
        ROUND(COUNT(DISTINCT CASE WHEN has_converted THEN user_id END) * 1.0 / COUNT(DISTINCT user_id), 4) AS conversion_rate,
        -- Guardrail: Support tickets
        COUNT(DISTINCT CASE WHEN had_support_ticket THEN user_id END) AS support_ticket_users,
        ROUND(COUNT(DISTINCT CASE WHEN had_support_ticket THEN user_id END) * 1.0 / COUNT(DISTINCT user_id), 4) AS support_ticket_rate,
        -- Revenue
        ROUND(AVG(total_revenue_usd), 2) AS arpu_usd,
        ROUND(AVG(total_events_count), 1) AS avg_events_per_user
    FROM fct_experiments
    GROUP BY experiment_id, variant
),

paired_variants AS (
    SELECT
        c.experiment_id,
        c.variant AS control_variant,
        t.variant AS treatment_variant,
        c.total_assigned_users AS control_n,
        t.total_assigned_users AS treatment_n,
        c.activation_rate AS control_activation_rate,
        t.activation_rate AS treatment_activation_rate,
        ROUND(t.activation_rate - c.activation_rate, 4) AS activation_absolute_lift,
        ROUND((t.activation_rate - c.activation_rate) / c.activation_rate * 100.0, 2) AS activation_relative_lift_pct,
        c.conversion_rate AS control_conversion_rate,
        t.conversion_rate AS treatment_conversion_rate,
        ROUND(t.conversion_rate - c.conversion_rate, 4) AS conversion_absolute_lift,
        c.support_ticket_rate AS control_ticket_rate,
        t.support_ticket_rate AS treatment_ticket_rate,
        ROUND(t.support_ticket_rate - c.support_ticket_rate, 4) AS ticket_rate_delta,
        c.arpu_usd AS control_arpu,
        t.arpu_usd AS treatment_arpu
    FROM variant_metrics c
    INNER JOIN variant_metrics t ON c.experiment_id = t.experiment_id
    WHERE c.variant LIKE 'Control%' AND t.variant LIKE 'Treatment%'
)

SELECT
    experiment_id,
    control_variant,
    treatment_variant,
    control_n,
    treatment_n,
    control_activation_rate,
    treatment_activation_rate,
    activation_absolute_lift,
    activation_relative_lift_pct,
    control_conversion_rate,
    treatment_conversion_rate,
    conversion_absolute_lift,
    control_ticket_rate,
    treatment_ticket_rate,
    ticket_rate_delta,
    control_arpu,
    treatment_arpu
FROM paired_variants
ORDER BY experiment_id ASC;
