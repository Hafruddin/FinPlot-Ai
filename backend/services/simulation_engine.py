"""
FinPilot AI — Server-Authoritative Historical Simulation Engine
Guarantees Strict Anti-Future-Leakage Protection:
At simulation step T, the client receives historical data ONLY up to date T.
Future prices, return sequences, and macro events are strictly withheld.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    SimulationSession, SimulationOrder, SimulationPosition,
    CompanyEvent, User, UserFinancialIQ, IQActivityLedger
)
from backend.services.decision_quality_service import DecisionQualityService

# Curated Historical Scenarios with True Market Timelines
HISTORICAL_SCENARIOS = {
    "covid_shock_2020": {
        "id": "covid_shock_2020",
        "title": "March 2020 Covid Crash & Recovery",
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Ltd",
        "description": "Navigate the steepest crash in modern Indian market history followed by a massive liquidity-driven turnaround.",
        "difficulty": "Advanced",
        "market_theme": "Panic Downturn & Fast Rebound",
        "initial_cash": 100000.0,
        "timeline": [
            {"date": "2020-01-15", "price": 1520.0, "high": 1545.0, "low": 1510.0, "volume": 14200000, "condition": "NORMAL"},
            {"date": "2020-01-30", "price": 1485.0, "high": 1510.0, "low": 1475.0, "volume": 12800000, "condition": "NORMAL"},
            {"date": "2020-02-14", "price": 1460.0, "high": 1490.0, "low": 1450.0, "volume": 13500000, "condition": "NORMAL"},
            {"date": "2020-02-28", "price": 1360.0, "high": 1410.0, "low": 1340.0, "volume": 21000000, "condition": "VOLATILE"},
            {"date": "2020-03-09", "price": 1115.0, "high": 1240.0, "low": 1090.0, "volume": 38000000, "condition": "PANIC_DOWNTURN"},
            {"date": "2020-03-16", "price": 1015.0, "high": 1130.0, "low": 995.0,  "volume": 42000000, "condition": "PANIC_DOWNTURN"},
            {"date": "2020-03-23", "price": 880.0,  "high": 960.0,  "low": 867.0,  "volume": 58000000, "condition": "PANIC_DOWNTURN"},
            {"date": "2020-03-31", "price": 1050.0, "high": 1090.0, "low": 1010.0, "volume": 36000000, "condition": "VOLATILE"},
            {"date": "2020-04-15", "price": 1180.0, "high": 1210.0, "low": 1150.0, "volume": 29000000, "condition": "NORMAL"},
            {"date": "2020-04-22", "price": 1360.0, "high": 1400.0, "low": 1310.0, "volume": 45000000, "condition": "NORMAL"},
            {"date": "2020-05-15", "price": 1455.0, "high": 1480.0, "low": 1430.0, "volume": 24000000, "condition": "NORMAL"},
            {"date": "2020-06-15", "price": 1580.0, "high": 1610.0, "low": 1560.0, "volume": 22000000, "condition": "NORMAL"},
            {"date": "2020-07-15", "price": 1840.0, "high": 1870.0, "low": 1810.0, "volume": 26000000, "condition": "EUPHORIC_PEAK"},
            {"date": "2020-08-15", "price": 2110.0, "high": 2160.0, "low": 2080.0, "volume": 31000000, "condition": "EUPHORIC_PEAK"},
            {"date": "2020-09-15", "price": 2320.0, "high": 2369.0, "low": 2280.0, "volume": 29000000, "condition": "EUPHORIC_PEAK"}
        ],
        "events": [
            {"date": "2020-02-28", "headline": "WHO Raises Global Risk Alert to Very High", "content": "Global supply chains face severe friction as virus spreads to Europe and Asia."},
            {"date": "2020-03-09", "headline": "Black Monday: Crude Oil Collapses 30% & Circuit Breaker Triggered", "content": "OPEC+ talks collapse; Saudi initiates price war while equities sell off worldwide."},
            {"date": "2020-03-23", "headline": "Nationwide 21-Day Strict Lockdown Enacted Across India", "content": "Economic activity comes to an abrupt standstill. Sensex logs worst one-day drop of 3,934 points."},
            {"date": "2020-04-22", "headline": "Jio Platforms Raises ₹43,574 Crore from Meta (Facebook)", "content": "Meta acquires a 9.99% stake in Jio, bringing massive liquidity and debt elimination clarity."}
        ]
    },
    "tech_bull_2021": {
        "id": "tech_bull_2021",
        "title": "2021 Tech Super-Cycle & Cloud Migration",
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services",
        "description": "Manage capital through rapid digital transformation, cloud migrations, and tech hiring expansions.",
        "difficulty": "Intermediate",
        "market_theme": "Steady Growth & Value Appreciation",
        "initial_cash": 100000.0,
        "timeline": [
            {"date": "2021-01-10", "price": 3120.0, "high": 3175.0, "low": 3090.0, "volume": 3200000, "condition": "NORMAL"},
            {"date": "2021-02-15", "price": 3190.0, "high": 3230.0, "low": 3150.0, "volume": 2800000, "condition": "NORMAL"},
            {"date": "2021-03-20", "price": 3050.0, "high": 3110.0, "low": 3020.0, "volume": 3100000, "condition": "VOLATILE"},
            {"date": "2021-04-25", "price": 3100.0, "high": 3140.0, "low": 3070.0, "volume": 2900000, "condition": "NORMAL"},
            {"date": "2021-06-15", "price": 3280.0, "high": 3310.0, "low": 3250.0, "volume": 2500000, "condition": "NORMAL"},
            {"date": "2021-07-20", "price": 3200.0, "high": 3240.0, "low": 3170.0, "volume": 2700000, "condition": "NORMAL"},
            {"date": "2021-08-30", "price": 3720.0, "high": 3750.0, "low": 3680.0, "volume": 4800000, "condition": "EUPHORIC_PEAK"},
            {"date": "2021-09-30", "price": 3770.0, "high": 3810.0, "low": 3730.0, "volume": 4100000, "condition": "EUPHORIC_PEAK"},
            {"date": "2021-10-15", "price": 3650.0, "high": 3700.0, "low": 3610.0, "volume": 3500000, "condition": "VOLATILE"},
            {"date": "2021-12-15", "price": 3580.0, "high": 3630.0, "low": 3540.0, "volume": 3000000, "condition": "NORMAL"}
        ],
        "events": [
            {"date": "2021-01-10", "headline": "Q3 Profit Surges 7% on Robust Cloud Transformation Demand", "content": "TCS reports multi-billion dollar total contract value as enterprises migrate to AWS and Azure."},
            {"date": "2021-08-30", "headline": "IT Sector Leads Nifty to Historic 17,000 Milestone", "content": "Unprecedented demand for Indian engineering talent drives record earnings projections."}
        ]
    }
}


class SimulationEngine:
    """Orchestrates historical simulations with zero future data leakage."""

    @staticmethod
    def get_available_scenarios() -> List[Dict[str, Any]]:
        """Returns scenario summaries without leaking future price trajectories."""
        res = []
        for s_id, s_data in HISTORICAL_SCENARIOS.items():
            res.append({
                "id": s_id,
                "title": s_data["title"],
                "symbol": s_data["symbol"],
                "company_name": s_data["company_name"],
                "description": s_data["description"],
                "difficulty": s_data["difficulty"],
                "market_theme": s_data["market_theme"],
                "initial_cash": s_data["initial_cash"],
                "total_steps": len(s_data["timeline"]),
                "start_date": s_data["timeline"][0]["date"],
                "end_date": s_data["timeline"][-1]["date"]
            })
        return res

    @staticmethod
    def start_session(user_id: int, scenario_id: str, db: Session) -> Dict[str, Any]:
        """Initializes a new historical session at Step 0."""
        if scenario_id not in HISTORICAL_SCENARIOS:
            scenario_id = "covid_shock_2020"

        sc = HISTORICAL_SCENARIOS[scenario_id]
        session_id = f"sim_{uuid.uuid4().hex[:12]}"
        t0 = sc["timeline"][0]

        new_sess = SimulationSession(
            id=session_id,
            user_id=user_id,
            scenario_id=scenario_id,
            symbol=sc["symbol"],
            current_step_index=0,
            total_steps=len(sc["timeline"]),
            start_date=t0["date"],
            end_date=sc["timeline"][-1]["date"],
            current_date=t0["date"],
            initial_cash=sc["initial_cash"],
            cash_balance=sc["initial_cash"],
            status="ACTIVE",
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            decision_score_avg=0.0
        )
        db.add(new_sess)

        # Initialize empty position
        init_pos = SimulationPosition(
            session_id=session_id,
            symbol=sc["symbol"],
            quantity=0.0,
            avg_price=0.0
        )
        db.add(init_pos)
        db.commit()

        return SimulationEngine.get_session_state(session_id, db)

    @staticmethod
    def get_session_state(session_id: str, db: Session) -> Dict[str, Any]:
        """
        Returns session view with STRICT ANTI-FUTURE-LEAKAGE.
        Candles and events are filtered ONLY up to current_step_index.
        """
        sess = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
        if not sess:
            raise ValueError(f"Simulation session {session_id} not found")

        sc = HISTORICAL_SCENARIOS.get(sess.scenario_id, HISTORICAL_SCENARIOS["covid_shock_2020"])
        idx = sess.current_step_index
        total_steps = len(sc["timeline"])

        # Sliced historical prices up to step idx (strictly NO future dates)
        sliced_timeline = sc["timeline"][:idx + 1]
        current_candle = sliced_timeline[-1]

        # Events strictly on or before current date
        current_date = current_candle["date"]
        sliced_events = [ev for ev in sc["events"] if ev["date"] <= current_date]

        # Position and P&L
        pos = db.query(SimulationPosition).filter(SimulationPosition.session_id == session_id).first()
        qty = pos.quantity if pos else 0.0
        avg_p = pos.avg_price if pos else 0.0

        current_equity_val = qty * current_candle["price"]
        unrealized_pnl = (current_candle["price"] - avg_p) * qty if qty > 0 else 0.0
        total_portfolio_value = sess.cash_balance + current_equity_val

        # Orders history
        orders = db.query(SimulationOrder).filter(SimulationOrder.session_id == session_id).order_by(SimulationOrder.step_index.asc()).all()
        order_history = [
            {
                "step": o.step_index,
                "date": o.date,
                "action": o.action,
                "quantity": o.quantity,
                "price": o.price,
                "reasoning": o.reasoning,
                "decision_score": o.decision_score,
                "feedback": o.decision_feedback
            }
            for o in orders
        ]

        return {
            "session_id": sess.id,
            "scenario_id": sess.scenario_id,
            "scenario_title": sc["title"],
            "symbol": sess.symbol,
            "company_name": sc["company_name"],
            "current_step_index": idx,
            "total_steps": total_steps,
            "current_date": current_date,
            "current_price": current_candle["price"],
            "status": sess.status,
            "cash_balance": round(sess.cash_balance, 2),
            "position": {
                "quantity": qty,
                "avg_price": round(avg_p, 2),
                "current_equity_value": round(current_equity_val, 2),
                "unrealized_pnl": round(unrealized_pnl, 2)
            },
            "portfolio": {
                "total_value": round(total_portfolio_value, 2),
                "initial_cash": sc["initial_cash"],
                "total_pnl": round(sess.realized_pnl + unrealized_pnl, 2),
                "return_pct": round(((total_portfolio_value - sc["initial_cash"]) / sc["initial_cash"]) * 100.0, 2)
            },
            "decision_score_avg": round(sess.decision_score_avg, 1),
            "candles_revealed": sliced_timeline, # ZERO future leakage
            "events_revealed": sliced_events,     # ZERO future leakage
            "order_history": order_history
        }

    @staticmethod
    def execute_order(
        session_id: str,
        action: str, # BUY, SELL, HOLD, WAIT
        quantity: float,
        reasoning: str,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Executes a user order, runs DecisionQuality evaluation, updates cash & position,
        records in SimulationOrder, and updates user Financial IQ ledger.
        """
        sess = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
        if not sess:
            raise ValueError("Session not found")
        if sess.status != "ACTIVE":
            raise ValueError("Simulation session has already completed or been abandoned")

        sc = HISTORICAL_SCENARIOS[sess.scenario_id]
        current_candle = sc["timeline"][sess.current_step_index]
        curr_price = current_candle["price"]
        curr_condition = current_candle.get("condition", "NORMAL")

        pos = db.query(SimulationPosition).filter(SimulationPosition.session_id == session_id).first()
        current_qty = pos.quantity if pos else 0.0

        action = action.upper()
        if action not in ("BUY", "SELL", "HOLD", "WAIT"):
            action = "HOLD"

        # Validate order constraints
        if action == "BUY":
            cost = quantity * curr_price
            if cost > sess.cash_balance:
                raise ValueError(f"Insufficient virtual cash (Required: ₹{cost:,.2f}, Available: ₹{sess.cash_balance:,.2f})")
            # Update Position
            new_qty = current_qty + quantity
            new_avg = ((current_qty * pos.avg_price) + cost) / new_qty if new_qty > 0 else 0.0
            sess.cash_balance -= cost
            pos.quantity = new_qty
            pos.avg_price = new_avg

        elif action == "SELL":
            if quantity > current_qty:
                raise ValueError(f"Cannot sell {quantity} shares; you only hold {current_qty} shares")
            proceeds = quantity * curr_price
            realized = (curr_price - pos.avg_price) * quantity
            sess.cash_balance += proceeds
            sess.realized_pnl += realized
            pos.quantity = current_qty - quantity
            if pos.quantity == 0:
                pos.avg_price = 0.0

        # Evaluate Decision Quality
        dq_result = DecisionQualityService.evaluate_decision(
            action=action,
            quantity=quantity,
            price=curr_price,
            portfolio_cash=sess.cash_balance,
            portfolio_equity_val=pos.quantity * curr_price,
            risk_profile="moderate",
            reasoning=reasoning,
            market_condition=curr_condition
        )

        d_score = dq_result["decision_score"]

        # Record order
        order = SimulationOrder(
            session_id=session_id,
            step_index=sess.current_step_index,
            date=current_candle["date"],
            action=action,
            quantity=quantity,
            price=curr_price,
            reasoning=reasoning,
            decision_score=d_score,
            decision_feedback=dq_result["feedback"]
        )
        db.add(order)

        # Update average decision score on session
        prev_orders_count = db.query(SimulationOrder).filter(SimulationOrder.session_id == session_id).count()
        sess.decision_score_avg = ((sess.decision_score_avg * prev_orders_count) + d_score) / (prev_orders_count + 1)

        # Sync with Financial IQ Ledger: updates decision_discipline dimension
        user_iq = db.query(UserFinancialIQ).filter(UserFinancialIQ.user_id == user_id).first()
        if not user_iq:
            user_iq = UserFinancialIQ(user_id=user_id)
            db.add(user_iq)

        old_dec = user_iq.decision_discipline if user_iq.decision_discipline is not None else 6.0
        # Delta is small bounded nudge: e.g. score of 90 gives +0.2; score of 30 gives -0.2
        delta = round((d_score - 60.0) / 100.0, 2)
        new_dec = round(max(1.0, min(10.0, old_dec + delta)), 2)
        user_iq.decision_discipline = new_dec
        user_iq.updated_at = datetime.utcnow()

        ledger = IQActivityLedger(
            user_id=user_id,
            dimension="decision_discipline",
            delta=delta,
            old_score=old_dec,
            new_score=new_dec,
            reason=f"Simulation {sc['title']}: {action} Decision Quality ({d_score}/100)",
            evidence_json=f'{{"pillars": {dq_result["pillars"]}, "reasoning": "{reasoning}"}}'
        )
        db.add(ledger)
        db.commit()

        return {
            "order_status": "EXECUTED",
            "decision_quality": dq_result,
            "session": SimulationEngine.get_session_state(session_id, db)
        }

    @staticmethod
    def advance_step(session_id: str, db: Session) -> Dict[str, Any]:
        """Advances the historical timeline by 1 step."""
        sess = db.query(SimulationSession).filter(SimulationSession.id == session_id).first()
        if not sess:
            raise ValueError("Session not found")

        sc = HISTORICAL_SCENARIOS[sess.scenario_id]
        if sess.current_step_index + 1 < len(sc["timeline"]):
            sess.current_step_index += 1
            sess.current_date = sc["timeline"][sess.current_step_index]["date"]
        else:
            sess.status = "COMPLETED"

        db.commit()
        return SimulationEngine.get_session_state(session_id, db)
