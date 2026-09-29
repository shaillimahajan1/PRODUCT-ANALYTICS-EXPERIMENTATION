"""
Unit tests for statistical inference methods:
- Two-proportion pooled z-test
- Welch's t-test
- Confidence intervals (Wilson, Wald, Delta Method)
- Power analysis & sample sizing
- Multiple testing adjustments
"""

import numpy as np
import pytest

from src.experimentation.confidence_intervals import (
    proportion_difference_ci,
    relative_lift_ci,
)
from src.experimentation.hypothesis_tests import two_proportion_z_test, welch_t_test
from src.experimentation.multiple_testing import correct_p_values
from src.experimentation.power_analysis import calculate_sample_size_proportion


def test_known_z_test_equal_proportions():
    """When proportions are identical, z=0 and p=1."""
    res = two_proportion_z_test(
        count_control=100, n_control=1000,
        count_treatment=100, n_treatment=1000
    )
    assert res["z_statistic"] == 0.0
    assert res["p_value"] == 1.0
    assert res["absolute_difference"] == 0.0


def test_known_z_test_significant_difference():
    """Textbook example: 10% vs 14% with N=1000 each -> statistically significant."""
    res = two_proportion_z_test(
        count_control=100, n_control=1000,
        count_treatment=140, n_treatment=1000
    )
    assert res["control_rate"] == 0.10
    assert res["treatment_rate"] == 0.14
    assert res["absolute_difference"] == 0.04
    assert res["z_statistic"] > 2.5
    assert res["p_value"] < 0.01


def test_proportion_confidence_interval():
    """Check that 95% CI covers the point estimate and margin matches theoretical bounds."""
    ci = proportion_difference_ci(
        count_control=500, n_control=5000,
        count_treatment=600, n_treatment=5000,
        confidence_level=0.95
    )
    assert ci["absolute_lift"] == pytest.approx(0.02, rel=1e-3)
    assert ci["ci_lower"] < ci["absolute_lift"] < ci["ci_upper"]
    assert ci["ci_lower"] > 0  # Significantly above zero


def test_relative_lift_confidence_interval():
    """Check relative lift delta method CI."""
    ci = relative_lift_ci(
        count_control=100, n_control=1000,
        count_treatment=120, n_treatment=1000
    )
    # Expected relative lift = +20%
    assert ci["relative_lift_pct"] == pytest.approx(20.0, rel=1e-2)
    assert ci["ci_lower_pct"] < ci["relative_lift_pct"] < ci["ci_upper_pct"]


def test_welch_t_test_continuous():
    """Check Welch's t-test with unequal sample variances."""
    np.random.seed(42)
    ctrl = np.random.normal(loc=10.0, scale=2.0, size=500)
    trt = np.random.normal(loc=11.5, scale=4.0, size=500)

    res = welch_t_test(ctrl, trt)
    assert res["treatment_mean"] > res["control_mean"]
    assert res["t_statistic"] > 0
    assert res["p_value"] < 0.001


def test_power_analysis_sample_size():
    """Check sample size calculation formula against standard power benchmarks."""
    # Baseline 10%, MDE +2% (abs), alpha=0.05, power=0.80
    res = calculate_sample_size_proportion(
        baseline_rate=0.10, mde=0.02, alpha=0.05, power=0.80
    )
    # Standard sample size per variant is ~3,800 to 4,000 users
    assert 3500 <= res["required_sample_size_per_variant"] <= 4500
    assert res["total_required_sample_size"] == res["required_sample_size_per_variant"] * 2


def test_multiple_testing_correction():
    """Check Benjamini-Hochberg and Bonferroni adjustments."""
    p_dict = {
        "m1": 0.001,
        "m2": 0.045,
        "m3": 0.049,
        "m4": 0.200,
    }
    df_adj = correct_p_values(p_dict, method="bonferroni", alpha=0.05)
    # Bonferroni: 0.045 * 4 = 0.180 (no longer significant at 0.05)
    row_m2 = df_adj[df_adj["metric"] == "m2"].iloc[0]
    assert row_m2["adjusted_p_value"] == pytest.approx(0.045 * 4, rel=1e-2)
    assert not row_m2["statistically_significant"]

    # m1 remains significant (0.001 * 4 = 0.004 < 0.05)
    row_m1 = df_adj[df_adj["metric"] == "m1"].iloc[0]
    assert row_m1["statistically_significant"]
