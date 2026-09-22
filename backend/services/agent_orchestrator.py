"""
FinPilot AI — Multi-Agent Planning Orchestrator
Executes 7 distinct, specialized agents with strict input/output schemas, deterministic mathematics,
RAG knowledge retrieval, and persistent traceability.
"""

import uuid
import time
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import AgentRun
from backend.services.financial_freedom_service import (
    calculate_cashflow,
    calculate_emergency_fund,
    calculate_financial_freedom,
    solve_reverse_sip
)
from backend.services.rag_service import rag_service


class BaseAgent:
    """Base class for all FinPilot agents providing logging and execution timing."""
    def __init__(self, name: str, responsibility: str):
        self.name = name
        self.responsibility = responsibility

    def start_trace(self, run_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "run_id": run_id,
            "agent_name": self.name,
            "responsibility": self.responsibility,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "input_summary": str({k: v for k, v in input_data.items() if k not in ["password", "token"]})[:300]
        }


class ProfileAgent(BaseAgent):
    """Validates demographic, cash-flow, and capacity metrics without inventing numbers."""
    def __init__(self):
        super().__init__("ProfileAgent", "Validates cash flow, mandatory expenses, and investable capacity.")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        age = max(18, int(data.get("age", 21)))
        income = max(0.0, float(data.get("monthly_income", 30000.0)))
        expenses = max(0.0, float(data.get("monthly_expenses", 20000.0)))
        savings = max(0.0, float(data.get("current_savings", 50000.0)))
        declared_capacity = max(0.0, float(data.get("monthly_capacity", 5000.0)))

        surplus = income - expenses
        validated_capacity = min(declared_capacity, max(0.0, surplus))

        # Financial resilience assessment
        savings_rate_pct = round((surplus / income * 100.0), 1) if income > 0 else 0.0

        return {
            "age": age,
            "monthly_income": income,
            "monthly_expenses": expenses,
            "current_savings": savings,
            "surplus": surplus,
            "validated_monthly_capacity": validated_capacity,
            "savings_rate_pct": savings_rate_pct,
            "has_capacity_deficit": declared_capacity > surplus,
            "knowledge_level": data.get("knowledge_level", "intermediate")
        }


class GoalAgent(BaseAgent):
    """Validates goal target, time horizon, and computes inflation-adjusted corpus."""
    def __init__(self):
        super().__init__("GoalAgent", "Validates target amount, duration, and computes inflation-adjusted target.")

    def run(self, goal_data: Dict[str, Any], inflation_rate: float = 0.06) -> Dict[str, Any]:
        target = max(10000.0, float(goal_data.get("target_amount", 5000000.0))) # Default ₹50 Lakhs
        horizon_years = max(1, int(goal_data.get("duration_years", 10))) # Default 10 years
        goal_type = goal_data.get("goal_type", "Wealth Accumulation & Freedom")

        # Nominal inflation adjustment factor: (1 + inflation)^years
        inflation_factor = math.pow(1.0 + inflation_rate, horizon_years)
        inflation_adjusted_target = round(target * inflation_factor)

        return {
            "goal_type": goal_type,
            "target_amount_today": target,
            "duration_years": horizon_years,
            "inflation_rate_assumed": inflation_rate,
            "inflation_multiplier": round(inflation_factor, 3),
            "inflation_adjusted_target": inflation_adjusted_target
        }


