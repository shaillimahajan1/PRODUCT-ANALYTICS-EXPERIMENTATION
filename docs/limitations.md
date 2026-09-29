# Analytical Limitations & Boundary Conditions

To maintain high data integrity and professional standards, the following technical and analytical limitations are openly acknowledged:

---

## 1. Observational vs Causal Boundaries

1. **Correlation Is Not Causality in Observational Retention**:
   - Analysis demonstrating that users who adopted the `custom_dashboard_created` feature retain at a higher 7-day rate ($+22.4\%$) is strictly observational.
   - Users who build custom dashboards have higher latent motivation and technical intent; the feature itself cannot be asserted as the sole causal driver without a randomized feature-gating experiment.
2. **Attribution Windows**:
   - Touchpoint attribution in the product funnel uses first-touch acquisition channel tracking. Multi-touch attribution (e.g., Markov chains or Shapley values across retargeting and email) is not currently implemented in this event model.

---

## 2. Statistical & Experimentation Limitations

1. **Novelty & Primacy Effects**:
   - Short-duration tests (e.g. 4-6 weeks) may capture temporary novelty spikes from existing active users encountering newly modified interfaces. Ongoing post-rollout monitoring is required to verify effect permanence.
2. **Continuous Metric Tail Heaviness**:
   - While Welch's t-test is resilient to unequal variances, extreme high-value enterprise transactions ($1,999.00) introduce positive skew into revenue distributions. Non-parametric rank tests (Mann-Whitney U) and bootstrap intervals are utilized to validate asymptotic t-test conclusions.
3. **Synthetic Experimentation Layer**:
   - In accordance with prompt guidelines (Section 5 & 6), while user demographics and behavioral event flows mirror authentic SaaS activity distributions, experiment treatment assignments are generated via a documented deterministic data-generating process to allow verifiable testing of statistical methods and decision frameworks.
