"""
Unit tests for experimentation engine:
- Hash assignment determinism
- Split balance
- Duplicate detection
- Sample Ratio Mismatch (SRM) detection
"""

import pandas as pd
import pytest

from src.experimentation.assignment import assign_variant_hash, assign_experiment_cohort
from src.experimentation.sample_ratio import check_sample_ratio_mismatch


def test_hash_assignment_determinism():
    """Hash assignment must be completely deterministic and reproducible."""
    uid = "USR_12345"
    salt = "EXPERIMENT_2026_SALT"

    v1 = assign_variant_hash(uid, salt, split_ratio=0.5)
    v2 = assign_variant_hash(uid, salt, split_ratio=0.5)
    assert v1 == v2

    # Different salt produces independent hashing
    v_diff = assign_variant_hash(uid, "DIFFERENT_SALT_xyz", split_ratio=0.5)
    # Both must be valid variant names
    assert v1 in ("Control", "Treatment")
    assert v_diff in ("Control", "Treatment")


def test_hash_assignment_balance():
    """Over 10,000 simulated users, 50/50 split should be within +/- 2%."""
    n = 10000
    salt = "BALANCE_TEST_SALT"
    treatments = sum(
        assign_variant_hash(f"USR_{i:06d}", salt, split_ratio=0.5) == "Treatment"
        for i in range(n)
    )
    ratio = treatments / n
    assert 0.48 <= ratio <= 0.52


def test_sample_ratio_mismatch_pass():
    """SRM check should pass with 5000 vs 5020 (p > 0.001)."""
    res = check_sample_ratio_mismatch(control_count=5000, treatment_count=5020, alpha=0.001)
    assert not res["srm_detected"]
    assert res["status"] == "SRM_PASSED"
    assert res["p_value"] > 0.05


def test_sample_ratio_mismatch_fail():
    """SRM check must trigger when traffic is corrupted (e.g., 4700 vs 5300 with N=10,000)."""
    res = check_sample_ratio_mismatch(control_count=4700, treatment_count=5300, alpha=0.001)
    assert res["srm_detected"]
    assert res["status"] == "SRM_ALERT_FAIL"
    assert res["p_value"] < 0.001


def test_duplicate_assignment_detection():
    """Duplicate user in cohort must raise an exception or be detected."""
    df_users = pd.DataFrame({
        "user_id": ["U1", "U2", "U1"],
        "signup_timestamp": [pd.Timestamp.now()] * 3,
    })
    with pytest.raises(ValueError, match="Duplicate assignment detected"):
        assign_experiment_cohort(
            df_users,
            experiment_id="EXP_TEST",
            salt="TEST_SALT",
            control_label="Control",
            treatment_label="Treatment",
        )
