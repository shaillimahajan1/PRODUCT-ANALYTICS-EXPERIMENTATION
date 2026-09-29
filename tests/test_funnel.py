"""
Unit tests for Product Funnel calculations:
- Conversion rate monotonicity
- Drop-off calculation sanity
- Time to stage logic
"""

import pandas as pd
import pytest

from src.analytics.funnel import compute_funnel_metrics


def test_funnel_computation():
    """Verify standard funnel stage metrics on synthetic test events."""
    base_time = pd.Timestamp("2026-03-01 10:00:00")
    events = []

    # 100 signups
    for i in range(100):
        uid = f"U_{i}"
        events.append({"user_id": uid, "event_name": "signup", "event_timestamp": base_time})
        # 60 activate
        if i < 60:
            events.append({"user_id": uid, "event_name": "onboarding_completed", "event_timestamp": base_time + pd.Timedelta(minutes=15)})
        # 30 adopt feature
        if i < 30:
            events.append({"user_id": uid, "event_name": "feature_used", "event_timestamp": base_time + pd.Timedelta(hours=2)})
        # 15 intent
        if i < 15:
            events.append({"user_id": uid, "event_name": "intent_action", "event_timestamp": base_time + pd.Timedelta(days=1)})
        # 5 purchase
        if i < 5:
            events.append({"user_id": uid, "event_name": "purchase", "event_timestamp": base_time + pd.Timedelta(days=2)})

    df_events = pd.DataFrame(events)
    funnel = compute_funnel_metrics(df_events)

    assert len(funnel) == 5
    assert funnel.iloc[0]["users_reached"] == 100
    assert funnel.iloc[1]["users_reached"] == 60
    assert funnel.iloc[2]["users_reached"] == 30
    assert funnel.iloc[3]["users_reached"] == 15
    assert funnel.iloc[4]["users_reached"] == 5

    # Check stage conversion rates
    assert funnel.iloc[0]["stage_conversion_rate"] == 1.0
    assert funnel.iloc[1]["stage_conversion_rate"] == 0.60
    assert funnel.iloc[2]["stage_conversion_rate"] == 0.50  # 30 / 60
    assert funnel.iloc[3]["stage_conversion_rate"] == 0.50  # 15 / 30
    assert funnel.iloc[4]["stage_conversion_rate"] == pytest.approx(0.3333, abs=1e-3)  # 5 / 15

    # Cumulative conversion
    assert funnel.iloc[4]["cumulative_conversion_rate"] == 0.05  # 5 / 100
    # Drop-off rate
    assert funnel.iloc[1]["drop_off_rate"] == 0.40
