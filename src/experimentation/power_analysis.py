"""
Experiment Power Analysis and Sample Size Calculator.
Implements standard sample size sizing formulas for proportions and means,
as well as Minimum Detectable Effect (MDE) curves.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from scipy import stats

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def calculate_sample_size_proportion(
    baseline_rate: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
    alternative: str = "two-sided",
) -> Dict[str, Any]:
    """
    Calculate required sample size per variant for comparing two proportions.
    
    Formula based on standard normal approximation:
      n = [ (Z_{alpha/2} * sqrt(2*p_bar*(1-p_bar)) + Z_beta * sqrt(p1*(1-p1) + p2*(1-p2))) / (p2 - p1) ]^2
      
    Args:
        baseline_rate: Control conversion rate (e.g. 0.10 for 10%).
        mde: Absolute Minimum Detectable Effect (e.g. 0.02 for +2% lift).
        alpha: Type I error rate (default: 0.05).
        power: Statistical power 1 - beta (default: 0.80).
        alternative: 'two-sided' or 'one-sided'.
        
    Returns:
        Dict with required sample size per variant and assumptions.
    """
    if baseline_rate <= 0 or baseline_rate >= 1:
        raise ValueError("baseline_rate must be between 0 and 1.")
    if mde == 0:
        raise ValueError("mde cannot be zero.")

    p1 = baseline_rate
    p2 = baseline_rate + mde
    if p2 <= 0 or p2 >= 1:
        raise ValueError(f"Target rate p2 = {p2:.4f} must be between 0 and 1.")

    p_bar = (p1 + p2) / 2.0

    z_alpha = stats.norm.ppf(1.0 - (alpha / 2.0 if alternative == "two-sided" else alpha))
    z_beta = stats.norm.ppf(power)

    numerator = (
        z_alpha * np.sqrt(2 * p_bar * (1 - p_bar))
        + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    )
    n_per_variant = (numerator / abs(p2 - p1)) ** 2
    n_per_variant_int = int(np.ceil(n_per_variant))

    return {
        "baseline_rate": baseline_rate,
        "absolute_mde": mde,
        "relative_mde_pct": round((mde / baseline_rate) * 100.0, 2),
        "target_rate": round(p2, 4),
        "alpha": alpha,
        "power": power,
        "alternative": alternative,
        "required_sample_size_per_variant": n_per_variant_int,
        "total_required_sample_size": n_per_variant_int * 2,
    }


def calculate_mde(
    baseline_rate: float,
    sample_size_per_variant: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """
    Calculate the Minimum Detectable Effect (absolute) achievable given sample size.
    """
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    z_beta = stats.norm.ppf(power)
    # Approximation for small effects
    factor = (z_alpha + z_beta) * np.sqrt(2 * baseline_rate * (1 - baseline_rate) / sample_size_per_variant)
    return round(float(factor), 5)


def generate_power_curve(
    baseline_rate: float,
    sample_size_per_variant: int,
    mde_range: List[float] = None,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Generate power curve mapping effect size to achieved statistical power.
    """
    if mde_range is None:
        mde_range = list(np.linspace(0.005, 0.05, 20))

    records = []
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    n = sample_size_per_variant

    for effect in mde_range:
        p1 = baseline_rate
        p2 = baseline_rate + effect
        se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
        z_stat = (abs(p2 - p1) / se) - z_alpha
        power_val = float(stats.norm.cdf(z_stat))
        records.append({
            "absolute_mde": round(effect, 4),
            "relative_mde_pct": round((effect / baseline_rate) * 100.0, 2),
            "sample_size_per_variant": n,
            "power": round(power_val, 4),
        })

    return pd.DataFrame(records)
