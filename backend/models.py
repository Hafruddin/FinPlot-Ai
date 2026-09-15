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
    financial_iq = Column(Integer, default=340)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    paper_cash = Column(Float, default=100000.0)

    # Relationships
    completions = relationship("LessonCompletion", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", uselist=False, cascade="all, delete-orphan")
    holdings = relationship("AssetHolding", back_populates="user", cascade="all, delete-orphan")
    paper_holdings = relationship("PaperHolding", back_populates="user", cascade="all, delete-orphan")


class LessonCompletion(Base):
    __tablename__ = "lessons_completed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="completions")


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

