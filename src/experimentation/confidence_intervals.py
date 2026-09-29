"""
Confidence Intervals Engine.
Calculates rigorous uncertainty intervals for absolute lift, relative lift,
differences in proportions, and differences in means.
"""

from typing import Dict, Tuple
import numpy as np
from scipy import stats


def proportion_difference_ci(
    count_control: int,
    n_control: int,
    count_treatment: int,
    n_treatment: int,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """
    Computes confidence interval for absolute difference in proportions (p_treatment - p_control)
    using unpooled standard error and normal approximation.
    """
    p1 = count_control / n_control
    p2 = count_treatment / n_treatment
    diff = p2 - p1

    se = np.sqrt((p1 * (1 - p1) / n_control) + (p2 * (1 - p2) / n_treatment))
    z = stats.norm.ppf(1.0 - (1.0 - confidence_level) / 2.0)
    margin = z * se

    ci_lower = diff - margin
    ci_upper = diff + margin

    return {
        "absolute_lift": round(diff, 5),
        "ci_lower": round(ci_lower, 5),
        "ci_upper": round(ci_upper, 5),
        "standard_error": round(se, 5),
        "margin_of_error": round(margin, 5),
        "confidence_level": confidence_level,
    }


def relative_lift_ci(
    count_control: int,
    n_control: int,
    count_treatment: int,
    n_treatment: int,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """
    Computes confidence interval for relative lift ((p2 - p1) / p1) using the Delta Method
    on log(relative risk).
    """
    p1 = count_control / n_control
    p2 = count_treatment / n_treatment
    if p1 <= 0 or p2 <= 0:
        return {"relative_lift": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

    rr = p2 / p1
    relative_lift = rr - 1.0

    # Variance of log(RR)
    var_log_rr = ((1 - p1) / (n_control * p1)) + ((1 - p2) / (n_treatment * p2))
    se_log_rr = np.sqrt(var_log_rr)

    z = stats.norm.ppf(1.0 - (1.0 - confidence_level) / 2.0)
    ci_lower_rr = np.exp(np.log(rr) - z * se_log_rr)
    ci_upper_rr = np.exp(np.log(rr) + z * se_log_rr)

    return {
        "relative_lift_pct": round(relative_lift * 100.0, 2),
        "ci_lower_pct": round((ci_lower_rr - 1.0) * 100.0, 2),
        "ci_upper_pct": round((ci_upper_rr - 1.0) * 100.0, 2),
    }


def welch_mean_difference_ci(
    control_values: np.ndarray | list,
    treatment_values: np.ndarray | list,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """
    Computes Welch's t-confidence interval for difference in continuous means.
    """
    c = np.asarray(control_values, dtype=float)
    t = np.asarray(treatment_values, dtype=float)

    n1, n2 = len(c), len(t)
    m1, m2 = float(np.mean(c)), float(np.mean(t))
    v1, v2 = float(np.var(c, ddof=1)), float(np.var(t, ddof=1))
    diff = m2 - m1

    se = np.sqrt(v1 / n1 + v2 / n2)
    # Welch-Satterthwaite degrees of freedom
    df = ((v1 / n1 + v2 / n2) ** 2) / (
        ((v1 / n1) ** 2) / (n1 - 1) + ((v2 / n2) ** 2) / (n2 - 1)
    )

    t_crit = stats.t.ppf(1.0 - (1.0 - confidence_level) / 2.0, df=df)
    ci_lower = diff - t_crit * se
    ci_upper = diff + t_crit * se

    return {
        "absolute_lift": round(diff, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "degrees_of_freedom": round(df, 1),
        "standard_error": round(se, 4),
    }


def bootstrap_ci(
    control_values: np.ndarray | list,
    treatment_values: np.ndarray | list,
    stat_func: str = "mean",
    n_bootstraps: int = 2000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Non-parametric bootstrap confidence interval for difference in metric.
    """
    np.random.seed(seed)
    c = np.asarray(control_values, dtype=float)
    t = np.asarray(treatment_values, dtype=float)

    func = np.mean if stat_func == "mean" else np.median
    diffs = np.zeros(n_bootstraps)

    for i in range(n_bootstraps):
        sample_c = np.random.choice(c, size=len(c), replace=True)
        sample_t = np.random.choice(t, size=len(t), replace=True)
        diffs[i] = func(sample_t) - func(sample_c)

    alpha = 1.0 - confidence_level
    ci_lower = np.percentile(diffs, 100.0 * (alpha / 2.0))
    ci_upper = np.percentile(diffs, 100.0 * (1.0 - alpha / 2.0))

    return {
        "observed_lift": round(float(func(t) - func(c)), 4),
        "ci_lower": round(float(ci_lower), 4),
        "ci_upper": round(float(ci_upper), 4),
        "bootstrap_replications": n_bootstraps,
    }
