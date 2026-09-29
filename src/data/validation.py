"""
Data Quality and Validation Framework.
Performs automated assertions on uniqueness, nullability, referential integrity,
experiment assignment invariants, and metrics sanity.
"""

from typing import Any, Dict, List
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class DataQualityValidator:
    """Runs data quality rules and generates QA status reports."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def log_check(self, table: str, check_name: str, passed: bool, details: str) -> None:
        status = "PASSED" if passed else "FAILED"
        self.results.append({
            "table": table,
            "check": check_name,
            "status": status,
            "details": details,
        })
        if not passed:
            logger.error(f"[DATA QA FAILURE] {table} - {check_name}: {details}")
        else:
            logger.debug(f"[DATA QA PASS] {table} - {check_name}: {details}")

    def validate_users(self, df_users: pd.DataFrame) -> None:
        """Validate user dimension invariants."""
        # Uniqueness of user_id
        is_unique = df_users["user_id"].is_unique
        self.log_check(
            "dim_user",
            "user_id_uniqueness",
            is_unique,
            f"Total rows: {len(df_users)}, Unique IDs: {df_users['user_id'].nunique()}",
        )

        # No nulls in key fields
        null_keys = df_users[["user_id", "signup_timestamp", "country", "device_type"]].isna().sum().to_dict()
        has_no_nulls = sum(null_keys.values()) == 0
        self.log_check(
            "dim_user",
            "not_null_key_attributes",
            has_no_nulls,
            f"Null counts: {null_keys}",
        )

    def validate_events(self, df_events: pd.DataFrame, df_users: pd.DataFrame) -> None:
        """Validate events fact table invariants."""
        # Uniqueness of event_id
        is_unique = df_events["event_id"].is_unique
        self.log_check(
            "fct_events",
            "event_id_uniqueness",
            is_unique,
            f"Total rows: {len(df_events)}, Unique IDs: {df_events['event_id'].nunique()}",
        )

        # Referential integrity
        user_ids = set(df_users["user_id"])
        event_users = set(df_events["user_id"])
        orphaned = len(event_users - user_ids)
        self.log_check(
            "fct_events",
            "referential_integrity_user_id",
            orphaned == 0,
            f"Orphaned user_ids in events: {orphaned}",
        )

        # Valid event names
        known_events = {
            "signup",
            "onboarding_started",
            "onboarding_completed",
            "session_started",
            "product_view",
            "search",
            "feature_used",
            "intent_action",
            "checkout_started",
            "purchase",
            "support_interaction",
        }
        invalid_events = set(df_events["event_name"]) - known_events
        self.log_check(
            "fct_events",
            "valid_event_vocabulary",
            len(invalid_events) == 0,
            f"Invalid event names found: {invalid_events}",
        )

    def validate_sessions(self, df_sessions: pd.DataFrame) -> None:
        """Validate sessions invariants."""
        # Session duration >= 0
        invalid_duration = (df_sessions["duration_seconds"] < 0).sum()
        self.log_check(
            "fct_sessions",
            "non_negative_duration",
            invalid_duration == 0,
            f"Sessions with negative duration: {invalid_duration}",
        )

        # Uniqueness
        is_unique = df_sessions["session_id"].is_unique
        self.log_check(
            "fct_sessions",
            "session_id_uniqueness",
            is_unique,
            f"Total rows: {len(df_sessions)}, Unique IDs: {df_sessions['session_id'].nunique()}",
        )

    def validate_experiments(self, df_assignments: pd.DataFrame) -> None:
        """Validate A/B experiment assignment invariants."""
        # One assignment per user per experiment
        dups = df_assignments.duplicated(subset=["experiment_id", "user_id"]).sum()
        self.log_check(
            "fct_experiment_assignments",
            "single_assignment_per_user_per_experiment",
            dups == 0,
            f"Duplicate assignments detected: {dups}",
        )

        # Valid variant values
        has_null_variants = df_assignments["variant"].isna().sum() > 0
        self.log_check(
            "fct_experiment_assignments",
            "valid_variant_labels",
            not has_null_variants,
            f"Null variants: {df_assignments['variant'].isna().sum()}",
        )

    def generate_report(self) -> pd.DataFrame:
        """Returns QA report summary as DataFrame."""
        return pd.DataFrame(self.results)

    def generate_markdown_report(self) -> str:
        """Returns QA report formatted as Markdown."""
        df = self.generate_report()
        passed_count = (df["status"] == "PASSED").sum()
        total_count = len(df)
        md = [
            "# Data Quality & Integrity Validation Report",
            f"\n**Status**: {'ALL CHECKS PASSED ✅' if passed_count == total_count else 'WARNING: CHECKS FAILED ⚠️'}",
            f"**Passed**: {passed_count} / {total_count} ({passed_count/total_count:.1%})\n",
            "| Table / Model | Check Name | Status | Details |",
            "|---|---|---|---|",
        ]
        for _, row in df.iterrows():
            icon = "✅" if row["status"] == "PASSED" else "❌"
            md.append(f"| `{row['table']}` | `{row['check']}` | {icon} {row['status']} | {row['details']} |")

        return "\n".join(md)
