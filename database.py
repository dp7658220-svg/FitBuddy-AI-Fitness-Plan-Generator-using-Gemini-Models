"""
database.py
-----------
SQLAlchemy models + persistence helpers for FitBuddy.

Stores each user's profile plus their AI-generated workout plan.
The original plan and any feedback-updated plan are kept as
separate columns so both versions remain visible in the admin view.
"""

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    workout_plan = Column(Text, nullable=False)
    nutrition_tip = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------

def save_user(db, user_id: str, username: str, age: int, weight: str, goal: str, intensity: str) -> User:
    existing = db.query(User).filter(User.user_id == user_id).first()
    if existing:
        existing.username = username
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing.intensity = intensity
        db.commit()
        db.refresh(existing)
        return existing

    user = User(
        user_id=user_id,
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_all_users(db) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


# ---------------------------------------------------------------------
# Plan helpers
# ---------------------------------------------------------------------

def save_plan(db, user_id: str, workout_plan: str, nutrition_tip: str) -> Plan:
    plan = Plan(user_id=user_id, workout_plan=workout_plan, nutrition_tip=nutrition_tip)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_original_plan(db, user_id: str) -> Plan | None:
    return (
        db.query(Plan)
        .filter(Plan.user_id == user_id)
        .order_by(Plan.created_at.desc())
        .first()
    )


def update_plan(db, plan: Plan, updated_plan: str, feedback: str) -> Plan:
    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan


def get_all_plans(db) -> list[Plan]:
    return db.query(Plan).order_by(Plan.created_at.desc()).all()
