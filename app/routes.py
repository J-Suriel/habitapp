from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date, timedelta
from .models import Habit, HabitProgress
from . import db
from .utils import (
    calculate_streak,
    reward_for_completion,
    get_level,
    get_xp_progress,
)

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/dashboard")
@login_required
def dashboard():
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    habit_data = []
    analytics = []
    today = date.today()
    week_ago = today - timedelta(days=6)  # last 7 days inclusive

    for h in habits:
        today_prog = HabitProgress.query.filter_by(
            habit_id=h.id, day=today
        ).first()
        completed_today = bool(today_prog and today_prog.completed)
        streak = calculate_streak(h)

        # 7-day completion analytics
        last_week_progs = HabitProgress.query.filter(
            HabitProgress.habit_id == h.id,
            HabitProgress.day >= week_ago,
            HabitProgress.day <= today,
        ).all()
        completed_count = sum(1 for p in last_week_progs if p.completed)
        completion_rate = int((completed_count / 7) * 100)  # percent

        total_completions = HabitProgress.query.filter_by(
            habit_id=h.id, completed=True
        ).count()

        habit_data.append({
            "habit": h,
            "completed_today": completed_today,
            "streak": streak,
        })

        analytics.append({
            "habit": h,
            "streak": streak,
            "completed_last_7": completed_count,
            "completion_rate_7": completion_rate,
            "total_completions": total_completions,
        })

    xp_info = get_xp_progress(current_user.xp)

    return render_template(
        "dashboard.html",
        habit_data=habit_data,
        analytics=analytics,
        xp_info=xp_info,
        user=current_user,
    )

# ---------- Habits CRUD ----------

@main.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")

        new_habit = Habit(
            user_id=current_user.id,
            name=name,
            description=description,
        )
        db.session.add(new_habit)
        db.session.commit()

        return redirect(url_for("main.habits"))

    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template("habits.html", habits=habits)

@main.route("/habits/<int:habit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.habits"))

    if request.method == "POST":
        habit.name = request.form.get("name")
        habit.description = request.form.get("description", "")
        db.session.commit()
        return redirect(url_for("main.habits"))

    return render_template("edit_habit.html", habit=habit)

@main.route("/habits/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.habits"))

    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for("main.habits"))

# ---------- Daily completion ----------

@main.route("/habits/<int:habit_id>/complete", methods=["POST"])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.dashboard"))

    today = date.today()
    prog = HabitProgress.query.filter_by(
        habit_id=habit.id, day=today
    ).first()

    if not prog:
        prog = HabitProgress(habit_id=habit.id, day=today, completed=True)
        db.session.add(prog)
    else:
        prog.completed = True

    db.session.commit()

    # reward
    streak = calculate_streak(habit)
    coins = reward_for_completion(streak)
    current_user.currency += coins
    current_user.xp += 10
    db.session.commit()

    return redirect(url_for("main.dashboard"))

@main.route("/habits/<int:habit_id>/uncomplete", methods=["POST"])
@login_required
def uncomplete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.dashboard"))

    today = date.today()
    prog = HabitProgress.query.filter_by(
        habit_id=habit.id, day=today
    ).first()

    if prog:
        prog.completed = False
        db.session.commit()

    return redirect(url_for("main.dashboard"))
