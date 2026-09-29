# Experimentation Methodology & Platform Framework

## 1. Randomization & Assignment Architecture

Randomized controlled trials (A/B testing) constitute the gold standard for establishing causal product mechanisms. FlowPulse enforces cryptographic, deterministic assignment to prevent allocation leakage and sample imbalances.

### 1.1 Hash-Based Assignment Function
Users are assigned to variants using the SHA-256 cryptographic hash of their unique identifier combined with an experiment-specific salt string:
$$\text{Hash Integer} = \text{SHA256}(\text{user\_id} \parallel \text{salt}) \pmod{10,000}$$
$$\text{Traffic Fraction} = \frac{\text{Hash Integer}}{10,000.0}$$
$$\text{Variant} = \begin{cases} \text{Treatment}, & \text{if Traffic Fraction} < \text{split\_ratio} \\ \text{Control}, & \text{otherwise} \end{cases}$$

### Key Properties
- **Determinism**: Given a user ID and salt, variant assignment is permanent and reproducible across repeated sessions.
- **Independence**: Changing the salt creates an orthogonal, uncorrelated assignment for subsequent experiments without residual interference.
- **Zero Leakage**: Users can never receive conflicting variants across visits or devices.

---

## 2. Sample Ratio Mismatch (SRM) Quality Gate

Before computing any treatment effect, the platform executes a **Sample Ratio Mismatch (SRM)** validation using a Pearson Chi-Square Goodness-of-Fit test:
$$\chi^2 = \frac{(O_c - E_c)^2}{E_c} + \frac{(O_t - E_t)^2}{E_t}$$
Where $O_c, O_t$ are observed sample sizes, and $E_c = E_t = \frac{O_c + O_t}{2}$ for 50/50 splits.

- **Significance Threshold**: $\alpha_{\text{SRM}} = 0.001$.
- **Protocol**: If $p < 0.001$, the experiment status is set to `FAILED_SRM` and results are labeled `INVALID`. No decision to ship can be rendered on corrupted traffic allocations.

---

## 3. Metrics Hierarchy

Every experiment rigorously pre-declares three classes of metrics:

### 3.1 Primary Metric
- The sole metric upon which the statistical hypothesis test and go/no-go ship decision is based (e.g. `activation_rate`, `checkout_conversion_rate`).

### 3.2 Secondary Metrics
- Supporting behavioral indicators explaining how users interacted with the intervention (e.g., feature adoption rates, session frequencies, ARPU).

### 3.3 Guardrail Metrics
- Critical health indicators that must not deteriorate beyond tolerance bounds (e.g., support ticket rate, refund request rate, funnel drop-off).
- If a guardrail metric is breached with statistical significance, the decision defaults to `DO NOT SHIP` regardless of primary metric lift.
