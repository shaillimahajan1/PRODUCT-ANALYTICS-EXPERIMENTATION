"""
Synthetic data generation engine for FlowPulse Product Analytics & Experimentation.
Generates realistic user lifecycle events, sessions, conversions, and deterministic A/B testing layers.
"""

from datetime import datetime, timedelta
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def generate_synthetic_dataset(
    config: Dict[str, Any],
    num_users: int = 35000,
    seed: int = 42,
    output_dir: str | Path = "data/raw",
) -> Dict[str, pd.DataFrame]:
    """
    Generate realistic synthetic product analytics data:
    - Users (demographics, channel, device, signup date)
    - Sessions (session duration, page views, conversions)
    - Events (granular event stream: signup, onboarding, feature use, checkout, purchase)
    - Conversions (transactions, revenue, plan tier)
    - Experiment Assignments and Outcomes for 3 distinct experiments

    All stochastic processes use fixed seeds and probabilistic data generating processes.
    """
    np.random.seed(seed)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    start_date = datetime.strptime(config["data_generation"]["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(config["data_generation"]["end_date"], "%Y-%m-%d")
    total_days = (end_date - start_date).days

    logger.info(f"Generating synthetic product data for {num_users} users over {total_days} days...")

    # 1. Generate Users
    countries = ["United States", "United Kingdom", "Germany", "Canada", "India", "Australia", "France"]
    country_weights = [0.42, 0.16, 0.12, 0.10, 0.09, 0.06, 0.05]

    channels = ["Organic Search", "Paid Social", "Direct", "Referral", "Product Hunt", "Email Campaign"]
    channel_weights = [0.30, 0.25, 0.18, 0.12, 0.08, 0.07]

    devices = ["Desktop", "Mobile", "Tablet"]
    device_weights = [0.65, 0.28, 0.07]

    browsers = ["Chrome", "Safari", "Edge", "Firefox"]
    browser_weights = [0.62, 0.22, 0.10, 0.06]

    user_ids = [f"USR_{i+1:06d}" for i in range(num_users)]
    signup_days_offset = np.random.randint(0, total_days, size=num_users)
    signup_seconds_offset = np.random.randint(0, 86400, size=num_users)
    signup_timestamps = [
        start_date + timedelta(days=int(d), seconds=int(s))
        for d, s in zip(signup_days_offset, signup_seconds_offset)
    ]

    assigned_countries = np.random.choice(countries, size=num_users, p=country_weights)
    assigned_channels = np.random.choice(channels, size=num_users, p=channel_weights)
    assigned_devices = np.random.choice(devices, size=num_users, p=device_weights)
    assigned_browsers = np.random.choice(browsers, size=num_users, p=browser_weights)

    # Initial plan
    initial_plans = np.random.choice(
        ["Free", "Starter_Trial", "Pro_Trial"],
        size=num_users,
        p=[0.70, 0.20, 0.10],
    )

    df_users = pd.DataFrame({
        "user_id": user_ids,
        "signup_timestamp": pd.to_datetime(signup_timestamps),
        "country": assigned_countries,
        "acquisition_channel": assigned_channels,
        "device_type": assigned_devices,
        "browser": assigned_browsers,
        "initial_plan": initial_plans,
    }).sort_values("signup_timestamp").reset_index(drop=True)

    # User latent engagement tier: Power (10%), Regular (40%), Casual (35%), Churned Day 1 (15%)
    user_tiers = np.random.choice(
        ["power", "regular", "casual", "drop_day1"],
        size=num_users,
        p=[0.12, 0.38, 0.35, 0.15],
    )
    df_users["latent_tier"] = user_tiers

    logger.info("Users generated. Now generating sessions and event streams...")

    # 2. Generate Events & Sessions
    all_events: List[Dict[str, Any]] = []
    all_sessions: List[Dict[str, Any]] = []
    all_conversions: List[Dict[str, Any]] = []

    features_list = [
        "custom_dashboard_created",
        "report_exported",
        "webhook_configured",
        "slack_integrated",
        "csv_imported",
    ]

    event_counter = 1
    session_counter = 1
    conversion_counter = 1

    # Deterministic assignment helper for experiment treatment assignment
    def get_variant(u_id: str, salt: str, split: float = 0.5) -> str:
        h = int(hashlib.sha256(f"{u_id}_{salt}".encode()).hexdigest(), 16) % 10000
        return "Treatment" if (h / 10000.0) < split else "Control"

    # Precompute experiment assignments
    exp1_start = datetime.strptime(config["experiments"]["exp_01"]["start_date"], "%Y-%m-%d")
    exp1_end = datetime.strptime(config["experiments"]["exp_01"]["end_date"], "%Y-%m-%d")

    exp2_start = datetime.strptime(config["experiments"]["exp_02"]["start_date"], "%Y-%m-%d")
    exp2_end = datetime.strptime(config["experiments"]["exp_02"]["end_date"], "%Y-%m-%d")

    exp3_start = datetime.strptime(config["experiments"]["exp_03"]["start_date"], "%Y-%m-%d")
    exp3_end = datetime.strptime(config["experiments"]["exp_03"]["end_date"], "%Y-%m-%d")

    exp_assignments: List[Dict[str, Any]] = []

    for idx, row in df_users.iterrows():
        u_id = row["user_id"]
        t_signup = row["signup_timestamp"]
        tier = row["latent_tier"]
        device = row["device_type"]
        country = row["country"]

        # Track Experiment 1 eligibility (Signups during Exp 1 window)
        in_exp1 = exp1_start <= t_signup <= exp1_end
        exp1_variant = None
        if in_exp1:
            exp1_variant = get_variant(u_id, "EXP_01_SALT_2026")
            exp_assignments.append({
                "assignment_id": f"ASG_01_{len(exp_assignments)+1:06d}",
                "experiment_id": "EXP-2026-01",
                "user_id": u_id,
                "variant": "Treatment_Checklist" if exp1_variant == "Treatment" else "Control_Standard_Modal",
                "assigned_timestamp": t_signup,
                "pre_experiment_segment": f"{row['device_type']}|{row['country']}",
            })

        # Session 1: Onboarding Session
        s1_id = f"SES_{session_counter:08d}"
        session_counter += 1
        s1_start = t_signup
        s1_events = []

        # 1. Signup event
        s1_events.append({
            "event_id": f"EVT_{event_counter:09d}",
            "event_timestamp": s1_start,
            "user_id": u_id,
            "session_id": s1_id,
            "event_name": "signup",
            "feature_name": None,
            "page_path": "/signup",
            "device_type": device,
            "country": country,
        })
        event_counter += 1

        # Onboarding flow probability
        p_onboard_start = 0.85
        # Exp 1 effect on activation: Treatment increases completion probability by ~4.5% relative
        p_onboard_complete = 0.58 if tier != "drop_day1" else 0.10
        if in_exp1 and exp1_variant == "Treatment":
            p_onboard_complete += 0.038  # realistic positive lift

        completed_onboarding = False
        cur_time = s1_start

        if np.random.rand() < p_onboard_start:
            cur_time += timedelta(seconds=np.random.randint(20, 120))
            s1_events.append({
                "event_id": f"EVT_{event_counter:09d}",
                "event_timestamp": cur_time,
                "user_id": u_id,
                "session_id": s1_id,
                "event_name": "onboarding_started",
                "feature_name": None,
                "page_path": "/onboarding/step1",
                "device_type": device,
                "country": country,
            })
            event_counter += 1

            if np.random.rand() < p_onboard_complete:
                cur_time += timedelta(seconds=np.random.randint(60, 300))
                s1_events.append({
                    "event_id": f"EVT_{event_counter:09d}",
                    "event_timestamp": cur_time,
                    "user_id": u_id,
                    "session_id": s1_id,
                    "event_name": "onboarding_completed",
                    "feature_name": None,
                    "page_path": "/onboarding/finish",
                    "device_type": device,
                    "country": country,
                })
                event_counter += 1
                completed_onboarding = True

        # Initial feature view in session 1
        if completed_onboarding or np.random.rand() < 0.4:
            cur_time += timedelta(seconds=np.random.randint(30, 180))
            s1_events.append({
                "event_id": f"EVT_{event_counter:09d}",
                "event_timestamp": cur_time,
                "user_id": u_id,
                "session_id": s1_id,
                "event_name": "product_view",
                "feature_name": "dashboard_view",
                "page_path": "/app/dashboard",
                "device_type": device,
                "country": country,
            })
            event_counter += 1

            # Feature used in session 1
            if completed_onboarding and np.random.rand() < 0.65:
                cur_time += timedelta(seconds=np.random.randint(45, 240))
                f_name = np.random.choice(features_list)
                s1_events.append({
                    "event_id": f"EVT_{event_counter:09d}",
                    "event_timestamp": cur_time,
                    "user_id": u_id,
                    "session_id": s1_id,
                    "event_name": "feature_used",
                    "feature_name": f_name,
                    "page_path": f"/app/features/{f_name}",
                    "device_type": device,
                    "country": country,
                })
                event_counter += 1

        s1_end = cur_time + timedelta(seconds=np.random.randint(10, 60))
        all_sessions.append({
            "session_id": s1_id,
            "user_id": u_id,
            "session_start": s1_start,
            "session_end": s1_end,
            "duration_seconds": int((s1_end - s1_start).total_seconds()),
            "event_count": len(s1_events),
            "device_type": device,
            "country": country,
            "had_conversion": False,
        })
        all_events.extend(s1_events)

        if tier == "drop_day1":
            continue

        # Subsequent Sessions based on tier
        if tier == "power":
            num_followup_sessions = np.random.randint(12, 35)
        elif tier == "regular":
            num_followup_sessions = np.random.randint(4, 15)
        else:  # casual
            num_followup_sessions = np.random.randint(1, 5)

        last_session_time = s1_end
        user_converted = False

        for _ in range(num_followup_sessions):
            gap_days = np.random.exponential(scale=3.5 if tier == "power" else (7.0 if tier == "regular" else 14.0))
            sess_time = last_session_time + timedelta(days=gap_days, seconds=np.random.randint(300, 7200))
            if sess_time > end_date:
                break

            s_id = f"SES_{session_counter:08d}"
            session_counter += 1
            sess_events = []
            c_time = sess_time

            # session_started
            sess_events.append({
                "event_id": f"EVT_{event_counter:09d}",
                "event_timestamp": c_time,
                "user_id": u_id,
                "session_id": s_id,
                "event_name": "session_started",
                "feature_name": None,
                "page_path": "/app/home",
                "device_type": device,
                "country": country,
            })
            event_counter += 1

            # Feature usage events in session
            num_features = np.random.randint(1, 5 if tier == "power" else 3)
            for _ in range(num_features):
                c_time += timedelta(seconds=np.random.randint(30, 200))
                feat = np.random.choice(features_list)
                sess_events.append({
                    "event_id": f"EVT_{event_counter:09d}",
                    "event_timestamp": c_time,
                    "user_id": u_id,
                    "session_id": s_id,
                    "event_name": "feature_used",
                    "feature_name": feat,
                    "page_path": f"/app/features/{feat}",
                    "device_type": device,
                    "country": country,
                })
                event_counter += 1

            # Check eligibility for EXP-2026-03 (Gamification badges during May-June 2026)
            in_exp3 = exp3_start <= c_time <= exp3_end
            if in_exp3 and not any(a["user_id"] == u_id and a["experiment_id"] == "EXP-2026-03" for a in exp_assignments):
                exp3_variant = get_variant(u_id, "EXP_03_SALT_2026")
                exp_assignments.append({
                    "assignment_id": f"ASG_03_{len(exp_assignments)+1:06d}",
                    "experiment_id": "EXP-2026-03",
                    "user_id": u_id,
                    "variant": "Treatment_Gamified_Badges" if exp3_variant == "Treatment" else "Control_No_Badges",
                    "assigned_timestamp": c_time,
                    "pre_experiment_segment": f"{row['device_type']}|{row['country']}",
                })

            # Intent & Checkout funnel events
            p_intent = 0.22 if tier == "power" else (0.12 if tier == "regular" else 0.04)
            had_conv_this_session = False

            if not user_converted and np.random.rand() < p_intent:
                c_time += timedelta(seconds=np.random.randint(40, 150))
                sess_events.append({
                    "event_id": f"EVT_{event_counter:09d}",
                    "event_timestamp": c_time,
                    "user_id": u_id,
                    "session_id": s_id,
                    "event_name": "intent_action",
                    "feature_name": "pricing_modal_view",
                    "page_path": "/pricing",
                    "device_type": device,
                    "country": country,
                })
                event_counter += 1

                # Checkout started
                if np.random.rand() < 0.60:
                    c_time += timedelta(seconds=np.random.randint(30, 90))
                    sess_events.append({
                        "event_id": f"EVT_{event_counter:09d}",
                        "event_timestamp": c_time,
                        "user_id": u_id,
                        "session_id": s_id,
                        "event_name": "checkout_started",
                        "feature_name": "checkout_flow",
                        "page_path": "/checkout",
                        "device_type": device,
                        "country": country,
                    })
                    event_counter += 1

                    # Check EXP-2026-02 eligibility (Checkout flow test in April-May)
                    in_exp2 = exp2_start <= c_time <= exp2_end
                    exp2_variant = None
                    if in_exp2 and not any(a["user_id"] == u_id and a["experiment_id"] == "EXP-2026-02" for a in exp_assignments):
                        exp2_variant = get_variant(u_id, "EXP_02_SALT_2026")
                        exp_assignments.append({
                            "assignment_id": f"ASG_02_{len(exp_assignments)+1:06d}",
                            "experiment_id": "EXP-2026-02",
                            "user_id": u_id,
                            "variant": "Treatment_Transparent_Calculator" if exp2_variant == "Treatment" else "Control_MultiStep_Form",
                            "assigned_timestamp": c_time,
                            "pre_experiment_segment": f"{row['device_type']}|{row['country']}",
                        })

                    # Checkout completion probability
                    p_checkout_complete = 0.52
                    if in_exp2 and exp2_variant == "Treatment":
                        p_checkout_complete += 0.048  # Positive conversion lift

                    if np.random.rand() < p_checkout_complete:
                        c_time += timedelta(seconds=np.random.randint(60, 240))
                        sess_events.append({
                            "event_id": f"EVT_{event_counter:09d}",
                            "event_timestamp": c_time,
                            "user_id": u_id,
                            "session_id": s_id,
                            "event_name": "purchase",
                            "feature_name": "subscription_success",
                            "page_path": "/checkout/success",
                            "device_type": device,
                            "country": country,
                        })
                        event_counter += 1
                        user_converted = True
                        had_conv_this_session = True

                        # Plan and revenue determination
                        plan_choice = np.random.choice(
                            ["Starter_Monthly", "Pro_Monthly", "Starter_Annual", "Pro_Annual", "Enterprise"],
                            p=[0.45, 0.32, 0.12, 0.08, 0.03],
                        )
                        revenue_map = {
                            "Starter_Monthly": 29.0,
                            "Pro_Monthly": 79.0,
                            "Starter_Annual": 290.0,
                            "Pro_Annual": 790.0,
                            "Enterprise": 1999.0,
                        }
                        rev = revenue_map[plan_choice]
                        all_conversions.append({
                            "conversion_id": f"CNV_{conversion_counter:06d}",
                            "user_id": u_id,
                            "session_id": s_id,
                            "conversion_timestamp": c_time,
                            "plan_name": plan_choice,
                            "billing_cycle": "Annual" if "Annual" in plan_choice else ("Monthly" if "Monthly" in plan_choice else "Custom"),
                            "revenue_usd": rev,
                            "country": country,
                            "acquisition_channel": row["acquisition_channel"],
                        })
                        conversion_counter += 1

            # Occasional support ticket or cancellation intent
            if np.random.rand() < 0.025:
                sess_events.append({
                    "event_id": f"EVT_{event_counter:09d}",
                    "event_timestamp": c_time + timedelta(seconds=30),
                    "user_id": u_id,
                    "session_id": s_id,
                    "event_name": "support_interaction",
                    "feature_name": "help_ticket",
                    "page_path": "/support/ticket",
                    "device_type": device,
                    "country": country,
                })
                event_counter += 1

            s_end = c_time + timedelta(seconds=np.random.randint(15, 60))
            all_sessions.append({
                "session_id": s_id,
                "user_id": u_id,
                "session_start": sess_time,
                "session_end": s_end,
                "duration_seconds": int((s_end - sess_time).total_seconds()),
                "event_count": len(sess_events),
                "device_type": device,
                "country": country,
                "had_conversion": had_conv_this_session,
            })
            all_events.extend(sess_events)
            last_session_time = s_end

    df_events = pd.DataFrame(all_events).sort_values("event_timestamp").reset_index(drop=True)
    df_sessions = pd.DataFrame(all_sessions).sort_values("session_start").reset_index(drop=True)
    df_conversions = pd.DataFrame(all_conversions).sort_values("conversion_timestamp").reset_index(drop=True)
    df_assignments = pd.DataFrame(exp_assignments).sort_values("assigned_timestamp").reset_index(drop=True)

    # Export to raw files
    df_users.to_csv(output_path / "raw_users.csv", index=False)
    df_events.to_parquet(output_path / "raw_events.parquet", index=False)
    df_events.head(50000).to_csv(output_path / "raw_events_sample.csv", index=False)
    df_sessions.to_parquet(output_path / "raw_sessions.parquet", index=False)
    df_sessions.head(20000).to_csv(output_path / "raw_sessions_sample.csv", index=False)
    df_conversions.to_csv(output_path / "raw_conversions.csv", index=False)
    df_assignments.to_csv(output_path / "raw_experiment_assignments.csv", index=False)

    logger.info(
        f"Synthetic data generation complete:\n"
        f"  - Users: {len(df_users):,}\n"
        f"  - Events: {len(df_events):,}\n"
        f"  - Sessions: {len(df_sessions):,}\n"
        f"  - Conversions: {len(df_conversions):,}\n"
        f"  - Experiment Assignments: {len(df_assignments):,}"
    )

    return {
        "users": df_users,
        "events": df_events,
        "sessions": df_sessions,
        "conversions": df_conversions,
        "assignments": df_assignments,
    }
