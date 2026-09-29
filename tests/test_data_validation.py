"""
Unit tests for Data Quality Validation checks.
"""

import pandas as pd
import pytest

from src.data.validation import DataQualityValidator


def test_validator_detects_duplicate_users():
    """Validator should flag duplicate user IDs."""
    validator = DataQualityValidator()
    df_users = pd.DataFrame({
        "user_id": ["U1", "U1", "U2"],
        "signup_timestamp": [pd.Timestamp.now()] * 3,
        "country": ["US", "US", "UK"],
        "device_type": ["Desktop"] * 3,
    })
    validator.validate_users(df_users)
    report = validator.generate_report()
    dup_check = report[report["check"] == "user_id_uniqueness"].iloc[0]
    assert dup_check["status"] == "FAILED"


def test_validator_detects_orphaned_events():
    """Validator should flag events associated with unknown users."""
    validator = DataQualityValidator()
    df_users = pd.DataFrame({"user_id": ["U1", "U2"]})
    df_events = pd.DataFrame({
        "event_id": ["E1", "E2"],
        "user_id": ["U1", "U999_ORPHAN"],
        "event_name": ["signup", "signup"],
    })
    validator.validate_events(df_events, df_users)
    report = validator.generate_report()
    ref_check = report[report["check"] == "referential_integrity_user_id"].iloc[0]
    assert ref_check["status"] == "FAILED"
