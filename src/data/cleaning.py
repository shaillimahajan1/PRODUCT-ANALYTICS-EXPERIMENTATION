"""
Data cleaning and staging module.
Performs type casting, deduplication, timestamp validation, and integrity checks.
"""

from pathlib import Path
from typing import Dict
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def clean_and_stage_data(raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean raw datasets and prepare staging dataframes.
    
    Args:
        raw_data: Dict of raw DataFrames (users, events, sessions, conversions, assignments)
        
    Returns:
        Dict of staged clean DataFrames
    """
    logger.info("Starting cleaning and staging pipeline...")

    # 1. Staging Users
    df_users = raw_data["users"].copy()
    df_users["signup_timestamp"] = pd.to_datetime(df_users["signup_timestamp"])
    df_users["signup_date"] = df_users["signup_timestamp"].dt.date
    df_users["signup_month"] = pd.to_datetime(df_users["signup_timestamp"].dt.to_period("M").dt.to_timestamp())
    df_users = df_users.drop_duplicates(subset=["user_id"]).reset_index(drop=True)

    # 2. Staging Events
    df_events = raw_data["events"].copy()
    df_events["event_timestamp"] = pd.to_datetime(df_events["event_timestamp"])
    df_events["event_date"] = df_events["event_timestamp"].dt.date
    df_events = df_events.drop_duplicates(subset=["event_id"]).reset_index(drop=True)
    
    # Ensure foreign key validity: events must belong to existing users
    valid_user_set = set(df_users["user_id"])
    df_events = df_events[df_events["user_id"].isin(valid_user_set)].copy()

    # 3. Staging Sessions
    df_sessions = raw_data["sessions"].copy()
    df_sessions["session_start"] = pd.to_datetime(df_sessions["session_start"])
    df_sessions["session_date"] = df_sessions["session_start"].dt.date
    df_sessions["session_end"] = pd.to_datetime(df_sessions["session_end"])
    # Validate positive duration
    df_sessions["duration_seconds"] = (
        (df_sessions["session_end"] - df_sessions["session_start"]).dt.total_seconds().clip(lower=0)
    )
    df_sessions["duration_minutes"] = (df_sessions["duration_seconds"] / 60.0).round(2)
    df_sessions = df_sessions.drop_duplicates(subset=["session_id"]).reset_index(drop=True)
    df_sessions = df_sessions[df_sessions["user_id"].isin(valid_user_set)].copy()

    # 4. Staging Conversions
    df_conversions = raw_data["conversions"].copy()
    df_conversions["conversion_timestamp"] = pd.to_datetime(df_conversions["conversion_timestamp"])
    df_conversions["conversion_date"] = df_conversions["conversion_timestamp"].dt.date
    df_conversions = df_conversions.drop_duplicates(subset=["conversion_id"]).reset_index(drop=True)
    df_conversions = df_conversions[df_conversions["user_id"].isin(valid_user_set)].copy()

    # 5. Staging Experiment Assignments
    df_assignments = raw_data["assignments"].copy()
    df_assignments["assigned_timestamp"] = pd.to_datetime(df_assignments["assigned_timestamp"])
    df_assignments["assigned_date"] = df_assignments["assigned_timestamp"].dt.date
    # Ensure exactly 1 assignment per user per experiment (no duplicate assignment or leakage)
    df_assignments = df_assignments.drop_duplicates(subset=["experiment_id", "user_id"]).reset_index(drop=True)
    df_assignments = df_assignments[df_assignments["user_id"].isin(valid_user_set)].copy()

    logger.info(
        f"Staging complete:\n"
        f"  - stg_users: {len(df_users):,} rows\n"
        f"  - stg_events: {len(df_events):,} rows\n"
        f"  - stg_sessions: {len(df_sessions):,} rows\n"
        f"  - stg_conversions: {len(df_conversions):,} rows\n"
        f"  - stg_experiment_assignments: {len(df_assignments):,} rows"
    )

    return {
        "stg_users": df_users,
        "stg_events": df_events,
        "stg_sessions": df_sessions,
        "stg_conversions": df_conversions,
        "stg_experiment_assignments": df_assignments,
    }
