from . import db
from flask_login import UserMixin
from datetime import datetime, date

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)

    habits = db.relationship("Habit", backref="user", lazy=True)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progresses = db.relationship("HabitProgress", backref="habit", lazy=True, cascade="all, delete-orphan")

class HabitProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habit.id"), nullable=False)
    day = db.Column(db.Date, nullable=False, default=date.today)
    completed = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint("habit_id", "day", name="unique_progress_per_day"),
    )

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), default="")

class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey("reward.id"), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)

    reward = db.relationship("Reward")  # lets us access redemption.reward.name