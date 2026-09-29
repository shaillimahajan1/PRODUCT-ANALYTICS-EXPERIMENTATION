# FlowPulse Metric Definitions & Mathematical Formulations

This document establishes the official definitions, formulas, and operational bounds for all product performance, engagement, retention, and experimentation metrics.

---

## 1. Product Lifecycle & Conversion Metrics

### 1.1 Activation Rate (7-Day)
- **Business Meaning**: Measures the proportion of newly registered users who complete onboarding within 7 days of signup, indicating early value realization.
- **Formula**:
  $$\text{Activation Rate} = \frac{\sum \mathbb{I}(\text{onboarding\_completed\_at} \le \text{signup\_timestamp} + 7\text{d})}{\text{Total Eligible Registered Users}}$$
- **Denominator**: Total users who registered within the evaluation window.
- **Target Benchmark**: $\ge 55.0\%$.

### 1.2 Stage-to-Stage Conversion Rate
- **Business Meaning**: Measures progression efficiency between consecutive funnel milestones.
- **Formula**:
  $$\text{Stage Conversion Rate}_{k} = \frac{U_{k}}{U_{k-1}}$$
  Where $U_k$ is the count of distinct users who reached Stage $k$, and $U_{k-1}$ reached Stage $k-1$.
- **Drop-Off Rate**:
  $$\text{Drop-Off Rate}_{k} = 1 - \text{Stage Conversion Rate}_{k}$$

### 1.3 Cumulative Funnel Conversion Rate
- **Business Meaning**: Measures end-to-end conversion from top-of-funnel entry (Signup) to terminal outcome (Paid Purchase).
- **Formula**:
  $$\text{Cumulative Conversion Rate}_{k} = \frac{U_{k}}{U_{1}}$$
  Where $U_1$ is the total volume of users who signed up.

---

## 2. Retention Metrics

### 2.1 Classic N-Day Retention
- **Business Meaning**: The proportion of cohort users active on exactly Day $N$ post-signup ($[N \times 24\text{h}, (N+1) \times 24\text{h})$).
- **Formula**:
  $$\text{Retention Rate}_{\text{Day } N} = \frac{\text{Users with } \ge 1 \text{ event during } [t_{\text{signup}} + N\text{d}, t_{\text{signup}} + (N+1)\text{d})}{\text{Total Users in Signup Cohort}}$$

### 2.2 Rolling Retention (Unbounded Retention)
- **Business Meaning**: The proportion of users who return on or after Day $N$.
- **Formula**:
  $$\text{Rolling Retention Rate}_{\text{Day } N} = \frac{\text{Users with } \ge 1 \text{ event on or after } t_{\text{signup}} + N\text{d}}{\text{Total Users in Signup Cohort}}$$

### 2.3 Monthly Cohort Retention
- **Business Meaning**: Tracks cohort activity decay across subsequent calendar months following registration month.
- **Formula**:
  $$\text{Cohort Retention Rate}_{M, P} = \frac{\text{Unique Active Users in Cohort } M \text{ during Month } (M + P)}{\text{Total Registered Users in Cohort } M}$$
  Where $M$ is signup month (e.g., 2026-01) and $P \in \{0, 1, 2, 3, 4, 5, 6\}$.

---

## 3. Product Engagement & Stickiness Metrics

### 3.1 Daily Active Users (DAU)
- Count of unique users who executed at least one non-passive product event on date $D$.

### 3.2 Weekly Active Users (WAU)
- Count of unique active users in the 7-day rolling window ending on date $D$: $[D - 6\text{d}, D]$.

### 3.3 Monthly Active Users (MAU)
- Count of unique active users in the 30-day rolling window ending on date $D$: $[D - 29\text{d}, D]$.

### 3.4 DAU / MAU Stickiness Ratio
- **Business Meaning**: Measures user habituation and frequency of product utilization.
- **Formula**:
  $$\text{Stickiness} = \frac{\text{DAU}_D}{\text{MAU}_D}$$
- **SaaS Benchmark**: $> 20\%$ indicates healthy engagement; $> 35\%$ indicates high habituation.

---

## 4. Experimentation Statistical Metrics

### 4.1 Absolute Lift
- **Formula**:
  $$\Delta = \hat{p}_{\text{treatment}} - \hat{p}_{\text{control}}$$
  Where $\hat{p} = \frac{X}{N}$ denotes observed proportion.

### 4.2 Relative Lift
- **Formula**:
  $$\text{Relative Lift (\%)} = \left(\frac{\hat{p}_{\text{treatment}} - \hat{p}_{\text{control}}}{\hat{p}_{\text{control}}}\right) \times 100\%$$

### 4.3 Two-Proportion Pooled Z-Test
- **Test Statistic**:
  $$Z = \frac{\hat{p}_t - \hat{p}_c}{\sqrt{\hat{p}_{\text{pool}}(1 - \hat{p}_{\text{pool}})\left(\frac{1}{N_t} + \frac{1}{N_c}\right)}}$$
  Where $\hat{p}_{\text{pool}} = \frac{X_t + X_c}{N_t + N_c}$.

### 4.4 Sample Ratio Mismatch (SRM) Test
- **Chi-Square Goodness-of-Fit**:
  $$\chi^2 = \sum_{i \in \{c, t\}} \frac{(O_i - E_i)^2}{E_i}, \quad df = 1$$
- **Threshold**: SRM alerted if $p < 0.001$.

### 4.5 Minimum Detectable Effect (MDE)
- **Sample Size Formulation**:
  $$N_{\text{variant}} = \frac{\left( Z_{1-\alpha/2}\sqrt{2\bar{p}(1-\bar{p})} + Z_{1-\beta}\sqrt{p_1(1-p_1) + p_2(1-p_2)} \right)^2}{(p_2 - p_1)^2}$$
