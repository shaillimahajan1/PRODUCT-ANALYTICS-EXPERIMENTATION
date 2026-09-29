"""
Subgroup and Heterogeneous Treatment Effect Analysis Module.
Evaluates experiment treatment effects across pre-treatment dimensions (device, country, channel).
Calculates sample sizes, conversion rates, lifts, confidence intervals, and p-values per segment.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

from src.experimentation.confidence_intervals import proportion_difference_ci
from src.experimentation.hypothesis_tests import two_proportion_z_test


def evaluate_segment_effects(
    df_experiment_users: pd.DataFrame,
    segment_col: str,
    outcome_col: str,
    variant_col: str = "variant",
    control_label: str = "Control",
    min_sample_size: int = 50,
) -> pd.DataFrame:
    """
    Compute subgroup treatment effects for a binary outcome across categories of a segment dimension.
    
    Args:
        df_experiment_users: DataFrame with user_id, segment_col, variant_col, outcome_col (0 or 1).
        segment_col: Column to segment by (e.g., 'device_type', 'country', 'acquisition_channel').
        outcome_col: Binary outcome indicator (1 if activated/converted, 0 otherwise).
        variant_col: Column indicating variant assignment.
        control_label: Substring identifying control variant.
        min_sample_size: Minimum sample size per variant in segment to run test.
        
    Returns:
        DataFrame of segment-level results.
    """
    segments = sorted(df_experiment_users[segment_col].dropna().unique())
    results = []

    for seg in segments:
        sub = df_experiment_users[df_experiment_users[segment_col] == seg]
        
        # Partition control vs treatment
        ctrl = sub[sub[variant_col].str.contains(control_label, case=False, na=False)]
        trt = sub[~sub[variant_col].str.contains(control_label, case=False, na=False)]

        n_c = len(ctrl)
        n_t = len(trt)

        if n_c < min_sample_size or n_t < min_sample_size:
            continue

        c_success = int(ctrl[outcome_col].sum())
        t_success = int(trt[outcome_col].sum())

        p_c = c_success / n_c if n_c > 0 else 0.0
        p_t = t_success / n_t if n_t > 0 else 0.0
        abs_lift = p_t - p_c
        rel_lift = (abs_lift / p_c * 100.0) if p_c > 0 else 0.0

        # Run z-test and CI
        z_res = two_proportion_z_test(c_success, n_c, t_success, n_t)
        ci_res = proportion_difference_ci(c_success, n_c, t_success, n_t)

        results.append({
            "segment_dimension": segment_col,
            "segment_value": seg,
            "control_n": n_c,
            "treatment_n": n_t,
            "control_rate": round(p_c, 4),
            "treatment_rate": round(p_t, 4),
            "absolute_lift": round(abs_lift, 4),
            "relative_lift_pct": round(rel_lift, 2),
            "ci_lower": ci_res["ci_lower"],
            "ci_upper": ci_res["ci_upper"],
            "p_value": z_res["p_value"],
            "statistically_significant": z_res["p_value"] < 0.05,
        })

    return pd.DataFrame(results)
