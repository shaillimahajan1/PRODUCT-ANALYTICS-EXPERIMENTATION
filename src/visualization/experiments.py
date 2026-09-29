"""
Experimentation charts and forest plot visualizations.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_experiment_forest(df_results: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders a forest plot showing treatment effect point estimates with 95% confidence intervals.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    
    y_pos = np.arange(len(df_results))
    lifts = df_results["absolute_lift"]
    ci_lower = df_results["ci_lower"]
    ci_upper = df_results["ci_upper"]

    xerr_left = lifts - ci_lower
    xerr_right = ci_upper - lifts

    colors = [
        "#10B981" if "SHIP" in d and "DO NOT" not in d else ("#EF4444" if "DO NOT" in d else "#6B7280")
        for d in df_results["decision"]
    ]

    for i in range(len(df_results)):
        lift = lifts.iloc[i]
        left = xerr_left.iloc[i]
        right = xerr_right.iloc[i]
        c = colors[i]
        ax.errorbar(
            lift,
            y_pos[i],
            xerr=[[left], [right]],
            fmt="o",
            color="#1E3A8A",
            ecolor=c,
            elinewidth=3,
            capsize=6,
            markersize=8,
        )

    # Reference zero line
    ax.axvline(x=0, color="#9CA3AF", linestyle="--", linewidth=1.5)

    ax.set_yticks(y_pos)
    labels = [f"{row['experiment_id']}: {row['primary_metric']}" for _, row in df_results.iterrows()]
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Absolute Lift (Treatment - Control) with 95% CI", fontsize=11, labelpad=10)
    ax.set_title("A/B Testing Effect Estimates & Uncertainty Intervals", fontsize=13, fontweight="bold", pad=15)
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_segment_lifts(df_seg: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders bar chart of segment-level treatment lifts.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    y_pos = np.arange(len(df_seg))

    colors = ["#3B82F6" if sig else "#9CA3AF" for sig in df_seg["statistically_significant"]]

    ax.barh(y_pos, df_seg["absolute_lift"] * 100.0, color=colors, height=0.6)
    ax.axvline(0, color="black", linestyle="-", linewidth=0.8)

    labels = [f"{row['segment_dimension']}: {row['segment_value']}" for _, row in df_seg.iterrows()]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Absolute Lift (Percentage Points)", fontsize=11)
    ax.set_title("Subgroup Treatment Lifts (Blue = Statistically Significant)", fontsize=13, fontweight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
