import datetime
import os
import math
import random
import json
from typing import List, Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import engine, get_db
from backend.models import Base, User, LessonCompletion, UserGoal, AssetHolding, PaperHolding, FinancialFreedomPlan
from backend.auth import get_password_hash, verify_password, create_access_token, get_current_user
from backend.schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    LessonCompletionRequest, LessonCompletionResponse,
    GoalSaveRequest, GoalResponse, RebalanceRequest, RebalanceResponse, AssetHoldingResponse,
    HealthCheckRequest, PaperTradeRequest, PaperHoldingResponse, CopilotQueryRequest,
    FinancialFreedomCalculateRequest, FinancialFreedomPlanSaveRequest
)
from backend.services.financial_freedom_service import (
    calculate_cashflow,
    calculate_emergency_fund,
    calculate_financial_freedom,
    calculate_years_to_freedom,
    calculate_scenarios,
    calculate_readiness_score
)

# Root directory for serving static frontend files
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinPilot AI Core API", version="1.0.0")

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH ENDPOINTS ---

@app.post("/api/auth/signup", response_model=Token)
def signup(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # Hash password and create user
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        financial_iq=340
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return JWT token
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    # Return JWT token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- USER PROFILE & ACADEMY ---

@app.get("/api/user/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completions = db.query(LessonCompletion).filter(LessonCompletion.user_id == current_user.id).all()
    completed_ids = [c.lesson_id for c in completions]
    
    goal_data = None
    if current_user.goals:
        goal_data = {
            "goal_type": current_user.goals.goal_type,
            "target_amount": current_user.goals.target_amount,
            "duration_years": current_user.goals.duration_years,
            "monthly_capacity": current_user.goals.monthly_capacity,
            "savings_amount": current_user.goals.savings_amount,
            "risk_appetite": current_user.goals.risk_appetite
        }
        
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "financial_iq": current_user.financial_iq,
        "completed_lessons": completed_ids,
        "goals": goal_data
    }


@app.post("/api/user/lesson")
def complete_lesson(req: LessonCompletionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if already completed
    existing = db.query(LessonCompletion).filter(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.lesson_id == req.lesson_id
    ).first()
    
    if existing:
        return {"message": "Lesson already marked completed.", "financial_iq": current_user.financial_iq}
        
    # Record completion
    completion = LessonCompletion(user_id=current_user.id, lesson_id=req.lesson_id)
    db.add(completion)
    
    # Increment Financial IQ
    current_user.financial_iq = min(1000, current_user.financial_iq + 50)
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Lesson marked completed. Financial IQ increased!",
        "financial_iq": current_user.financial_iq,
        "lesson_id": req.lesson_id
    }


# --- FINANCIAL GOALS & WEALTH RECOMMENDATIONS ---

@app.post("/api/user/goal", response_model=GoalResponse)
def save_goal(goal_data: GoalSaveRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if goals already exist
    existing_goal = db.query(UserGoal).filter(UserGoal.user_id == current_user.id).first()
    
    if existing_goal:
        existing_goal.goal_type = goal_data.goal_type
        existing_goal.target_amount = goal_data.target_amount
        existing_goal.duration_years = goal_data.duration_years
        existing_goal.monthly_capacity = goal_data.monthly_capacity
        existing_goal.savings_amount = goal_data.savings_amount
        existing_goal.risk_appetite = goal_data.risk_appetite
        goal = existing_goal
    else:
        goal = UserGoal(
            user_id=current_user.id,
            goal_type=goal_data.goal_type,
            target_amount=goal_data.target_amount,
            duration_years=goal_data.duration_years,
            monthly_capacity=goal_data.monthly_capacity,
            savings_amount=goal_data.savings_amount,
            risk_appetite=goal_data.risk_appetite
        )
        db.add(goal)

    # Re-calculate default asset holdings for the user
    # Delete old holdings first
    db.query(AssetHolding).filter(AssetHolding.user_id == current_user.id).delete()
    
    allocations = []
    initial_value = goal_data.savings_amount + goal_data.monthly_capacity
    
    if goal_data.risk_appetite == "conservative":
        allocations = [
            {"asset_class": "Debt Mutual Funds", "weight": 70.0},
            {"asset_class": "Index Funds (Equity)", "weight": 20.0},
            {"asset_class": "Sovereign Gold Bonds", "weight": 10.0}
        ]
    elif goal_data.risk_appetite == "moderate":
        allocations = [
            {"asset_class": "Equity Index Funds", "weight": 50.0},
            {"asset_class": "Large Cap Stocks", "weight": 30.0},
            {"asset_class": "Gold / Commodities", "weight": 10.0},
            {"asset_class": "Liquid Cash / Debt Reserve", "weight": 10.0}
        ]
    else: # aggressive
        allocations = [
            {"asset_class": "Large & Mid-Cap Equity Funds", "weight": 70.0},
            {"asset_class": "Direct Growth Stocks", "weight": 20.0},
            {"asset_class": "Alternative Assets / Smallcap", "weight": 10.0}
        ]

    for alloc in allocations:
        holding = AssetHolding(
            user_id=current_user.id,
            asset_class=alloc["asset_class"],
            weight=alloc["weight"],
            current_value=(alloc["weight"] / 100.0) * initial_value
        )
        db.add(holding)

    db.commit()
    db.refresh(goal)
    return goal


# --- SIMULATION & PORTFOLIO ENGINE ---

@app.post("/api/portfolio/rebalance", response_model=RebalanceResponse)
def rebalance_portfolio(req: RebalanceRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Real DB modification - shifts 5% from stock risk categories to Gold / Cash safety assets
    holdings = db.query(AssetHolding).filter(AssetHolding.user_id == current_user.id).all()
    
    if not holdings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No portfolio holdings found. Please build a goal strategy first."
        )

    # Shift 5% from direct stocks or index equity to Gold/Cash
    reallocated_value = req.current_value * 1.012 # simulated 1.2% recovery
    
    # Adjust weights and values
    for h in holdings:
        if "Equity" in h.asset_class or "Stocks" in h.asset_class:
            h.weight = max(10, h.weight - 5)
        elif "Gold" in h.asset_class or "Cash" in h.asset_class or "Debt" in h.asset_class:
            h.weight += 5
            
        # Recalculate values based on new weights
        h.current_value = (h.weight / 100.0) * reallocated_value
        
    db.commit()
    
    # Query updated holdings
    updated_holdings = db.query(AssetHolding).filter(AssetHolding.user_id == current_user.id).all()
    response_holdings = [
        AssetHoldingResponse(
            asset_class=h.asset_class,
            weight=h.weight,
            current_value=h.current_value
        ) for h in updated_holdings
    ]
    
    return {
        "total_value": reallocated_value,
        "holdings": response_holdings,
        "message": "AI Rebalancing successful. Adjusted tech holdings into debt and gold."
    }


@app.get("/api/market/news")
def get_market_news(current_user: User = Depends(get_current_user)):
    # Generates custom alerts based on risk appetite
    try:
        risk = "moderate"
        if current_user.goals:
            risk = current_user.goals.risk_appetite
            
        alerts = [
            {
                "id": 1,
                "type": "info",
                "title": "Guardian Scan Completed",
                "desc": "Portfolio allocations are in line with risk parameters."
            }
        ]
        
        if risk == "aggressive" or risk == "moderate":
            alerts.insert(0, {
                "id": 2,
                "type": "warning",
                "title": "IT Sector Heavy Drag Detected",
                "desc": "Tech stocks index drops 6.2% on global correction. Rebalancing recommended."
            })
        elif risk == "conservative":
            alerts.insert(0, {
                "id": 3,
                "type": "info",
                "title": "Yield Spike Notice",
                "desc": "Short term debt yields have increased by 0.25%. Stabilizing portfolios."
            })
            
        return alerts
    except Exception:
        return [
            {
                "id": 0,
                "type": "info",
                "title": "Guardian Online",
                "desc": "Market monitoring is active. No critical alerts at this time."
            }
        ]


# --- PAPER TRADING PRACTICE MODE ---

@app.get("/api/paper-trading/portfolio")
def get_paper_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(PaperHolding).filter(PaperHolding.user_id == current_user.id).all()
    total_invested = sum(h.quantity * h.buy_price for h in holdings)
    current_value = sum(h.quantity * h.current_price for h in holdings)
    pnl = current_value - total_invested
    pnl_percent = (pnl / total_invested * 100) if total_invested > 0 else 0.0

    return {
        "cash": current_user.paper_cash or 100000.0,
        "total_value": (current_user.paper_cash or 100000.0) + current_value,
        "invested_value": total_invested,
        "current_holdings_value": current_value,
        "pnl": pnl,
        "pnl_percent": round(pnl_percent, 2),
        "holdings": [
            {
                "id": h.id,
                "symbol": h.symbol,
                "name": h.name,
                "quantity": h.quantity,
                "buy_price": h.buy_price,
                "current_price": h.current_price,
                "total_val": h.quantity * h.current_price,
                "gain": (h.current_price - h.buy_price) * h.quantity
            } for h in holdings
        ]
    }


@app.post("/api/paper-trading/trade")
def execute_paper_trade(req: PaperTradeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_cost = req.quantity * req.price

    if req.action.lower() == "buy":
        if current_user.paper_cash < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient practice capital.")
        
        current_user.paper_cash -= total_cost
        existing = db.query(PaperHolding).filter(
            PaperHolding.user_id == current_user.id,
            PaperHolding.symbol == req.symbol
        ).first()

        if existing:
            new_qty = existing.quantity + req.quantity
            new_avg = ((existing.quantity * existing.buy_price) + total_cost) / new_qty
            existing.quantity = new_qty
            existing.buy_price = new_avg
            existing.current_price = req.price
        else:
            stock_names = {
                "RELIANCE": "Reliance Industries Ltd",
                "TCS": "Tata Consultancy Services",
                "HDFCBANK": "HDFC Bank Ltd",
                "INFY": "Infosys Ltd",
                "ICICIBANK": "ICICI Bank Ltd",
                "TATAMOTORS": "Tata Motors Ltd",
                "ITC": "ITC Limited",
                "BHARTIARTL": "Bharti Airtel Ltd"
            }
            new_holding = PaperHolding(
                user_id=current_user.id,
                symbol=req.symbol,
                name=stock_names.get(req.symbol, req.symbol),
                quantity=req.quantity,
                buy_price=req.price,
                current_price=req.price
            )
            db.add(new_holding)
    elif req.action.lower() == "sell":
        existing = db.query(PaperHolding).filter(
            PaperHolding.user_id == current_user.id,
            PaperHolding.symbol == req.symbol
        ).first()
        if not existing or existing.quantity < req.quantity:
            raise HTTPException(status_code=400, detail="You do not own enough quantity to sell.")

        existing.quantity -= req.quantity
        current_user.paper_cash += total_cost
        if existing.quantity <= 0:
            db.delete(existing)
    else:
        raise HTTPException(status_code=400, detail="Invalid trade action.")

    db.commit()
    db.refresh(current_user)
    return {"message": f"Successfully executed {req.action.upper()} for {req.symbol}", "cash": current_user.paper_cash}


@app.post("/api/paper-trading/reset")
def reset_paper_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(PaperHolding).filter(PaperHolding.user_id == current_user.id).delete()
    current_user.paper_cash = 100000.0
    db.commit()
    return {"message": "Practice capital reset to ₹1,00,000"}


# --- EDUCATIONAL FINANCIAL HEALTH ASSESSMENT ---

@app.post("/api/health-check")
def calculate_health_check(req: HealthCheckRequest):
    savings_rate = max(0, ((req.monthly_income - req.monthly_expenses) / req.monthly_income * 100)) if req.monthly_income > 0 else 0
    emergency_months = (req.emergency_savings / req.monthly_expenses) if req.monthly_expenses > 0 else 0

    # Educational metric calculations (0-100 scale)
    savings_score = min(100, int((savings_rate / 30) * 100))
    emergency_score = min(100, int((emergency_months / 6) * 100))
    risk_score = 75 if req.risk_comfort in ["moderate", "balanced"] else (85 if req.risk_comfort == "aggressive" else 60)
    goal_score = 80 if req.horizon_years >= 5 else 65
    discipline_score = min(100, int((req.existing_investments / (req.monthly_income * 6 + 1)) * 100))

    overall = int((savings_score * 0.25) + (emergency_score * 0.25) + (risk_score * 0.20) + (goal_score * 0.15) + (discipline_score * 0.15))
    rating = "Excellent" if overall >= 80 else ("Good" if overall >= 65 else "Developing")

    return {
        "overall_score": overall,
        "rating": rating,
        "breakdown": {
            "knowledge": 70,
            "savings": savings_score,
            "risk_readiness": risk_score,
            "goal_clarity": goal_score,
            "investment_discipline": discipline_score
        },
        "insights": [
            f"Your savings rate is {savings_rate:.1f}%. Aim for 20-30% monthly allocation.",
            f"Emergency fund covers {emergency_months:.1f} months of expenses. Ideal buffer is 6 months.",
            "Complete 2 Academy lessons to increase your Knowledge readiness to 85+."
        ]
    }


# --- MARKETS, REAL-TIME DATA & PLAIN-ENGLISH STOCK EXPLAINER ---

ALL_STOCKS_DATA = [
    {
        "symbol": "NIFTY 50",
        "name": "NIFTY 50 Index",
        "sector": "Benchmark Index",
        "price": 24180.60,
        "change": 194.50,
        "change_percent": 0.81,
        "open": 24050.20,
        "high": 24220.45,
        "low": 24020.10,
        "prev_close": 23986.10,
        "volume": 328450000,
        "market_cap": "₹185L Cr",
        "pe": 22.4,
        "eps": 1079.5,
        "range_52w_low": 19223.40,
        "range_52w_high": 26277.35,
        "beta": 1.0,
        "is_index": True,
        "nse_symbol": "^NSEI",
        "bse_code": "NIFTY50"
    },
    {
        "symbol": "SENSEX",
        "name": "BSE SENSEX 30",
        "sector": "Benchmark Index",
        "price": 79243.18,
        "change": 576.34,
        "change_percent": 0.73,
        "open": 78850.00,
        "high": 79380.20,
        "low": 78790.60,
        "prev_close": 78666.84,
        "volume": 142100000,
        "market_cap": "₹150L Cr",
        "pe": 23.1,
        "eps": 3430.4,
        "range_52w_low": 63583.05,
        "range_52w_high": 85978.25,
        "beta": 0.98,
        "is_index": True,
        "nse_symbol": "^BSESN",
        "bse_code": "500001"
    },
    {
        "symbol": "BANK NIFTY",
        "name": "NIFTY Bank Index",
        "sector": "Banking Index",
        "price": 51432.10,
        "change": -186.20,
        "change_percent": -0.36,
        "open": 51680.00,
        "high": 51790.30,
        "low": 51320.40,
        "prev_close": 51618.30,
        "volume": 182300000,
        "market_cap": "₹45L Cr",
        "pe": 16.2,
        "eps": 3174.8,
        "range_52w_low": 43500.00,
        "range_52w_high": 54467.35,
        "beta": 1.15,
        "is_index": True,
        "nse_symbol": "^NSEBANK",
        "bse_code": "BANKNIFTY"
    },
    {
        "symbol": "RELIANCE",
        "name": "Reliance Industries Ltd",
        "sector": "Energy & Retail",
        "price": 2980.50,
        "change": 42.50,
        "change_percent": 1.45,
        "open": 2945.00,
        "high": 2994.00,
        "low": 2938.10,
        "prev_close": 2938.00,
        "volume": 6842300,
        "market_cap": "₹20.1L Cr",
        "pe": 26.4,
        "eps": 112.8,
        "range_52w_low": 2220.00,
        "range_52w_high": 3025.00,
        "beta": 1.05,
        "is_index": False,
        "nse_symbol": "RELIANCE",
        "bse_code": "500325"
    },
    {
        "symbol": "TCS",
        "name": "Tata Consultancy Services",
        "sector": "IT Services",
        "price": 4120.00,
        "change": -35.20,
        "change_percent": -0.85,
        "open": 4165.00,
        "high": 4178.50,
        "low": 4105.00,
        "prev_close": 4155.20,
        "volume": 2451000,
        "market_cap": "₹14.9L Cr",
        "pe": 31.2,
        "eps": 132.0,
        "range_52w_low": 3310.00,
        "range_52w_high": 4585.00,
        "beta": 0.78,
        "is_index": False,
        "nse_symbol": "TCS",
        "bse_code": "532540"
    },
    {
        "symbol": "HDFCBANK",
        "name": "HDFC Bank Ltd",
        "sector": "Banking & Finance",
        "price": 1640.25,
        "change": 9.80,
        "change_percent": 0.60,
        "open": 1632.00,
        "high": 1648.50,
        "low": 1628.00,
        "prev_close": 1630.45,
        "volume": 12890000,
        "market_cap": "₹12.5L Cr",
        "pe": 18.5,
        "eps": 88.6,
        "range_52w_low": 1360.00,
        "range_52w_high": 1794.00,
        "beta": 0.95,
        "is_index": False,
        "nse_symbol": "HDFCBANK",
        "bse_code": "500180"
    },
    {
        "symbol": "INFY",
        "name": "Infosys Ltd",
        "sector": "IT Services",
        "price": 1785.10,
        "change": -21.60,
        "change_percent": -1.20,
        "open": 1810.00,
        "high": 1815.00,
        "low": 1776.00,
        "prev_close": 1806.70,
        "volume": 5670000,
        "market_cap": "₹7.4L Cr",
        "pe": 27.8,
        "eps": 64.2,
        "range_52w_low": 1350.00,
        "range_52w_high": 1990.00,
        "beta": 0.88,
        "is_index": False,
        "nse_symbol": "INFY",
        "bse_code": "500209"
    },
    {
        "symbol": "ICICIBANK",
        "name": "ICICI Bank Ltd",
        "sector": "Banking & Finance",
        "price": 1210.80,
        "change": 24.90,
        "change_percent": 2.10,
        "open": 1190.00,
        "high": 1218.00,
        "low": 1188.00,
        "prev_close": 1185.90,
        "volume": 9430000,
        "market_cap": "₹8.5L Cr",
        "pe": 17.1,
        "eps": 70.8,
        "range_52w_low": 910.00,
        "range_52w_high": 1330.00,
        "beta": 1.12,
        "is_index": False,
        "nse_symbol": "ICICIBANK",
        "bse_code": "532174"
    },
    {
        "symbol": "SBIN",
        "name": "State Bank of India",
        "sector": "Banking & Finance",
        "price": 815.40,
        "change": 11.20,
        "change_percent": 1.39,
        "open": 806.00,
        "high": 821.50,
        "low": 803.20,
        "prev_close": 804.20,
        "volume": 18500000,
        "market_cap": "₹7.3L Cr",
        "pe": 10.8,
        "eps": 75.5,
        "range_52w_low": 555.00,
        "range_52w_high": 912.00,
        "beta": 1.25,
        "is_index": False,
        "nse_symbol": "SBIN",
        "bse_code": "500112"
    },
    {
        "symbol": "TATAMOTORS",
        "name": "Tata Motors Ltd",
        "sector": "Automobile",
        "price": 985.40,
        "change": 32.40,
        "change_percent": 3.40,
        "open": 958.00,
        "high": 992.00,
        "low": 955.00,
        "prev_close": 953.00,
        "volume": 11200000,
        "market_cap": "₹3.6L Cr",
        "pe": 11.6,
        "eps": 84.9,
        "range_52w_low": 610.00,
        "range_52w_high": 1179.00,
        "beta": 1.38,
        "is_index": False,
        "nse_symbol": "TATAMOTORS",
        "bse_code": "500570"
    },
    {
        "symbol": "ITC",
        "name": "ITC Limited",
        "sector": "FMCG",
        "price": 495.20,
        "change": 1.70,
        "change_percent": 0.35,
        "open": 494.00,
        "high": 498.00,
        "low": 492.50,
        "prev_close": 493.50,
        "volume": 14200000,
        "market_cap": "₹6.1L Cr",
        "pe": 28.1,
        "eps": 17.6,
        "range_52w_low": 399.00,
        "range_52w_high": 525.00,
        "beta": 0.65,
        "is_index": False,
        "nse_symbol": "ITC",
        "bse_code": "500875"
    },
    {
        "symbol": "BHARTIARTL",
        "name": "Bharti Airtel Ltd",
        "sector": "Telecom",
        "price": 1580.60,
        "change": 22.40,
        "change_percent": 1.44,
        "open": 1562.00,
        "high": 1588.00,
        "low": 1558.00,
        "prev_close": 1558.20,
        "volume": 4900000,
        "market_cap": "₹9.2L Cr",
        "pe": 54.2,
        "eps": 29.1,
        "range_52w_low": 890.00,
        "range_52w_high": 1780.00,
        "beta": 0.82,
        "is_index": False,
        "nse_symbol": "BHARTIARTL",
        "bse_code": "532454"
    },
    {
        "symbol": "LT",
        "name": "Larsen & Toubro Ltd",
        "sector": "Infrastructure & Capital Goods",
        "price": 3610.40,
        "change": 28.50,
        "change_percent": 0.80,
        "open": 3590.00,
        "high": 3635.00,
        "low": 3575.00,
        "prev_close": 3581.90,
        "volume": 2100000,
        "market_cap": "₹4.9L Cr",
        "pe": 34.5,
        "eps": 104.6,
        "range_52w_low": 2880.00,
        "range_52w_high": 3948.00,
        "beta": 1.08,
        "is_index": False,
        "nse_symbol": "LT",
        "bse_code": "500510"
    }
]

@app.get("/api/markets/status")
def get_market_status():
    """Returns current Indian market status (IST) and server timestamp."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
    
    # NSE/BSE trading days: Monday (0) to Friday (4)
    # Market hours: 09:15 to 15:30 IST
    weekday = ist_now.weekday()
    hour = ist_now.hour
    minute = ist_now.minute
    total_minutes = hour * 60 + minute
    
    market_open = (weekday < 5) and (9 * 60 + 15 <= total_minutes <= 15 * 60 + 30)
    
    status_str = "Market Open" if market_open else "Market Closed"
    time_str = ist_now.strftime("%H:%M:%S IST")
    date_str = ist_now.strftime("%d %b %Y")
    
    return {
        "status": status_str,
        "is_open": market_open,
        "time": time_str,
        "date": date_str,
        "exchange": "NSE / BSE",
        "data_mode": "Live Feed (Simulation Supported)",
        "last_updated": time_str
    }

@app.get("/api/markets/stocks")
def get_stocks_list():
    """Returns all tracked indices and equities with real-time style metrics."""
    return ALL_STOCKS_DATA

@app.get("/api/markets/search")
def search_stocks(q: str = Query("", description="Search term for symbol, name, or sector")):
    """Filters stocks by symbol, company name, or sector."""
    term = q.strip().lower()
    if not term:
        return ALL_STOCKS_DATA
    return [
        s for s in ALL_STOCKS_DATA
        if term in s["symbol"].lower() or term in s["name"].lower() or term in s["sector"].lower()
    ]

@app.get("/api/markets/stock/{symbol}/history")
def get_stock_history(symbol: str, timeframe: str = Query("1M", alias="range", pattern="^(1D|1W|1M|3M|6M|1Y|5Y)$"), interval: Optional[str] = None):
    """
    Generates realistic historical OHLC candlesticks + volume data
    tailored to the specific asset's baseline price and volatility.
    """
    sym = symbol.upper()
    stock = next((s for s in ALL_STOCKS_DATA if s["symbol"] == sym), None)
    base_price = stock["price"] if stock else 1500.0
    volatility = 0.012 if ("Index" in (stock.get("sector","") if stock else "")) else 0.018

    # Determine number of candles and date steps
    now = datetime.datetime.now(datetime.timezone.utc)
    range_config = {
        "1D": {"points": 45, "step_minutes": 5, "vol": 0.003},
        "1W": {"points": 35, "step_hours": 2, "vol": 0.007},
        "1M": {"points": 30, "step_days": 1, "vol": 0.014},
        "3M": {"points": 65, "step_days": 1, "vol": 0.016},
        "6M": {"points": 90, "step_days": 2, "vol": 0.019},
        "1Y": {"points": 120, "step_days": 3, "vol": 0.022},
        "5Y": {"points": 180, "step_days": 10, "vol": 0.035},
    }
    cfg = range_config.get(timeframe, range_config["1M"])
    points = cfg["points"]
    vol = cfg["vol"]

    candles = []
    # Work backwards from now to determine timestamps, then generate smooth price drift
    times = []
    curr = now
    for i in range(points):
        if "step_minutes" in cfg:
            curr = curr - datetime.timedelta(minutes=cfg["step_minutes"])
            time_str = curr.strftime("%H:%M")
        elif "step_hours" in cfg:
            curr = curr - datetime.timedelta(hours=cfg["step_hours"])
            time_str = curr.strftime("%d %b %H:%M")
        else:
            curr = curr - datetime.timedelta(days=cfg["step_days"])
            time_str = curr.strftime("%d %b %Y")
        times.append(time_str)
    times.reverse()

    # Generate random walk with mean-reversion around base_price
    # Seed based on symbol and timeframe for consistent charting across calls
    rng = random.Random(hash(f"{sym}_{timeframe}"))
    p = base_price * (1.0 - (rng.uniform(-0.08, 0.08)))
    
    for i in range(points):
        # Progress towards current price near the end
        target_pull = (base_price - p) * (0.05 + 0.95 * (i / points))
        delta = (rng.gauss(0, vol) * p) + (target_pull * 0.15)
        o = round(p, 2)
        c = round(max(10.0, p + delta), 2)
        h = round(max(o, c) + abs(rng.gauss(0, vol * 0.6) * p), 2)
        l = round(min(o, c) - abs(rng.gauss(0, vol * 0.6) * p), 2)
        volume = int(abs(rng.gauss(150000, 50000)) + abs(c - o) * 10000)
        
        candles.append({
            "time": times[i],
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": volume
        })
        p = c

    # Ensure last candle close strictly equals current price
    if candles:
        candles[-1]["close"] = round(base_price, 2)
        if candles[-1]["high"] < base_price:
            candles[-1]["high"] = round(base_price * 1.002, 2)
        if candles[-1]["low"] > base_price:
            candles[-1]["low"] = round(base_price * 0.998, 2)

    return {
        "symbol": sym,
        "range": range,
        "base_price": base_price,
        "candle_count": len(candles),
        "candles": candles
    }

@app.get("/api/markets/stock/{symbol}/explain")
def explain_stock(symbol: str):
    """Detailed plain-English breakdown of business model, risks, and beginner insights."""
    sym = symbol.upper()
    explainers = {
        "NIFTY 50": {
            "symbol": "NIFTY 50",
            "name": "NIFTY 50 Benchmark Index",
            "what_they_do": "India's premier benchmark stock market index representing 50 of the largest and most liquid Indian companies listed on the National Stock Exchange (NSE).",
            "how_they_make_money": "As an index, it does not earn revenue directly. It tracks the collective market capitalization and economic prosperity of India's leading industrial engines (HDFC, Reliance, TCS, etc.).",
            "growth_drivers": "Broad Indian GDP growth, corporate earnings expansion across 13 economic sectors, and systematic inflows from retail SIPs and global institutional funds.",
            "major_risks": "Global geopolitical crises, macroeconomic inflation spikes, crude oil volatility, and broad institutional sell-offs.",
            "valuation_basics": "Historically trades around 20–24 P/E ratio. Buying an index fund tracking Nifty 50 gives you diversified exposure to 50 giant corporations at ultra-low cost.",
            "beginner_takeaway": "Instead of picking individual stocks, buying a Nifty 50 Index Fund is widely considered the safest, lowest-cost foundation for wealth creation in India.",
            "things_to_learn": ["Free-Float Market Capitalization", "Index Weightage", "Tracking Error"]
        },
        "SENSEX": {
            "symbol": "SENSEX",
            "name": "BSE SENSEX 30 Benchmark",
            "what_they_do": "The oldest stock index in India, tracking 30 financially sound, blue-chip companies listed on the Bombay Stock Exchange (BSE) since 1979.",
            "how_they_make_money": "Reflects the weighted performance of India's top 30 corporate giants across finance, IT, energy, consumer, and auto.",
            "growth_drivers": "Domestic consumption expansion, industrialization, formalization of the economy, and long-term corporate compounding.",
            "major_risks": "Higher concentration risk compared to Nifty 50 because it holds only 30 companies instead of 50.",
            "valuation_basics": "Tracks closely with Nifty 50 valuation metrics, offering a reliable gauge of India's blue-chip corporate health.",
            "beginner_takeaway": "A reliable barometer of the Indian economy. If India's economy is doing well over a 10-year period, Sensex almost always tracks it upward.",
            "things_to_learn": ["Base Year Valuation (1978-79 = 100)", "Blue Chip Stocks", "Market Capitalization"]
        },
        "RELIANCE": {
            "symbol": "RELIANCE",
            "name": "Reliance Industries Ltd",
            "what_they_do": "India's most valuable enterprise, operating across oil refining & petrochemicals, telecom & digital services (Jio with 470M+ subscribers), retail stores (Reliance Retail), and clean energy.",
            "how_they_make_money": "Refines crude oil into diesel and aviation fuel; collects monthly data/voice subscription fees from Jio users; earns retail margins across 18,000+ stores nationwide.",
            "growth_drivers": "5G monetization, enterprise digital cloud partnerships, retail footprint expansion, and multi-billion dollar giga-factories for solar & green hydrogen.",
            "major_risks": "Global crude oil refining margin dips, heavy capital expenditure debt cycles, and government regulatory shifts in telecom spectrum or energy exports.",
            "valuation_basics": "Evaluated on a 'Sum-of-the-Parts' (SOTP) basis because its oil, retail, and telecom segments have completely different valuation multiples.",
            "beginner_takeaway": "Reliance is a gigantic conglomerate. When you buy Reliance, you are effectively buying a slice of India's energy, digital, and consumer retail sectors combined.",
            "things_to_learn": ["Sum-of-the-Parts (SOTP)", "ARPU (Average Revenue Per User)", "Gross Refining Margin (GRM)"]
        },
        "TCS": {
            "symbol": "TCS",
            "name": "Tata Consultancy Services",
            "what_they_do": "Global IT services, digital transformation, and consulting flagship of the Tata Group, employing over 600,000 technology professionals worldwide.",
            "how_they_make_money": "Bills Fortune 500 banks, retailers, and airlines for cloud migration, cybersecurity, custom software engineering, and AI automation systems.",
            "growth_drivers": "Corporate AI modernization deals, large enterprise cloud transformations, steady client retention, and massive multi-year deal pipelines (TCV).",
            "major_risks": "Economic recessions in the US and Europe causing corporate clients to freeze or delay IT budgets; rupee-dollar currency fluctuation; IT wage inflation.",
            "valuation_basics": "Commands a premium valuation due to exceptional corporate governance, near zero debt, high Return on Equity (ROE > 45%), and consistent dividends.",
            "beginner_takeaway": "TCS is a mature cash-generating powerhouse. It is less volatile than high-growth tech startups and regularly rewards shareholders with buybacks and dividends.",
            "things_to_learn": ["Operating Margin", "Total Contract Value (TCV)", "Attrition Rate"]
        },
        "HDFCBANK": {
            "symbol": "HDFCBANK",
            "name": "HDFC Bank Ltd",
            "what_they_do": "India's largest private sector bank, delivering personal loans, credit cards, mortgages, business loans, and digital banking to over 100 million customers.",
            "how_they_make_money": "Accepts deposits at lower interest rates (saving/fixed accounts) and lends to borrowers at higher interest rates. The difference is called Net Interest Income (NII).",
            "growth_drivers": "Post-merger branch network expansion into semi-urban and rural India, digital lending apps, and wealth management services.",
            "major_risks": "Asset quality risks (unpaid loans / NPAs) during economic downturns, and margin pressure if borrowing costs rise faster than loan yields.",
            "valuation_basics": "Banks are valued using Price-to-Book (P/B) ratio and Return on Assets (RoA). HDFC Bank historically generates industry-leading asset quality.",
            "beginner_takeaway": "Banking is the bloodstream of any modern economy. HDFC Bank is widely considered India's most disciplined private lender.",
            "things_to_learn": ["NPA (Non-Performing Assets)", "NIM (Net Interest Margin)", "CASA Ratio (Current & Savings Account)"]
        },
        "INFY": {
            "symbol": "INFY",
            "name": "Infosys Ltd",
            "what_they_do": "India's pioneer in enterprise software consulting and IT outsourcing, serving clients across North America, Europe, and Asia-Pacific.",
            "how_they_make_money": "Generates revenue through technical consulting, cloud engineering, enterprise ERP deployments, and digital transformation contracts.",
            "growth_drivers": "Generative AI enterprise platform (Infosys Topaz), cloud platform (Infosys Cobalt), and expanding European presence.",
            "major_risks": "US tech budget cutbacks, competitive pricing pressure, and visa/immigration policy changes in Western markets.",
            "valuation_basics": "Trades at a reasonable P/E multiple relative to long-term earnings growth, supported by steady dividend payouts.",
            "beginner_takeaway": "A reliable technology blue-chip with transparent governance and strong international export revenues.",
            "things_to_learn": ["Digital Revenue Share", "Free Cash Flow Conversion", "Billable Utilization Rate"]
        },
        "ICICIBANK": {
            "symbol": "ICICIBANK",
            "name": "ICICI Bank Ltd",
            "what_they_do": "One of India's top 2 private sector banks, recognized for rapid digital adoption (iMobile app), consumer lending, and retail mortgages.",
            "how_they_make_money": "Earns Net Interest Income through personal and commercial loans, alongside non-interest fee income from credit cards, mutual fund distribution, and forex.",
            "growth_drivers": "Superior digital customer acquisition, robust Return on Equity (ROE > 18%), and low credit costs with pristine underwriting standards.",
            "major_risks": "Macroeconomic credit cycles, interest rate changes by the Reserve Bank of India (RBI), and competitive deposit pricing.",
            "valuation_basics": "Trades at attractive valuation multiples backed by rapid earnings compounding over recent financial years.",
            "beginner_takeaway": "A high-momentum private bank that has transformed into one of India's most profitable financial institutions.",
            "things_to_learn": ["Return on Equity (ROE)", "Cost of Funds", "Provision Coverage Ratio (PCR)"]
        },
        "TATAMOTORS": {
            "symbol": "TATAMOTORS",
            "name": "Tata Motors Ltd",
            "what_they_do": "Leading automobile manufacturer producing passenger cars, electric vehicles (Tata.ev), commercial trucks, and global luxury brands Jaguar & Land Rover (JLR).",
            "how_they_make_money": "Designs and sells commercial freight trucks, passenger SUVs (Nexon, Harrier, Safari), electric vehicles, and luxury JLR vehicles worldwide.",
            "growth_drivers": "Electric vehicle market leadership in India (>70% passenger EV market share), strong JLR order book, and commercial fleet modernization.",
            "major_risks": "Cyclical nature of the automotive sector, raw material cost inflation (steel, lithium), and luxury car demand softness in China/Europe.",
            "valuation_basics": "Valued using Enterprise Value-to-EBITDA (EV/EBITDA) and net debt reduction progress across domestic and overseas divisions.",
            "beginner_takeaway": "An automotive turnaround success story with high growth upside in clean electric mobility, but subject to economic cycles.",
            "things_to_learn": ["Cyclical Stocks", "Operating Leverage", "EV Adoption Curve"]
        },
        "ITC": {
            "symbol": "ITC",
            "name": "ITC Limited",
            "what_they_do": "Diversified Indian conglomerate with operations spanning FMCG foods (Aashirvaad, Sunfeast), cigarettes, luxury hotels, paperboards, and agribusiness.",
            "how_they_make_money": "Generates immense cash flow from its tobacco leadership, which funds its high-growth branded packaged foods, personal care, and hotels business.",
            "growth_drivers": "Scale economies in FMCG brands, demerger of the hotel business to unlock shareholder value, and agricultural supply chain exports.",
            "major_risks": "Government excise taxes on tobacco products and intense FMCG competition from multinational rivals.",
            "valuation_basics": "Valued for steady defensive cash flows, high dividend yield (~3-4%), and substantial return on capital employed (ROCE).",
            "beginner_takeaway": "A defensive, cash-rich stock often chosen by conservative investors seeking capital preservation and steady dividend income.",
            "things_to_learn": ["Dividend Yield", "Defensive Stocks", "Cash Conversion Cycle"]
        }
    }

    if sym in explainers:
        return explainers[sym]
    
    # Smart fallback for other stocks
    st = next((s for s in ALL_STOCKS_DATA if s["symbol"] == sym), None)
    name = st["name"] if st else f"{sym} Corporation"
    sector = st["sector"] if st else "Commercial Industry"
    
    return {
        "symbol": sym,
        "name": name,
        "what_they_do": f"{name} is a leading enterprise operating in India's {sector} sector.",
        "how_they_make_money": "Generates revenue through product sales, long-term commercial supply contracts, and specialized industry services.",
        "growth_drivers": f"Rising domestic demand in the {sector} space, capacity expansion, and continuous operational efficiency improvements.",
        "major_risks": "Sectoral demand fluctuations, raw material price inflation, and broader economic cycles.",
        "valuation_basics": f"Evaluated based on price-to-earnings (P/E) multiples and quarterly earnings growth relative to peer competitors in the {sector} sector.",
        "beginner_takeaway": f"Before investing in {sym}, ensure you understand its industry position, debt levels, and how it performs in different market conditions.",
        "things_to_learn": ["Price to Earnings (P/E)", "Operating Margin", "Earnings Per Share (EPS)"]
    }

@app.get("/api/markets/news")
def get_market_news(category: Optional[str] = None):
    """Returns curated financial news covering markets, economy, stocks, and mutual funds."""
    all_news = [
        {
            "id": 1,
            "category": "Markets",
            "headline": "Nifty 50 approaches record high amid steady domestic institutional inflows",
            "source": "Economic Times",
            "time": "25 mins ago",
            "summary": "Benchmark indices gained ground today led by private banking and energy majors. Systematic investment plan (SIP) monthly flows hit a new all-time high of ₹23,500 Crore."
        },
        {
            "id": 2,
            "category": "Economy",
            "headline": "RBI keeps repo rate unchanged at 6.5%, projects 7.2% annual GDP growth",
            "source": "Livemint",
            "time": "1 hour ago",
            "summary": "The Monetary Policy Committee maintained its stance focused on withdrawal of accommodation to ensure inflation aligns durably with the 4% medium-term target."
        },
        {
            "id": 3,
            "category": "Stocks",
            "headline": "Tata Motors expands EV charging network partnerships ahead of festive season",
            "source": "Moneycontrol",
            "time": "2 hours ago",
            "summary": "Tata Passenger Electric Mobility announced strategic tie-ups with oil marketing companies to establish 10,000 public fast chargers across India by 2026."
        },
        {
            "id": 4,
            "category": "Mutual Funds",
            "headline": "Flexi-cap and Multi-cap funds lead equity mutual fund net inflows this quarter",
            "source": "Bloomberg Quint",
            "time": "3 hours ago",
            "summary": "Financial advisors recommend diversified equity fund categories over thematic funds for new retail investors seeking disciplined long-term capital compounding."
        },
        {
            "id": 5,
            "category": "Stocks",
            "headline": "Reliance Retail reports double-digit footfall growth and digital commerce expansion",
            "source": "Financial Express",
            "time": "4 hours ago",
            "summary": "India's largest retailer registered significant grocery and consumer electronics volume growth supported by expanding Tier-2 and Tier-3 store presence."
        },
        {
            "id": 6,
            "category": "Markets",
            "headline": "Foreign institutional investors turn net buyers in Indian equities after three-week pause",
            "source": "Business Standard",
            "time": "5 hours ago",
            "summary": "Global funds invested ₹3,400 Crore in cash market equities today as macroeconomic indicators and corporate margin expansions remain resilient."
        }
    ]
    if category and category.lower() != "all":
        filtered = [n for n in all_news if n["category"].lower() == category.lower()]
        return filtered if filtered else all_news
    return all_news


# --- FINPILOT COPILOT CONTEXT-AWARE ASSISTANT ---

@app.post("/api/copilot/chat")
def copilot_chat(req: CopilotQueryRequest, current_user: User = Depends(get_current_user)):
    msg = req.message.lower()
    
    if "sip" in msg or "lumpsum" in msg:
        reply = (
            "A **SIP (Systematic Investment Plan)** allows you to invest a fixed amount regularly (e.g., monthly), "
            "benefiting from rupee cost averaging and compounding. A **Lumpsum** is a one-time single investment. "
            "For beginners, SIP reduces the risk of market timing!"
        )
    elif "risk" in msg or "diversif" in msg:
        reply = (
            "Diversification means not putting all your eggs in one basket. Splitting capital across Equity (growth), "
            "Debt (stability), and Gold (inflation hedge) protects your total portfolio when one market dips."
        )
    elif "stock" in msg or "share" in msg:
        reply = (
            "A stock represents partial ownership in a business. Before buying any stock, understand how the company "
            "makes money, its growth drivers, and its major risks—never buy based solely on price momentum."
        )
    elif "goal" in msg or "plan" in msg:
        target = current_user.goals.target_amount if current_user.goals else 5000000
        reply = f"Your current target goal is ₹{target:,.0f}. To stay on track, maintain consistent monthly contributions and review your asset allocation annually."
    elif "pe" in msg or "ratio" in msg or "valuation" in msg:
        reply = (
            "The **P/E (Price-to-Earnings) Ratio** indicates how much investors are willing to pay for every ₹1 of profit "
            "the company makes. A lower P/E may suggest a stock is reasonably priced or undervalued, while a high P/E "
            "often reflects high future growth expectations."
        )
    else:
        reply = (
            f"Hello {current_user.name}! I'm Arya, your FinPilot Wealth Mentor. I'm here to help you learn financial concepts, "
            f"understand portfolio risks, and build healthy investment habits. What concept would you like to explore?"
        )

    return {"reply": reply, "financial_iq": current_user.financial_iq}


@app.get("/api/funds")
def get_mutual_funds(category: Optional[str] = None, search: Optional[str] = None):
    """Returns curated mutual funds catalog with educational categorization."""
    funds = [
        {
            "id": "mf-1",
            "name": "UTI Nifty 50 Index Fund",
            "category": "Index Funds",
            "risk": "Low-Medium",
            "er": "0.18%",
            "aum": "₹19,200 Cr",
            "nav": 184.25,
            "min_sip": 500,
            "r1": "16.4%",
            "r3": "15.8%",
            "r5": "16.2%",
            "horizon": "5+ Years",
            "obj": "Passive replication of India top 50 giants with lowest tracking error.",
            "eduNote": "Best for core long-term equity allocation without fund manager risk."
        },
        {
            "id": "mf-2",
            "name": "Mirae Asset Large Cap Fund",
            "category": "Large Cap",
            "risk": "Low-Medium",
            "er": "0.54%",
            "aum": "₹37,800 Cr",
            "nav": 112.40,
            "min_sip": 1000,
            "r1": "14.8%",
            "r3": "15.2%",
            "r5": "16.9%",
            "horizon": "5+ Years",
            "obj": "Active investment in established market leaders across Indian industry.",
            "eduNote": "Combines bluechip stability with selective tactical stock overweighting."
        },
        {
            "id": "mf-3",
            "name": "Parag Parikh Flexi Cap Fund",
            "category": "Flexi Cap",
            "risk": "Medium",
            "er": "0.62%",
            "aum": "₹68,400 Cr",
            "nav": 74.60,
            "min_sip": 1000,
            "r1": "23.4%",
            "r3": "19.8%",
            "r5": "21.4%",
            "horizon": "7+ Years",
            "obj": "Value-oriented multi-cap fund investing in Indian and select global leaders.",
            "eduNote": "Provides automatic market cap diversification and foreign currency hedge."
        },
        {
            "id": "mf-4",
            "name": "HDFC Mid-Cap Opportunities",
            "category": "Mid Cap",
            "risk": "Medium-High",
            "er": "0.72%",
            "aum": "₹58,100 Cr",
            "nav": 164.80,
            "min_sip": 1000,
            "r1": "28.1%",
            "r3": "24.5%",
            "r5": "23.1%",
            "horizon": "7–10 Years",
            "obj": "High-growth mid-sized companies poised to become tomorrow large caps.",
            "eduNote": "Higher volatility than large caps, but historically accelerates compounding."
        },
        {
            "id": "mf-5",
            "name": "Nippon India Small Cap Fund",
            "category": "Small Cap",
            "risk": "High",
            "er": "0.76%",
            "aum": "₹52,000 Cr",
            "nav": 148.90,
            "min_sip": 1000,
            "r1": "33.8%",
            "r3": "27.4%",
            "r5": "25.6%",
            "horizon": "10+ Years",
            "obj": "High risk, high potential small caps for aggressive long-horizon investors.",
            "eduNote": "Strictly for long horizons; prone to 20-30% cyclical drawdowns."
        },
        {
            "id": "mf-6",
            "name": "ICICI Prudential Balanced Advantage",
            "category": "Hybrid",
            "risk": "Low-Medium",
            "er": "0.85%",
            "aum": "₹56,200 Cr",
            "nav": 65.30,
            "min_sip": 500,
            "r1": "14.2%",
            "r3": "12.8%",
            "r5": "13.4%",
            "horizon": "3–5 Years",
            "obj": "Dynamically shifts between equity and debt according to market valuation.",
            "eduNote": "Cuts downside drawdowns during expensive market valuations automatically."
        },
        {
            "id": "mf-7",
            "name": "HDFC Short Term Debt Fund",
            "category": "Debt",
            "risk": "Low",
            "er": "0.35%",
            "aum": "₹16,500 Cr",
            "nav": 29.40,
            "min_sip": 500,
            "r1": "7.6%",
            "r3": "7.1%",
            "r5": "7.4%",
            "horizon": "1–3 Years",
            "obj": "Capital preservation and liquidity with high credit quality bonds.",
            "eduNote": "Ideal for emergency funds and short-term capital parking."
        }
    ]
    if category and category != "All":
        funds = [f for f in funds if f["category"].lower() == category.lower()]
    if search:
        s = search.lower()
        funds = [f for f in funds if s in f["name"].lower() or s in f["category"].lower() or s in f["obj"].lower()]
    return {"status": "ok", "total": len(funds), "funds": funds}


# --- FINANCIAL FREEDOM PLANNER ENDPOINTS ---

@app.post("/api/freedom/calculate")
def calculate_freedom_plan(req: FinancialFreedomCalculateRequest):
    """
    Computes end-to-end Financial Freedom planning numbers:
    Cashflow, Emergency Fund, Freedom Corpus, Reverse SIP, Timeline, Scenarios, Readiness Score.
    """
    cf = calculate_cashflow(
        income_dict=req.income,
        essential_dict=req.essential_expenses,
        lifestyle_dict=req.lifestyle_expenses,
        emi_dict=req.emis,
        custom_expenses=req.custom_expenses,
        current_investments_dict=req.current_investments,
        current_savings=req.current_savings,
        emergency_target_months=req.emergency_target_months,
        risk_level=req.risk_level
    )

    ef = calculate_emergency_fund(
        essential_monthly=cf["total_essential_expenses"],
        emi_monthly=cf["total_emis"],
        current_savings=req.current_savings,
        multiplier_months=req.emergency_target_months,
        monthly_capacity=cf["safe_investment_capacity"]
    )

    existing_investments_total = cf["total_current_investments"]

    ff = calculate_financial_freedom(
        monthly_expense_today=req.desired_monthly_expense_today,
        inflation_rate=req.inflation_rate,
        horizon_years=req.horizon_years,
        withdrawal_rate=req.withdrawal_rate,
        existing_investments=existing_investments_total,
        return_assumption=req.return_assumption,
        monthly_investment_capacity=cf["safe_investment_capacity"]
    )

    y2f = calculate_years_to_freedom(
        current_corpus=existing_investments_total,
        monthly_sip=cf["safe_investment_capacity"],
        return_rate=req.return_assumption,
        monthly_expense_today=req.desired_monthly_expense_today,
        inflation_rate=req.inflation_rate,
        withdrawal_rate=req.withdrawal_rate
    )

    scenarios = calculate_scenarios(
        monthly_expense_today=req.desired_monthly_expense_today,
        inflation_rate=req.inflation_rate,
        horizon_years=req.horizon_years,
        withdrawal_rate=req.withdrawal_rate,
        existing_investments=existing_investments_total,
        monthly_sip=cf["safe_investment_capacity"]
    )

    monthly_obligation = cf["total_essential_expenses"] + cf["total_emis"]
    current_ef_months = (req.current_savings / monthly_obligation) if monthly_obligation > 0 else 12.0
    cap_to_sip_ratio = (cf["safe_investment_capacity"] / ff["required_sip"]) if ff["required_sip"] > 0 else 1.0

    readiness = calculate_readiness_score(
        emergency_fund_months=current_ef_months,
        emi_burden_pct=cf["emi_burden_pct"],
        savings_rate_pct=cf["savings_rate_pct"],
        capacity_to_sip_ratio=cap_to_sip_ratio,
        horizon_years=req.horizon_years
    )

    return {
        "status": "ok",
        "cashflow": cf,
        "emergency_fund": ef,
        "financial_freedom": ff,
        "years_to_freedom": y2f,
        "scenarios": scenarios,
        "readiness_score": readiness,
        "disclaimer": "All calculations, projections, and scenarios are illustrative planning assumptions and do not constitute a guarantee of future investment returns or financial freedom."
    }


@app.get("/api/freedom/profile")
def get_freedom_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves user's persisted Financial Freedom plan."""
    plan = db.query(FinancialFreedomPlan).filter(FinancialFreedomPlan.user_id == current_user.id).first()
    if not plan:
        return {"saved": False, "profile_data": None, "results_data": None}
    return {
        "saved": True,
        "user_id": plan.user_id,
        "profile_data": json.loads(plan.profile_data),
        "results_data": json.loads(plan.results_data) if plan.results_data else None,
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
    }


@app.post("/api/freedom/profile")
def save_freedom_profile(
    plan_data: FinancialFreedomPlanSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Saves or updates user's Financial Freedom plan."""
    plan = db.query(FinancialFreedomPlan).filter(FinancialFreedomPlan.user_id == current_user.id).first()
    if not plan:
        plan = FinancialFreedomPlan(
            user_id=current_user.id,
            profile_data=json.dumps(plan_data.profile_data),
            results_data=json.dumps(plan_data.results_data) if plan_data.results_data else None
        )
        db.add(plan)
    else:
        plan.profile_data = json.dumps(plan_data.profile_data)
        if plan_data.results_data:
            plan.results_data = json.dumps(plan_data.results_data)
        plan.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(plan)
    return {"status": "success", "message": "Financial Freedom plan saved successfully"}


# --- HEALTH CHECK & STATIC FRONTEND SERVING ---

@app.get("/api/health")
def health_check():
    """Simple health/ping endpoint for frontend connectivity checks."""
    return {
        "status": "ok",
        "service": "FinPilot AI Core API",
        "version": "1.2.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    }

@app.get("/")
def serve_index():
    """Serves the main FinPilot AI single page web application."""
    index_path = os.path.join(ROOT_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/index.html")
def serve_index_html():
    return serve_index()

@app.get("/styles.css")
def serve_styles():
    css_path = os.path.join(ROOT_DIR, "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="styles.css not found")

@app.get("/app.js")
def serve_app_js():
    js_path = os.path.join(ROOT_DIR, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="app.js not found")



