"""
Product Funnel Analysis Module.
Calculates multi-stage conversion rates, stage-to-stage drop-off, time between stages,
and segment breakdowns.
"""

from typing import Dict, List, Optional
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def compute_funnel_metrics(
    df_events: pd.DataFrame,
    stages: Optional[List[Dict[str, str]]] = None,
    group_by: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculate full product funnel metrics.
    
    Default stages:
      1. Signup
      2. Activation (onboarding_completed)
      3. Feature Adoption (feature_used)
      4. Intent Action (intent_action / pricing view)
      5. Purchase (purchase / conversion)
      
    Args:
        df_events: Event fact DataFrame.
        stages: Ordered list of stage dicts [{'name': 'Signup', 'event': 'signup'}, ...].
        group_by: Optional column name for breakdown (e.g., 'device_type', 'country', 'acquisition_channel').
        
    Returns:
        DataFrame with funnel summary metrics.
    """
    if stages is None:
        stages = [
            {"name": "1. Signup", "event": "signup"},
            {"name": "2. Activation", "event": "onboarding_completed"},
            {"name": "3. Feature Adoption", "event": "feature_used"},
            {"name": "4. Intent Action", "event": "intent_action"},
            {"name": "5. Purchase", "event": "purchase"},
        ]

    stage_events = [s["event"] for s in stages]

    # Filter relevant events
    filtered = df_events[df_events["event_name"].isin(stage_events)].copy()
    
    # Earliest timestamp per user per event
    if group_by and group_by in filtered.columns:
        user_stages = (
            filtered.groupby(["user_id", group_by, "event_name"])["event_timestamp"]
            .min()
            .unstack("event_name")
            .reset_index()
        )
        groups = user_stages[group_by].unique()
    else:
        user_stages = (
            filtered.groupby(["user_id", "event_name"])["event_timestamp"]
            .min()
            .unstack("event_name")
            .reset_index()
        )
        groups = [None]

    results = []

    for grp in groups:
        df_sub = user_stages if grp is None else user_stages[user_stages[group_by] == grp]
        top_of_funnel = 0
        prev_stage_users = 0

        for i, stage in enumerate(stages):
            evt = stage["event"]
            s_name = stage["name"]
            
            # Count users who reached this stage
            if evt in df_sub.columns:
                stage_users = int(df_sub[evt].notna().sum())
            else:
                stage_users = 0

            if i == 0:
                top_of_funnel = stage_users
                prev_stage_users = stage_users
                stage_conv = 1.0 if stage_users > 0 else 0.0
                cum_conv = 1.0 if stage_users > 0 else 0.0
                drop_off = 0.0
                time_to_stage_hours = 0.0
            else:
                stage_conv = (stage_users / prev_stage_users) if prev_stage_users > 0 else 0.0
                cum_conv = (stage_users / top_of_funnel) if top_of_funnel > 0 else 0.0
                drop_off = 1.0 - stage_conv
                
                # Median time from previous stage
                prev_evt = stages[i - 1]["event"]
                if prev_evt in df_sub.columns and evt in df_sub.columns:
                    time_diff = (df_sub[evt] - df_sub[prev_evt]).dt.total_seconds() / 3600.0
                    time_diff = time_diff[time_diff >= 0]
                    time_to_stage_hours = float(time_diff.median()) if len(time_diff) > 0 else 0.0
                else:
                    time_to_stage_hours = 0.0

                prev_stage_users = stage_users

            row = {
                "stage_order": i + 1,
                "stage_name": s_name,
                "event_name": evt,
                "users_reached": stage_users,
                "stage_conversion_rate": round(stage_conv, 4),
                "cumulative_conversion_rate": round(cum_conv, 4),
                "drop_off_rate": round(drop_off, 4),
                "median_hours_from_prev_stage": round(time_to_stage_hours, 2),
            }
            if grp is not None and group_by is not None:
                row[group_by] = grp
            results.append(row)

    return pd.DataFrame(results)
