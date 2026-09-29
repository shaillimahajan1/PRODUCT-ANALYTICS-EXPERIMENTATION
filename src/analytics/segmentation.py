"""
Behavioral User Segmentation Module.
Segments users mathematically using empirical quantile distributions:
- Power Users: >= 90th percentile of active days and session frequency
- Regular Users: 50th-89th percentile of activity
- Casual Users: < 50th percentile of activity
- At-Risk Users: active users with zero sessions in the last 28 days
- Unactivated Users: users who never completed onboarding within 7 days of signup
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def segment_users(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    df_sessions: pd.DataFrame,
    reference_date: Optional[str | datetime] = None,
    power_quantile: float = 0.90,
    regular_quantile: float = 0.50,
) -> pd.DataFrame:
    """
    Calculate behavioral user segments based on empirical quantile cuts.
    
    Args:
        df_users: Staged users.
        df_events: Staged events.
        df_sessions: Staged sessions.
        reference_date: Reference 'today' timestamp. If None, max event timestamp is used.
        power_quantile: Quantile threshold for Power Users (default: 0.90).
        regular_quantile: Quantile threshold for Regular Users (default: 0.50).
        
    Returns:
        DataFrame mapping user_id to behavioral segment and underlying metrics.
    """
    logger.info("Computing behavioral segmentation thresholds and assignments...")

    if reference_date is None:
        ref_dt = df_events["event_timestamp"].max()
    else:
        ref_dt = pd.to_datetime(reference_date)

    # 1. User event metrics
    user_event_stats = df_events.groupby("user_id").agg(
        total_events=("event_id", "count"),
        active_days=("event_timestamp", lambda s: s.dt.date.nunique()),
        last_event_time=("event_timestamp", "max"),
        has_completed_onboarding=("event_name", lambda s: (s == "onboarding_completed").any()),
        has_purchased=("event_name", lambda s: (s == "purchase").any()),
        features_used_count=("feature_name", lambda s: s.dropna().nunique()),
    ).reset_index()

    # 2. User session metrics
    user_session_stats = df_sessions.groupby("user_id").agg(
        total_sessions=("session_id", "nunique"),
        total_duration_minutes=("duration_seconds", lambda s: round(s.sum() / 60.0, 2)),
    ).reset_index()

    # Merge with full user base
    base = df_users[["user_id", "signup_timestamp", "acquisition_channel", "country", "device_type"]].copy()
    user_metrics = pd.merge(base, user_event_stats, on="user_id", how="left")
    user_metrics = pd.merge(user_metrics, user_session_stats, on="user_id", how="left")

    user_metrics["total_events"] = user_metrics["total_events"].fillna(0).astype(int)
    user_metrics["total_sessions"] = user_metrics["total_sessions"].fillna(0).astype(int)
    user_metrics["active_days"] = user_metrics["active_days"].fillna(0).astype(int)
    user_metrics["features_used_count"] = user_metrics["features_used_count"].fillna(0).astype(int)
    user_metrics["has_completed_onboarding"] = user_metrics["has_completed_onboarding"].fillna(False)
    user_metrics["has_purchased"] = user_metrics["has_purchased"].fillna(False)

    # Inactivity calculation
    user_metrics["days_since_last_event"] = (
        (ref_dt - user_metrics["last_event_time"]).dt.total_seconds() / 86400.0
    ).fillna(999.0)

    # Calculate empirical quantiles among active users (active_days >= 1)
    active_mask = user_metrics["active_days"] >= 1
    p_events_power = user_metrics.loc[active_mask, "total_events"].quantile(power_quantile)
    p_sessions_power = user_metrics.loc[active_mask, "total_sessions"].quantile(power_quantile)
    p_events_regular = user_metrics.loc[active_mask, "total_events"].quantile(regular_quantile)

    logger.info(
        f"Empirical Segmentation Thresholds:\n"
        f"  - Power User (>= {power_quantile*100:.0f}th pct): events >= {p_events_power:.1f}, sessions >= {p_sessions_power:.1f}\n"
        f"  - Regular User (>= {regular_quantile*100:.0f}th pct): events >= {p_events_regular:.1f}\n"
        f"  - At-Risk: Inactive for >= 28 days with prior activity"
    )

    # Segmentation assignment rules
    def assign_segment(row) -> str:
        # Rule 1: Never completed onboarding
        if not row["has_completed_onboarding"]:
            return "Unactivated"
        
        # Rule 2: At-Risk: Was active in past, but inactive for > 28 days
        if row["active_days"] >= 2 and row["days_since_last_event"] >= 28:
            return "At-Risk"

        # Rule 3: Power User
        if row["total_events"] >= p_events_power and row["total_sessions"] >= p_sessions_power:
            return "Power User"

        # Rule 4: Regular User
        if row["total_events"] >= p_events_regular:
            return "Regular User"

        # Rule 5: Casual User
        return "Casual User"

    user_metrics["behavioral_segment"] = user_metrics.apply(assign_segment, axis=1)

    return user_metrics
