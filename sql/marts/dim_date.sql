-- ====================================================================
-- Mart: dim_date
-- Purpose: Calendar date dimension supporting slicing and cohort intervals
-- Grain: One row per calendar date (2026-01-01 to 2026-12-31)
-- ====================================================================

WITH date_spine AS (
    SELECT 
        CAST('2026-01-01' AS DATE) + (i * INTERVAL '1 day') AS date_day
    FROM range(0, 365) AS t(i)
)
SELECT
    date_day,
    EXTRACT(year FROM date_day) AS year_num,
    EXTRACT(quarter FROM date_day) AS quarter_num,
    EXTRACT(month FROM date_day) AS month_num,
    STRFTIME(date_day, '%B') AS month_name,
    DATE_TRUNC('month', date_day) AS month_start_date,
    EXTRACT(week FROM date_day) AS week_of_year,
    EXTRACT(isodow FROM date_day) AS day_of_week_num,
    STRFTIME(date_day, '%A') AS day_of_week_name,
    CASE 
        WHEN EXTRACT(isodow FROM date_day) IN (6, 7) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend
FROM date_spine;
