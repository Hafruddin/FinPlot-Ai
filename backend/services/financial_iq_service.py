"""
FinPilot AI — Multi-Dimensional Financial IQ Assessment Engine
Computes genuine, verifiable Financial IQ scores across 6 distinct competency pillars:
- Financial Knowledge (30 pts)
- Risk Understanding (20 pts)
- Inflation Understanding (15 pts)
- Goal Planning (15 pts)
- Diversification (10 pts)
- Decision Making (10 pts)
Total Scale = 100 Points.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Quiz, QuizAttempt, FinancialIQRecord, User, LessonCompletion

# Authoritative Question Bank across the 6 Core Dimensions
ASSESSMENT_QUESTIONS = [
    # 1. Financial Knowledge (Max: 30)
    {
        "id": "q_know_1",
        "dimension": "knowledge",
        "weight": 15.0,
        "question": "What is the primary difference between a Mutual Fund Direct Plan and a Regular Plan?",
        "options": [
            "Direct plans have higher returns because they invest in riskier small caps",
            "Direct plans have lower expense ratios because distributor commissions are eliminated",
            "Regular plans are guaranteed by SEBI while direct plans carry no investor protection",
            "There is no financial difference between direct and regular plans"
        ],
        "correct_index": 1,
        "explanation": "Direct plans bypass distributor commissions, resulting in a 0.5%–1.2% lower Total Expense Ratio (TER) which compounds significantly over long horizons."
    },
    {
        "id": "q_know_2",
        "dimension": "knowledge",
        "weight": 15.0,
        "question": "How does compound interest behave over long investment horizons compared to simple interest?",
        "options": [
            "It grows linearly at a predictable fixed rupee addition per year",
            "It grows exponentially because accumulated earnings earn their own subsequent returns",
            "It only benefits investors who deposit new principal every single month",
            "It delivers returns only after the initial 15 years elapse"
        ],
        "correct_index": 1,
        "explanation": "Compounding reinvests prior gains, producing an exponential hockey-stick growth curve where late-stage gains vastly overshadow initial principal."
    },

    # 2. Risk Understanding (Max: 20)
    {
        "id": "q_risk_1",
        "dimension": "risk",
        "weight": 10.0,
        "question": "If your financial goal requires capital within 2 years, which asset class is most suitable?",
        "options": [
            "Small-cap equity mutual funds for maximum acceleration",
            "Cryptocurrency or leveraged intraday futures contracts",
            "High-quality short-term debt, liquid funds, or bank fixed deposits",
            "Gold mining equity stocks"
        ],
        "correct_index": 2,
        "explanation": "Short horizons (<3 years) cannot absorb equity market downturns. Capital preservation and liquidity in fixed income instruments take precedence."
    },
    {
        "id": "q_risk_2",
        "dimension": "risk",
        "weight": 10.0,
        "question": "What is the recommended size of an emergency fund for an individual with ₹20,000 in mandatory monthly expenses?",
        "options": [
            "₹20,000 (1 month of expenses)",
            "₹60,000 to ₹1,20,000 (3 to 6 months of mandatory expenses)",
            "₹5,00,000 locked in a 10-year equity mutual fund",
            "No cash buffer is needed if you possess a high credit card limit"
        ],
        "correct_index": 1,
        "explanation": "Standard financial risk management requires 3 to 6 months of mandatory living expenses held in liquid, safe instruments to absorb unexpected shocks."
    },

    # 3. Inflation Understanding (Max: 15)
    {
        "id": "q_inf_1",
        "dimension": "inflation",
        "weight": 15.0,
        "question": "If your savings account yields 4.0% interest and annual consumer inflation is 6.5%, what is your approximate Real Rate of Return?",
        "options": [
            "+10.5% annual gain",
            "+4.0% guaranteed capital growth",
            "-2.5% loss in purchasing power",
            "0.0% breakeven"
        ],
        "correct_index": 2,
        "explanation": "Real Return ≈ Nominal Return - Inflation (4.0% - 6.5% = -2.5%). Despite nominal rupee increases, your real purchasing power shrinks each year."
    },

    # 4. Goal Planning (Max: 15)
    {
        "id": "q_goal_1",
        "dimension": "goals",
        "weight": 15.0,
        "question": "When target goal deadline is extended from 10 years to 15 years, what happens to the required monthly SIP contribution?",
        "options": [
            "The required monthly SIP increases because the goal becomes larger",
            "The required monthly SIP decreases significantly because compounding has 5 more years to generate wealth",
            "The monthly requirement remains precisely identical regardless of timeline",
            "You are forced to take on twice as much equity risk"
        ],
        "correct_index": 1,
        "explanation": "Extending investment duration harnesses additional compounding cycles, dramatically reducing the monthly out-of-pocket savings required."
    },

    # 5. Diversification (Max: 10)
    {
        "id": "q_div_1",
        "dimension": "diversification",
        "weight": 10.0,
        "question": "Which type of financial risk is directly minimized by holding 25-30 stocks across different economic sectors?",
        "options": [
            "Systematic market risk (such as a nationwide recession)",
            "Unsystematic specific risk (such as a single company's bankruptcy or management failure)",
            "Currency inflation risk across all commodities",
            "Risk of tax law modifications"
        ],
        "correct_index": 1,
        "explanation": "Diversification neutralizes company-specific and sector-specific unsystematic risk. Macroeconomic systematic risk cannot be eliminated through diversification."
    },

    # 6. Decision Making (Max: 10)
    {
        "id": "q_dec_1",
        "dimension": "decision_making",
        "weight": 10.0,
        "question": "You have ₹50,000 in savings, but hold a ₹40,000 credit card balance charging 38% p.a. interest. What is the most financially rational move?",
        "options": [
            "Invest all ₹50,000 into a high-risk equity stock hoping for a 50% quick return",
            "Pay off the ₹40,000 credit card balance immediately, securing a guaranteed 38% effective return by eliminating debt",
            "Ignore the debt and maintain only minimum monthly payments to build credit",
            "Buy physical gold jewelry"
        ],
        "correct_index": 1,
        "explanation": "Eliminating a 38% interest liability delivers a risk-free, tax-free effective return of 38%—superior to any realistic market investment return."
    }
]


class FinancialIQService:
    """Calculates multidimensional financial IQ, identifies strengths/weaknesses, and persists attempts."""

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
            for q in ASSESSMENT_QUESTIONS
        ]

    def evaluate_answers(
        self,
        answers_dict: Dict[str, int],
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Evaluates submitted answer indices, scores each dimension strictly,
        computes total 0-100 score, identifies strengths & weak areas,
        and saves records to the database.
        """
        dimension_scores = {
            "knowledge": 0.0,
            "risk": 0.0,
            "inflation": 0.0,
            "goals": 0.0,
            "diversification": 0.0,
            "decision_making": 0.0
        }
        max_scores = {
            "knowledge": 30.0,
            "risk": 20.0,
            "inflation": 15.0,
            "goals": 15.0,
            "diversification": 10.0,
            "decision_making": 10.0
        }

        detailed_feedback = []

        for q in ASSESSMENT_QUESTIONS:
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
                dimension_scores[dim] += q["weight"]

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
                        selected_option=user_choice,
                        is_correct=1 if is_correct else 0,
                        dimension=dim
                    )
                    db.add(attempt)
                except Exception:
                    pass

        # Total IQ Score (0-100)
        total_score = sum(dimension_scores.values())

        # Determine Strengths & Weak Areas
        strengths = []
        weak_areas = []
        recommended_learning = []

        for dim, score in dimension_scores.items():
            max_s = max_scores[dim]
            pct = (score / max_s) * 100.0
            dim_label = dim.replace("_", " ").title()

            if pct >= 80.0:
                strengths.append(f"{dim_label} Mastery ({round(score)}/{round(max_s)} pts)")
            elif pct <= 50.0:
                weak_areas.append(f"{dim_label} Gap ({round(score)}/{round(max_s)} pts)")
                if dim == "inflation":
                    recommended_learning.append("Lesson 2: Inflation & The Real Rate of Return")
                elif dim == "risk":
                    recommended_learning.append("Lesson 3: Emergency Fund Architecture & Liquidity")
                elif dim == "goals":
                    recommended_learning.append("Lesson 4: Reverse SIP & Compounding Math")
                elif dim == "diversification":
                    recommended_learning.append("Lesson 5: Asset Allocation & Risk Diversification")
                elif dim == "decision_making":
                    recommended_learning.append("Lesson 6: Debt Avalanche & High-Interest Payoff")
                else:
                    recommended_learning.append("Lesson 1: Financial Foundations & Direct Mutual Funds")

        if not weak_areas:
            weak_areas.append("None identified! Excellent holistic financial competency.")
        if not recommended_learning:
            recommended_learning.append("Advanced Wealth Structuring & Tax Optimization")

        # Derive Pedagogical Tier
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
        elif total_score >= 25:
            tier_name = "Foundation Builder"
            tier_badge = "Developing"
        else:
            tier_name = "Beginner"
            tier_badge = "Getting Started"

        # Persist IQ Record
        if db and user_id is not None:
            try:
                record = FinancialIQRecord(
                    user_id=user_id,
                    total_score=total_score,
                    knowledge_score=dimension_scores["knowledge"],
                    risk_score=dimension_scores["risk"],
                    inflation_score=dimension_scores["inflation"],
                    goals_score=dimension_scores["goals"],
                    diversification_score=dimension_scores["diversification"],
                    decision_score=dimension_scores["decision_making"],
                    strengths_json=str(strengths),
                    weak_areas_json=str(weak_areas),
                    recommended_learning_json=str(recommended_learning)
                )
                db.add(record)

                # Update user profile
                usr = db.query(User).filter(User.id == user_id).first()
                if usr:
                    # Update User model (stores 0-1000 scale, so multiply by 10)
                    usr.financial_iq = int(total_score * 10)

                db.commit()
            except Exception as e:
                db.rollback()

        return {
            "total_score": round(total_score, 1),
            "scale_maximum": 100,
            "normalized_1000_score": int(total_score * 10),
            "tier_name": tier_name,
            "tier_badge": tier_badge,
            "dimensions": {
                "knowledge": {"score": dimension_scores["knowledge"], "max": 30.0, "label": "Financial Knowledge"},
                "risk": {"score": dimension_scores["risk"], "max": 20.0, "label": "Risk Understanding"},
                "inflation": {"score": dimension_scores["inflation"], "max": 15.0, "label": "Inflation Understanding"},
                "goals": {"score": dimension_scores["goals"], "max": 15.0, "label": "Goal Planning"},
                "diversification": {"score": dimension_scores["diversification"], "max": 10.0, "label": "Diversification"},
                "decision_making": {"score": dimension_scores["decision_making"], "max": 10.0, "label": "Decision Making"}
            },
            "strengths": strengths,
            "weak_areas": weak_areas,
            "recommended_learning": recommended_learning,
            "detailed_feedback": detailed_feedback
        }


financial_iq_service = FinancialIQService()

def evaluate_financial_iq(answers: Dict[str, str], user_id: Optional[int] = None, db: Optional[Any] = None) -> Dict[str, Any]:
    return financial_iq_service.evaluate_answers(answers, user_id=user_id, db=db)

def get_iq_questions() -> List[Dict[str, Any]]:
    return financial_iq_service.get_assessment_questions()
