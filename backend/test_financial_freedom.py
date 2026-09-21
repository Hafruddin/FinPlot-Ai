"""
Unit tests for FinPilot AI Financial Freedom Calculation Services
Tests cash flow, safe capacity, emergency fund, inflation, freedom corpus,
reverse SIP annuity solver, edge cases, and readiness score.
"""

import unittest
import math
from backend.services.financial_freedom_service import (
    calculate_cashflow,
    calculate_emergency_fund,
    calculate_financial_freedom,
    calculate_years_to_freedom,
    calculate_scenarios,
    calculate_readiness_score
)


class TestFinancialFreedomService(unittest.TestCase):

    def test_cashflow_demo_profile(self):
        """Test with user's specific demo profile: Income 75k, Essential 25k, Lifestyle 8k, EMIs 7k."""
        income = {"monthly_income": 75000, "additional_income": 0, "rental_income": 0, "spouse_income": 0}
        essential = {"rent": 15000, "groceries": 7000, "utilities": 3000}  # total 25k
        lifestyle = {"dining": 5000, "shopping": 3000}                      # total 8k
        emis = {"car_loan": 7000}                                           # total 7k

        res = calculate_cashflow(income, essential, lifestyle, emis, current_savings=180000)

        self.assertEqual(res["total_monthly_income"], 75000)
        self.assertEqual(res["total_essential_expenses"], 25000)
        self.assertEqual(res["total_lifestyle_expenses"], 8000)
        self.assertEqual(res["total_emis"], 7000)
        self.assertEqual(res["total_monthly_expenses"], 40000)
        self.assertEqual(res["monthly_surplus"], 35000)
        self.assertGreater(res["suggested_safety_buffer"], 0)
        self.assertLess(res["suggested_safety_buffer"], 35000)
        self.assertEqual(res["monthly_surplus"], res["safe_investment_capacity"] + res["suggested_safety_buffer"])

    def test_emergency_fund_readiness(self):
        """Test emergency fund calculation for 6 months buffer."""
        # Obligations = 25k essential + 7k emi = 32k/month. 6 months = 192,000.
        res = calculate_emergency_fund(essential_monthly=25000, emi_monthly=7000, current_savings=180000, multiplier_months=6, monthly_capacity=25000)
        self.assertEqual(res["target_amount"], 192000)
        self.assertEqual(res["gap"], 12000)
        self.assertFalse(res["is_ready"])
        self.assertEqual(res["months_to_complete"], 1)

        # When fully funded
        res_ready = calculate_emergency_fund(essential_monthly=25000, emi_monthly=7000, current_savings=200000, multiplier_months=6)
        self.assertTrue(res_ready["is_ready"])
        self.assertEqual(res_ready["gap"], 0)
        self.assertEqual(res_ready["months_to_complete"], 0)

    def test_financial_freedom_corpus_and_reverse_sip(self):
        """Test inflation-adjusted future expense and reverse SIP equation."""
        # 40,000/mo current living expense, 6% inflation, 10 years, 4% withdrawal rate
        # 10% expected return, 95k existing investments
        res = calculate_financial_freedom(
            monthly_expense_today=40000,
            inflation_rate=0.06,
            horizon_years=10,
            withdrawal_rate=0.04,
            existing_investments=95000,
            return_assumption=0.10,
            monthly_investment_capacity=25000
        )

        # Inflation factor (1.06)^10 = 1.790847...
        # Future monthly expense = 40000 * 1.790847 = ~71,634
        self.assertAlmostEqual(res["future_monthly_expense"], 71634, delta=50)
        # Freedom corpus = annual / 0.04 = future_monthly * 12 * 25 = ~2,14,90,000
        self.assertGreater(res["freedom_corpus"], 20000000)
        # Required SIP must be positive and non-zero
        self.assertGreater(res["required_sip"], 0)
        # Verify existing investment compounding (95k * 1.10^10 = ~246,406)
        self.assertAlmostEqual(res["existing_investments_fv"], 246408, delta=100)

    def test_reverse_sip_mathematical_precision(self):
        """Verify reverse annuity solver against a known manual calculation."""
        # Target = 10,00,000, Existing = 0, n = 5 years (60 months), r = 12% (1% / mo)
        # Formula: FV = P * [ ((1.01)^60 - 1) / 0.01 ] * 1.01
        # (1.01^60 - 1)/0.01 = 81.66966986; * 1.01 = 82.48636656
        # P = 1,000,000 / 82.48636656 = ~12,123.21 => 12,124
        # At withdrawal rate 0.04 and 10L target:
        res = calculate_financial_freedom(
            monthly_expense_today=1000000 * 0.04 / 12, # so corpus = 1,000,000
            inflation_rate=0.0,
            horizon_years=5,
            withdrawal_rate=0.04,
            existing_investments=0,
            return_assumption=0.12,
            monthly_investment_capacity=20000
        )
        self.assertEqual(res["freedom_corpus"], 1000000)
        self.assertAlmostEqual(res["required_sip"], 12124, delta=2)

    def test_target_already_achieved(self):
        """If existing investments compound to exceed target corpus, required SIP is 0."""
        res = calculate_financial_freedom(
            monthly_expense_today=20000,
            inflation_rate=0.05,
            horizon_years=10,
            withdrawal_rate=0.04,
            existing_investments=50000000, # 5 Crore existing
            return_assumption=0.12,
            monthly_investment_capacity=20000
        )
        self.assertEqual(res["required_sip"], 0)
        self.assertTrue(res["sip_target_already_achieved"])
        self.assertFalse(res["has_capacity_shortfall"])

    def test_edge_cases(self):
        """Test zero inflation, zero return, and zero surplus."""
        # Zero return assumption
        res_zero_r = calculate_financial_freedom(
            monthly_expense_today=30000,
            inflation_rate=0.05,
            horizon_years=10,
            withdrawal_rate=0.04,
            existing_investments=0,
            return_assumption=0.0,
            monthly_investment_capacity=10000
        )
        self.assertGreater(res_zero_r["required_sip"], 0)
        self.assertFalse(math.isnan(res_zero_r["required_sip"]))

        # Zero income / negative surplus
        cf_neg = calculate_cashflow(
            {"monthly_income": 30000},
            {"rent": 25000},
            {"lifestyle": 10000},
            {"emi": 5000}
        )
        self.assertEqual(cf_neg["monthly_surplus"], -10000)
        self.assertEqual(cf_neg["safe_investment_capacity"], 0)

    def test_years_to_freedom_simulation(self):
        """Test month-by-month simulation."""
        res = calculate_years_to_freedom(
            current_corpus=100000,
            monthly_sip=25000,
            return_rate=0.12,
            monthly_expense_today=40000,
            inflation_rate=0.06,
            withdrawal_rate=0.04,
            max_years=40
        )
        self.assertTrue(res["achievable"])
        self.assertGreater(res["years"], 0)
        self.assertLess(res["years"], 40)
        self.assertIn("Under these assumptions", res["display_text"])

    def test_scenarios_comparison(self):
        """Verify Conservative, Base, and Optimistic scenarios."""
        scenarios = calculate_scenarios(
            monthly_expense_today=40000,
            inflation_rate=0.06,
            horizon_years=10,
            withdrawal_rate=0.04,
            existing_investments=95000,
            monthly_sip=25000
        )
        self.assertEqual(len(scenarios), 3)
        self.assertEqual(scenarios[0]["scenario"], "Conservative")
        self.assertEqual(scenarios[1]["scenario"], "Base")
        self.assertEqual(scenarios[2]["scenario"], "Optimistic")
        # Higher return -> lower required SIP to meet target
        self.assertGreater(scenarios[0]["required_sip"], scenarios[1]["required_sip"])
        self.assertGreater(scenarios[1]["required_sip"], scenarios[2]["required_sip"])

    def test_readiness_score(self):
        """Verify explainable 0-100 score."""
        score_res = calculate_readiness_score(
            emergency_fund_months=5.6,
            emi_burden_pct=9.3,
            savings_rate_pct=46.7,
            capacity_to_sip_ratio=0.85,
            horizon_years=10
        )
        self.assertGreaterEqual(score_res["score"], 0)
        self.assertLessEqual(score_res["score"], 100)
        self.assertIn(score_res["category"], ["Starting", "Building", "Progressing", "Strong"])
        self.assertEqual(len(score_res["explanations"]), 5)


if __name__ == "__main__":
    unittest.main()
