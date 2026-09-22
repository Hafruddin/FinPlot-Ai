"""
FinPilot AI — Portfolio Guardian Allocation & Risk Drift Analysis Engine
Replaces artificial recovery multipliers with authoritative asset allocation analysis,
drift calculation, concentration warnings, and non-advisory educational rebalance reviews.
"""

from typing import Dict, Any, List, Optional


DEFAULT_TARGET_ALLOCATIONS = {
    "conservative": {"Equity": 30.0, "Debt": 55.0, "Gold": 10.0, "Cash": 5.0},
    "moderate": {"Equity": 70.0, "Debt": 25.0, "Gold": 0.0, "Cash": 5.0},
    "aggressive": {"Equity": 80.0, "Debt": 15.0, "Gold": 0.0, "Cash": 5.0}
}


class PortfolioGuardianService:
    """Evaluates portfolio asset allocation deviations and concentration risk."""

    def analyze_portfolio(
        self,
        holdings: List[Dict[str, Any]],
        risk_profile: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Analyzes holdings against benchmark target allocation for user's risk profile.
        Computes exact percentage deviations and provides educational rebalancing guidance.
        """
        risk_key = risk_profile.lower() if risk_profile else "moderate"
        target_allocation = DEFAULT_TARGET_ALLOCATIONS.get(risk_key, DEFAULT_TARGET_ALLOCATIONS["moderate"])

        # Compute total portfolio value
        total_value = sum(max(0.0, float(h.get("current_value", 0.0))) for h in holdings)
        if total_value <= 0.0:
            total_value = sum(max(0.0, float(h.get("weight", 0.0))) for h in holdings)

        # Categorize current holdings into major 4 buckets
        current_breakdown = {"Equity": 0.0, "Debt": 0.0, "Gold": 0.0, "Cash": 0.0}
        for h in holdings:
            asset_class = str(h.get("asset_class", "")).strip().lower()
            val = float(h.get("current_value", 0.0))
            if any(k in asset_class for k in ["equit", "stock", "large", "mid", "flexi", "nifty"]):
                current_breakdown["Equity"] += val
            elif any(k in asset_class for k in ["debt", "bond", "fixed", "liquid"]):
                current_breakdown["Debt"] += val
            elif any(k in asset_class for k in ["gold", "silver", "commodity"]):
                current_breakdown["Gold"] += val
            else:
                current_breakdown["Cash"] += val

        # Compute actual current percentages
        current_pcts = {}
        deviations = {}
        for k in ["Equity", "Debt", "Gold", "Cash"]:
            pct = (current_breakdown[k] / total_value * 100.0) if total_value > 0 else target_allocation[k]
            current_pcts[k] = round(pct, 1)
            deviations[k] = round(pct - target_allocation[k], 1)

        # Assess maximum absolute deviation
        max_deviation = max(abs(d) for d in deviations.values())

        if max_deviation <= 5.0:
            status = "BALANCED"
            headline = "Portfolio in Balanced Alignment"
            recommendation = "Current asset weights are within the healthy ±5% tolerance band. No rebalancing required."
        elif max_deviation <= 10.0:
            status = "MODERATE_DRIFT"
            headline = "Review Recommended (Moderate Drift)"
            drift_asset = max(deviations, key=lambda k: abs(deviations[k]))
            dev_val = deviations[drift_asset]
            direction = f"+{dev_val}% overweight" if dev_val > 0 else f"{dev_val}% underweight"
            recommendation = (
                f"Review recommended: {drift_asset} has drifted by {direction} against your {risk_profile.title()} target. "
                f"Consider directing incremental fresh monthly investments toward underweight categories to restore equilibrium "
                f"without incurring capital gains taxes."
            )
        else:
            status = "SIGNIFICANT_DRIFT"
            headline = "Significant Drift Detected"
            drift_asset = max(deviations, key=lambda k: abs(deviations[k]))
            dev_val = deviations[drift_asset]
            recommendation = (
                f"Significant allocation shift: {drift_asset} is currently {dev_val:+.1f}% deviated from target. "
                f"During strong bull runs, equity expansion can expose conservative portfolios to higher drawdown risk. "
                f"Consult with an advisor or systematically rebalance to safeguard gains."
            )

        # Concentration Warnings
        concentration_warnings = []
        if current_pcts["Equity"] > 70.0 and risk_key in ["conservative", "moderate"]:
            concentration_warnings.append(
                f"High Equity Concentration ({current_pcts['Equity']}%): Exceeds recommended ceiling for {risk_profile} risk profile."
            )
        if current_pcts["Cash"] > 25.0:
            concentration_warnings.append(
                f"High Cash Drag ({current_pcts['Cash']}%): Excessive idle cash is eroding purchasing power against inflation."
            )

        return {
            "total_portfolio_value": round(total_value, 2),
            "risk_profile": risk_profile,
            "status": status,
            "headline": headline,
            "max_deviation_pct": max_deviation,
            "target_allocation": target_allocation,
            "current_allocation": current_pcts,
            "deviations": deviations,
            "recommendation": recommendation,
            "concentration_warnings": concentration_warnings,
            "disclaimer": (
                "Educational portfolio diagnostic only. FinPilot AI does not execute broker trades. "
                "Asset allocation models are illustrative and do not guarantee future performance."
            )
        }


portfolio_guardian = PortfolioGuardianService()

def analyze_portfolio_drift(
    portfolio_value: float = 300000.0,
    current_equity: float = 237000.0,
    current_debt: float = 45000.0,
    current_cash: float = 18000.0,
    risk_tolerance: str = "moderate"
) -> Dict[str, Any]:
    holdings = [
        {"asset_class": "Equities & Mutual Funds", "current_value": current_equity},
        {"asset_class": "Fixed Income & Debt", "current_value": current_debt},
        {"asset_class": "Liquid Cash Reserve", "current_value": current_cash},
    ]
    report = portfolio_guardian.analyze_portfolio(holdings, risk_profile=risk_tolerance)
    eq_dev = report["deviations"].get("Equity", 0.0)
    report["drift_status"] = "MODERATE_DRIFT" if abs(eq_dev) >= 5.0 else "TARGET_ALIGNED"
    report["equity_drift_pct"] = abs(eq_dev)
    report["review_recommended"] = abs(eq_dev) >= 5.0
    report["rebalance_action_plan"] = [report["recommendation"], "Deploy upcoming fresh SIP inflows into underweighted asset classes"]
    report["health_score"] = max(50, 100 - int(report["max_deviation_pct"] * 2))
    return report
