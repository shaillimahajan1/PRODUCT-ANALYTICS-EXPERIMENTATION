# Experiment Decision Framework & Governance

## 1. Decision Flowchart

The FlowPulse decision engine enforces an objective, multi-stage decision tree designed to eliminate confirmation bias and prevent shipping interventions that harm downstream metrics.

```mermaid
flowchart TD
    START([Experiment Analysis Completed]) --> SRM_CHECK{Sample Ratio Mismatch<br/>Chi-Square p >= 0.001?}
    
    SRM_CHECK -- No --> SRM_FAIL["Decision: INVALID (SRM FAILED)<br/>Alert: Allocation Corrupted. Do not trust results."]
    SRM_CHECK -- Yes --> GUARD_CHECK{Guardrail Metrics OK?<br/>(e.g. Support tickets within tolerance)}
    
    GUARD_CHECK -- No --> GUARD_FAIL["Decision: DO NOT SHIP (GUARDRAIL BREACH)<br/>Negative downstream risk detected."]
    GUARD_CHECK -- Yes --> STAT_SIG{Primary Metric<br/>Statistically Significant?<br/>(p < 0.05 & Lift > 0)}
    
    STAT_SIG -- No (Decline) --> NEG_RESULT["Decision: DO NOT SHIP (NEGATIVE RESULT)<br/>Statistically significant decline."]
    STAT_SIG -- No (p >= 0.05) --> INCONC["Decision: INCONCLUSIVE / DO NOT SHIP<br/>Insufficient statistical evidence."]
    
    STAT_SIG -- Yes --> MDE_CHECK{Effect Magnitude<br/>>= Business MDE?}
    
    MDE_CHECK -- Yes --> SHIP["Decision: SHIP<br/>Statistically significant, practically meaningful, guardrails intact."]
    MDE_CHECK -- No --> ITERATE["Decision: ITERATE (STAT_SIG_BELOW_MDE)<br/>Positive effect, but below target MDE. Refine intervention."]
```

---

## 2. Decision Categories

1. **`SHIP`**:
   - Primary metric lift is positive and statistically significant ($p < 0.05$).
   - Effect magnitude meets or exceeds business MDE.
   - All guardrail metrics remain within safety thresholds.
   - SRM test passed ($p \ge 0.001$).
   - Subgroup treatment effects are broadly consistent without severe negative interaction.

2. **`ITERATE (STAT_SIG_BELOW_MDE)`**:
   - Primary metric shows statistically significant improvement, but point estimate falls below required business MDE.
   - Product team evaluates engineering maintenance cost against modest gain or conducts iteration.

3. **`DO NOT SHIP (NEGATIVE RESULT)`**:
   - Treatment caused a statistically significant decline in primary target metric.

4. **`DO NOT SHIP (GUARDRAIL BREACH)`**:
   - Primary metric may have improved, but one or more guardrails breached critical safety thresholds (e.g., support ticket volume spike or cancellation intent).

5. **`INCONCLUSIVE / DO NOT SHIP`**:
   - Observed difference is not statistically distinguishable from noise ($p \ge 0.05$).

6. **`INVALID (SRM FAILED)`**:
   - Sample Ratio Mismatch detected ($p < 0.001$). Traffic split was corrupted; results must be discarded and engineering instrumentation debugged.
