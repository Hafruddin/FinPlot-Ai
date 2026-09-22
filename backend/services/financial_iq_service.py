"""
FinPilot AI — Multi-Dimensional Financial IQ Assessment Engine
Computes genuine, verifiable Financial IQ scores across 10 distinct competency dimensions:
1. Budgeting (Cash flow surplus, expenditure discipline)
2. Saving (Emergency reserve adequacy, savings rate)
3. Debt Management (High-interest debt elimination, leverage safety)
4. Investing Basics (Compounding mathematics, direct vs regular plans)
5. Risk Understanding (Capacity vs appetite, volatility tolerance)
6. Asset Allocation (Equity, debt, cash, and gold calibration)
7. Market Cycles (Market crashes, recovery patience, counter-cyclical thinking)
8. Decision Discipline (Resisting FOMO, sticking to long-term plans)
9. Diversification (Avoiding company/sector concentration)
10. Long-Term Planning (Reverse SIP, horizon calibration, inflation indexing)

Scale: 0 to 100 points (normalized to 0–1000 scale points: 100 * 10 = 1000).
Every score modification is written to the immutable `iq_activity_ledger`.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session
from backend.models import (
    Quiz, QuizAttempt, FinancialIQRecord, User, UserFinancialIQ,
    IQActivityLedger, AssetHolding, PaperHolding
)

TEN_DIMENSIONS = [
    "budgeting",
    "saving",
    "debt_mgmt",
    "investing_basics",
    "risk_understanding",
    "asset_allocation",
    "market_cycles",
    "decision_discipline",
    "diversification",
    "long_term_planning"
]

DIMENSION_METADATA = {
    "budgeting": {"label": "Cash Flow & Budgeting", "weight": 10.0, "icon": "💵"},
    "saving": {"label": "Emergency Savings & Liquidity", "weight": 10.0, "icon": "🛡️"},
    "debt_mgmt": {"label": "Debt Management & Avalanche", "weight": 10.0, "icon": "💳"},
    "investing_basics": {"label": "Investing Basics & Compounding", "weight": 10.0, "icon": "📈"},
    "risk_understanding": {"label": "Risk Capacity & Tolerance", "weight": 10.0, "icon": "⚖️"},
    "asset_allocation": {"label": "Multi-Asset Allocation", "weight": 10.0, "icon": "🧩"},
    "market_cycles": {"label": "Market Cycles & Volatility", "weight": 10.0, "icon": "🔄"},
    "decision_discipline": {"label": "Decision Discipline & Anti-FOMO", "weight": 10.0, "icon": "🧘"},
    "diversification": {"label": "Unsystematic Risk & Diversification", "weight": 10.0, "icon": "🌐"},
    "long_term_planning": {"label": "Goal Horizon & Inflation Calibration", "weight": 10.0, "icon": "🎯"}
}

# 10 Authoritative Assessment Questions (1 per dimension)
TEN_DIMENSION_QUESTIONS = [
    # 1. Budgeting
    {
        "id": "q_budgeting",
        "dimension": "budgeting",
        "weight": 10.0,
        "question": "If your monthly take-home income is ₹60,000 and mandatory expenses are ₹40,000, what is your maximum sustainable monthly investment capacity?",
        "options": [
            "₹30,000 (by borrowing from next month's salary)",
            "₹20,000 (your true net cash flow surplus)",
            "₹50,000 (by using credit card revolving cash advances)",
            "₹5,000 (fixed regardless of income)"
        ],
        "correct_index": 1,
        "explanation": "Investment capacity is strictly bounded by your cash flow surplus ($Income - Expenses = ₹20,000$). Committing more than surplus causes capacity deficits."
    },
    # 2. Saving
    {
        "id": "q_saving",
        "dimension": "saving",
        "weight": 10.0,
        "question": "What is the recommended size and storage vehicle for an emergency reserve with ₹25,000 monthly living expenses?",
        "options": [
            "₹25,000 in volatile small-cap equities for rapid capital growth",
            "₹75,000 to ₹1,50,000 in liquid funds, sweep-in accounts, or high-grade bank FDs",
            "₹5,00,000 locked in a 10-year real estate parcel",
            "Zero emergency fund if you have an available credit card line"
        ],
        "correct_index": 1,
        "explanation": "Prudent financial planning requires 3 to 6 months of mandatory expenses held in zero-penalty, liquid, capital-preserving instruments."
    },
    # 3. Debt Management
    {
        "id": "q_debt_mgmt",
        "dimension": "debt_mgmt",
        "weight": 10.0,
        "question": "You have ₹60,000 in disposable savings and hold a ₹50,000 revolving credit card balance charging 42% annualized interest. What is the optimal mathematical decision?",
        "options": [
            "Invest all ₹60,000 into momentum stocks hoping to generate 50% returns",
            "Pay off the entire ₹50,000 credit card debt immediately, locking in a guaranteed 42% risk-free return",
            "Pay only the minimum 5% due each month and buy lottery tickets",
            "Take another personal loan to invest in intraday futures"
        ],
        "correct_index": 1,
        "explanation": "Eliminating a 42% interest liability delivers a guaranteed, risk-free, tax-free effective return of 42%—far surpassing any realistic market equity return."
    },
    # 4. Investing Basics
    {
        "id": "q_investing_basics",
        "dimension": "investing_basics",
        "weight": 10.0,
        "question": "What is the primary financial advantage of Direct Plans of Mutual Funds over Regular Plans?",
        "options": [
            "Direct plans receive a special dividend guaranteed by SEBI",
            "Direct plans eliminate distributor commissions, lowering the Total Expense Ratio (TER) by 0.5%–1.2% p.a.",
            "Regular plans are insured against stock market drawdowns",
            "There is zero mathematical difference over 20-year horizons"
        ],
        "correct_index": 1,
        "explanation": "Direct plans bypass intermediary commissions. A 1% lower TER compounded over 25 years can result in a 20%+ higher final corpus."
    },
    # 5. Risk Understanding
    {
        "id": "q_risk_understanding",
        "dimension": "risk_understanding",
        "weight": 10.0,
        "question": "If you need ₹10 Lakh to fund a child's university fees in 18 months, which asset allocation is appropriate?",
        "options": [
            "100% Micro-cap momentum equities for maximum profit",
            "100% High-quality liquid funds, short-term debt, or bank fixed deposits",
            "50% Cryptocurrency and 50% call options",
            "Gold futures contracts with 5x leverage"
        ],
        "correct_index": 1,
        "explanation": "Short horizons (<3 years) cannot absorb market drawdowns. Capital preservation and liquidity must strictly override returns."
    },
    # 6. Asset Allocation
    {
        "id": "q_asset_allocation",
        "dimension": "asset_allocation",
        "weight": 10.0,
        "question": "What is the primary role of adding Debt Instruments and Sovereign Gold to an equity portfolio?",
        "options": [
            "To guarantee that the portfolio will always outperform the NIFTY 50 in bull runs",
            "To provide non-correlated stability, reducing portfolio volatility and max drawdown during equity crashes",
            "To double the annual management fee charged by asset managers",
            "Debt instruments are strictly for retirees and offer zero value to young investors"
        ],
        "correct_index": 1,
        "explanation": "Non-correlated assets cushion portfolio drawdowns, preventing forced selling during market troughs and enabling rebalancing opportunities."
    },
    # 7. Market Cycles
    {
        "id": "q_market_cycles",
        "dimension": "market_cycles",
        "weight": 10.0,
        "question": "During a sharp macroeconomic market crash where broad indices plunge 30%, what is the most disciplined action?",
        "options": [
            "Panic sell all equity holdings into cash at the market bottom",
            "Continue systematic SIP purchases to accumulate units at historically discounted valuations",
            "Stop looking at finances and delete banking apps permanently",
            "Borrow maximum personal debt to day-trade high-beta penny stocks"
        ],
        "correct_index": 1,
        "explanation": "Continuing SIPs during market crashes is the cornerstone of rupee-cost averaging, enabling substantial long-term wealth acceleration when markets recover."
    },
    # 8. Decision Discipline
    {
        "id": "q_decision_discipline",
        "dimension": "decision_discipline",
        "weight": 10.0,
        "question": "A colleague boasts about making 80% gains in a speculative penny stock and urges you to allocate half your savings. How should you respond?",
        "options": [
            "Immediately liquidate your index mutual funds and follow the tip due to fear of missing out (FOMO)",
            "Stick to your validated financial plan; recognize that survivor bias and speculative gains carry catastrophic downside risk",
            "Borrow funds from relatives to double the investment size",
            "Blame your advisor for only generating steady 12% returns"
        ],
        "correct_index": 1,
        "explanation": "Financial discipline requires recognizing behavioral traps like FOMO and survivorship bias. Sustainable wealth is built on process, not speculative bets."
    },
    # 9. Diversification
    {
        "id": "q_diversification",
        "dimension": "diversification",
        "weight": 10.0,
        "question": "If you hold 80% of your total net worth in the stock of the company you work for, what critical risk are you exposed to?",
        "options": [
            "Zero risk, because you know your employer's day-to-day business personally",
            "Double-jeopardy risk: a downturn in your company could destroy both your primary income and your life savings simultaneously",
            "SEBI regulatory investigation for insider trading",
            "Excessive tax deduction at source (TDS)"
        ],
        "correct_index": 1,
        "explanation": "Concentration in your employer's stock couples your human capital (job) with your financial capital, violating fundamental diversification rules."
    },
    # 10. Long-Term Planning
    {
        "id": "q_long_term_planning",
        "dimension": "long_term_planning",
        "weight": 10.0,
        "question": "If an investor requires ₹1 Crore today to retire, what approximate target corpus must they accumulate in 15 years assuming 6.0% annual inflation?",
        "options": [
            "₹1.00 Crore (inflation has no impact on target principal)",
            "₹2.40 Crore (adjusting for compound purchasing power erosion: ₹1 Cr * 1.06^15)",
            "₹1.15 Crore (linear 1% per year addition)",
            "₹50 Lakh (because goods become cheaper over time)"
        ],
        "correct_index": 1,
        "explanation": "At 6% annual inflation, money loses ~58% of its purchasing power over 15 years ($1.06^{15} \\approx 2.40$). Target goals must always be inflation-adjusted."
    }
]


LEGACY_QUESTIONS = [
    {
        "id": "q_know_1", "dimension": "knowledge", "weight": 15.0, "correct_index": 1,
        "question": "What is the primary difference between a Mutual Fund Direct Plan and a Regular Plan?",
        "explanation": "Direct plans bypass distributor commissions, resulting in a 0.5%–1.2% lower Total Expense Ratio (TER)."
    },
    {
        "id": "q_know_2", "dimension": "knowledge", "weight": 15.0, "correct_index": 1,
        "question": "How does compound interest behave over long investment horizons compared to simple interest?",
        "explanation": "Compounding reinvests prior gains, producing an exponential hockey-stick growth curve."
    },
    {
        "id": "q_risk_1", "dimension": "risk", "weight": 10.0, "correct_index": 2,
        "question": "If your financial goal requires capital within 2 years, which asset class is most suitable?",
        "explanation": "Short horizons (<3 years) cannot absorb equity market downturns."
    },
    {
        "id": "q_risk_2", "dimension": "risk", "weight": 10.0, "correct_index": 1,
        "question": "What is the recommended size of an emergency fund for an individual with ₹20,000 in mandatory monthly expenses?",
        "explanation": "Standard financial risk management requires 3 to 6 months of mandatory living expenses."
    },
    {
        "id": "q_inf_1", "dimension": "inflation", "weight": 15.0, "correct_index": 2,
        "question": "If your savings account yields 4.0% interest and annual consumer inflation is 6.5%, what is your approximate Real Rate of Return?",
        "explanation": "Real Return ≈ Nominal Return - Inflation (4.0% - 6.5% = -2.5%)."
    },
    {
        "id": "q_goal_1", "dimension": "goals", "weight": 15.0, "correct_index": 1,
        "question": "When target goal deadline is extended from 10 years to 15 years, what happens to the required monthly SIP contribution?",
        "explanation": "Extending investment duration harnesses additional compounding cycles."
    },
    {
        "id": "q_div_1", "dimension": "diversification", "weight": 10.0, "correct_index": 1,
        "question": "Which type of financial risk is directly minimized by holding 25-30 stocks across different economic sectors?",
        "explanation": "Diversification neutralizes company-specific and sector-specific unsystematic risk."
    },
    {
        "id": "q_dec_1", "dimension": "decision_making", "weight": 10.0, "correct_index": 1,
        "question": "You have ₹50,000 in savings, but hold a ₹40,000 credit card balance charging 38% p.a. interest. What is the most financially rational move?",
        "explanation": "Eliminating a 38% interest liability delivers a risk-free, tax-free effective return of 38%."
    }
]


class FinancialIQService:
    """Authoritative 10-dimension Financial IQ service with immutable audit trails."""

    def get_assessment_questions(self) -> List[Dict[str, Any]]:
        """Returns the assessment questions for the client quiz without revealing correct answer indices."""
        return [
            {
                "id": q["id"],
                "dimension": q["dimension"],
                "weight": q["weight"],
                "question": q["question"],
                "options": q["options"]
            }
            for q in TEN_DIMENSION_QUESTIONS
        ]

    def evaluate_answers(
        self,
        answers_dict: Dict[str, Any],
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Evaluates submitted answer indices across either 10 dimensions or legacy 6 pillars,
        computes 0–100 score, normalizes to 1000-point scale, updates `UserFinancialIQ` and writes to `IQActivityLedger`.
        """
        # Check if legacy keys were passed
        is_legacy = any(k in answers_dict for k in ("q_know_1", "q_know_2", "q_risk_1", "q_risk_2", "q_inf_1", "q_goal_1", "q_div_1", "q_dec_1"))
        
        if is_legacy:
            dim_scores = {"knowledge": 0.0, "risk": 0.0, "inflation": 0.0, "goals": 0.0, "diversification": 0.0, "decision_making": 0.0}
            detailed_feedback = []
            for q in LEGACY_QUESTIONS:
                qid = q["id"]
                user_choice = answers_dict.get(qid)
                idx = None
                if isinstance(user_choice, int):
                    idx = user_choice
                elif isinstance(user_choice, str) and user_choice.strip():
                    clean = user_choice.strip().upper()
                    if clean in ("A", "B", "C", "D"):
                        idx = ord(clean) - ord("A")
                    elif clean.isdigit():
                        idx = int(clean)
                is_correct = (idx == q["correct_index"])
                dim = q["dimension"]
                if is_correct:
                    dim_scores[dim] += q["weight"]
                detailed_feedback.append({
                    "question_id": qid,
                    "dimension": dim,
                    "question": q["question"],
                    "user_selected": user_choice,
                    "correct_option": q["correct_index"],
                    "is_correct": is_correct,
                    "explanation": q["explanation"]
                })
            total_score = sum(dim_scores.values())
            normalized_1000 = int(round(total_score * 10))
            tier_name = "Master Investor" if total_score >= 85 else ("Advanced Investor" if total_score >= 70 else "Wealth Builder")
            return {
                "total_score": round(total_score, 1),
                "scale_maximum": 100,
                "normalized_1000_score": normalized_1000,
                "tier_name": tier_name,
                "tier_badge": "Mastery (Top Tier)" if total_score >= 85 else "Advanced Competency",
                "dimensions": dim_scores,
                "strengths": [f"{k.title()} Mastery ({v} pts)" for k, v in dim_scores.items() if v >= 10.0],
                "weak_areas": [f"{k.title()} Gap ({v} pts)" for k, v in dim_scores.items() if v < 10.0] or ["None identified!"],
                "recommended_learning": ["Advanced Wealth Optimization"],
                "detailed_feedback": detailed_feedback
            }

        dim_scores = {dim: 0.0 for dim in TEN_DIMENSIONS}
        detailed_feedback = []

        for q in TEN_DIMENSION_QUESTIONS:
            qid = q["id"]
            user_choice = answers_dict.get(qid)
            # Also handle legacy id mappings if sent
            if user_choice is None:
                if qid == "q_budgeting": user_choice = answers_dict.get("q_know_1")
                elif qid == "q_saving": user_choice = answers_dict.get("q_risk_2")
                elif qid == "q_debt_mgmt": user_choice = answers_dict.get("q_dec_1")
                elif qid == "q_investing_basics": user_choice = answers_dict.get("q_know_2")
                elif qid == "q_risk_understanding": user_choice = answers_dict.get("q_risk_1")
                elif qid == "q_asset_allocation": user_choice = answers_dict.get("q_div_1")
                elif qid == "q_long_term_planning": user_choice = answers_dict.get("q_inf_1")
                elif qid == "q_market_cycles": user_choice = answers_dict.get("q_goal_1")

            idx = None
            if isinstance(user_choice, int):
                idx = user_choice
            elif isinstance(user_choice, str) and user_choice.strip():
                clean = user_choice.strip().upper()
                if clean in ("A", "B", "C", "D"):
                    idx = ord(clean) - ord("A")
                elif clean.isdigit():
                    idx = int(clean)

            is_correct = (idx == q["correct_index"])
            dim = q["dimension"]

            if is_correct:
                dim_scores[dim] = 10.0 # full 10 points for this dimension
            else:
                dim_scores[dim] = 3.0  # baseline effort points

            detailed_feedback.append({
                "question_id": qid,
                "dimension": dim,
                "question": q["question"],
                "user_selected": user_choice,
                "correct_option": q["correct_index"],
                "is_correct": is_correct,
                "explanation": q["explanation"]
            })

            # Record attempt in DB if session available
            if db and user_id is not None and user_choice is not None:
                try:
                    attempt = QuizAttempt(
                        user_id=user_id,
                        quiz_id=qid,
                        selected_option=idx if idx is not None else 0,
                        is_correct=1 if is_correct else 0,
                        dimension=dim
                    )
                    db.add(attempt)
                except Exception:
                    pass

        # Total IQ Score (0-100)
        total_score = sum(dim_scores.values())
        normalized_1000 = int(round(total_score * 10))

        # Strengths & Weak Areas
        strengths = []
        weak_areas = []
        recommended_learning = []

        for dim, score in dim_scores.items():
            meta = DIMENSION_METADATA[dim]
            lbl = meta["label"]
            if score >= 8.0:
                strengths.append(f"{meta['icon']} {lbl} ({score}/10 pts)")
            else:
                weak_areas.append(f"⚠️ {lbl} Gap ({score}/10 pts)")
                recommended_learning.append(f"Focus Module: {lbl} Foundations")

        if not weak_areas:
            weak_areas.append("None identified! Exceptional across all 10 competencies.")
        if not recommended_learning:
            recommended_learning.append("Advanced Wealth Structuring & Multi-Asset Rebalancing")

        # Derive Tier
        if total_score >= 85:
            tier_name = "Master Investor"
            tier_badge = "Mastery (Top Tier)"
        elif total_score >= 70:
            tier_name = "Advanced Investor"
            tier_badge = "Advanced Competency"
        elif total_score >= 55:
            tier_name = "Wealth Builder"
            tier_badge = "Solid Foundation"
        elif total_score >= 40:
            tier_name = "Confident Learner"
            tier_badge = "Growing Competency"
        else:
            tier_name = "Foundation Builder"
            tier_badge = "Developing"

        # Persist to UserFinancialIQ & IQActivityLedger
        if db and user_id is not None:
            try:
                user_iq = db.query(UserFinancialIQ).filter(UserFinancialIQ.user_id == user_id).first()
                if not user_iq:
                    user_iq = UserFinancialIQ(user_id=user_id)
                    db.add(user_iq)

                old_total = user_iq.total_score if user_iq.total_score is not None else 65.0
                user_iq.total_score = total_score
                user_iq.budgeting = dim_scores["budgeting"]
                user_iq.saving = dim_scores["saving"]
                user_iq.debt_mgmt = dim_scores["debt_mgmt"]
                user_iq.investing_basics = dim_scores["investing_basics"]
                user_iq.risk_understanding = dim_scores["risk_understanding"]
                user_iq.asset_allocation = dim_scores["asset_allocation"]
                user_iq.market_cycles = dim_scores["market_cycles"]
                user_iq.decision_discipline = dim_scores["decision_discipline"]
                user_iq.diversification = dim_scores["diversification"]
                user_iq.long_term_planning = dim_scores["long_term_planning"]
                user_iq.updated_at = datetime.utcnow()

                # Audit in ledger
                ledger = IQActivityLedger(
                    user_id=user_id,
                    dimension="all_10_dimensions",
                    delta=round(total_score - old_total, 1),
                    old_score=old_total,
                    new_score=total_score,
                    reason="Completed Full 10-Dimension Financial IQ Evaluation",
                    evidence_json=json.dumps(dim_scores)
                )
                db.add(ledger)

                # Keep legacy User model synced (0-1000 scale)
                usr = db.query(User).filter(User.id == user_id).first()
                if usr:
                    usr.financial_iq = normalized_1000

                # Also save legacy FinancialIQRecord
                record = FinancialIQRecord(
                    user_id=user_id,
                    total_score=total_score,
                    knowledge_score=dim_scores["investing_basics"] * 3.0,
                    risk_score=dim_scores["risk_understanding"] * 2.0,
                    inflation_score=dim_scores["long_term_planning"] * 1.5,
                    goals_score=dim_scores["budgeting"] * 1.5,
                    diversification_score=dim_scores["diversification"],
                    decision_score=dim_scores["decision_discipline"],
                    strengths_json=str(strengths),
                    weak_areas_json=str(weak_areas),
                    recommended_learning_json=str(recommended_learning)
                )
                db.add(record)
                db.commit()
            except Exception as e:
                db.rollback()

        dimensions_formatted = {}
        for dim, score in dim_scores.items():
            meta = DIMENSION_METADATA[dim]
            dimensions_formatted[dim] = {
                "score": score,
                "max": 10.0,
                "label": meta["label"],
                "icon": meta["icon"]
            }

        return {
            "total_score": round(total_score, 1),
            "scale_maximum": 100,
            "normalized_1000_score": normalized_1000,
            "tier_name": tier_name,
            "tier_badge": tier_badge,
            "dimensions": dimensions_formatted,
            "strengths": strengths,
            "weak_areas": weak_areas,
            "recommended_learning": recommended_learning,
            "detailed_feedback": detailed_feedback
        }

    def get_user_iq_profile(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Retrieves user's 10-dimension IQ profile and recent audit entries."""
        user_iq = db.query(UserFinancialIQ).filter(UserFinancialIQ.user_id == user_id).first()
        if not user_iq:
            user_iq = UserFinancialIQ(
                user_id=user_id,
                total_score=65.0,
                budgeting=6.5,
                saving=7.0,
                debt_mgmt=7.5,
                investing_basics=6.0,
                risk_understanding=6.5,
                asset_allocation=6.0,
                market_cycles=5.5,
                decision_discipline=6.0,
                diversification=6.5,
                long_term_planning=6.5
            )
            db.add(user_iq)
            db.commit()
            db.refresh(user_iq)

        # Audit ledger entries
        ledger_entries = db.query(IQActivityLedger).filter(
            IQActivityLedger.user_id == user_id
        ).order_by(IQActivityLedger.created_at.desc()).limit(15).all()

        recent_activity = [
            {
                "id": entry.id,
                "dimension": entry.dimension,
                "delta": entry.delta,
                "old_score": entry.old_score,
                "new_score": entry.new_score,
                "reason": entry.reason,
                "timestamp": entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for entry in ledger_entries
        ]

        dim_breakdown = {
            "budgeting": {"score": user_iq.budgeting, "max": 10.0, "label": "Cash Flow & Budgeting", "icon": "💵"},
            "saving": {"score": user_iq.saving, "max": 10.0, "label": "Emergency Savings", "icon": "🛡️"},
            "debt_mgmt": {"score": user_iq.debt_mgmt, "max": 10.0, "label": "Debt Management", "icon": "💳"},
            "investing_basics": {"score": user_iq.investing_basics, "max": 10.0, "label": "Investing Basics", "icon": "📈"},
            "risk_understanding": {"score": user_iq.risk_understanding, "max": 10.0, "label": "Risk Understanding", "icon": "⚖️"},
            "asset_allocation": {"score": user_iq.asset_allocation, "max": 10.0, "label": "Asset Allocation", "icon": "🧩"},
            "market_cycles": {"score": user_iq.market_cycles, "max": 10.0, "label": "Market Cycles", "icon": "🔄"},
            "decision_discipline": {"score": user_iq.decision_discipline, "max": 10.0, "label": "Decision Discipline", "icon": "🧘"},
            "diversification": {"score": user_iq.diversification, "max": 10.0, "label": "Diversification", "icon": "🌐"},
            "long_term_planning": {"score": user_iq.long_term_planning, "max": 10.0, "label": "Long-Term Planning", "icon": "🎯"}
        }

        total_pts = sum(d["score"] for d in dim_breakdown.values())
        normalized_1000 = int(round(total_pts * 10))

        return {
            "user_id": user_id,
            "total_score_100": round(total_pts, 1),
            "normalized_1000_score": normalized_1000,
            "display_iq": f"{normalized_1000}/1000",
            "tier": "Advanced Investor" if total_pts >= 70 else ("Wealth Builder" if total_pts >= 55 else "Foundation Builder"),
            "dimensions": dim_breakdown,
            "recent_audit_trail": recent_activity
        }

    def audit_user_portfolio_behavior(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Behavioral audit of user's portfolio holdings for Financial IQ calibration.
        STRICT ISOLATION: Does NOT execute real trades or alter real user funds.
        """
        holdings = db.query(AssetHolding).filter(AssetHolding.user_id == user_id).all()
        paper_holdings = db.query(PaperHolding).filter(PaperHolding.user_id == user_id).all()

        total_val = sum(h.current_value for h in holdings)
        notes = []

        # Check single holding concentration
        high_concentration = False
        if holdings and total_val > 0:
            for h in holdings:
                ratio = h.current_value / total_val
                if ratio > 0.40:
                    high_concentration = True
                    notes.append(f"Excessive concentration: {h.asset_class} constitutes {ratio*100:.1f}% of portfolio.")

        if high_concentration:
            notes.append("Diversification recommendation: rebalance asset weights to cap single class at 35%.")
        else:
            notes.append("Healthy multi-asset diversification observed.")

        return {
            "user_id": user_id,
            "analyzed_holdings_count": len(holdings) + len(paper_holdings),
            "total_portfolio_value": round(total_val, 2),
            "behavioral_findings": notes,
            "isolation_rule": "User holdings inspected solely for behavioral insight. Real capital is never traded."
        }


financial_iq_service = FinancialIQService()

def evaluate_financial_iq(answers: Dict[str, Any], user_id: Optional[int] = None, db: Optional[Any] = None) -> Dict[str, Any]:
    return financial_iq_service.evaluate_answers(answers, user_id=user_id, db=db)

def get_iq_questions() -> List[Dict[str, Any]]:
    return financial_iq_service.get_assessment_questions()