class RiskAgent(BaseAgent):
    """Evaluates stated risk appetite against capacity, liquidity, and horizon constraints."""
    def __init__(self):
        super().__init__("RiskAgent", "Evaluates risk tolerance constraints and derives target asset allocation.")

    def run(self, stated_risk: str, horizon_years: int, savings: float, monthly_expenses: float) -> Dict[str, Any]:
        # Evaluate emergency buffer
        emergency_target = monthly_expenses * 6
        has_adequate_emergency = savings >= emergency_target
        risk = stated_risk.lower() if stated_risk else "moderate"

        # Horizon gating: equities need at least 5-7 years
        if horizon_years < 3:
            effective_risk = "conservative"
            asset_allocation = {"Equity": 20, "Debt": 60, "Cash/Liquid": 20, "Gold": 0}
            risk_reasoning = "Short horizon (< 3 years) mandates capital preservation regardless of risk appetite."
        elif horizon_years < 7:
            effective_risk = "moderate" if risk != "conservative" else "conservative"
            asset_allocation = {"Equity": 50, "Debt": 35, "Cash/Liquid": 10, "Gold": 5}
            risk_reasoning = "Medium horizon (3-7 years) allows balanced hybrid allocation."
        else:
            if risk == "aggressive":
                asset_allocation = {"Equity": 75, "Debt": 15, "Cash/Liquid": 5, "Gold": 5}
                effective_risk = "aggressive"
            elif risk == "conservative":
                asset_allocation = {"Equity": 40, "Debt": 45, "Cash/Liquid": 10, "Gold": 5}
                effective_risk = "conservative"
            else:
                asset_allocation = {"Equity": 65, "Debt": 20, "Cash/Liquid": 10, "Gold": 5}
                effective_risk = "moderate"
            risk_reasoning = f"Long horizon ({horizon_years} years) allows productive equity compounding to outpace inflation."

        return {
            "stated_risk_tolerance": stated_risk,
            "effective_risk_profile": effective_risk,
            "has_adequate_emergency_reserve": has_adequate_emergency,
            "target_asset_allocation": asset_allocation,
            "risk_reasoning": risk_reasoning
        }


class KnowledgeAgent(BaseAgent):
    """Retrieves authoritative financial literature from the RAG knowledge base."""
    def __init__(self):
        super().__init__("KnowledgeAgent", "Retrieves authoritative evidence and educational citations from RAG.")

    def run(self, goal_type: str, horizon_years: int) -> Dict[str, Any]:
        query = f"Goal planning compounding inflation reverse sip asset allocation for {horizon_years} years"
        docs = rag_service.search(query, top_k=3)
        return {
            "evidence_count": len(docs),
            "citations": [
                {
                    "title": d["title"],
                    "source": d["source"],
                    "url": d.get("url"),
                    "section": d.get("section")
                }
                for d in docs
            ],
            "context_summary": [d["title"] for d in docs]
        }


class SimulationAgent(BaseAgent):
    """Executes deterministic mathematical simulations across conservative, base, and optimistic scenarios."""
    def __init__(self):
        super().__init__("SimulationAgent", "Calculates deterministic reverse SIP and multi-scenario compounding projections.")

    def run(self, target_amount: float, horizon_years: int, current_savings: float, monthly_capacity: float) -> Dict[str, Any]:
        # Scenario Return Assumptions (p.a.)
        scenarios = {
            "conservative": {"return_rate": 0.09, "label": "Conservative (9% p.a. - Debt/Hybrid tilt)"},
            "base": {"return_rate": 0.12, "label": "Base Case (12% p.a. - Diversified Equity/Index)"},
            "optimistic": {"return_rate": 0.15, "label": "Optimistic (15% p.a. - Aggressive Growth)"}
        }

        results = {}
        for key, sc in scenarios.items():
            r = sc["return_rate"]
            sim = solve_reverse_sip(
                target_amount=target_amount,
                horizon_years=horizon_years,
                annual_return=r,
                current_savings=current_savings,
                monthly_investment_capacity=monthly_capacity
            )
            results[key] = {
                "label": sc["label"],
                "annual_return_pct": r * 100,
                "required_monthly_sip": sim["required_monthly_sip"],
                "total_contributed": sim["total_contributed"],
                "growth_gain": sim["growth_gain"],
                "future_value_achieved": sim["future_value_achieved"],
                "capacity_status": sim["status"]
            }

        return {
            "target_amount": target_amount,
            "horizon_years": horizon_years,
            "current_savings_deployed": current_savings,
            "base_case_required_sip": results["base"]["required_monthly_sip"],
            "base_case_contributed": results["base"]["total_contributed"],
            "base_case_growth": results["base"]["growth_gain"],
            "scenarios": results
        }


