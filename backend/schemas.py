from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# User Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    financial_iq: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Academy Schemas
class LessonCompletionRequest(BaseModel):
    lesson_id: str

class LessonCompletionResponse(BaseModel):
    lesson_id: str
    completed_at: datetime.datetime

    class Config:
        from_attributes = True

# Goal Schemas
class GoalSaveRequest(BaseModel):
    goal_type: str
    target_amount: float
    duration_years: int
    monthly_capacity: float
    savings_amount: float
    risk_appetite: str

class GoalResponse(BaseModel):
    goal_type: str
    target_amount: float
    duration_years: int
    monthly_capacity: float
    savings_amount: float
    risk_appetite: str

    class Config:
        from_attributes = True

# Portfolio Schemas
class AssetHoldingResponse(BaseModel):
    asset_class: str
    weight: float
    current_value: float

    class Config:
        from_attributes = True

class RebalanceRequest(BaseModel):
    current_value: float
    risk_appetite: str

class RebalanceResponse(BaseModel):
    total_value: float
    holdings: List[AssetHoldingResponse]
    message: str

# Health Check Assessment Schema
class HealthCheckRequest(BaseModel):
    age: int
    monthly_income: float
    monthly_expenses: float
    current_savings: float
    existing_investments: float
    emergency_savings: float
    goal_type: str
    horizon_years: int
    risk_comfort: str

# Paper Trading Schemas
class PaperTradeRequest(BaseModel):
    symbol: str
    action: str  # buy or sell
    quantity: float
    price: float

class PaperHoldingResponse(BaseModel):
    id: int
    symbol: str
    name: str
    quantity: float
    buy_price: float
    current_price: float

    class Config:
        from_attributes = True

# Copilot Request Schema
class CopilotQueryRequest(BaseModel):
    message: str
    context: Optional[dict] = None


# Financial Freedom Planner Schemas
class FinancialFreedomCalculateRequest(BaseModel):
    income: dict
    essential_expenses: dict
    lifestyle_expenses: dict
    emis: dict
    custom_expenses: Optional[List[dict]] = None
    current_investments: Optional[dict] = None
    current_savings: float = 0.0
    emergency_target_months: int = 6
    goal_type: str = "financial_freedom"
    desired_monthly_expense_today: float = 40000.0
    inflation_rate: float = 0.06
    withdrawal_rate: float = 0.04
    return_assumption: float = 0.10
    horizon_years: int = 10
    risk_level: str = "moderate"
    planning_mode: str = "guide"


class FinancialFreedomPlanSaveRequest(BaseModel):
    profile_data: dict
    results_data: Optional[dict] = None


class FinancialFreedomPlanResponse(BaseModel):
    user_id: int
    profile_data: dict
    results_data: Optional[dict] = None
    updated_at: datetime.datetime


# --- Market Gateway Schemas ---
class MarketStatusResponse(BaseModel):
    status: str
    state: str
    is_open: bool
    time: str
    date: str
    exchange: str
    active_provider: str
    last_updated: str


class StockQuoteResponse(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: float
    change: float
    change_percent: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    sector: Optional[str] = None
    exchange: Optional[str] = "NSE"
    is_index: Optional[bool] = False
    source: Optional[str] = "FinPilot"
    data_mode: Optional[str] = "LIVE"


class CandleItem(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockHistoryResponse(BaseModel):
    symbol: str
    timeframe: str
    source: str
    candles: List[CandleItem]


class StockExplainerResponse(BaseModel):
    symbol: str
    name: str
    summary: str
    business_model: str
    key_metrics: dict
    educational_takeaway: str
    what_they_do: Optional[str] = None
    how_they_make_money: Optional[str] = None
    growth_drivers: Optional[str] = None
    major_risks: Optional[str] = None
    beginner_takeaway: Optional[str] = None


class TechnicalIndicatorsResponse(BaseModel):
    sma_20: Optional[float] = None
    ema_20: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[dict] = None
    bollinger: Optional[dict] = None
    atr: Optional[float] = None
    momentum_signal: str
    source: str


class MarketHealthResponse(BaseModel):
    status: str
    timestamp: float
    services: dict


