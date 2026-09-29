# Experiment Design & Test Catalog

This document specifies the business hypotheses, treatment interventions, sample sizing, power calculations, and evaluation criteria for all product experiments executed on FlowPulse.

---

## 1. Catalog of Experiments

### 1.1 EXP-2026-01: Streamlined Interactive Onboarding Flow
- **Business Problem**: First-time signups experience cognitive friction during modal-heavy profile configuration, leading to early drop-off before reaching core analytics features.
- **Hypothesis**: Replacing static multi-step setup modals with an interactive 3-step in-app checklist increases user 7-day activation rate by at least $+2.0\%$ without increasing support ticket volume or immediate churn.
- **Target Population**: All newly registered users signing up between 2026-03-01 and 2026-04-15.
- **Randomization Unit**: `user_id` (deterministic 50/50 split).
- **Variants**:
  - `Control_Standard_Modal`: Legacy modal wizard requiring all settings upfront.
  - `Treatment_Checklist`: Lightweight persistent checklist embedded in sidebar.
- **Primary Metric**: `activation_rate` (Completed onboarding + $\ge 1$ core feature action within 7 days).
- **Secondary Metrics**: `feature_adoption_rate`, `day7_retention_rate`, `conversion_rate`.
- **Guardrail Metrics**:
  - `support_ticket_rate`: Must not increase by $> +1.5\%$.
  - `funnel_drop_off_rate`: Must not increase by $> +2.0\%$.
- **Power Sizing**: Baseline $= 58.0\%$, Target $\text{MDE} = +2.0\%$, $\alpha = 0.05$, Power $= 0.80$ $\implies N_{\text{variant}} \approx 6,000$ users.

---

### 1.2 EXP-2026-02: Self-Serve Checkout & Pricing Transparency
- **Business Problem**: High drop-off at `/pricing` and `/checkout` stages due to hidden add-on costs and complex multi-page billing forms.
- **Hypothesis**: Adding upfront pricing tier calculator and a simplified 1-click checkout modal increases checkout-to-purchase conversion rate by at least $+2.5\%$ and lifts 30-day ARPU.
- **Target Population**: Users reaching checkout between 2026-04-01 and 2026-05-31.
- **Randomization Unit**: `user_id`.
- **Variants**:
  - `Control_MultiStep_Form`: Legacy 3-step checkout redirect.
  - `Treatment_Transparent_Calculator`: Upfront interactive billing calculator with 1-click modal purchase.
- **Primary Metric**: `checkout_conversion_rate` (Checkout started to completed purchase).
- **Continuous Metric**: `revenue_per_user` (30-day gross revenue).
- **Secondary Metric**: `pro_plan_share`.
- **Guardrail Metric**: `refund_request_rate` (must not increase by $> +1.0\%$).
- **Power Sizing**: Baseline $= 52.0\%$, Target $\text{MDE} = +2.5\%$, $\alpha = 0.05$, Power $= 0.80$ $\implies N_{\text{variant}} \approx 4,000$ users.

---

### 1.3 EXP-2026-03: In-App Gamification Badges
- **Business Problem**: Growth team hypothesized that celebratory badges on feature adoption would drive repeat retention and DAU/MAU stickiness.
- **Hypothesis**: Displaying achievement badges after feature actions increases 30-day retention and DAU/MAU engagement without frustrating power users.
- **Target Population**: Active users between 2026-05-01 and 2026-06-30.
- **Randomization Unit**: `user_id`.
- **Variants**:
  - `Control_No_Badges`: Standard product UI without popups.
  - `Treatment_Gamified_Badges`: Animated badge popups on milestone actions.
- **Primary Metric**: `day30_retention_rate`.
- **Secondary Metrics**: `dau_mau_ratio`, `sessions_per_user`.
- **Guardrail Metrics**:
  - `support_ticket_rate`: Must not increase by $> +1.0\%$.
  - `cancellation_intent_rate`: Must not increase by $> +1.5\%$.
- **Power Sizing**: Baseline $= 35.0\%$, Target $\text{MDE} = +2.0\%$, $\alpha = 0.05$, Power $= 0.80$ $\implies N_{\text{variant}} \approx 5,000$ users.
