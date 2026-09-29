-- ====================================================================
-- Staging: stg_experiment_assignments
-- Purpose: Invariant check - exactly one assignment per user per experiment
-- Grain: One row per user per experiment
-- ====================================================================

WITH deduplicated AS (
    SELECT
        assignment_id,
        experiment_id,
        user_id,
        variant,
        CAST(assigned_timestamp AS TIMESTAMP) AS assigned_timestamp,
        pre_experiment_segment,
        ROW_NUMBER() OVER (
            PARTITION BY experiment_id, user_id 
            ORDER BY assigned_timestamp ASC
        ) AS row_num
    FROM raw_experiment_assignments
)
SELECT
    assignment_id,
    experiment_id,
    user_id,
    variant,
    assigned_timestamp,
    CAST(assigned_timestamp AS DATE) AS assigned_date,
    pre_experiment_segment
FROM deduplicated
WHERE row_num = 1;
