# Power BI Semantic Model & Report Implementation Guide

This guide details the Power BI star-schema dimensional model, the production DAX measure library, and the exact design architecture for the 6-page **FlowPulse Product Analytics & Experimentation** executive dashboard.

---

## 1. Semantic Data Model (Star Schema)

The dashboard connects directly to the analytical parquet/CSV data marts exported in `data/marts/`:

```
                           ┌─────────────────┐
                           │    dim_date     │
                           │  (date_day PK)  │
                           └────────┬────────┘
                                    │ 1
                                    │ *
 ┌─────────────────┐       ┌────────▼────────┐       ┌─────────────────┐
 │    dim_users    │ 1   * │   fct_events    │ *   1 │ fct_experiments │
 │  (user_id PK)   ├───────┤   (event_id PK) │───────┤(assignment_id PK│
 └────────┬────────┘       └─────────────────┘       └─────────────────┘
          │ 1
          │ *
 ┌────────▼────────┐       ┌─────────────────┐
 │  fct_sessions   │       │ fct_conversions │
 │  (session_id PK)│       │(conversion_id PK│
 └─────────────────┘       └─────────────────┘
```

### Table Relationships
1. `dim_users[user_id]` (1) $\longrightarrow$ `fct_events[user_id]` (*) [Single direction]
2. `dim_users[user_id]` (1) $\longrightarrow$ `fct_sessions[user_id]` (*) [Single direction]
3. `dim_users[user_id]` (1) $\longrightarrow$ `fct_conversions[user_id]` (*) [Single direction]
4. `dim_users[user_id]` (1) $\longrightarrow$ `fct_experiments[user_id]` (*) [Single direction]
5. `dim_date[date_day]` (1) $\longrightarrow$ `fct_events[event_date]` (*) [Single direction]
6. `dim_date[date_day]` (1) $\longrightarrow$ `fct_sessions[session_date]` (*) [Single direction]
7. `dim_date[date_day]` (1) $\longrightarrow$ `fct_conversions[conversion_date]` (*) [Single direction]

---

## 2. Production DAX Measure Library

Place these measures inside a dedicated measure table `_Measures`:

### Core User & Lifecycle Measures
```dax
Total Users = DISTINCTCOUNT(dim_users[user_id])

Activated Users = 
CALCULATE(
    DISTINCTCOUNT(dim_users[user_id]),
    dim_users[is_activated_7d] = TRUE()
)

Activation Rate = 
DIVIDE([Activated Users], [Total Users], 0)

Paying Customers = 
CALCULATE(
    DISTINCTCOUNT(dim_users[user_id]),
    dim_users[is_paying_customer] = TRUE()
)

Customer Conversion Rate = 
DIVIDE([Paying Customers], [Total Users], 0)

Gross Revenue = SUM(fct_conversions[revenue_usd])

ARPU = DIVIDE([Gross Revenue], [Total Users], 0)

ARPPU = DIVIDE([Gross Revenue], [Paying Customers], 0)
```

### Engagement & Activity Measures
```dax
Daily Active Users (DAU) = 
CALCULATE(
    DISTINCTCOUNT(fct_events[user_id]),
    USERELATIONSHIP(fct_events[event_date], dim_date[date_day])
)

Total Product Events = COUNTROWS(fct_events)

Total Sessions = DISTINCTCOUNT(fct_sessions[session_id])

Avg Events per User = DIVIDE([Total Product Events], [Total Users], 0)

Avg Sessions per User = DIVIDE([Total Sessions], [Total Users], 0)

Avg Session Duration Minutes = AVERAGE(fct_sessions[duration_minutes])
```

### Experimentation & A/B Testing Measures
```dax
Experiment Users = DISTINCTCOUNT(fct_experiments[user_id])

Control Users = 
CALCULATE(
    DISTINCTCOUNT(fct_experiments[user_id]),
    SEARCH("Control", fct_experiments[variant], 1, 0) > 0
)

Treatment Users = 
CALCULATE(
    DISTINCTCOUNT(fct_experiments[user_id]),
    SEARCH("Treatment", fct_experiments[variant], 1, 0) > 0
)

Control Conversion = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(fct_experiments[user_id]),
        fct_experiments[is_activated_7d] = TRUE(),
        SEARCH("Control", fct_experiments[variant], 1, 0) > 0
    ),
    [Control Users],
    0
)

Treatment Conversion = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(fct_experiments[user_id]),
        fct_experiments[is_activated_7d] = TRUE(),
        SEARCH("Treatment", fct_experiments[variant], 1, 0) > 0
    ),
    [Treatment Users],
    0
)

Absolute Lift = [Treatment Conversion] - [Control Conversion]

Relative Lift = 
DIVIDE([Absolute Lift], [Control Conversion], 0)
```

