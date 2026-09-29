"""
Statistical Hypothesis Testing Engine for A/B Experiments.
Implements:
- Two-proportion z-test (pooled variance)
- Chi-Square test of independence
- Fisher's exact test (for small cell counts)
- Welch's t-test (unequal variance continuous outcomes)
- Mann-Whitney U test (non-parametric rank-sum)
- Bootstrap hypothesis testing & confidence intervals
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np
from scipy import stats

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def two_proportion_z_test(
    count_control: int,
    n_control: int,
    count_treatment: int,
    n_treatment: int,
    alternative: str = "two-sided",
) -> Dict[str, Any]:
    """
    Two-proportion pooled z-test.
    
    H0: p_treatment - p_control = 0
    H1: p_treatment != p_control (if alternative == 'two-sided')
    """
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError("Sample sizes must be strictly positive.")

    p1 = count_control / n_control
    p2 = count_treatment / n_treatment
    diff = p2 - p1

    # Pooled probability under H0
    p_pool = (count_control + count_treatment) / (n_control + n_treatment)
    se_pool = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n_control + 1.0 / n_treatment))

    if se_pool == 0:
        z_stat = 0.0
        p_val = 1.0
    else:
        z_stat = diff / se_pool
        if alternative == "two-sided":
            p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))
        elif alternative == "larger":
            p_val = 1.0 - stats.norm.cdf(z_stat)
        elif alternative == "smaller":
            p_val = stats.norm.cdf(z_stat)
        else:
            raise ValueError(f"Unknown alternative: {alternative}")

    return {
        "test_name": "two_proportion_z_test",
        "control_n": n_control,
        "control_success": count_control,
        "control_rate": round(p1, 5),
        "treatment_n": n_treatment,
        "treatment_success": count_treatment,
        "treatment_rate": round(p2, 5),
        "absolute_difference": round(diff, 5),
        "relative_difference_pct": round((diff / p1 * 100.0) if p1 > 0 else 0.0, 2),
        "z_statistic": round(float(z_stat), 4),
        "p_value": float(p_val),
    }


def welch_t_test(
    control_values: np.ndarray | list,
    treatment_values: np.ndarray | list,
    alternative: str = "two-sided",
) -> Dict[str, Any]:
    """
    Welch's t-test for comparing continuous outcomes without assuming equal variances.
    """
    c = np.asarray(control_values, dtype=float)
    t = np.asarray(treatment_values, dtype=float)

    n1, n2 = len(c), len(t)
    if n1 < 2 or n2 < 2:
        raise ValueError("Each group must contain at least 2 observations for t-test.")

    m1, m2 = float(np.mean(c)), float(np.mean(t))
    v1, v2 = float(np.var(c, ddof=1)), float(np.var(t, ddof=1))
    diff = m2 - m1

    res = stats.ttest_ind(t, c, equal_var=False, alternative=alternative)

    return {
        "test_name": "welch_t_test",
        "control_n": n1,
        "control_mean": round(m1, 4),
        "control_std": round(float(np.sqrt(v1)), 4),
        "treatment_n": n2,
        "treatment_mean": round(m2, 4),
        "treatment_std": round(float(np.sqrt(v2)), 4),
        "absolute_difference": round(diff, 4),
        "relative_difference_pct": round((diff / m1 * 100.0) if m1 != 0 else 0.0, 2),
        "t_statistic": round(float(res.statistic), 4),
        "p_value": float(res.pvalue),
    }


def mann_whitney_u_test(
    control_values: np.ndarray | list,
    treatment_values: np.ndarray | list,
    alternative: str = "two-sided",
) -> Dict[str, Any]:
    """
    Mann-Whitney U test (Wilcoxon rank-sum test) for skewed continuous distributions.
    """
    c = np.asarray(control_values, dtype=float)
    t = np.asarray(treatment_values, dtype=float)

    res = stats.mannwhitneyu(t, c, alternative=alternative)

    return {
        "test_name": "mann_whitney_u_test",
        "control_n": len(c),
        "control_median": round(float(np.median(c)), 4),
        "treatment_n": len(t),
        "treatment_median": round(float(np.median(t)), 4),
        "u_statistic": round(float(res.statistic), 4),
        "p_value": float(res.pvalue),
    }
