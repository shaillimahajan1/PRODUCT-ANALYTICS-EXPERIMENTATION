"""
Funnel charts and conversion flow visualizations.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_funnel(df_funnel: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders a high-resolution horizontal bar funnel chart.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Filter to overall aggregate funnel if grouped
    if "stage_order" in df_funnel.columns:
        df = df_funnel.sort_values("stage_order", ascending=False).copy()
    else:
        df = df_funnel.copy()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    colors = ["#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
    bars = ax.barh(df["stage_name"], df["users_reached"], color=colors[:len(df)], height=0.55)

    # Annotate counts and percentages
    top_users = df["users_reached"].max()
    for bar in bars:
        w = bar.get_width()
        pct = (w / top_users * 100.0) if top_users > 0 else 0
        ax.text(
            w + (top_users * 0.015),
            bar.get_y() + bar.get_height() / 2,
            f"{int(w):,}  ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color="#1F2937",
        )

    ax.set_title("FlowPulse Product Conversion Funnel", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Unique Users Reaching Stage", fontsize=11, labelpad=10)
    ax.set_xlim(0, top_users * 1.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
