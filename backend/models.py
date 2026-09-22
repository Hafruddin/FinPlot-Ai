import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    financial_iq = Column(Integer, default=650)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    paper_cash = Column(Float, default=100000.0)

    # Relationships
    completions = relationship("LessonCompletion", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    holdings = relationship("AssetHolding", back_populates="user", cascade="all, delete-orphan")
    paper_holdings = relationship("PaperHolding", back_populates="user", cascade="all, delete-orphan")
    freedom_plan = relationship("FinancialFreedomPlan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    iq_records = relationship("FinancialIQRecord", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="user", cascade="all, delete-orphan")
    tutor_messages = relationship("TutorConversation", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, default=21)
    monthly_income = Column(Float, default=30000.0)
    monthly_expenses = Column(Float, default=20000.0)
    current_savings = Column(Float, default=50000.0)
    monthly_investable = Column(Float, default=5000.0)
    risk_tolerance = Column(String, default="moderate")  # conservative, moderate, aggressive
    knowledge_level = Column(String, default="intermediate") # beginner, intermediate, advanced
    goals_json = Column(String, nullable=True) # JSON of user target goals
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String, primary_key=True, index=True) # e.g. "lesson_1"
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g. "Basics", "Investing", "Risk"
    duration = Column(String, default="5 min")
    description = Column(String, nullable=False)
    content_markdown = Column(String, nullable=True)
    order_index = Column(Integer, default=0)


class LessonCompletion(Base):
    __tablename__ = "lessons_completed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="completions")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True) # e.g. "quiz_compounding_1"
    topic = Column(String, nullable=False) # knowledge, risk, inflation, goals, diversification, decision_making
    question = Column(String, nullable=False)
    options_json = Column(String, nullable=False) # JSON array of 4 options
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(String, nullable=False)
    dimension = Column(String, nullable=False) # knowledge(30), risk(20), inflation(15), goals(15), diversification(10), decision_making(10)
    weight = Column(Float, default=1.0)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(String, nullable=False)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Integer, default=0) # 1 if correct, 0 if incorrect
    dimension = Column(String, nullable=True)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="quiz_attempts")


class FinancialIQRecord(Base):
    __tablename__ = "financial_iq_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_score = Column(Float, default=0.0) # 0 to 100
    knowledge_score = Column(Float, default=0.0) # out of 30
    risk_score = Column(Float, default=0.0) # out of 20
    inflation_score = Column(Float, default=0.0) # out of 15
    goals_score = Column(Float, default=0.0) # out of 15
    diversification_score = Column(Float, default=0.0) # out of 10
    decision_score = Column(Float, default=0.0) # out of 10
    strengths_json = Column(String, nullable=True) # JSON list
    weak_areas_json = Column(String, nullable=True) # JSON list
    recommended_learning_json = Column(String, nullable=True) # JSON list
    assessed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="iq_records")


class UserGoal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    duration_years = Column(Integer, nullable=False)
    monthly_capacity = Column(Float, nullable=False)
    savings_amount = Column(Float, nullable=False)
    risk_appetite = Column(String, default="moderate")

    user = relationship("User", back_populates="goals")


class AssetHolding(Base):
    __tablename__ = "asset_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_class = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)

    user = relationship("User", back_populates="holdings")


class PaperHolding(Base):
    __tablename__ = "paper_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)

    user = relationship("User", back_populates="paper_holdings")


class FinancialFreedomPlan(Base):
    __tablename__ = "financial_freedom_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    profile_data = Column(String, nullable=False)  # JSON encoded input profile & expenses
    results_data = Column(String, nullable=True)   # JSON encoded calculations & scenarios
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="freedom_plan")


class SimulationRecord(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_amount = Column(Float, nullable=False)
    duration_years = Column(Integer, nullable=False)
    monthly_contribution = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=False)
    inflation_rate = Column(Float, default=0.06)
    future_value = Column(Float, nullable=False)
    inflation_adjusted_value = Column(Float, nullable=False)
    scenarios_json = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_name = Column(String, nullable=False) # ProfileAgent, GoalAgent, RiskAgent, KnowledgeAgent, SimulationAgent, StrategyAgent, ExplanationAgent
    status = Column(String, default="queued") # queued, running, completed, failed
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, default=0.0)
    input_summary = Column(String, nullable=True)
    output_summary = Column(String, nullable=True)
    evidence_json = Column(String, nullable=True) # citations, calculations, source references
    error = Column(String, nullable=True)

    user = relationship("User", back_populates="agent_runs")


class TutorConversation(Base):
    __tablename__ = "tutor_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String, nullable=False) # user, assistant, system
    content = Column(String, nullable=False)
    intent = Column(String, nullable=True)
    citations_json = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="tutor_messages")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # compounding, inflation, sip, risk, asset_allocation, emergency_fund
    source_name = Column(String, nullable=False) # SEBI, RBI, AMFI, NISM, FinPilot Education
    url = Column(String, nullable=True)
    section = Column(String, nullable=True)
    content_chunk = Column(String, nullable=False)
    keywords = Column(String, nullable=True) # comma separated terms
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


