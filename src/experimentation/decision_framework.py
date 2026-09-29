"""
A/B Test Decision Framework Engine.
Applies rigorous multi-stage criteria to arrive at reproducible decisions:
1. SRM Check: Must pass (p >= 0.001) or flagged as INVALID / DATA_QUALITY_ALERT
2. Guardrail Checks: Must not exceed degradation threshold
3. Statistical Significance: Primary metric p-value < alpha (0.05)
4. Practical Significance: Point estimate or lower CI bound meets business MDE
5. Recommendation: SHIP, ITERATE, DO NOT SHIP, or INCONCLUSIVE
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def evaluate_experiment_decision(
    experiment_id: str,
    experiment_name: str,
    primary_metric_name: str,
    control_n: int,
    treatment_n: int,
    control_value: float,
    treatment_value: float,
    absolute_lift: float,
    relative_lift_pct: float,
    ci_lower: float,
    ci_upper: float,
    p_value: float,
    adjusted_p_value: float,
    mde: float,
    srm_passed: bool,
    guardrail_results: List[Dict[str, Any]],
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Evaluates complete experimental outcome through a deterministic decision tree.
    """
    # Step 1: SRM Check
    if not srm_passed:
        decision = "INVALID (SRM FAILED)"
        reason = "Sample Ratio Mismatch detected. Traffic allocation is corrupted; results cannot be trusted."
        quality_flag = "FAILED_SRM"
        stat_sig = False
        pract_sig = False
        guardrails_ok = False
        return {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "decision": decision,
            "quality_flag": quality_flag,
            "decision_reason": reason,
            "primary_metric": primary_metric_name,
            "control_n": control_n,
            "treatment_n": treatment_n,
            "control_value": control_value,
            "treatment_value": treatment_value,
            "absolute_lift": absolute_lift,
            "relative_lift_pct": relative_lift_pct,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "p_value": p_value,
            "adjusted_p_value": adjusted_p_value,
            "statistically_significant": False,
            "practically_significant": False,
            "guardrail_status": "NOT_EVALUATED",
            "sample_ratio_check": "FAILED",
        }

    # Step 2: Guardrails Evaluation
    guardrails_ok = True
    failing_guardrails = []
    for g in guardrail_results:
        if not g.get("passed", True):
            guardrails_ok = False
            failing_guardrails.append(g.get("metric", "unknown"))

    guardrail_status = "PASSED" if guardrails_ok else f"BREACHED ({', '.join(failing_guardrails)})"

    # Step 3: Statistical Significance
    stat_sig = bool(adjusted_p_value < alpha and absolute_lift > 0)
    stat_neg = bool(adjusted_p_value < alpha and absolute_lift < 0)

    # Step 4: Practical Significance (lift >= MDE)
    pract_sig = bool(absolute_lift >= mde)

    # Decision Matrix
    if not guardrails_ok:
        decision = "DO NOT SHIP (GUARDRAIL BREACH)"
        reason = f"Guardrail metric(s) breached: {', '.join(failing_guardrails)}. Negative downstream business risk."
        quality_flag = "VALID_SAMPLE"
    elif stat_neg:
        decision = "DO NOT SHIP (NEGATIVE RESULT)"
        reason = "Treatment caused a statistically significant decline in primary metric."
        quality_flag = "VALID_SAMPLE"
    elif stat_sig and pract_sig:
        decision = "SHIP"
        reason = f"Primary metric improved significantly (lift = +{absolute_lift:.4f}, p = {adjusted_p_value:.4f}) meeting business MDE ({mde:.4f}) with intact guardrails."
        quality_flag = "VALID_SAMPLE"
    elif stat_sig and not pract_sig:
        decision = "ITERATE (STAT_SIG_BELOW_MDE)"
        reason = f"Statistically significant positive lift (p = {adjusted_p_value:.4f}), but magnitude (+{absolute_lift:.4f}) is below target MDE ({mde:.4f}). Consider cost vs benefit or refining treatment."
        quality_flag = "VALID_SAMPLE"
    else:  # Not statistically significant
        decision = "INCONCLUSIVE / DO NOT SHIP"
        reason = f"No statistically significant difference observed (p = {adjusted_p_value:.4f} >= {alpha}). Insufficient evidence to justify shipping changes."
        quality_flag = "VALID_SAMPLE"

    logger.info(f"Experiment [{experiment_id}] Decision: {decision} | Reason: {reason}")

    return {
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "decision": decision,
        "quality_flag": quality_flag,
        "decision_reason": reason,
        "primary_metric": primary_metric_name,
        "control_n": control_n,
        "treatment_n": treatment_n,
        "control_value": round(control_value, 4),
        "treatment_value": round(treatment_value, 4),
        "absolute_lift": round(absolute_lift, 4),
        "relative_lift_pct": round(relative_lift_pct, 2),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "p_value": round(p_value, 5),
        "adjusted_p_value": round(adjusted_p_value, 5),
        "statistically_significant": stat_sig,
        "practically_significant": pract_sig,
        "guardrail_status": guardrail_status,
        "sample_ratio_check": "PASSED",
    }