---

## 3. Six-Page Executive Report Architecture

### Page 1 — Product Executive Overview
- **Header**: FlowPulse Executive Product Command Center.
- **Top KPI Cards**: Total Users (35,000), 7-Day Activation Rate (60.8%), Paying Customers (6,508), Gross Revenue ($720K+), DAU/MAU Stickiness (24.2%).
- **Visuals**:
  1. Monthly Signup & Revenue Trend (Dual-line area chart).
  2. End-to-End Funnel Overview (Horizontal bar chart).
  3. Retention Trajectory Curve (Line chart across days 1 to 30).
  4. Active Experiments Status Tile (EXP-01 SHIP, EXP-02 SHIP, EXP-03 INCONCLUSIVE).
- **Slicers**: Date range, Acquisition channel, Country.

### Page 2 — Funnel & Conversion
- **Header**: User Acquisition & Milestone Conversion Flow.
- **Visuals**:
  1. 5-Stage Conversion Funnel: Signup $\to$ Activation $\to$ Feature Adoption $\to$ Intent Action $\to$ Purchase.
  2. Stage-to-stage Drop-off Breakdown (% drop and volume lost).
  3. Median Hours Between Stages (Bar chart).
  4. Funnel by Device (Desktop vs Mobile vs Tablet stacked bars).
- **Slicers**: Date, Device Type, Country, User Segment.

### Page 3 — Cohort & Retention
- **Header**: Cohort Retention Decay & Longitudinal Health.
- **Visuals**:
  1. Monthly Signup Cohort Retention Heatmap (Month 0 through Month 6 matrix).
  2. Retention Decay Curves by Cohort Month (Comparing Jan, Feb, Mar, etc.).
  3. Milestone Retention Bar Chart (Day 1, Day 3, Day 7, Day 14, Day 30).
  4. Feature Adoption vs Day 7 Retention Correlation Table.
- **Slicers**: Signup Month, Acquisition Channel, Device.

### Page 4 — User Engagement & Feature Adoption
- **Header**: Product Stickiness, Activity Intensity & Feature Adoption.
- **Visuals**:
  1. DAU / WAU / MAU 8-Month Trajectory (Multi-line chart).
  2. DAU/MAU Stickiness Ratio (%) Trend.
  3. Feature Usage Breakdown (Unique users & events for Custom Dashboards, Exports, Slack, etc.).
  4. Behavioral User Segmentation Donut & Bar Chart (Power, Regular, Casual, At-Risk).
- **Slicers**: Feature Name, Behavioral Segment, Country.

### Page 5 — Experimentation Overview
- **Header**: Experimentation Portfolio & Statistical Review.
- **Visuals**:
  1. Experiment Summary Matrix (ID, Hypothesis, Primary Metric, Lift, p-value, Guardrail, Decision).
  2. Forest Plot of Treatment Effects (Point estimate + 95% CI error bars).
  3. Traffic Split Balance & SRM Verification Status Cards.
  4. Decision Badge Distribution (Green = SHIP, Red = DO NOT SHIP, Amber = INCONCLUSIVE).
- **Slicers**: Experiment Selector, Decision Category.

### Page 6 — Experiment Deep Dive & PM Decision Review
- **Header**: Product Manager Decision Memo & Subgroup Deep Dive.
- **Visuals**:
  1. Selected Experiment Header (Hypothesis, Sample Size, Duration, Target MDE).
  2. Variant Performance Comparison Cards (Control vs Treatment Metric with Lift).
  3. Subgroup Heterogeneity Forest Plot (Lift across Desktop, Mobile, Tablet).
  4. Guardrail Metrics Safety Matrix (Support ticket delta, refund request rate).
  5. Executive PM Recommendation Box (Ship rationale, annual projected revenue impact under stated assumptions).
- **Slicers**: Experiment ID dropdown.
