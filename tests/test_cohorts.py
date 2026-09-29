"""
Unit tests for Cohort Retention matrix computation.
"""

import pandas as pd

from src.analytics.cohorts import compute_monthly_cohorts


def test_cohort_retention_computation():
    """Verify that cohort sizes and retention percentages compute accurately."""
    users = pd.DataFrame({
        "user_id": ["U1", "U2", "U3"],
        "signup_timestamp": [
            pd.Timestamp("2026-01-15"),
            pd.Timestamp("2026-01-20"),
            pd.Timestamp("2026-02-10"),
        ],
    })

    events = pd.DataFrame([
        # U1 active in Jan, Feb, Mar
        {"user_id": "U1", "event_timestamp": pd.Timestamp("2026-01-16")},
        {"user_id": "U1", "event_timestamp": pd.Timestamp("2026-02-12")},
        {"user_id": "U1", "event_timestamp": pd.Timestamp("2026-03-05")},
        # U2 active in Jan only
        {"user_id": "U2", "event_timestamp": pd.Timestamp("2026-01-25")},
        # U3 active in Feb and Mar
        {"user_id": "U3", "event_timestamp": pd.Timestamp("2026-02-11")},
        {"user_id": "U3", "event_timestamp": pd.Timestamp("2026-03-20")},
    ])

    cohort_counts, cohort_pct, _ = compute_monthly_cohorts(users, events)

    # 2026-01 cohort has 2 users
    jan_period = pd.Period("2026-01", "M")
    feb_period = pd.Period("2026-02", "M")

    assert cohort_counts.loc[jan_period, "cohort_size"] == 2
    assert cohort_counts.loc[jan_period, 0] == 2  # Month 0: both active
    assert cohort_counts.loc[jan_period, 1] == 1  # Month 1: U1 only (50%)
    assert cohort_counts.loc[jan_period, 2] == 1  # Month 2: U1 only (50%)

    assert cohort_pct.loc[jan_period, 0] == 100.0
    assert cohort_pct.loc[jan_period, 1] == 50.0

    # 2026-02 cohort has 1 user
    assert cohort_counts.loc[feb_period, "cohort_size"] == 1
    assert cohort_counts.loc[feb_period, 0] == 1
    assert cohort_counts.loc[feb_period, 1] == 1
    assert cohort_pct.loc[feb_period, 1] == 100.0
