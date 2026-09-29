"""
Product engagement and segmentation charts.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_engagement_trends(df_engagement: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders DAU/WAU/MAU trends over time with DAU/MAU ratio on secondary axis.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    df = df_engagement.copy()
    dates = pd.to_datetime(df["date"])

    ax1.plot(dates, df["dau"], label="DAU", color="#3B82F6", linewidth=1.5)
    ax1.plot(dates, df["wau"], label="WAU", color="#10B981", linewidth=2.0)
    ax1.plot(dates, df["mau"], label="MAU", color="#1E3A8A", linewidth=2.5)

    ax1.set_ylabel("Active Users", fontsize=11, color="#1E3A8A")
    ax1.set_xlabel("Date", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left")

    # Secondary axis for DAU / MAU Stickiness
    ax2 = ax1.twinx()
    ax2.plot(dates, df["dau_mau_ratio"] * 100.0, label="DAU/MAU Stickiness (%)", color="#F59E0B", linestyle=":", linewidth=2)
    ax2.set_ylabel("DAU/MAU Stickiness (%)", fontsize=11, color="#B45309")
    ax2.set_ylim(0, 50)
    ax2.legend(loc="upper right")

    plt.title("FlowPulse Product Engagement & Stickiness Trajectory", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_segment_distribution(df_segments: pd.DataFrame, output_path: str | Path) -> None:
    """
    Renders bar chart and breakdown of behavioral user segments.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    counts = df_segments["behavioral_segment"].value_counts()
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    colors = ["#3B82F6", "#10B981", "#6366F1", "#F59E0B", "#EF4444"]
    
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], width=0.55)

    total = counts.sum()
    for bar in bars:
        h = bar.get_height()
        pct = (h / total * 100.0) if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + (total * 0.01),
            f"{int(h):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("Behavioral User Segmentation Distribution", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("User Count", fontsize=11)
    ax.set_ylim(0, max(counts.values) * 1.20)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