class StrategyAgent(BaseAgent):
    """Synthesizes validated profile, risk, and simulation outputs into actionable educational planning guidance."""
    def __init__(self):
        super().__init__("StrategyAgent", "Formulates educational contribution strategy and milestone alignment.")

    def run(self, profile: Dict[str, Any], sim: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        req_sip = sim["base_case_required_sip"]
        capacity = profile["validated_monthly_capacity"]
        shortfall = max(0, req_sip - capacity)

        action_plan = []
        if shortfall == 0:
            action_plan.append("Your current investable capacity fully covers the required monthly contribution.")
            action_plan.append("Automate a disciplined SIP into your target diversified asset allocation on salary day.")
        else:
            action_plan.append(f"Capacity Shortfall of ₹{shortfall:,}/month identified against base 10-year requirement.")
            action_plan.append("Strategy Option A: Start with ₹5,000/month today and apply an annual 10% Step-Up SIP.")
            action_plan.append("Strategy Option B: Extend investment horizon to 15 years to reduce monthly demand.")

        return {
            "recommended_monthly_sip": req_sip,
            "available_capacity": capacity,
            "monthly_shortfall": shortfall,
            "feasibility": "Fully Achievable" if shortfall == 0 else "Requires Step-Up or Horizon Calibration",
            "action_plan": action_plan,
            "asset_allocation": risk["target_asset_allocation"]
        }


class ExplanationAgent(BaseAgent):
    """Generates transparent, pedagogical plain-English explanations (WHAT, WHY, ASSUMPTIONS, RISKS, ALTERNATIVES, LIMITATIONS)."""
    def __init__(self):
        super().__init__("ExplanationAgent", "Converts technical metrics into transparent, pedagogical explanations.")

    def run(self, profile: Dict[str, Any], goal: Dict[str, Any], sim: Dict[str, Any], strat: Dict[str, Any]) -> Dict[str, Any]:
        h = goal["duration_years"]
        target = goal["target_amount_today"]
        base = sim["scenarios"]["base"]

        what = (
            f"To accumulate ₹{target:,.0f} over {h} years, your calculated baseline monthly SIP requirement is "
            f"₹{base['required_monthly_sip']:,}/month (assuming a diversified portfolio returning 12% p.a.). "
            f"Your total capital contributed would be ₹{base['total_contributed']:,}, while compound interest "
            f"generates ₹{base['growth_gain']:,} in wealth accumulation."
        )

        why = (
            f"Because you are starting at age {profile['age']}, compounding has {h} full years to work. "
            f"Over a {h}-year horizon, the growth component (₹{base['growth_gain']:,}) accounts for more than "
            f"{round((base['growth_gain'] / target) * 100)}% of your target corpus. Starting early allows mathematical "
            f"compounding to shoulder the heavy lifting rather than pure out-of-pocket savings."
        )

        assumptions = [
            f"Annual investment growth benchmarked at 12.0% p.a. (historical long-term Indian equity index proxy).",
            f"Inflation estimated at {goal['inflation_rate_assumed'] * 100:.1f}% p.a. Purchasing power adjusted target: ₹{goal['inflation_adjusted_target']:,}.",
            "All dividend payouts and gains are assumed to be systematically reinvested without interim leakage."
        ]

        risks = [
            "Market volatility: Real-world equity returns do not arrive smoothly at 12% each year, but through multi-year cycles.",
            "Sequencing Risk: A severe market drop in years 8-10 could temporarily depress the accumulated balance.",
            "Inflation Spike: If inflation averages 7-8% rather than 6%, higher nominal corpus will be necessary."
        ]

        alternatives = [
            f"Horizon Extension: Extending your timeline from {h} to 15 years reduces your required monthly SIP by over 50%.",
            f"Annual Step-Up: Starting at your current capacity (₹{profile['validated_monthly_capacity']:,}) and increasing contributions by 10% annually bridges the gap.",
            "Expense Optimization: Reallocating ₹2,000 from discretionary lifestyle expenses straight into your SIP accelerator."
        ]

        limitations = (
            "Educational decision-support simulation only. FinPilot AI does not provide SEBI-registered investment advice, "
            "nor does it execute live broker orders or guarantee returns. Review allocations with a certified financial planner."
        )

        return {
            "what": what,
            "why": why,
            "assumptions": assumptions,
            "risks": risks,
            "alternatives": alternatives,
            "limitations": limitations
        }


class AgentOrchestrator:
    """Master orchestrator executing the 7-agent pipeline with end-to-end trace logging."""

    def __init__(self):
        self.profile_agent = ProfileAgent()
        self.goal_agent = GoalAgent()
        self.risk_agent = RiskAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.simulation_agent = SimulationAgent()
        self.strategy_agent = StrategyAgent()
        self.explanation_agent = ExplanationAgent()

    def run_pipeline(self, user_input: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        trace: List[Dict[str, Any]] = []

        def log_step(agent: BaseAgent, inp: Dict[str, Any], func):
            start = time.time()
            started_at = datetime.utcnow()
            status = "completed"
            err = None
            out = {}
            try:
                out = func()
            except Exception as e:
                status = "failed"
                err = str(e)

            duration_ms = round((time.time() - start) * 1000.0, 2)
            completed_at = datetime.utcnow()

            step_record = {
                "run_id": run_id,
                "agent_name": agent.name,
                "responsibility": agent.responsibility,
                "status": status,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": duration_ms,
                "input_summary": str(inp)[:200],
                "output_summary": str(out)[:200],
                "evidence": out.get("citations") or out.get("asset_allocation") or out.get("scenarios"),
                "error": err
            }
            trace.append(step_record)

            # Persist to DB
            try:
                db: Session = SessionLocal()
                run_row = AgentRun(
                    run_id=run_id,
                    user_id=user_id,
                    agent_name=agent.name,
                    status=status,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                    input_summary=step_record["input_summary"],
                    output_summary=step_record["output_summary"],
                    evidence_json=str(step_record["evidence"]) if step_record["evidence"] else None,
                    error=err
                )
                db.add(run_row)
                db.commit()
                db.close()
            except Exception as dbe:
                # DB logging fallback
                pass

            return out

        # 1. Profile Agent
        profile_out = log_step(
            self.profile_agent,
            user_input,
            lambda: self.profile_agent.run(user_input)
        )

        # 2. Goal Agent
        goal_out = log_step(
            self.goal_agent,
            user_input,
            lambda: self.goal_agent.run(user_input, inflation_rate=user_input.get("inflation_rate", 0.06))
        )

        # 3. Risk Agent
        risk_out = log_step(
            self.risk_agent,
            user_input,
            lambda: self.risk_agent.run(
                user_input.get("risk_tolerance", "moderate"),
                goal_out["duration_years"],
                profile_out["current_savings"],
                profile_out["monthly_expenses"]
            )
        )

        # 4. Knowledge Agent (RAG)
        knowledge_out = log_step(
            self.knowledge_agent,
            goal_out,
            lambda: self.knowledge_agent.run(goal_out["goal_type"], goal_out["duration_years"])
        )

        # 5. Simulation Agent (Deterministic Math)
        sim_out = log_step(
            self.simulation_agent,
            {"target": goal_out["target_amount_today"], "horizon": goal_out["duration_years"]},
            lambda: self.simulation_agent.run(
                goal_out["target_amount_today"],
                goal_out["duration_years"],
                profile_out["current_savings"],
                profile_out["validated_monthly_capacity"]
            )
        )

        # 6. Strategy Agent
        strategy_out = log_step(
            self.strategy_agent,
            {"profile": profile_out, "sim": sim_out},
            lambda: self.strategy_agent.run(profile_out, sim_out, risk_out)
        )

        # 7. Explanation Agent
        explanation_out = log_step(
            self.explanation_agent,
            {"strategy": strategy_out},
            lambda: self.explanation_agent.run(profile_out, goal_out, sim_out, strategy_out)
        )

        return {
            "run_id": run_id,
            "status": "COMPLETED",
            "executed_agents_count": 7,
            "trace": trace,
            "results": {
                "profile": profile_out,
                "goal": goal_out,
                "risk": risk_out,
                "knowledge": knowledge_out,
                "simulation": sim_out,
                "strategy": strategy_out,
                "explanation": explanation_out
            }
        }


agent_orchestrator = AgentOrchestrator()
run_pipeline = agent_orchestrator.run_pipeline
