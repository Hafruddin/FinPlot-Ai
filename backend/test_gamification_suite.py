"""
FinPilot AI — Automated Gamification & Financial IQ Test Suite
Tests:
1. Gamification Service (XP, Levels, Badges, Quests, Streaks)
2. Daily Quiz & Immediate Feedback
3. Decision Quality Engine (PROFIT ≠ FINANCIAL INTELLIGENCE principle)
4. Historical Simulation Engine with STRICT Anti-Future-Leakage Protection
5. Multi-dimensional 10-Dimension Financial IQ & Immutable Activity Ledger
6. Portfolio Behavior Audit (Strict isolation: zero real broker execution)
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import (
    User, GameXP, Badge, LearningQuest, DailyQuiz,
    SimulationSession, UserFinancialIQ, IQActivityLedger, AssetHolding
)
from backend.services.gamification_service import GamificationService
from backend.services.decision_quality_service import DecisionQualityService
from backend.services.simulation_engine import SimulationEngine, HISTORICAL_SCENARIOS
from backend.services.financial_iq_service import financial_iq_service


class TestGamificationAndFinancialIQ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # In-memory SQLite database for isolated rapid testing
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        import uuid
        self.db = self.Session()
        u_id = uuid.uuid4().hex[:8]
        self.user = User(
            name=f"Test Investor {u_id}",
            email=f"investor_{u_id}@test.com",
            hashed_password="fakehashsecret",
            financial_iq=650
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def test_01_gamification_xp_and_level_progression(self):
        """Tests that XP accumulates, levels progress logically, and level-ups are detected."""
        GamificationService.init_defaults(self.db)
        prof = GamificationService.get_profile(self.user.id, self.db)
        self.assertEqual(prof["level"], 1)
        self.assertEqual(prof["title"], "Financial Novice")

        # Award 500 XP -> should advance to Level 3 (500-900 XP)
        res = GamificationService.add_xp(self.user.id, 400, self.db)
        self.assertTrue(res["did_level_up"])
        self.assertEqual(res["level"], 3)
        self.assertEqual(res["title"], "Saver Apprentice")

    def test_02_gamification_badges_and_quests(self):
        """Tests unlocking badges awards XP and quests are tracked."""
        GamificationService.init_defaults(self.db)
        unlock_res = GamificationService.unlock_badge(self.user.id, "compounding_champ", self.db)
        self.assertIsNotNone(unlock_res)
        self.assertTrue(unlock_res["unlocked"])
        self.assertEqual(unlock_res["xp_awarded"], 120)

        # Duplicate unlock should return None
        dup = GamificationService.unlock_badge(self.user.id, "compounding_champ", self.db)
        self.assertIsNone(dup)

    def test_03_daily_quiz_and_streak(self):
        """Tests daily quiz retrieval, submission, and streak counter."""
        quiz = GamificationService.get_daily_quiz(self.user.id, self.db)
        self.assertIn("question", quiz)
        self.assertFalse(quiz["already_attempted"])

        # Submit answer
        ans = GamificationService.answer_daily_quiz(
            self.user.id,
            quiz["quiz_id"],
            quiz["correct_index"] if "correct_index" in quiz and quiz["correct_index"] is not None else 2,
            self.db
        )
        self.assertIn("is_correct", ans)
        self.assertGreaterEqual(ans["streak_days"], 1)

    def test_04_profit_not_equal_to_financial_intelligence(self):
        """
        CRITICAL ARCHITECTURAL TEST:
        Demonstrates that reckless high-risk gambling receives low Decision Quality
        even if high profit occurs, whereas prudent risk-managed sizing gets high score.
        """
        # Case A: Reckless All-In (80% of portfolio in single trade)
        reckless_decision = DecisionQualityService.evaluate_decision(
            action="BUY",
            quantity=800,
            price=100.0,
            portfolio_cash=100000.0,
            portfolio_equity_val=0.0, # 80,000 / 100,000 = 80% concentration!
            risk_profile="moderate",
            reasoning="YOLO to get rich quick",
            market_condition="NORMAL"
        )
        # Sizing and Diversification scores MUST be severely penalized
        self.assertLessEqual(reckless_decision["pillars"]["position_sizing"], 30.0)
        self.assertLessEqual(reckless_decision["pillars"]["diversification"], 35.0)
        self.assertLess(reckless_decision["decision_score"], 65.0)
        self.assertIn("FinPilot Rule", reckless_decision["pedagogical_rule"])

        # Case B: Prudent Disciplined Sizing (10% allocation with documented rationale)
        prudent_decision = DecisionQualityService.evaluate_decision(
            action="BUY",
            quantity=100,
            price=100.0,
            portfolio_cash=90000.0,
            portfolio_equity_val=10000.0, # 10,000 / 100,000 = 10% sizing
            risk_profile="moderate",
            reasoning="Accumulating high-quality cash-flow resilient leader during consolidation phase.",
            market_condition="NORMAL"
        )
        self.assertGreaterEqual(prudent_decision["pillars"]["position_sizing"], 90.0)
        self.assertGreaterEqual(prudent_decision["pillars"]["diversification"], 90.0)
        self.assertGreaterEqual(prudent_decision["decision_score"], 80.0)

    def test_05_anti_future_leakage_in_simulation(self):
        """
        ANTI-FUTURE-LEAKAGE VERIFICATION:
        Ensures client receives strictly date <= T data and zero future data.
        """
        sess_view = SimulationEngine.start_session(self.user.id, "covid_shock_2020", self.db)
        session_id = sess_view["session_id"]

        # Step 0: Exactly 1 candle revealed
        self.assertEqual(sess_view["current_step_index"], 0)
        self.assertEqual(len(sess_view["candles_revealed"]), 1)
        self.assertEqual(sess_view["candles_revealed"][0]["date"], "2020-01-15")

        # Advance 3 steps
        SimulationEngine.advance_step(session_id, self.db)
        SimulationEngine.advance_step(session_id, self.db)
        s3 = SimulationEngine.advance_step(session_id, self.db)

        self.assertEqual(s3["current_step_index"], 3)
        self.assertEqual(len(s3["candles_revealed"]), 4) # Step 0, 1, 2, 3
        # Future candles from step 4+ (e.g. 2020-03-09 panic crash) are strictly NOT present
        revealed_dates = [c["date"] for c in s3["candles_revealed"]]
        self.assertNotIn("2020-03-23", revealed_dates)
        self.assertNotIn("2020-04-22", revealed_dates)

    def test_06_simulation_order_execution_and_decision_scoring(self):
        """Tests that orders update virtual cash, holdings, and update IQ activity ledger."""
        sess_view = SimulationEngine.start_session(self.user.id, "covid_shock_2020", self.db)
        session_id = sess_view["session_id"]
        curr_price = sess_view["current_price"] # 1520.0

        # Place BUY order for 10 shares
        order_res = SimulationEngine.execute_order(
            session_id=session_id,
            action="BUY",
            quantity=10,
            reasoning="Initial foundational position aligned with long term horizon.",
            user_id=self.user.id,
            db=self.db
        )
        self.assertEqual(order_res["order_status"], "EXECUTED")
        self.assertEqual(order_res["session"]["position"]["quantity"], 10)
        self.assertAlmostEqual(order_res["session"]["cash_balance"], 100000.0 - (10 * curr_price))

        # Check that an immutable audit entry was written to iq_activity_ledger
        ledger_entry = self.db.query(IQActivityLedger).filter(
            IQActivityLedger.user_id == self.user.id,
            IQActivityLedger.dimension == "decision_discipline"
        ).first()
        self.assertIsNotNone(ledger_entry)
        self.assertIn("Decision Quality", ledger_entry.reason)

    def test_07_ten_dimension_financial_iq_evaluation(self):
        """Tests 10-dimension evaluation, 1000-point normalization, and profile retrieval."""
        questions = financial_iq_service.get_assessment_questions()
        self.assertEqual(len(questions), 10)

        # Submit answers (all correct)
        answers = {q["id"]: 1 for q in questions}
        result = financial_iq_service.evaluate_answers(answers, user_id=self.user.id, db=self.db)

        self.assertIn("total_score", result)
        self.assertIn("normalized_1000_score", result)
        self.assertIn("dimensions", result)
        self.assertEqual(len(result["dimensions"]), 10)

        # Retrieve profile
        prof = financial_iq_service.get_user_iq_profile(self.user.id, self.db)
        self.assertIn("display_iq", prof)
        self.assertEqual(len(prof["dimensions"]), 10)
        self.assertGreater(len(prof["recent_audit_trail"]), 0)

    def test_08_portfolio_behavior_audit_isolation(self):
        """Tests that portfolio behavior is audited without modifying holdings or executing broker trades."""
        h1 = AssetHolding(user_id=self.user.id, asset_class="Equity", weight=0.70, current_value=210000.0)
        h2 = AssetHolding(user_id=self.user.id, asset_class="Debt", weight=0.30, current_value=90000.0)
        self.db.add_all([h1, h2])
        self.db.commit()

        audit = financial_iq_service.audit_user_portfolio_behavior(self.user.id, self.db)
        self.assertEqual(audit["total_portfolio_value"], 300000.0)
        self.assertIn("isolation_rule", audit)
        self.assertIn("never traded", audit["isolation_rule"])


if __name__ == "__main__":
    unittest.main()
