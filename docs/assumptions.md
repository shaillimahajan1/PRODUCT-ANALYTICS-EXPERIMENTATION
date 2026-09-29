# Analytical Assumptions & Methodological Declarations

This document explicitly enumerates all business, behavioral, and statistical assumptions incorporated into the FlowPulse platform. As mandated by rigorous analytics engineering standards, assumptions are strictly segregated from observed empirical facts.

---

## 1. Segregation of Facts, Metrics, and Assumptions

```
┌─────────────────────────────────┐
│         Observed Facts          │  Raw user IDs, session timestamps, event names,
│   (Empirical Ground Truth)      │  country codes, device categories, transaction amounts.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│         Derived Metrics         │  Activation rates, DAU/MAU ratios, cohort retention %,
│   (Calculated via SQL/Python)   │  stage-to-stage drop-off, inter-session recency.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       Experiment Results        │  Empirical lifts, two-proportion z-statistics,
│   (Observed Inferences & CIs)   │  p-values, 95% Wilson intervals, SRM test results.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│      Business Assumptions       │  Annual volume extrapolations, constant lift stability,
│    (Explicit Projections)       │  causal non-interference across calendar seasons.
└─────────────────────────────────┘
```

---

## 2. Business & Monetization Assumptions

1. **Annualized Rollout Impact**:
   - **Assumption**: Projections of annual incremental revenue assume 100% rollout of the winning variant to an annual volume of 50,000 eligible users with an average subscription customer value of $145.00 USD.
   - **Caveat**: This represents an estimated economic ceiling under static market conditions; it is not realized historical revenue.
2. **Pricing Structure Invariance**:
   - **Assumption**: Plan pricing tiers ($29/mo Starter, $79/mo Pro, $290/yr Starter Annual, $790/yr Pro Annual, $1,999 Enterprise) remain constant throughout the evaluation window.
3. **Activation Window Invariance**:
   - **Assumption**: A 7-day window post-signup represents the critical threshold for onboarding habituation. Users who do not activate within 7 days exhibit $>85\%$ probability of long-term dormancy.

---

## 3. Experimentation & Statistical Assumptions

1. **Stable Unit Treatment Value Assumption (SUTVA)**:
   - **Assumption**: Assignment of any given user to Treatment does not affect the outcomes of other users (no network interference or spillover).
   - **Justification**: FlowPulse is evaluated at the individual account level, and users operate within isolated project workspaces.
2. **Independence of Stochastic Randomization**:
   - **Assumption**: Cryptographic hashing (SHA-256 modulo 10,000 with per-experiment salt) produces independent, identically distributed assignment vectors with no longitudinal correlation.
3. **No Unobserved Seasonal Interactions**:
   - **Assumption**: Pre-treatment segment baseline conversion propensities remain stable between control and treatment cohorts during the 6-to-8 week test horizons.
4. **Normality of Large-Sample Proportions**:
   - **Assumption**: Given $N_{\text{variant}} \ge 1,400$ and $N \hat{p} \ge 100$, the Central Limit Theorem holds, justifying standard normal and Chi-Square asymptotic approximations.
