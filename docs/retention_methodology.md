# Retention Analysis Methodology

## 1. Overview & Definitions

Retention is the definitive metric of product-market fit and sustained product engagement. FlowPulse supports three distinct retention methodologies to avoid analytical ambiguity:

```
[Day 0: Signup] ───> [Day 1] ───> [Day 3] ───> [Day 7] ───> [Day 14] ───> [Day 30]
```

### 1.1 Classic N-Day Retention (Bracketed Window)
- **Definition**: A user is retained on Day $N$ if and only if they record at least one event in the 24-hour interval between $N \times 24$ hours and $(N+1) \times 24$ hours post-registration.
- **Formula**:
  $$\text{Classic Retention}_N = \frac{|\{u \in \text{Cohort} : \exists e \in E(u) \text{ with } t_e - t_{\text{signup}} \in [N\text{d}, (N+1)\text{d})\}|}{N_{\text{cohort}}}$$
- **Use Case**: Evaluating daily habituation and day-specific return frequency.

### 1.2 Rolling Retention (Unbounded Return)
- **Definition**: A user is retained on Day $N$ if they record at least one event on or after Day $N$.
- **Formula**:
  $$\text{Rolling Retention}_N = \frac{|\{u \in \text{Cohort} : \exists e \in E(u) \text{ with } t_e - t_{\text{signup}} \ge N\text{d}\}|}{N_{\text{cohort}}}$$
- **Use Case**: Assessing churn risk; rolling retention monotonically decreases over time and represents users who have not permanently abandoned the product.

---

## 2. Retention Disaggregation Dimensions

Retention curves are decomposed across:
1. **Acquisition Channel**: Identifying high-LTV vs high-churn channels.
2. **Device Category**: Desktop vs Mobile application retention dynamics.
3. **Core Feature Adoption**: Comparing Day 7 retention between users who engaged specific features (e.g. `custom_dashboard_created`, `slack_integrated`) versus those who did not.

> [!IMPORTANT]
> **Causality Disclaimer**:
> Observational correlation between feature adoption and 7-day retention does **not** prove that adopting the feature caused users to retain. Highly motivated users naturally adopt more features and retain longer (selection bias). Only randomized A/B experimentation demonstrates causal treatment impact.
