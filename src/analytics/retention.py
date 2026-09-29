"""
Retention Analysis Module.
Implements N-Day Retention (Day 1, 3, 7, 14, 30), Rolling Retention, and Classic Window Retention.
Breaks down retention by acquisition channel, device, country, and feature adoption.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def compute_n_day_retention(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    days_list: List[int] = [1, 3, 7, 14, 30],
    dimension: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculate N-Day Retention.
    
    Definition:
      A user is retained on Day N if they have at least one event in the window [Day N, Day N+1).
      Rolling Day N retention: at least one event on or after Day N.
      
    Args:
        df_users: Staged user DataFrame.
        df_events: Staged event DataFrame.
        days_list: List of milestone days (e.g. 1, 3, 7, 14, 30).
        dimension: Optional column to group by ('device_type', 'acquisition_channel', 'country').
        
    Returns:
        DataFrame containing retention rates per milestone day and segment.
    """
    logger.info(f"Computing N-Day retention for milestones: {days_list}")

    cols_to_keep = ["user_id", "signup_timestamp"]
    if dimension and dimension in df_users.columns:
        cols_to_keep.append(dimension)

    users = df_users[cols_to_keep].copy()
    events = df_events[["user_id", "event_timestamp"]].copy()

    # Merge user signups with subsequent events
    merged = pd.merge(events, users, on="user_id", how="inner")
    merged["days_since_signup"] = (
        (merged["event_timestamp"] - merged["signup_timestamp"]).dt.total_seconds() / 86400.0
    )
    # Only keep activity strictly after signup (exclude signup instant)
    merged = merged[merged["days_since_signup"] > 0.01]

    groups = [None] if not dimension else sorted(users[dimension].dropna().unique())
    records = []

    for grp in groups:
        sub_users = users if grp is None else users[users[dimension] == grp]
        total_eligible = len(sub_users)
        sub_merged = merged if grp is None else merged[merged[dimension] == grp]

        for d in days_list:
            # Classic Day N: event occurred between Day d and Day d+1
            retained_exact = sub_merged[
                (sub_merged["days_since_signup"] >= d) & (sub_merged["days_since_signup"] < d + 1)
            ]["user_id"].nunique()

            # Rolling Day N: event occurred on or after Day d
            retained_rolling = sub_merged[
                sub_merged["days_since_signup"] >= d
            ]["user_id"].nunique()

            row = {
                "day_n": d,
                "cohort_size": total_eligible,
                "retained_users_exact": retained_exact,
                "retention_rate_exact": round(retained_exact / total_eligible, 4) if total_eligible > 0 else 0.0,
                "retained_users_rolling": retained_rolling,
                "retention_rate_rolling": round(retained_rolling / total_eligible, 4) if total_eligible > 0 else 0.0,
            }
            if grp is not None:
                row[dimension] = grp
            records.append(row)

    return pd.DataFrame(records)


def compute_feature_retention_correlation(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    retention_day: int = 7,
) -> pd.DataFrame:
    """
    Observational analysis: Compare Day 7 retention between users who adopted a feature vs users who did not.
    Note: As per project guidelines, correlation is NOT causality!
    """
    feature_events = df_events[df_events["event_name"] == "feature_used"].copy()
    features = feature_events["feature_name"].dropna().unique()

    # Identify users retained on or after Day 7
    users = df_users[["user_id", "signup_timestamp"]].copy()
    merged = pd.merge(df_events, users, on="user_id", how="inner")
    merged["days_since_signup"] = (
        (merged["event_timestamp"] - merged["signup_timestamp"]).dt.total_seconds() / 86400.0
    )
    retained_users = set(merged[merged["days_since_signup"] >= retention_day]["user_id"])

    results = []
    for feat in features:
        users_with_feat = set(feature_events[feature_events["feature_name"] == feat]["user_id"])
        users_without_feat = set(users["user_id"]) - users_with_feat

        n_with = len(users_with_feat)
        n_without = len(users_without_feat)

        retained_with = len(users_with_feat.intersection(retained_users))
        retained_without = len(users_without_feat.intersection(retained_users))

        rate_with = retained_with / n_with if n_with > 0 else 0.0
        rate_without = retained_without / n_without if n_without > 0 else 0.0

        results.append({
            "feature_name": feat,
            "users_adopted": n_with,
            "retention_rate_with_feature": round(rate_with, 4),
            "users_not_adopted": n_without,
            "retention_rate_without_feature": round(rate_without, 4),
            "retention_rate_difference": round(rate_with - rate_without, 4),
            "note": "Observational correlation only; not proven causal.",
        })

    return pd.DataFrame(results)
