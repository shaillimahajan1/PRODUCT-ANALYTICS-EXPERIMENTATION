# Product Funnel Analysis Methodology

## 1. Funnel Architecture

FlowPulse tracks a 5-stage sequential conversion funnel representing user progression from registration to paid monetization:

```
[1. Signup] ──(Activation Conv)──> [2. Activation] ──(Feature Adoption)──> [3. Feature Adoption] ──(Intent Conv)──> [4. Purchase Intent] ──(Terminal Conv)──> [5. Purchase]
```

### Stage Definitions & Event Triggers
1. **Stage 1 — Signup**: User account is successfully provisioned (`event_name = 'signup'`). Top of funnel (100% entry baseline).
2. **Stage 2 — Activation**: User successfully finishes onboarding configuration (`event_name = 'onboarding_completed'`) within 7 days of signup.
3. **Stage 3 — Feature Adoption**: User executes at least one core interactive product capability (`event_name = 'feature_used'`) such as creating a custom dashboard, running a funnel query, or configuring a webhook.
4. **Stage 4 — Purchase Intent**: User actively inspects upgrade offerings or triggers checkout intent (`event_name = 'intent_action'` or `event_name = 'checkout_started'`).
5. **Stage 5 — Purchase**: User successfully settles a paid subscription plan invoice (`event_name = 'purchase'`).

---

## 2. Calculation Standards & Invariants

### 2.1 Monotonic Progression
- A user can only count towards Stage $k$ if they have completed Stage 1 (Signup) and event timestamp $t_k \ge t_{1}$.
- In calculating stage-to-stage transition metrics, $U_k$ is the distinct count of users who reached Stage $k$.
- By construction:
  $$U_1 \ge U_2 \ge U_3 \ge U_4 \ge U_5$$

### 2.2 Transition Duration
- Time between stages is calculated as the positive duration difference in hours between the first timestamp of Stage $k-1$ and Stage $k$:
  $$\Delta t_k = \frac{t_k - t_{k-1}}{3600 \text{ seconds}}$$
- The platform reports the **median duration** to remain robust against long right-skewed tails from returning dormant users.

### 2.3 Segment Slicing
- Funnels are decomposed across:
  - **Device Type**: Desktop, Mobile, Tablet.
  - **Country**: United States, United Kingdom, Germany, Canada, India, Australia, France.
  - **Acquisition Channel**: Organic Search, Paid Social, Direct, Referral, Product Hunt, Email Campaign.
