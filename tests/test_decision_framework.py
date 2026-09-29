"""
Unit tests for Experiment Decision Framework.
Verifies all 5 standard business scenarios:
1. Significant Positive Result (Ship)
2. Significant Negative Result (Do Not Ship)
3. Non-Significant Result (Inconclusive / Do Not Ship)
4. Guardrail Failure (Do Not Ship / Breach)
5. SRM Failure (Invalid Experiment)
"""

import pytest
from src.experimentation.decision_framework import evaluate_experiment_decision


def test_scenario_significant_positive_ship():
    """Scenario 1: Primary metric improved significantly, exceeds MDE, guardrails intact -> SHIP."""
    res = evaluate_experiment_decision(
        experiment_id="EXP-TEST-01",
        experiment_name="Onboarding Redesign",
        primary_metric_name="activation_rate",
        control_n=5000,
        treatment_n=5000,
        control_value=0.10,
        treatment_value=0.13,
        absolute_lift=0.03,
        relative_lift_pct=30.0,
        ci_lower=0.021,
        ci_upper=0.039,
        p_value=0.0001,
        adjusted_p_value=0.0001,
        mde=0.02,
        srm_passed=True,
        guardrail_results=[{"metric": "support_ticket_rate", "passed": True}],
    )
    assert res["decision"] == "SHIP"
    assert res["statistically_significant"]
    assert res["practically_significant"]
    assert res["guardrail_status"] == "PASSED"


def test_scenario_significant_negative_reject():
    """Scenario 2: Primary metric declined with statistical significance -> DO NOT SHIP."""
    res = evaluate_experiment_decision(
        experiment_id="EXP-TEST-02",
        experiment_name="New Paywall",
        primary_metric_name="activation_rate",
        control_n=5000,
        treatment_n=5000,
        control_value=0.15,
        treatment_value=0.12,
        absolute_lift=-0.03,
        relative_lift_pct=-20.0,
        ci_lower=-0.042,
        ci_upper=-0.018,
        p_value=0.001,
        adjusted_p_value=0.001,
        mde=0.02,
        srm_passed=True,
        guardrail_results=[{"metric": "support_ticket_rate", "passed": True}],
    )
    assert "DO NOT SHIP (NEGATIVE RESULT)" in res["decision"]
    assert not res["statistically_significant"]


def test_scenario_inconclusive():
    """Scenario 3: No statistically significant difference (p > 0.05) -> INCONCLUSIVE / DO NOT SHIP."""
    res = evaluate_experiment_decision(
        experiment_id="EXP-TEST-03",
        experiment_name="Button Color",
        primary_metric_name="activation_rate",
        control_n=5000,
        treatment_n=5000,
        control_value=0.100,
        treatment_value=0.102,
        absolute_lift=0.002,
        relative_lift_pct=2.0,
        ci_lower=-0.008,
        ci_upper=0.012,
        p_value=0.45,
        adjusted_p_value=0.45,
        mde=0.02,
        srm_passed=True,
        guardrail_results=[{"metric": "support_ticket_rate", "passed": True}],
    )
    assert "INCONCLUSIVE" in res["decision"]


def test_scenario_guardrail_breach():
    """Scenario 4: Primary metric improved, but guardrail metric breached -> DO NOT SHIP."""
    res = evaluate_experiment_decision(
        experiment_id="EXP-TEST-04",
        experiment_name="Aggressive Popups",
        primary_metric_name="activation_rate",
        control_n=5000,
        treatment_n=5000,
        control_value=0.10,
        treatment_value=0.14,
        absolute_lift=0.04,
        relative_lift_pct=40.0,
        ci_lower=0.028,
        ci_upper=0.052,
        p_value=0.0001,
        adjusted_p_value=0.0001,
        mde=0.02,
        srm_passed=True,
        guardrail_results=[{"metric": "support_ticket_rate", "passed": False}],  # Breached!
    )
    assert "DO NOT SHIP (GUARDRAIL BREACH)" in res["decision"]
    assert "BREACHED" in res["guardrail_status"]


def test_scenario_srm_failure():
    """Scenario 5: SRM check failed -> Results invalid and untrusted."""
    res = evaluate_experiment_decision(
        experiment_id="EXP-TEST-05",
        experiment_name="Corrupted Allocation Test",
        primary_metric_name="activation_rate",
        control_n=4000,
        treatment_n=6000,
        control_value=0.10,
        treatment_value=0.15,
        absolute_lift=0.05,
        relative_lift_pct=50.0,
        ci_lower=0.035,
        ci_upper=0.065,
        p_value=0.00001,
        adjusted_p_value=0.00001,
        mde=0.02,
        srm_passed=False,  # Failed SRM!
        guardrail_results=[],
    )
    assert "INVALID (SRM FAILED)" in res["decision"]
    assert res["quality_flag"] == "FAILED_SRM"
