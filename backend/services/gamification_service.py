"""
FinPilot AI — Gamification & Progression Service
Manages XP, Levels (Novice to Wealth Sage), Badges, Learning Quests, and Streaks.
Note: Strictly distinct from Financial IQ. XP rewards effort and engagement; Financial IQ measures competence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import json
from sqlalchemy.orm import Session
from backend.models import (
    GameXP, Badge, UserBadge, LearningQuest, QuestProgress,
    DailyQuiz, DailyQuizAttempt, User
)

LEVEL_THRESHOLDS = [
    (1, "Financial Novice", 0, 200),
    (2, "Budget Tracker", 200, 500),
    (3, "Saver Apprentice", 500, 900),
    (4, "Asset Allocator", 900, 1400),
    (5, "Market Explorer", 1400, 2000),
    (6, "Compounder Specialist", 2000, 2800),
    (7, "Portfolio Strategist", 2800, 3800),
    (8, "Crisis Resilience Master", 3800, 5000),
    (9, "Financial Freedom Pioneer", 5000, 7000),
    (10, "Wealth Sage", 7000, 999999)
]

SEED_BADGES = [
    {
        "id": "first_assessment",
        "name": "Self-Aware Investor",
        "description": "Completed your baseline 10-dimension Financial IQ evaluation.",
        "icon": "🧭",
        "category": "Milestone",
        "xp_reward": 100
    },
    {
        "id": "compounding_champ",
        "name": "Eighth Wonder",
        "description": "Mastered the mathematics of long-term reverse SIP annuity compounding.",
        "icon": "📈",
        "category": "Mastery",
        "xp_reward": 120
    },
    {
        "id": "emergency_shield",
        "name": "Fort Knox Reserve",
        "description": "Established and validated an emergency liquidity cushion of at least 3 months.",
        "icon": "🛡️",
        "category": "Discipline",
        "xp_reward": 150
    },
    {
        "id": "anti_fomo",
        "name": "Iron Discipline",
        "description": "Maintained high decision score during a panic crash simulation without panic selling.",
        "icon": "💎",
        "category": "Discipline",
        "xp_reward": 180
    },
    {
        "id": "diversified_mind",
        "name": "Non-Correlated Mindset",
        "description": "Constructed a diversified multi-asset blueprint spanning Equity, Debt, and Liquid Cash.",
        "icon": "🌐",
        "category": "Risk",
        "xp_reward": 140
    },
    {
        "id": "streak_7",
        "name": "Consistency Titan",
        "description": "Maintained a 7-day continuous daily financial learning streak.",
        "icon": "🔥",
        "category": "Milestone",
        "xp_reward": 200
    }
]

SEED_QUESTS = [
    {
        "id": "quest_daily_quiz",
        "title": "Daily Market Intelligence Challenge",
        "description": "Answer today's financial literacy question to maintain your daily streak.",
        "category": "Daily",
        "xp_reward": 50,
        "target_count": 1
    },
    {
        "id": "quest_sim_crash",
        "title": "Survive the 2020 Covid Shock",
        "description": "Execute orders with an average Decision Quality score of 75+ in historical simulation.",
        "category": "Milestone",
        "xp_reward": 150,
        "target_count": 1
    },
    {
        "id": "quest_rag_research",
        "title": "Regulatory Literature Search",
        "description": "Consult the SEBI and AMFI RAG knowledge base for authoritative investment guidelines.",
        "category": "Weekly",
        "xp_reward": 75,
        "target_count": 1
    }
]

DAILY_QUIZZES_BANK = [
    {
        "id": "dq_compounding",
        "question": "If you invest ₹5,000 monthly at 12% annual return for 20 years, approximately what percentage of your final ₹50 Lakh corpus comes from interest/growth rather than your own pocket?",
        "options": [
            "Approximately 25%",
            "Approximately 50%",
            "Approximately 75% or more",
            "100% is your own deposited capital"
        ],
        "correct_index": 2,
        "explanation": "Out of ₹50 Lakh, you contributed only ₹12 Lakh (24%), while compound growth generated ₹38 Lakh (76%)!",
        "dimension": "investing_basics"
    },
    {
        "id": "dq_panic_selling",
        "question": "During a sudden 20% macroeconomic market crash with sound company fundamentals, what does behavioral finance identify as the costliest retail error?",
        "options": [
            "Rebalancing portfolio back to target asset weights",
            "Panic selling equities into cash at rock-bottom valuations",
            "Continuing systematic SIP contributions undisturbed",
            "Checking company quarterly cash flow reports"
        ],
        "correct_index": 1,
        "explanation": "Panic selling locks in temporary paper drawdowns as permanent capital losses, forfeiting the subsequent recovery rally.",
        "dimension": "market_cycles"
    },
    {
        "id": "dq_real_return",
        "question": "If a fixed deposit pays 6.5% interest and headline consumer inflation is 6.0%, what is your approximate real purchasing power gain after 30% tax bracket on interest?",
        "options": [
            "+6.5% annual wealth increase",
            "+0.5% positive real return",
            "Negative real return (-1.45% after tax)",
            "Zero change"
        ],
        "correct_index": 2,
        "explanation": "After 30% tax, 6.5% becomes 4.55%. Subtracting 6.0% inflation leaves an effective negative return of -1.45% in purchasing power.",
        "dimension": "saving"
    }
]


class GamificationService:
    @staticmethod
    def init_defaults(db: Session):
        """Pre-populates seed badges and quests if not present."""
        for b in SEED_BADGES:
            if not db.query(Badge).filter(Badge.id == b["id"]).first():
                db.add(Badge(**b))
        for q in SEED_QUESTS:
            if not db.query(LearningQuest).filter(LearningQuest.id == q["id"]).first():
                db.add(LearningQuest(**q))
        db.commit()

    @staticmethod
    def get_or_create_user_xp(user_id: int, db: Session) -> GameXP:
        """Retrieves or provisions user GameXP profile."""
        xp_profile = db.query(GameXP).filter(GameXP.user_id == user_id).first()
        if not xp_profile:
            xp_profile = GameXP(user_id=user_id, total_xp=150, level=1, title="Financial Novice", streak_days=1)
            db.add(xp_profile)
            db.commit()
            db.refresh(xp_profile)
        return xp_profile

    @staticmethod
    def add_xp(user_id: int, amount: int, db: Session) -> Dict[str, Any]:
        """Awards XP, recalculates Level, and detects level-up events."""
        xp_profile = GamificationService.get_or_create_user_xp(user_id, db)
        old_level = xp_profile.level
        xp_profile.total_xp += amount

        # Determine new level
        current_xp = xp_profile.total_xp
        new_level = 1
        new_title = "Financial Novice"
        for lvl, title, min_x, max_x in LEVEL_THRESHOLDS:
            if current_xp >= min_x:
                new_level = lvl
                new_title = title

        xp_profile.level = new_level
        xp_profile.title = new_title
        xp_profile.updated_at = datetime.utcnow()
        db.commit()

        return {
            "awarded_xp": amount,
            "total_xp": xp_profile.total_xp,
            "level": xp_profile.level,
            "title": xp_profile.title,
            "did_level_up": (new_level > old_level)
        }

    @staticmethod
    def get_profile(user_id: int, db: Session) -> Dict[str, Any]:
        """Returns full gamification status: XP, level, next level progress, badges, quests, and streak."""
        GamificationService.init_defaults(db)
        xp_profile = GamificationService.get_or_create_user_xp(user_id, db)

        # Level progress calculation
        cur_lvl_info = LEVEL_THRESHOLDS[min(xp_profile.level - 1, len(LEVEL_THRESHOLDS) - 1)]
        next_lvl_min = cur_lvl_info[3]
        cur_lvl_min = cur_lvl_info[2]
        progress_pct = min(100.0, max(0.0, ((xp_profile.total_xp - cur_lvl_min) / max(1, next_lvl_min - cur_lvl_min)) * 100.0))

        # Badges
        all_badges = db.query(Badge).all()
        user_unlocked_ids = {ub.badge_id for ub in db.query(UserBadge).filter(UserBadge.user_id == user_id).all()}
        badge_list = []
        for b in all_badges:
            badge_list.append({
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category,
                "xp_reward": b.xp_reward,
                "unlocked": b.id in user_unlocked_ids
            })

        # Quests
        all_quests = db.query(LearningQuest).all()
        progress_records = {qp.quest_id: qp for qp in db.query(QuestProgress).filter(QuestProgress.user_id == user_id).all()}
        quest_list = []
        for q in all_quests:
            qp = progress_records.get(q.id)
            current_c = qp.current_count if qp else 0
            is_done = (qp.is_completed == 1) if qp else False
            quest_list.append({
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "category": q.category,
                "xp_reward": q.xp_reward,
                "target_count": q.target_count,
                "current_count": current_c,
                "is_completed": is_done
            })

        return {
            "total_xp": xp_profile.total_xp,
            "level": xp_profile.level,
            "title": xp_profile.title,
            "progress_to_next_level_pct": round(progress_pct, 1),
            "xp_for_next_level": next_lvl_min,
            "streak_days": xp_profile.streak_days,
            "badges": badge_list,
            "quests": quest_list
        }

    @staticmethod
    def unlock_badge(user_id: int, badge_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Unlocks a badge and awards its XP reward if not already unlocked."""
        existing = db.query(UserBadge).filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id).first()
        if existing:
            return None
        badge = db.query(Badge).filter(Badge.id == badge_id).first()
        if not badge:
            return None

        ub = UserBadge(user_id=user_id, badge_id=badge_id)
        db.add(ub)
        db.commit()

        xp_res = GamificationService.add_xp(user_id, badge.xp_reward, db)
        return {
            "unlocked": True,
            "badge": {"id": badge.id, "name": badge.name, "icon": badge.icon},
            "xp_awarded": badge.xp_reward,
            "new_xp": xp_res["total_xp"]
        }

    @staticmethod
    def get_daily_quiz(user_id: int, db: Session) -> Dict[str, Any]:
        """Returns today's daily quiz challenge and whether user already attempted it."""
        today_str = date.today().isoformat()
        q_record = db.query(DailyQuiz).filter(DailyQuiz.date_str == today_str).first()
        if not q_record:
            # Deterministically choose from bank
            day_idx = date.today().timetuple().tm_yday % len(DAILY_QUIZZES_BANK)
            seed = DAILY_QUIZZES_BANK[day_idx]
            q_record = DailyQuiz(
                id=f"dq_{today_str}",
                date_str=today_str,
                question=seed["question"],
                options_json=json.dumps(seed["options"]),
                correct_index=seed["correct_index"],
                explanation=seed["explanation"],
                dimension=seed["dimension"],
                xp_reward=50
            )
            db.add(q_record)
            db.commit()
            db.refresh(q_record)

        attempt = db.query(DailyQuizAttempt).filter(
            DailyQuizAttempt.user_id == user_id,
            DailyQuizAttempt.quiz_id == q_record.id
        ).first()

        options = json.loads(q_record.options_json)
        return {
            "quiz_id": q_record.id,
            "date": q_record.date_str,
            "question": q_record.question,
            "options": options,
            "xp_reward": q_record.xp_reward,
            "already_attempted": attempt is not None,
            "user_selected": attempt.selected_index if attempt else None,
            "is_correct": bool(attempt.is_correct) if attempt else None,
            "correct_index": q_record.correct_index if attempt else None,
            "explanation": q_record.explanation if attempt else None
        }

    @staticmethod
    def answer_daily_quiz(user_id: int, quiz_id: str, selected_index: int, db: Session) -> Dict[str, Any]:
        """Processes user answer, updates streak, awards XP, and returns feedback."""
        q_record = db.query(DailyQuiz).filter(DailyQuiz.id == quiz_id).first()
        if not q_record:
            raise ValueError("Quiz not found")

        existing = db.query(DailyQuizAttempt).filter(
            DailyQuizAttempt.user_id == user_id,
            DailyQuizAttempt.quiz_id == quiz_id
        ).first()
        if existing:
            return {
                "already_attempted": True,
                "is_correct": bool(existing.is_correct),
                "correct_index": q_record.correct_index,
                "explanation": q_record.explanation
            }

        is_correct = (selected_index == q_record.correct_index)
        attempt = DailyQuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            selected_index=selected_index,
            is_correct=1 if is_correct else 0
        )
        db.add(attempt)

        # Update streak in GameXP
        xp_profile = GamificationService.get_or_create_user_xp(user_id, db)
        today_str = date.today().isoformat()
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()

        if xp_profile.last_active_date == yesterday_str:
            xp_profile.streak_days += 1
        elif xp_profile.last_active_date != today_str:
            xp_profile.streak_days = 1
        xp_profile.last_active_date = today_str

        # Award XP if correct
        xp_gained = q_record.xp_reward if is_correct else 15
        xp_result = GamificationService.add_xp(user_id, xp_gained, db)

        # Check streak badge
        if xp_profile.streak_days >= 7:
            GamificationService.unlock_badge(user_id, "streak_7", db)

        db.commit()

        return {
            "is_correct": is_correct,
            "correct_index": q_record.correct_index,
            "explanation": q_record.explanation,
            "xp_awarded": xp_gained,
            "total_xp": xp_result["total_xp"],
            "streak_days": xp_profile.streak_days
        }
