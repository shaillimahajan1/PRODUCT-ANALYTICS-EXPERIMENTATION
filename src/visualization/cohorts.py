"""
Cohort Heatmap and Retention Curve Visualizations.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_cohort_heatmap(df_retention_pct: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders monthly cohort retention heatmap.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Format index as strings
    data = df_retention_pct.copy()
    data.index = [str(idx) for idx in data.index]
    data.columns = [f"M{col}" for col in data.columns]

    sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        cbar_kws={"label": "Retention Rate (%)"},
        linewidths=0.5,
        linecolor="#E5E7EB",
        ax=ax,
        vmin=0,
        vmax=100,
    )

    ax.set_title("FlowPulse Monthly Signup Cohort Retention (%)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Cohort Period (Months Since Signup)", fontsize=11, labelpad=10)
    ax.set_ylabel("Signup Cohort Month", fontsize=11, labelpad=10)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_retention_curves(df_retention_pct: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders retention decay curves comparing signup cohorts over time.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    data = df_retention_pct.copy()

    for idx in data.index:
        series = data.loc[idx].dropna()
        ax.plot(series.index, series.values, marker="o", linewidth=2, label=str(idx))

    ax.set_title("Retention Decay Curves by Cohort", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month Since Signup", fontsize=11)
    ax.set_ylabel("Retention Rate (%)", fontsize=11)
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(title="Cohort Month", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
