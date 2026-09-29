"""
FlowPulse Product Analytics & Experimentation Intelligence Platform.
Entry point for executing the end-to-end data pipeline, statistical analysis,
and data mart generation.
"""

import sys
from src.pipeline import run_pipeline


def main():
    """Main execution function."""
    try:
        results = run_pipeline()
        print("\n" + "=" * 70)
        print("FLOWPULSE PRODUCT ANALYTICS PIPELINE EXECUTED SUCCESSFULLY")
        print("=" * 70)
        print(f"Users Processed:       {results['users_count']:,}")
        print(f"Events Processed:      {results['events_count']:,}")
        print(f"Execution Duration:    {results['duration_seconds']:.1f} seconds")
        print(f"Experiments Evaluated: {len(results['experiment_results'])}")
        print("=" * 70)
        for exp in results["experiment_results"]:
            print(f"[{exp['experiment_id']}] {exp['experiment_name']}")
            print(f"  -> Decision: {exp['decision']}")
            print(f"  -> Lift:     {exp['absolute_lift']:+.2%} [95% CI: {exp['ci_lower']:+.2%}, {exp['ci_upper']:+.2%}]")
            print(f"  -> p-value:  {exp['p_value']:.4f}")
            print(f"  -> Status:   {exp['quality_flag']}\n")
        print("Generated marts ready for Power BI in: data/marts/")
        print("Visual reports generated in:           reports/figures/")
        print("Decision memo generated in:            reports/pm_experiment_decision_memo.md")
        print("=" * 70)
    except Exception as e:
        print(f"\nPipeline failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
