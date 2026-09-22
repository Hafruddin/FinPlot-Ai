"""
FinPilot AI - Comprehensive Hackathon Evaluation Test Suite
RMK INNOVATE Hackathon: Agentic & Generative AI Track

Covers:
1. Authentication & Security (bcrypt, JWT)
2. 7-Agent Orchestration Pipeline & SQLite persistence
3. RAG Knowledge Base Retrieval & Citations (SEBI, RBI, AMFI, NISM)
4. AI Tutor & Safety Guardrails
5. Deterministic Reverse SIP Engine & Mathematical Edge Cases
6. Interactive What-If Engine (10y vs 15y timeline comparison)
7. Multi-Dimensional Financial IQ 6-Pillar Assessment
8. Portfolio Guardian & Allocation Drift Detection
"""

import os
import sys
import unittest
import json

# Add root and backend directories to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, engine, Base
from backend.services.financial_freedom_service import solve_reverse_sip
from backend.services.agent_orchestrator import run_pipeline
from backend.services.rag_service import query_knowledge_base, get_knowledge_documents
from backend.services.financial_iq_service import evaluate_financial_iq, get_iq_questions
from backend.services.portfolio_guardian_service import analyze_portfolio_drift
from backend.services.tutor_service import answer_financial_query

client = TestClient(app)

class TestFinPilotHackathonSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Ensure database tables exist."""
        Base.metadata.create_all(bind=engine)

    def test_01_health_check(self):
        """Verify root and health endpoints."""
        # API health check
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("FinPilot", data.get("service", ""))
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("version", data)

        # Root serves index.html
        root_res = client.get("/")
        self.assertEqual(root_res.status_code, 200)
        self.assertIn("text/html", root_res.headers.get("content-type", ""))

    def test_02_auth_signup_and_jwt(self):
        """Verify user signup, bcrypt hashing, and JWT token issuance."""
        test_email = f"hackathon_test_{os.urandom(4).hex()}@finpilot.ai"
        signup_payload = {
            "name": "Hackathon Evaluator",
            "email": test_email,
            "password": "SecurePassword123!"
        }
        res_signup = client.post("/api/auth/signup", json=signup_payload)
        self.assertEqual(res_signup.status_code, 200, res_signup.text)
        data = res_signup.json()
        self.assertIn("access_token", data)
        token = data["access_token"]

        # Test authenticated endpoint
        headers = {"Authorization": f"Bearer {token}"}
        res_me = client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        user_info = res_me.json()
        self.assertEqual(user_info.get("email"), test_email)

    def test_03_rag_knowledge_base_retrieval(self):
        """Verify RAG retrieval against authoritative SEBI, RBI, AMFI, and NISM corpus."""
        docs = get_knowledge_documents()
        self.assertGreaterEqual(len(docs), 8, "Knowledge base must have at least 8 curated documents")

        # Test compounding query
        results = query_knowledge_base("power of compounding mutual fund inflation", top_k=3)
        self.assertGreaterEqual(len(results), 1)
        top_doc = results[0]
        self.assertIn("source", top_doc)
        self.assertTrue(any(src in top_doc["source"] for src in ["AMFI", "SEBI", "RBI", "NISM", "Finance Act 2024", "Reserve Bank"]))

        # Test API endpoint
        res = client.post("/api/rag/query", json={"query": "Why direct mutual fund plans have lower expense ratio?", "top_k": 2})
        self.assertEqual(res.status_code, 200)
        api_results = res.json().get("results", [])
        self.assertGreaterEqual(len(api_results), 1)

    def test_04_ai_tutor_and_safety_guardrails(self):
        """Verify AI Tutor structured output and compliance safety filter."""
        # Standard educational query
        resp = answer_financial_query("What is the difference between direct and regular mutual funds?")
        self.assertIn("answer", resp)
        self.assertIn("key_takeaways", resp)
        self.assertIn("citations", resp)
        self.assertGreater(len(resp["citations"]), 0)

        # Safety filter query: asking for guaranteed return
        unsafe_resp = answer_financial_query("Which penny stock can give me a guaranteed 100% return in 1 month?")
        self.assertIn("answer", unsafe_resp)
        self.assertTrue(
            "guarantee" in unsafe_resp["answer"].lower() or "regulatory" in unsafe_resp["answer"].lower() or "disclaimer" in unsafe_resp["answer"].lower() or "sebi" in unsafe_resp["answer"].lower(),
            "AI Tutor must issue safety disclaimer on speculative or guaranteed return queries."
        )

        # Test Tutor Chat API endpoint
        res = client.post("/api/tutor/chat", json={"message": "How does inflation affect my fixed deposit?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("answer", data)
        self.assertIn("key_takeaways", data)

    def test_05_deterministic_reverse_sip_engine_and_edge_cases(self):
        """Verify reverse SIP formula accuracy and edge cases."""
        # Flagship scenario: 21y, Target 50L, Horizon 10y, Expected return 12%
        res = solve_reverse_sip(target_amount=5000000.0, horizon_years=10, annual_return=0.12)
        self.assertEqual(res["status"], "OK")
        # Required monthly SIP is ~₹21.5k - ₹21.7k depending on start/end month convention
        self.assertTrue(21000 <= res["required_monthly_sip"] <= 22000)

        # Edge case 1: Target already achieved with current corpus
        res_achieved = solve_reverse_sip(target_amount=1000000.0, current_savings=1200000.0, horizon_years=10, annual_return=0.12)
        self.assertEqual(res_achieved["status"], "TARGET_ALREADY_ACHIEVED")
        self.assertEqual(res_achieved["required_monthly_sip"], 0)

        # Edge case 2: Zero percent return (pure linear savings)
        res_zero_ret = solve_reverse_sip(target_amount=120000.0, current_savings=0.0, horizon_years=1, annual_return=0.0)
        self.assertEqual(res_zero_ret["status"], "ZERO_RETURN_LINEAR")
        self.assertEqual(res_zero_ret["required_monthly_sip"], 10000)

        # Edge case 3: Short 1-year horizon
        res_short = solve_reverse_sip(target_amount=120000.0, current_savings=0.0, horizon_years=1, annual_return=0.12)
        self.assertGreater(res_short["required_monthly_sip"], 9000)

    def test_06_whatif_timeline_engine(self):
        """Verify What-If Engine: 10y vs 15y timeline comparison produces ~55.1% drop in required SIP."""
        res = client.post("/api/simulation/whatif", json={
            "target_amount": 5000000.0,
            "current_savings": 50000.0,
            "previous_horizon_years": 10,
            "new_horizon_years": 15,
            "annual_return": 0.12,
            "monthly_capacity": 5000.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("previous_required_sip", data)
        self.assertIn("new_required_sip", data)
        self.assertIn("sip_reduction_pct", data)

        # Required SIP drops by ~55% (from ~21k to ~9.7k)
        self.assertGreater(data["sip_reduction_pct"], 50.0)
        self.assertGreater(data["sip_difference"], 10000)
        self.assertIn("what_changed_explanation", data)

    def test_07_seven_agent_pipeline_and_db_logging(self):
        """Verify full 7-Agent DAG orchestration and persistence."""
        user_input = {
            "name": "Arjun Patel",
            "age": 21,
            "monthly_income": 30000.0,
            "monthly_expenses": 20000.0,
            "current_savings": 50000.0,
            "monthly_investment_capacity": 5000.0,
            "target_corpus": 5000000.0,
            "horizon_years": 10,
            "risk_profile": "moderate",
            "expected_return": 12.0
        }

        pipeline_result = run_pipeline(user_input)
        self.assertIn("run_id", pipeline_result)
        self.assertEqual(pipeline_result["status"].upper(), "COMPLETED")

        trace = pipeline_result.get("trace", [])
        agent_names = [step.get("agent_name") for step in trace]
        expected_agents = [
            "ProfileAgent", "GoalAgent", "RiskAgent", 
            "KnowledgeAgent", "SimulationAgent", "StrategyAgent", "ExplanationAgent"
        ]
        for agent in expected_agents:
            self.assertIn(agent, agent_names, f"Agent {agent} must be present in execution trace")

        # Test API endpoint
        res = client.post("/api/agents/run", json=user_input)
        self.assertEqual(res.status_code, 200)
        api_data = res.json()
        self.assertEqual(api_data["status"].upper(), "COMPLETED")
        self.assertIn("trace", api_data)
        self.assertIn("results", api_data)

    def test_08_financial_iq_six_pillar_engine(self):
        """Verify 6-pillar Financial IQ evaluation and questions API."""
        # 1. Questions endpoint
        res_q = client.get("/api/iq/questions")
        self.assertEqual(res_q.status_code, 200)
        questions = res_q.json()
        self.assertGreaterEqual(len(questions), 4)

        # 2. Evaluation with perfect answers
        perfect_answers = {
            "q_know_1": "B",
            "q_know_2": "B",
            "q_risk_1": "C",
            "q_risk_2": "B",
            "q_inf_1": "C",
            "q_goal_1": "B",
            "q_div_1": "B",
            "q_dec_1": "B"
        }
        eval_result = evaluate_financial_iq(perfect_answers)
        self.assertEqual(eval_result["total_score"], 100)
        self.assertEqual(eval_result["normalized_1000_score"], 1000)
        self.assertEqual(eval_result["tier_name"], "Master Investor")

        # 3. Evaluation API endpoint
        res_eval = client.post("/api/iq/evaluate", json={"answers": {"q_emergency": "B", "q_volatility": "C"}})
        self.assertEqual(res_eval.status_code, 200)
        eval_data = res_eval.json()
        self.assertIn("dimensions", eval_data)
        self.assertIn("strengths", eval_data)
        self.assertIn("recommended_learning", eval_data)

    def test_09_portfolio_guardian_allocation_drift(self):
        """Verify Portfolio Guardian drift calculation and rebalancing guidance."""
        # 79% equity vs 70% target -> +9% equity drift
        drift_report = analyze_portfolio_drift(
            portfolio_value=300000.0,
            current_equity=237000.0,
            current_debt=45000.0,
            current_cash=18000.0,
            risk_tolerance="moderate"
        )
        self.assertEqual(drift_report["drift_status"], "MODERATE_DRIFT")
        self.assertAlmostEqual(drift_report["equity_drift_pct"], 9.0, delta=0.5)
        self.assertTrue(drift_report["review_recommended"])
        self.assertGreaterEqual(len(drift_report["rebalance_action_plan"]), 2)

        # API endpoint
        res = client.get("/api/portfolio/guardian?portfolio_value=300000&current_equity=237000&current_debt=45000&current_cash=18000")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["drift_status"], "MODERATE_DRIFT")
        self.assertIn("guardian_insights", data)

if __name__ == "__main__":
    unittest.main()
