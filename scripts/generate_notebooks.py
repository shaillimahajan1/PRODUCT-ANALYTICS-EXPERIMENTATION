"""
Generates 5 production-grade Jupyter notebooks in notebooks/ directory.
"""

from pathlib import Path
import nbformat as nbf


def make_notebook_01():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 01. FlowPulse Data Exploration & Schema Validation\n"
            "This notebook inspects the raw event stream, validates data quality invariants, "
            "and explores user demographics, device distributions, and session characteristics."
        ),
        nbf.v4.new_code_cell(
            "import duckdb\n"
            "import pandas as pd\n"
            "from src.utils.config import load_config\n\n"
            "config = load_config()\n"
            "con = duckdb.connect(config['paths']['database'])\n"
            "con.execute('SHOW TABLES').df()"
        ),
        nbf.v4.new_markdown_cell("## 1. User Demographics & Plan Distribution"),
        nbf.v4.new_code_cell(
            "users_df = con.execute('SELECT country, device_type, acquisition_channel, COUNT(*) as user_count FROM dim_users GROUP BY country, device_type, acquisition_channel ORDER BY user_count DESC LIMIT 10').df()\n"
            "users_df"
        ),
        nbf.v4.new_markdown_cell("## 2. Event Vocabulary & Volume"),
        nbf.v4.new_code_cell(
            "con.execute('SELECT event_name, COUNT(*) as event_count, COUNT(DISTINCT user_id) as unique_users FROM fct_events GROUP BY event_name ORDER BY event_count DESC').df()"
        ),
        nbf.v4.new_markdown_cell("## 3. Data Quality & Referential Integrity Check"),
        nbf.v4.new_code_cell(
            "with open('reports/data_quality_report.md', 'r') as f:\n"
            "    print(f.read())"
        ),
    ]
    return nb


def make_notebook_02():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 02. Product Funnel & Milestone Conversion Analysis\n"
            "Evaluates multi-step product conversion from registration to paid purchase, "
            "identifying major drop-off bottlenecks and segment variances."
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "from src.utils.io import load_dataframe\n\n"
            "funnel_df = load_dataframe('data/marts/mart_funnel.parquet')\n"
            "funnel_df"
        ),
        nbf.v4.new_markdown_cell("## 1. Funnel Conversion & Drop-off Rates"),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(9, 4.5))\n"
            "ax.barh(funnel_df['stage_name'], funnel_df['users_reached'], color='#2563EB')\n"
            "ax.set_title('Product Funnel Progression')\n"
            "ax.set_xlabel('Unique Users')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("## 2. Segment-level Funnel by Device"),
        nbf.v4.new_code_cell(
            "device_funnel = load_dataframe('data/marts/mart_funnel_by_device.parquet')\n"
            "device_funnel.pivot(index='stage_name', columns='device_type', values='stage_conversion_rate')"
        ),
    ]
    return nb


def make_notebook_03():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 03. Cohort Retention Matrix & Longitudinal Decay\n"
            "Analyzes monthly signup cohorts, tracking retention over 6-month horizons, "
            "and evaluates observational correlation between feature usage and 7-day retention."
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "import seaborn as sns\n"
            "import matplotlib.pyplot as plt\n"
            "from src.utils.io import load_dataframe\n\n"
            "cohort_mart = load_dataframe('data/marts/mart_cohort_retention.parquet')\n"
            "matrix = cohort_mart.pivot(index='cohort_month', columns='period_month', values='retention_rate') * 100.0\n"
            "matrix"
        ),
        nbf.v4.new_markdown_cell("## 1. Monthly Retention Heatmap"),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(9, 5))\n"
            "sns.heatmap(matrix, annot=True, fmt='.1f', cmap='Blues', ax=ax)\n"
            "ax.set_title('Signup Cohort Monthly Retention (%)')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("## 2. Observational Feature Correlation (Note: Correlation != Causality)"),
        nbf.v4.new_code_cell(
            "feat_corr = load_dataframe('data/marts/mart_feature_retention_correlation.parquet')\n"
            "feat_corr[['feature_name', 'retention_rate_with_feature', 'retention_rate_without_feature', 'retention_rate_difference']]"
        ),
    ]
    return nb


def make_notebook_04():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 04. A/B Testing Statistical Inference & SRM Checks\n"
            "Performs formal hypothesis testing, Sample Ratio Mismatch validation, "
            "unpooled Wilson confidence intervals, and multiple-testing corrections."
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "from src.utils.io import load_dataframe\n\n"
            "exp_results = load_dataframe('data/marts/mart_experiment_results.parquet')\n"
            "exp_results[['experiment_id', 'experiment_name', 'primary_metric', 'control_value', 'treatment_value', 'absolute_lift', 'ci_lower', 'ci_upper', 'p_value', 'decision']]"
        ),
        nbf.v4.new_markdown_cell("## 1. Subgroup / Heterogeneous Treatment Effects"),
        nbf.v4.new_code_cell(
            "seg_results = load_dataframe('data/marts/mart_experiment_segments.parquet')\n"
            "seg_results"
        ),
    ]
    return nb


def make_notebook_05():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# 05. Product Manager Experimentation Decision Memo\n"
            "**Case Study**: Streamlined Onboarding Checklist (EXP-2026-01)\n\n"
            "### Structure:\n"
            "1. Business Problem & Opportunity\n"
            "2. Pre-experiment Power Sizing & Hypothesis\n"
            "3. Sample Ratio Mismatch (SRM) & Data Quality\n"
            "4. Statistical Hypothesis Testing & Confidence Intervals\n"
            "5. Subgroup Consistency & Interaction Checks\n"
            "6. Guardrail Metrics Verification\n"
            "7. Projected Annual Business Impact\n"
            "8. Final PM Decision: SHIP"
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "from src.utils.io import load_dataframe\n\n"
            "exp_results = load_dataframe('data/marts/mart_experiment_results.parquet')\n"
            "exp1 = exp_results[exp_results['experiment_id'] == 'EXP-2026-01'].iloc[0]\n\n"
            "print(f\"Experiment:   {exp1['experiment_name']}\")\n"
            "print(f\"Primary Lift: {exp1['absolute_lift']:+.2%} [95% CI: {exp1['ci_lower']:+.2%}, {exp1['ci_upper']:+.2%}]\")\n"
            "print(f\"p-value:      {exp1['p_value']:.4f}\")\n"
            "print(f\"Decision:     {exp1['decision']}\")\n"
            "print(f\"Rationale:    {exp1['decision_reason']}\")"
        ),
        nbf.v4.new_markdown_cell("### Business Impact Estimation"),
        nbf.v4.new_code_cell(
            "impact = load_dataframe('data/marts/mart_business_impact.parquet')\n"
            "impact"
        ),
    ]
    return nb


def main():
    root = Path("notebooks")
    root.mkdir(parents=True, exist_ok=True)

    notebooks = {
        "01_data_exploration.ipynb": make_notebook_01(),
        "02_product_analytics.ipynb": make_notebook_02(),
        "03_cohort_retention.ipynb": make_notebook_03(),
        "04_experiment_analysis.ipynb": make_notebook_04(),
        "05_experiment_storytelling.ipynb": make_notebook_05(),
    }

    for filename, nb in notebooks.items():
        filepath = root / filename
        with open(filepath, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
        print(f"Generated notebook: {filepath}")


if __name__ == "__main__":
    main()
