# Cohort Retention & Lifecycle Methodology

## 1. Cohort Construction

FlowPulse groups users into discrete cohorts based on their registration month:
$$\text{Cohort}(u) = \text{DATE\_TRUNC}('month', \text{signup\_timestamp}(u))$$

### Evaluation Parameters
- **Cohort Granularity**: Monthly calendar intervals (`YYYY-MM`).
- **Observation Horizon**: 6 months (Month 0 through Month 6).
- **Denominator**: Total unique users registered within that cohort month ($N_{\text{cohort}}$).
- **Numerator**: Distinct users in that cohort who triggered at least one active product event during calendar month $(M + P)$, where $P \in \{0, 1, 2, 3, 4, 5, 6\}$.

$$\text{Period Index } P = (\text{Year}_{\text{event}} - \text{Year}_{\text{signup}}) \times 12 + (\text{Month}_{\text{event}} - \text{Month}_{\text{signup}})$$

---

## 2. Retention Matrix Structure

| Cohort Month | Cohort Size | Month 0 | Month 1 | Month 2 | Month 3 | Month 4 | Month 5 | Month 6 |
|---|---|---|---|---|---|---|---|---|
| `2026-01` | $N_1$ | 100.0% | $R_{1,1}\%$ | $R_{1,2}\%$ | $R_{1,3}\%$ | $R_{1,4}\%$ | $R_{1,5}\%$ | $R_{1,6}\%$ |
| `2026-02` | $N_2$ | 100.0% | $R_{2,1}\%$ | $R_{2,2}\%$ | $R_{2,3}\%$ | $R_{2,4}\%$ | $R_{2,5}\%$ | — |
| `...` | ... | ... | ... | ... | ... | ... | ... | ... |

- **Month 0 Baseline**: Always 100.0% by definition, as user registration generates events in Month 0.
- **Incomplete Horizons**: Cells outside the observation window are left empty/null rather than filled with zero, preventing false reporting of 0% retention for unelapsed calendar periods.

---

## 3. Cohort Monetization Analysis
In addition to user retention percentages, the platform computes cumulative monthly gross revenue by cohort:
$$\text{Revenue}_{M, P} = \sum_{u \in \text{Cohort } M} \text{revenue\_usd}(u, M + P)$$
This enables calculating:
- **Cumulative Customer Lifetime Value (LTV)**: $\text{LTV}_P = \frac{\sum_{i=0}^P \text{Revenue}_{M, i}}{N_M}$.
- **Payback Period**: Duration required for cumulative gross revenue to offset customer acquisition cost (CAC).
