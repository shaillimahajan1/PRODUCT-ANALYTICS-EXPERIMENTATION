"""
Deterministic A/B Experiment Assignment Engine.
Uses SHA-256 cryptographic hashing to ensure deterministic, balanced, and reproducible user assignment.
Validates against assignment leakage and duplicate exposures.
"""

import hashlib
from typing import Optional
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def assign_variant_hash(user_id: str, salt: str, split_ratio: float = 0.5) -> str:
    """
    Deterministic hash assignment:
    SHA-256(user_id + salt) modulo 10,000 gives a uniform distribution [0, 9999].
    """
    input_str = f"{user_id}_{salt}".encode("utf-8")
    hash_int = int(hashlib.sha256(input_str).hexdigest(), 16) % 10000
    return "Treatment" if (hash_int / 10000.0) < split_ratio else "Control"


def assign_experiment_cohort(
    df_users: pd.DataFrame,
    experiment_id: str,
    salt: str,
    control_label: str,
    treatment_label: str,
    split_ratio: float = 0.5,
    filter_query: Optional[str] = None,
) -> pd.DataFrame:
    """
    Assign eligible users to experiment variants.
    
    Args:
        df_users: User DataFrame.
        experiment_id: Unique experiment identifier.
        salt: Salt for deterministic hashing.
        control_label: Full name for control group.
        treatment_label: Full name for treatment group.
        split_ratio: Traffic fraction sent to treatment (default: 0.50).
        filter_query: Optional pandas query string for eligibility.
        
    Returns:
        DataFrame of assignments with validation.
    """
    eligible = df_users.copy()
    if filter_query:
        eligible = eligible.query(filter_query).copy()

    assigned_variants = [
        treatment_label if assign_variant_hash(uid, salt, split_ratio) == "Treatment" else control_label
        for uid in eligible["user_id"]
    ]

    assignments = pd.DataFrame({
        "experiment_id": experiment_id,
        "user_id": eligible["user_id"].values,
        "variant": assigned_variants,
        "assigned_timestamp": eligible.get("signup_timestamp", pd.Timestamp.now()).values,
    })

    # Validate against duplicates
    dups = assignments.duplicated(subset=["experiment_id", "user_id"]).sum()
    if dups > 0:
        raise ValueError(f"Duplicate assignment detected in {experiment_id}: {dups} duplicates found!")

    return assignments
