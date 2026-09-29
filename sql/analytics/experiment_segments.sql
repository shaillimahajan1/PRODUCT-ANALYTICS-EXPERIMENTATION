-- ====================================================================
-- Analytics SQL: Experiment Subgroup / Segment Analysis
-- Purpose: Evaluate treatment lift across pre-treatment device and geography segments.
-- Advanced SQL: GROUP BY CUBE/ROLLUP, CTEs, Pivot Self-Join
-- ====================================================================

WITH segment_metrics AS (
    SELECT
        experiment_id,
        device_type,
        variant,
        COUNT(DISTINCT user_id) AS assigned_users,
        COUNT(DISTINCT CASE WHEN is_activated_7d THEN user_id END) AS activated_users,
        ROUND(COUNT(DISTINCT CASE WHEN is_activated_7d THEN user_id END) * 1.0 / COUNT(DISTINCT user_id), 4) AS activation_rate
    FROM fct_experiments
    GROUP BY experiment_id, device_type, variant
),

paired_segments AS (
    SELECT
        c.experiment_id,
        c.device_type,
        c.assigned_users AS control_users,
        t.assigned_users AS treatment_users,
        c.activation_rate AS control_rate,
        t.activation_rate AS treatment_rate,
        ROUND(t.activation_rate - c.activation_rate, 4) AS absolute_lift,
        ROUND((t.activation_rate - c.activation_rate) / c.activation_rate * 100.0, 2) AS relative_lift_pct
    FROM segment_metrics c
    INNER JOIN segment_metrics t 
        ON c.experiment_id = t.experiment_id 
       AND c.device_type = t.device_type
    WHERE c.variant LIKE 'Control%' AND t.variant LIKE 'Treatment%'
)

SELECT
    experiment_id,
    device_type,
    control_users,
    treatment_users,
    control_rate,
    treatment_rate,
    absolute_lift,
    relative_lift_pct
FROM paired_segments
ORDER BY experiment_id, device_type;
