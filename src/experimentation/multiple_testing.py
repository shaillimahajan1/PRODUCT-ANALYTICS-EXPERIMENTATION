"""
Multiple Testing and Family-Wise Error Rate / FDR Correction.
Implements:
- Bonferroni correction (controls Family-Wise Error Rate FWER)
- Benjamini-Hochberg procedure (controls False Discovery Rate FDR)
- Holm-Bonferroni step-down procedure
"""

from typing import Dict
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests


def correct_p_values(
    metrics_pvalues: Dict[str, float],
    method: str = "fdr_bh",
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Apply multiple-testing correction to raw p-values across multiple experiment metrics.
    
    Args:
        metrics_pvalues: Dict mapping metric_name -> raw p-value.
        method: 'bonferroni', 'fdr_bh' (Benjamini-Hochberg), or 'holm'.
        alpha: Target error rate (default: 0.05).
        
    Returns:
        DataFrame with raw p-value, adjusted p-value, and corrected significance status.
    """
    labels = list(metrics_pvalues.keys())
    p_vals = np.array([metrics_pvalues[k] for k in labels])

    reject, pvals_corrected, _, _ = multipletests(
        p_vals, alpha=alpha, method=method
    )

    results = []
    for label, raw_p, adj_p, is_sig in zip(labels, p_vals, pvals_corrected, reject):
        results.append({
            "metric": label,
            "raw_p_value": round(float(raw_p), 5),
            "adjusted_p_value": round(float(adj_p), 5),
            "method": method,
            "statistically_significant": bool(is_sig),
        })

    return pd.DataFrame(results)
