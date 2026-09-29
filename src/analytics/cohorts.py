"""
Cohort Retention and Lifecycle Analysis Module.
Builds monthly signup cohorts, tracks retention periods (Month 0 through Month 6),
calculates retained user counts, retention percentages, and cohort revenue.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def compute_monthly_cohorts(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    df_conversions: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate monthly cohort retention analysis.
    
    Cohort Definition: Signup Month (YYYY-MM).
    Retention Definition: User has at least one active event during calendar month (Cohort Month + N).
    Denominator: Total users who signed up in that cohort month.
    
    Returns:
        (cohort_counts, cohort_retention_pct, cohort_revenue)
    """
    logger.info("Computing monthly cohort retention matrix...")

    # Assign signup cohort
    users = df_users[["user_id", "signup_timestamp"]].copy()
    users["cohort_month"] = users["signup_timestamp"].dt.to_period("M")

    # Merge events with user cohort
    events = df_events[["user_id", "event_timestamp"]].copy()
    events["event_month"] = events["event_timestamp"].dt.to_period("M")

    merged = pd.merge(events, users, on="user_id", how="inner")
    # Calculate month index offset (Month 0, Month 1, ...)
    merged["cohort_period"] = (
        (merged["event_month"].dt.year - merged["cohort_month"].dt.year) * 12
        + (merged["event_month"].dt.month - merged["cohort_month"].dt.month)
    )
    # Filter negative periods (if any) and limit to 6 months
    merged = merged[(merged["cohort_period"] >= 0) & (merged["cohort_period"] <= 6)]

    # Aggregate active unique users per cohort and period
    cohort_activity = (
        merged.groupby(["cohort_month", "cohort_period"])["user_id"]
        .nunique()
        .reset_index()
    )

    # Pivot to matrix
    cohort_counts = cohort_activity.pivot(
        index="cohort_month", columns="cohort_period", values="user_id"
    ).fillna(0).astype(int)

    # Cohort base size (Month 0 count or total signups)
    cohort_sizes = users.groupby("cohort_month")["user_id"].nunique()
    cohort_counts.insert(0, "cohort_size", cohort_sizes)

    # Calculate retention percentages
    cohort_retention_pct = cohort_counts.drop(columns=["cohort_size"]).divide(
        cohort_counts["cohort_size"], axis=0
    ) * 100.0
    cohort_retention_pct = cohort_retention_pct.round(2)

    # Optional: Cohort Revenue Matrix
    if df_conversions is not None and not df_conversions.empty:
        conv = df_conversions[["user_id", "conversion_timestamp", "revenue_usd"]].copy()
        conv["conv_month"] = conv["conversion_timestamp"].dt.to_period("M")
        merged_conv = pd.merge(conv, users, on="user_id", how="inner")
        merged_conv["cohort_period"] = (
            (merged_conv["conv_month"].dt.year - merged_conv["cohort_month"].dt.year) * 12
            + (merged_conv["conv_month"].dt.month - merged_conv["cohort_month"].dt.month)
        )
        merged_conv = merged_conv[(merged_conv["cohort_period"] >= 0) & (merged_conv["cohort_period"] <= 6)]
        
        cohort_rev = (
            merged_conv.groupby(["cohort_month", "cohort_period"])["revenue_usd"]
            .sum()
            .reset_index()
        )
        cohort_revenue = cohort_rev.pivot(
            index="cohort_month", columns="cohort_period", values="revenue_usd"
        ).fillna(0.0).round(2)
    else:
        cohort_revenue = pd.DataFrame()

    return cohort_counts, cohort_retention_pct, cohort_revenue


def generate_flat_cohort_marts(
    cohort_counts: pd.DataFrame,
    cohort_retention_pct: pd.DataFrame,
) -> pd.DataFrame:
    """
    Format cohort matrix into a flat BI-ready tabular mart.
    """
    records = []
    for c_month in cohort_counts.index:
        c_size = int(cohort_counts.loc[c_month, "cohort_size"])
        for period in range(7):
            if period in cohort_counts.columns:
                retained_users = int(cohort_counts.loc[c_month, period])
                retention_rate = float(cohort_retention_pct.loc[c_month, period]) / 100.0
                records.append({
                    "cohort_month": str(c_month),
                    "period_month": period,
                    "cohort_size": c_size,
                    "retained_users": retained_users,
                    "retention_rate": round(retention_rate, 4),
                })
    return pd.DataFrame(records)
