"""
FinPilot AI — Decision Quality Scoring Engine
Implements strict pedagogical rule: PROFIT ≠ FINANCIAL INTELLIGENCE.

Evaluates every simulated trading decision across 6 multi-factor pillars:
1. Goal Alignment (25%): Does this decision match the target timeline and investment horizon?
2. Risk-Profile Alignment (20%): Does the asset volatility match the user's risk capacity?
3. Diversification Impact (20%): Does this trade avoid excessive concentration in one stock/sector?
4. Evidence / Data Grounding (15%): Was the decision supported by fundamentals or historical context?
5. Position Sizing Discipline (10%): Is capital allocation prudent (e.g. 5–15% vs 80% recklessness)?
6. Reflection & Rationale (10%): Did the user articulate a coherent reason vs impulsive FOMO?

Formula:
D = 0.25 * Goal + 0.20 * Risk + 0.20 * Div + 0.15 * Evidence + 0.10 * Sizing + 0.10 * Reflection
Total Score: 0 to 100
"""

from typing import Dict, Any, Optional

class DecisionQualityService:
    @staticmethod
    def evaluate_decision(
        action: str, # BUY, SELL, HOLD, WAIT
        quantity: float,
        price: float,
        portfolio_cash: float,
        portfolio_equity_val: float,
        risk_profile: str = "moderate",
        target_horizon_years: int = 10,
        reasoning: Optional[str] = None,
        market_condition: str = "VOLATILE",
        stock_sector: str = "IT"
    ) -> Dict[str, Any]:
        """
        Evaluates a decision objectively and server-authoritatively.
        Returns score (0-100), sub-scores, detailed breakdown, and pedagogical commentary.
        """
        total_portfolio = portfolio_cash + portfolio_equity_val
        trade_value = quantity * price

        # 1. Goal Alignment (0 to 100)
        # Long horizons favor staying invested or accumulating quality; short horizons penalize aggressive buying
        if action in ("BUY", "HOLD"):
            if target_horizon_years >= 5:
                goal_score = 90.0
            else:
                goal_score = 60.0 # short horizon risk
        elif action in ("WAIT", "HOLD"):
            goal_score = 85.0
        else: # SELL
            goal_score = 80.0

        # 2. Risk-Profile Alignment (0 to 100)
        risk_profile_lower = (risk_profile or "moderate").lower()
        if risk_profile_lower == "conservative":
            if action == "BUY" and (trade_value / max(total_portfolio, 1.0)) > 0.20:
                risk_score = 40.0 # Too aggressive for conservative profile
            else:
                risk_score = 85.0
        elif risk_profile_lower == "aggressive":
            risk_score = 90.0 # High risk appetite tolerated
        else: # moderate
            if action == "BUY" and (trade_value / max(total_portfolio, 1.0)) > 0.35:
                risk_score = 55.0
            else:
                risk_score = 88.0

        # 3. Diversification Impact (0 to 100)
        position_ratio = (trade_value) / max(total_portfolio, 1.0) if total_portfolio > 0 else 0
        if action == "BUY":
            if position_ratio > 0.40:
                div_score = 25.0 # Critical concentration penalty!
            elif position_ratio > 0.20:
                div_score = 60.0
            else:
                div_score = 95.0 # Healthy prudent sizing
        elif action == "SELL":
            div_score = 90.0 # Trimming / taking profits improves liquidity
        else:
            div_score = 85.0 # Holding maintains existing allocation

        # 4. Evidence & Historical Context (0 to 100)
        # Checks if user operates calmly during crashes vs panic selling
        if market_condition == "PANIC_DOWNTURN":
            if action == "SELL":
                evidence_score = 35.0 # Panic selling at bottom is classical behavioral error
            elif action == "BUY":
                evidence_score = 95.0 # Counter-cyclical value accumulation
            else:
                evidence_score = 85.0 # Calm patience
        elif market_condition == "EUPHORIC_PEAK":
            if action == "BUY" and position_ratio > 0.20:
                evidence_score = 40.0 # Buying aggressively at peak FOMO
            else:
                evidence_score = 85.0
        else:
            evidence_score = 80.0

        # 5. Position Sizing Discipline (0 to 100)
        if action == "BUY":
            if position_ratio > 0.50:
                sizing_score = 20.0 # Reckless all-in
            elif position_ratio > 0.25:
                sizing_score = 55.0
            elif position_ratio >= 0.03:
                sizing_score = 95.0 # Ideal 5-15% sizing
            else:
                sizing_score = 80.0
        elif action in ("HOLD", "WAIT"):
            sizing_score = 90.0
        else:
            sizing_score = 85.0

        # 6. Reflection & Rationale (0 to 100)
        r_text = (reasoning or "").strip()
        if len(r_text) > 40:
            reflection_score = 95.0
        elif len(r_text) > 15:
            reflection_score = 80.0
        elif len(r_text) > 0:
            reflection_score = 60.0
        else:
            reflection_score = 30.0 # Unreasoned trade

        # Composite Decision Score
        total_score = (
            0.25 * goal_score +
            0.20 * risk_score +
            0.20 * div_score +
            0.15 * evidence_score +
            0.10 * sizing_score +
            0.10 * reflection_score
        )
        total_score = round(max(0.0, min(100.0, total_score)), 1)

        # Core Philosophical Lesson
        pedagogical_lesson = (
            "FinPilot Rule: In professional investing, a high-quality decision with disciplined "
            "sizing and diversification is a WIN even if short-term prices drop. Conversely, "
            "gambling 80% on a single stock is a FAILING decision even if lucky market timing "
            "produced temporary profits."
        )

        feedback_notes = []
        if sizing_score < 60:
            feedback_notes.append("⚠️ Excessive capital committed in a single transaction. Keep individual allocations under 15%.")
        if div_score < 60:
            feedback_notes.append("⚠️ High single-stock concentration risk reduces portfolio resilience.")
        if reflection_score < 60:
            feedback_notes.append("💡 Always document your investment thesis before pulling the trigger to combat emotional bias.")
        if total_score >= 80:
            feedback_notes.append("✅ Excellent rational discipline aligned with core wealth-building principles.")

        return {
            "decision_score": total_score,
            "pillars": {
                "goal_alignment": round(goal_score, 1),
                "risk_alignment": round(risk_score, 1),
                "diversification": round(div_score, 1),
                "evidence_context": round(evidence_score, 1),
                "position_sizing": round(sizing_score, 1),
                "reflection": round(reflection_score, 1)
            },
            "feedback": " ".join(feedback_notes) if feedback_notes else "Disciplined execution.",
            "pedagogical_rule": pedagogical_lesson
        }
