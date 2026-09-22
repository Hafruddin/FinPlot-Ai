from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
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


# --- Agentic AI & Tutor Schemas ---
class TutorChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class CitationItem(BaseModel):
    title: str
    source: str
    url: Optional[str] = None
    section: Optional[str] = None


class TutorChatResponse(BaseModel):
    intent: str
    answer: str
    summary: str
    key_takeaways: List[str]
    example: str
    citations: List[CitationItem]
    limitations: str
    provider: str


class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    category: Optional[str] = None


class RAGDocumentItem(BaseModel):
    doc_id: str
    title: str
    category: str
    source: str
    url: Optional[str] = None
    section: Optional[str] = None
    content: str
    score: float


class RAGQueryResponse(BaseModel):
    query: str
    count: int
    results: List[RAGDocumentItem]


class AgentRunRequest(BaseModel):
    age: Optional[int] = 21
    monthly_income: Optional[float] = 30000.0
    monthly_expenses: Optional[float] = 20000.0
    current_savings: Optional[float] = 50000.0
    monthly_capacity: Optional[float] = 5000.0
    target_amount: Optional[float] = 5000000.0
    duration_years: Optional[int] = 10
    risk_tolerance: Optional[str] = "moderate"
    goal_type: Optional[str] = "Wealth Accumulation & Freedom"
    inflation_rate: Optional[float] = 0.06


class AgentTraceStep(BaseModel):
    run_id: str
    agent_name: str
    responsibility: str
    status: str
    started_at: str
    completed_at: str
    duration_ms: float
    input_summary: str
    output_summary: str
    evidence: Optional[Any] = None
    error: Optional[str] = None


class AgentRunResponse(BaseModel):
    run_id: str
    status: str
    executed_agents_count: int
    trace: List[AgentTraceStep]
    results: dict


class FinancialIQSubmitRequest(BaseModel):
    answers: Dict[str, Any]


class WhatIfRequest(BaseModel):
    previous_horizon_years: int = 10
    new_horizon_years: int = 15
    target_amount: float = 5000000.0
    current_savings: float = 50000.0
    monthly_capacity: float = 5000.0
    annual_return: float = 0.12
    inflation_rate: float = 0.06


class WhatIfResponse(BaseModel):
    target_amount: float
    current_savings: float
    previous_horizon: int
    new_horizon: int
    previous_required_sip: int
    new_required_sip: int
    sip_difference: int
    sip_reduction_pct: float
    previous_total_contributed: int
    new_total_contributed: int
    previous_growth_gain: int
    new_growth_gain: int
    what_changed_explanation: str
    educational_takeaway: str



