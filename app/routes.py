from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from .models import Habit, HabitProgress
from .utils import calculate_streak, reward_for_completion
from . import db

main = Blueprint("main", __name__)

# ---------- Home ----------
@main.route("/")
def index():
    return render_template("index.html")

# ---------- Dashboard ----------
@main.route("/dashboard")
@login_required
def dashboard():
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    # For each habit, attach today's completion + streak
    habit_data = []
    for h in habits:
        todays_prog = HabitProgress.query.filter_by(habit_id=h.id, day=date.today()).first()
        completed_today = bool(todays_prog and todays_prog.completed)
        streak = calculate_streak(h)
        habit_data.append({
            "habit": h,
            "completed_today": completed_today,
            "streak": streak
        })

    return render_template("dashboard.html", habit_data=habit_data, user=current_user)

# ---------- READ + CREATE ----------
@main.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")

        new_habit = Habit(user_id=current_user.id, name=name, description=description)
        db.session.add(new_habit)
        db.session.commit()
        return redirect(url_for("main.habits"))

    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template("habits.html", habits=habits)

# ---------- UPDATE ----------
@main.route("/habits/<int:habit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    # stop users from editing others' habits
    if habit.user_id != current_user.id:
        return redirect(url_for("main.habits"))

    if request.method == "POST":
        habit.name = request.form.get("name")
        habit.description = request.form.get("description", "")
        db.session.commit()
        return redirect(url_for("main.habits"))

    return render_template("edit_habit.html", habit=habit)

# ---------- DELETE ----------
@main.route("/habits/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.habits"))

    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for("main.habits"))

# ---------- DAILY COMPLETION ----------
@main.route("/habits/<int:habit_id>/complete", methods=["POST"])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.dashboard"))

    prog = HabitProgress.query.filter_by(
        habit_id=habit.id, day=date.today()
    ).first()

    if not prog:
        prog = HabitProgress(habit_id=habit.id, day=date.today(), completed=True)
        db.session.add(prog)
    else:
        prog.completed = True

    db.session.commit()

# ---- NEW: streak + reward ----
    streak = calculate_streak(habit)
    coins_earned = reward_for_completion(streak)

    current_user.currency += coins_earned
    current_user.xp += 10   # flat XP reward per completion for MVP

    db.session.commit()
# -----------------------------

    return redirect(url_for("main.dashboard"))


# ---------- OPTIONAL: UNCOMPLETE TODAY ----------
@main.route("/habits/<int:habit_id>/uncomplete", methods=["POST"])
@login_required
def uncomplete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        return redirect(url_for("main.dashboard"))

    prog = HabitProgress.query.filter_by(
        habit_id=habit.id, day=date.today()
    ).first()

    if prog:
        prog.completed = False
        db.session.commit()

    return redirect(url_for("main.dashboard"))