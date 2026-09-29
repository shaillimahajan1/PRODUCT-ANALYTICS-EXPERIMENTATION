"""
Business Impact Modeling Module.
Estimates potential incremental conversions and revenue impact under explicit stated assumptions.
Incorporates point estimates and 95% confidence intervals.
"""

from typing import Any, Dict


def estimate_business_impact(
    annual_user_volume: int,
    absolute_lift: float,
    ci_lower: float,
    ci_upper: float,
    avg_revenue_per_conversion: float = 120.0,
    assumption_notes: str = "Assumes rollout to 100% of eligible user base with constant lift over 12 months.",
) -> Dict[str, Any]:
    """
    Model projected potential business impact.
    
    IMPORTANT:
    This is an estimated potential impact model under explicitly stated assumptions,
    NOT actual realized historical revenue.
    """
    # Incremental conversions
    inc_conv_point = int(round(annual_user_volume * max(0.0, absolute_lift)))
    inc_conv_low = int(round(annual_user_volume * max(0.0, ci_lower)))
    inc_conv_high = int(round(annual_user_volume * max(0.0, ci_upper)))

    # Incremental revenue
    inc_rev_point = round(inc_conv_point * avg_revenue_per_conversion, 2)
    inc_rev_low = round(inc_conv_low * avg_revenue_per_conversion, 2)
    inc_rev_high = round(inc_conv_high * avg_revenue_per_conversion, 2)

    return {
        "annual_exposed_user_volume": annual_user_volume,
        "avg_revenue_per_conversion_usd": avg_revenue_per_conversion,
        "incremental_conversions_expected": inc_conv_point,
        "incremental_conversions_ci_lower": inc_conv_low,
        "incremental_conversions_ci_upper": inc_conv_high,
        "incremental_revenue_usd_expected": inc_rev_point,
        "incremental_revenue_usd_ci_lower": inc_rev_low,
        "incremental_revenue_usd_ci_upper": inc_rev_high,
        "assumption_notes": assumption_notes,
    }
