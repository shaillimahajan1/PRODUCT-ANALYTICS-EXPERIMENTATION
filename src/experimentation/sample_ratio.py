"""
Sample Ratio Mismatch (SRM) Validation Module.
Performs Chi-Square Goodness-of-Fit test to verify that observed traffic split matches expected traffic ratio.
"""

from typing import Any, Dict, Tuple
from scipy import stats

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def check_sample_ratio_mismatch(
    control_count: int,
    treatment_count: int,
    expected_ratio: Tuple[float, float] = (0.5, 0.5),
    alpha: float = 0.001,
) -> Dict[str, Any]:
    """
    Perform Chi-Square goodness-of-fit test for Sample Ratio Mismatch.
    
    Standard industry practice uses alpha = 0.001 (0.1%) to avoid false alarms
    with large sample sizes while catching real traffic allocation bugs.
    
    Args:
        control_count: Number of observed users in control.
        treatment_count: Number of observed users in treatment.
        expected_ratio: Tuple of expected fractions (e.g. (0.5, 0.5)).
        alpha: Significance threshold for SRM alert (default: 0.001).
        
    Returns:
        Dict containing test statistics, p-value, and pass/fail alert status.
    """
    total = control_count + treatment_count
    if total == 0:
        return {
            "srm_detected": False,
            "status": "INSUFFICIENT_DATA",
            "p_value": 1.0,
            "chi2_stat": 0.0,
            "control_observed": 0,
            "treatment_observed": 0,
            "control_expected": 0,
            "treatment_expected": 0,
        }

    expected_control = total * expected_ratio[0]
    expected_treatment = total * expected_ratio[1]

    observed = [control_count, treatment_count]
    expected = [expected_control, expected_treatment]

    chi2_stat, p_value = stats.chisquare(f_obs=observed, f_exp=expected)
    srm_detected = p_value < alpha

    if srm_detected:
        logger.warning(
            f"CRITICAL: SRM Detected! Control={control_count}, Treatment={treatment_count}, "
            f"chi2={chi2_stat:.4f}, p={p_value:.6e} (alpha={alpha})"
        )
    else:
        logger.info(
            f"SRM Check Passed: Control={control_count}, Treatment={treatment_count}, "
            f"chi2={chi2_stat:.4f}, p={p_value:.4f}"
        )

    return {
        "srm_detected": bool(srm_detected),
        "status": "SRM_ALERT_FAIL" if srm_detected else "SRM_PASSED",
        "p_value": float(p_value),
        "chi2_stat": float(chi2_stat),
        "control_observed": int(control_count),
        "treatment_observed": int(treatment_count),
        "control_expected": round(expected_control, 1),
        "treatment_expected": round(expected_treatment, 1),
        "observed_treatment_ratio": round(treatment_count / total, 4) if total > 0 else 0.0,
    }
