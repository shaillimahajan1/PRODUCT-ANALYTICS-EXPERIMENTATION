# FlowPulse Analytical Architecture & Technical Specifications

## 1. System Overview

The **Product Analytics & Experimentation Intelligence Platform** ("FlowPulse") is an enterprise-grade analytics engineering and statistical inference suite. It translates raw behavioral event streams into structured star-schema analytical models, cohort matrices, multi-stage conversion funnels, and rigorous statistical decisions for product experiments.

```mermaid
flowchart TD
    subgraph Ingestion ["Data Ingestion & Quality Layer"]
        RAW_U[("Raw Users CSV")]
        RAW_E[("Raw Events Parquet")]
        RAW_S[("Raw Sessions Parquet")]
        RAW_C[("Raw Conversions CSV")]
        RAW_A[("Raw Assignments CSV")]
        
        VAL["Data Quality Validator<br/>(Uniqueness, Schema, Invariants, Referential Integrity)"]
        QA_REP[("Data Quality Report MD")]
    end

    subgraph Staging ["DuckDB Staging & Transformation"]
        STG_U["stg_users"]
        STG_E["stg_events"]
        STG_S["stg_sessions"]
        STG_C["stg_conversions"]
        STG_A["stg_experiment_assignments"]
    end

    subgraph Intermediate ["Intermediate Business Logic (SQL)"]
        INT_LIFE["int_user_lifecycle<br/>(Milestones, Days to Activate, Spend)"]
        INT_SESS["int_session_metrics<br/>(Windowed Sequences, Recency LAG)"]
    end

    subgraph Marts ["Star Schema Analytical Marts"]
        DIM_U[("dim_users")]
        DIM_D[("dim_date")]
        FCT_E[("fct_events")]
        FCT_S[("fct_sessions")]
        FCT_C[("fct_conversions")]
        FCT_EXP[("fct_experiments")]
    end

    subgraph Analytics ["Product Analytics Engines"]
        FUNNEL["Multi-Stage Funnel Engine<br/>(Drop-off, Stage Conversion, Duration)"]
        COHORT["Monthly Cohort Retention Matrix<br/>(Month 0 - Month 6 Decay)"]
        RET["N-Day & Rolling Retention Engine<br/>(Day 1, 3, 7, 14, 30)"]
        ENG["Engagement & Stickiness Engine<br/>(DAU, WAU, MAU, DAU/MAU)"]
        SEG["Behavioral Segmentation Engine<br/>(Quantile-based: Power, Regular, Casual, At-Risk)"]
    end

    subgraph Experimentation ["A/B Testing & Statistical Inference"]
        SRM["Sample Ratio Mismatch (SRM)<br/>(Chi-Square Goodness-of-Fit)"]
        POWER["Power & Sample Sizing<br/>(Proportions, MDE Curves)"]
        STATS["Hypothesis Testing & Uncertainty<br/>(Two-proportion z-test, Welch t-test, Wilson CI, Delta Method)"]
        MULT["Multiple Testing Corrections<br/>(Benjamini-Hochberg FDR / Bonferroni)"]
        SUBGROUP["Heterogeneous Subgroup Analysis<br/>(Device, Geography, Acquisition Channel)"]
        DECISION{"Automated Decision Framework<br/>(SHIP / ITERATE / DO NOT SHIP / INCONCLUSIVE)"}
        IMPACT["Business Impact Modeling<br/>(Projected Lift & Revenue under 95% CI)"]
    end

    subgraph BI ["Presentation & BI Layer"]
        PBI["Power BI Executive Dashboard<br/>(6 Core Analytical Pages)"]
        MEMO["PM Experiment Decision Memo MD"]
        FIGS["Publication-Grade Visual Artifacts PNG"]
    end

    RAW_U & RAW_E & RAW_S & RAW_C & RAW_A --> VAL
    VAL --> QA_REP
    VAL --> STG_U & STG_E & STG_S & STG_C & STG_A
    STG_U & STG_E & STG_S & STG_C & STG_A --> INT_LIFE & INT_SESS
    INT_LIFE & INT_SESS --> DIM_U & DIM_D & FCT_E & FCT_S & FCT_C & FCT_EXP
    DIM_U & FCT_E & FCT_S --> FUNNEL & COHORT & RET & ENG & SEG
    FCT_EXP --> SRM --> STATS --> MULT --> SUBGROUP --> DECISION --> IMPACT
    POWER -.-> STATS
    FUNNEL & COHORT & RET & ENG & SEG & IMPACT --> PBI & MEMO & FIGS
```

## 2. Layer Definitions

### 2.1 Ingestion & Staging
- **Source**: Raw event streams and transactional records generated deterministically from stochastic data-generating distributions.
- **Engine**: Ingested and stored in high-performance columnar Parquet and CSV formats.
- **Validation**: Enforces primary key uniqueness, foreign key referential integrity, positive session durations, and non-empty timestamps before promotion.

### 2.2 Staging & Intermediate Modeling (DuckDB SQL)
- Implements dimensional modeling best practices in SQL.
- `int_user_lifecycle`: Aggregates user lifetime milestone timestamps, 7-day activation status, total revenue, and distinct core features used.
- `int_session_metrics`: Leverages window functions (`ROW_NUMBER()`, `LAG()`, `LEAD()`) to construct chronological user session sequences and inter-session inactivity intervals.

### 2.3 Dimensional Marts (Star Schema)
- `dim_users`: Granular user demographic, plan status, and behavioral tier.
- `dim_date`: Complete calendar dimension spanning all observed and projected dates.
- `fct_events`: Atomic event grain tracking exact timestamps, feature names, and devices.
- `fct_sessions`: Session duration, event counts, landing pages, and conversion indicators.
- `fct_conversions`: Order IDs, plan tiers, billing cycles, and transactional revenue.
- `fct_experiments`: Enriched experiment assignments containing pre-treatment segments and downstream activation, conversion, and guardrail outcomes.

### 2.4 Experimentation Engine
- **Randomization**: Deterministic SHA-256 cryptographic hashing on `user_id + experiment_salt` to guarantee 0% SRM under the null hypothesis, zero allocation leakage, and invariant balance.
- **Quality Gates**: Chi-Square goodness-of-fit SRM detection at $\alpha = 0.001$.
- **Statistical Tests**:
  - Two-proportion pooled z-test and Chi-square test for binary rates (Activation, Conversion, Retention).
  - Welch's t-test and Mann-Whitney U test for continuous metrics (Revenue per user, Session durations).
- **Uncertainty Quantification**: Two-sided 95% Wilson score and Wald confidence intervals for absolute lifts; Delta Method on log-relative risk for relative percentage lifts.
- **Multiple Testing**: Benjamini-Hochberg (FDR) and Bonferroni corrections across secondary and guardrail metrics.
- **Decision Engine**: Multi-tiered decision tree producing reproducible recommendations: `SHIP`, `ITERATE`, `DO NOT SHIP`, or `INCONCLUSIVE`.

### 2.5 BI & Reporting
- Power BI semantic data model with 30+ reusable DAX measures and 6 core report pages.
- Publication-quality PNG artifacts and automated Markdown executive decision memos.
