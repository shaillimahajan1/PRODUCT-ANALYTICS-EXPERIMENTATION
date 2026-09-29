"""
User Engagement and Product Stickiness Module.
Calculates Daily Active Users (DAU), Weekly Active Users (WAU), Monthly Active Users (MAU),
DAU/MAU stickiness ratio, sessions per user, events per session, and feature frequency.
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def compute_engagement_timeseries(df_events: pd.DataFrame) -> pd.DataFrame:
    """
    Computes daily engagement metrics:
      - DAU: Unique users with events on date D
      - WAU: Rolling 7-day unique active users ending on date D
      - MAU: Rolling 30-day unique active users ending on date D
      - DAU / MAU: Stickiness ratio
      - Total Daily Events
      - Daily Sessions
    """
    logger.info("Computing daily engagement time series and DAU/MAU stickiness...")
    events = df_events[["user_id", "event_timestamp", "session_id"]].copy()
    events["event_date"] = events["event_timestamp"].dt.floor("D")

    # Distinct daily users
    daily_user_df = events.groupby(["event_date", "user_id"]).size().reset_index().drop(columns=[0])
    
    # Date range
    min_date = daily_user_df["event_date"].min()
    max_date = daily_user_df["event_date"].max()
    all_dates = pd.date_range(min_date, max_date, freq="D")

    # Map dates to sets of active users
    date_to_users: Dict[pd.Timestamp, set] = (
        daily_user_df.groupby("event_date")["user_id"].apply(set).to_dict()
    )

    records = []
    for d in all_dates:
        # DAU: active on day d
        dau_users = date_to_users.get(d, set())
        dau = len(dau_users)

        # WAU: active in last 7 days [d - 6 days, d]
        wau_window_dates = [d - pd.Timedelta(days=i) for i in range(7)]
        wau_users = set().union(*[date_to_users.get(dt, set()) for dt in wau_window_dates])
        wau = len(wau_users)

        # MAU: active in last 30 days [d - 29 days, d]
        mau_window_dates = [d - pd.Timedelta(days=i) for i in range(30)]
        mau_users = set().union(*[date_to_users.get(dt, set()) for dt in mau_window_dates])
        mau = len(mau_users)

        stickiness = (dau / mau) if mau > 0 else 0.0

        records.append({
            "date": d.date(),
            "dau": dau,
            "wau": wau,
            "mau": mau,
            "dau_mau_ratio": round(stickiness, 4),
        })

    df_engagement = pd.DataFrame(records)

    # Daily events & sessions counts
    daily_stats = events.groupby("event_date").agg(
        total_events=("user_id", "count"),
        total_sessions=("session_id", "nunique"),
    ).reset_index()
    daily_stats["date"] = daily_stats["event_date"].dt.date
    daily_stats = daily_stats.drop(columns=["event_date"])

    df_merged = pd.merge(df_engagement, daily_stats, on="date", how="left").fillna(0)
    df_merged["events_per_dau"] = np.where(
        df_merged["dau"] > 0, (df_merged["total_events"] / df_merged["dau"]).round(2), 0.0
    )
    df_merged["sessions_per_dau"] = np.where(
        df_merged["dau"] > 0, (df_merged["total_sessions"] / df_merged["dau"]).round(2), 0.0
    )

    return df_merged


def compute_feature_adoption_metrics(df_events: pd.DataFrame) -> pd.DataFrame:
    """
    Computes adoption metrics across all tracked product features:
      - Unique users adopting feature
      - Total feature events
      - Average feature events per adopting user
      - Feature share of total events
    """
    feature_events = df_events[df_events["event_name"] == "feature_used"].copy()
    total_feature_events = len(feature_events)
    total_distinct_users = df_events["user_id"].nunique()

    feature_summary = feature_events.groupby("feature_name").agg(
        unique_users=("user_id", "nunique"),
        event_count=("event_id", "count"),
    ).reset_index()

    feature_summary["adoption_rate"] = (
        feature_summary["unique_users"] / total_distinct_users
    ).round(4)
    feature_summary["events_per_user"] = (
        feature_summary["event_count"] / feature_summary["unique_users"]
    ).round(2)
    feature_summary["feature_share_pct"] = (
        feature_summary["event_count"] / total_feature_events * 100.0
    ).round(2)

    return feature_summary.sort_values("adoption_rate", ascending=False).reset_index(drop=True)
