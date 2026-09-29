"""
FlowPulse Product Analytics & Experimentation Interactive Portal.
Streamlit application for exploring funnels, cohorts, and running live A/B test inference.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

from src.experimentation.confidence_intervals import proportion_difference_ci, relative_lift_ci
from src.experimentation.decision_framework import evaluate_experiment_decision
from src.experimentation.hypothesis_tests import two_proportion_z_test
from src.experimentation.power_analysis import calculate_sample_size_proportion, generate_power_curve
from src.experimentation.sample_ratio import check_sample_ratio_mismatch
from src.utils.config import load_config
from src.utils.io import load_dataframe

st.set_page_config(
    page_title="FlowPulse | Product Analytics & Experimentation",
    page_icon="📊",
    layout="wide",
)

st.title("📊 FlowPulse Product Analytics & Experimentation Intelligence")
st.markdown(
    "**Senior Product Data Analytics Platform** — Demonstrating funnel conversion, cohort retention, "
    "behavioral segmentation, and rigorous statistical A/B test decision-making."
)

config = load_config()
marts_dir = Path("data/marts")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Portal View:",
    [
        "Executive Overview",
        "Product Funnel & Conversion",
        "Cohort Retention Matrix",
        "A/B Experiment Analyzer",
        "Power & Sample Sizing Calculator",
    ],
)

# Page 1: Executive Overview
if page == "Executive Overview":
    st.subheader("🚀 Executive Product KPIs")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Registered Users", "35,000", "+100%")
    col2.metric("7-Day Activation Rate", "60.8%", "+3.2% MoM")
    col3.metric("Paying Customers", "6,508", "18.6% Payer Rate")
    col4.metric("Gross Revenue", "$720,000+", "$110.60 ARPU")
    col5.metric("Avg DAU/MAU Stickiness", "24.2%", "Healthy SaaS Tier")

    st.markdown("---")
    st.subheader("📈 Product Engagement & Traffic Trends")
    fig_path = Path("reports/figures/engagement_trends.png")
    if fig_path.exists():
        st.image(str(fig_path), caption="FlowPulse DAU, WAU, MAU Trajectory & Stickiness Ratio")

    st.subheader("👥 Behavioral User Segments Distribution")
    seg_fig_path = Path("reports/figures/segment_distribution.png")
    if seg_fig_path.exists():
        st.image(str(seg_fig_path), caption="Quantile-derived Behavioral Segments (Power, Regular, Casual, At-Risk)")

# Page 2: Funnel & Conversion
elif page == "Product Funnel & Conversion":
    st.subheader("🔻 Multi-Stage Product Conversion Funnel")
    funnel_df = load_dataframe(marts_dir / "mart_funnel.parquet")
    
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.dataframe(
            funnel_df[["stage_order", "stage_name", "users_reached", "stage_conversion_rate", "cumulative_conversion_rate", "drop_off_rate"]],
            use_container_width=True,
        )
    with col_right:
        funnel_fig = Path("reports/figures/funnel_chart.png")
        if funnel_fig.exists():
            st.image(str(funnel_fig), caption="Funnel Drop-off and Progression")

    st.subheader("📱 Funnel Breakdown by Device Category")
    device_funnel = load_dataframe(marts_dir / "mart_funnel_by_device.parquet")
    pivot_device = device_funnel.pivot(index="stage_name", columns="device_type", values="stage_conversion_rate")
    st.dataframe(pivot_device.style.format("{:.1%}"), use_container_width=True)

# Page 3: Cohort Retention Matrix
elif page == "Cohort Retention Matrix":
    st.subheader("📅 Monthly Signup Cohort Retention (%)")
    cohort_mart = load_dataframe(marts_dir / "mart_cohort_retention.parquet")
    matrix = cohort_mart.pivot(index="cohort_month", columns="period_month", values="retention_rate") * 100.0

    st.dataframe(matrix.style.format("{:.1f}%", na_rep="—"), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        hm_fig = Path("reports/figures/cohort_retention_heatmap.png")
        if hm_fig.exists():
            st.image(str(hm_fig), caption="Monthly Cohort Retention Heatmap")
    with col2:
        curves_fig = Path("reports/figures/cohort_retention_curves.png")
        if curves_fig.exists():
            st.image(str(curves_fig), caption="Retention Decay Curves across Cohort Months")

    st.markdown("---")
    st.subheader("🔍 Core Feature Adoption vs Day 7 Retention (Observational)")
    st.info("⚠️ Note: Observational correlation does NOT imply causality.")
    feat_corr = load_dataframe(marts_dir / "mart_feature_retention_correlation.parquet")
    st.dataframe(feat_corr, use_container_width=True)

# Page 4: A/B Experiment Analyzer
elif page == "A/B Experiment Analyzer":
    st.subheader("🧪 Production A/B Experiment Evaluator")
    
    exp_summary = load_dataframe(marts_dir / "mart_experiment_results.parquet")
    exp_list = exp_summary["experiment_id"].tolist()
    
    selected_exp_id = st.selectbox("Select Experiment to Inspect:", exp_list)
    conf_level = st.slider("Select Confidence Level (1 - Alpha):", min_value=0.90, max_value=0.99, value=0.95, step=0.01)

    exp_data = exp_summary[exp_summary["experiment_id"] == selected_exp_id].iloc[0]

    # Metrics Overview
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control Metric", f"{exp_data['control_value']:.2%}", f"N={exp_data['control_n']:,}")
    col2.metric("Treatment Metric", f"{exp_data['treatment_value']:.2%}", f"N={exp_data['treatment_n']:,}")
    col3.metric("Absolute Lift", f"{exp_data['absolute_lift']:+.2%}", f"p-val: {exp_data['p_value']:.4f}")
    col4.metric("Recommendation", exp_data["decision"], exp_data["quality_flag"])

    # Decision Banner
    if "SHIP" in exp_data["decision"] and "DO NOT" not in exp_data["decision"]:
        st.success(f"### ✅ PM Recommendation: {exp_data['decision']}\n{exp_data['decision_reason']}")
    elif "DO NOT SHIP" in exp_data["decision"]:
        st.error(f"### ❌ PM Recommendation: {exp_data['decision']}\n{exp_data['decision_reason']}")
    else:
        st.warning(f"### ⚠️ PM Recommendation: {exp_data['decision']}\n{exp_data['decision_reason']}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Statistical Confidence Bounds")
        st.write(f"- **Point Estimate**: `{exp_data['absolute_lift']:+.4f}`")
        st.write(f"- **95% Confidence Interval**: `[{exp_data['ci_lower']:+.4f}, {exp_data['ci_upper']:+.4f}]`")
        st.write(f"- **Relative Lift**: `{exp_data['relative_lift_pct']:+.2f}%`")
        st.write(f"- **Sample Ratio Mismatch Check**: `{exp_data['sample_ratio_check']}`")
        st.write(f"- **Guardrail Evaluation**: `{exp_data['guardrail_status']}`")

    with col_b:
        forest_path = Path("reports/figures/experiment_forest_plot.png")
        if forest_path.exists():
            st.image(str(forest_path), caption="Experiment Treatment Effects & 95% CIs")

    # Subgroups
    st.subheader("🔬 Subgroup Treatment Effects")
    seg_marts = load_dataframe(marts_dir / "mart_experiment_segments.parquet")
    sub_seg = seg_marts[seg_marts["experiment_id"] == selected_exp_id]
    if not sub_seg.empty:
        st.dataframe(sub_seg, use_container_width=True)

# Page 5: Power & Sample Sizing Calculator
elif page == "Power & Sample Sizing Calculator":
    st.subheader("⚙️ Experiment Planning & Statistical Power Sizing")
    st.markdown("Determine required sample size per variant and visualize power curves before experiment launch.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        base_rate = st.number_input("Baseline Conversion Rate (e.g. 0.10 for 10%):", min_value=0.01, max_value=0.90, value=0.10, step=0.01)
    with c2:
        target_mde = st.number_input("Target Absolute MDE (e.g. 0.02 for +2% lift):", min_value=0.005, max_value=0.20, value=0.02, step=0.005)
    with c3:
        target_alpha = st.selectbox("Significance Level (Alpha):", [0.01, 0.05, 0.10], index=1)
    with c4:
        target_power = st.selectbox("Desired Statistical Power (1 - Beta):", [0.80, 0.90, 0.95], index=0)

    sizing_res = calculate_sample_size_proportion(
        baseline_rate=base_rate,
        mde=target_mde,
        alpha=target_alpha,
        power=target_power,
    )

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Required Sample Size Per Variant", f"{sizing_res['required_sample_size_per_variant']:,}")
    kpi2.metric("Total Required Sample Size (Both Groups)", f"{sizing_res['total_required_sample_size']:,}")
    kpi3.metric("Relative MDE (%)", f"{sizing_res['relative_mde_pct']:.1f}%")

    # Power curve chart
    st.subheader("📊 Statistical Power Curve vs Detectable Effect Size")
    df_power = generate_power_curve(
        baseline_rate=base_rate,
        sample_size_per_variant=sizing_res["required_sample_size_per_variant"],
        alpha=target_alpha,
    )
    
    fig, ax = plt.subplots(figsize=(9, 4), dpi=200)
    ax.plot(df_power["absolute_mde"] * 100.0, df_power["power"] * 100.0, color="#2563EB", linewidth=2.5)
    ax.axhline(target_power * 100.0, color="#EF4444", linestyle="--", label=f"Target Power ({target_power*100:.0f}%)")
    ax.axvline(target_mde * 100.0, color="#10B981", linestyle=":", label=f"Target MDE ({target_mde*100:.1f}%)")
    ax.set_xlabel("Absolute Effect Size (Percentage Points)")
    ax.set_ylabel("Statistical Power (%)")
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    st.pyplot(fig)
