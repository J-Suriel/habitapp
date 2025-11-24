from datetime import date, timedelta
from .models import HabitProgress

def calculate_streak(habit):
    """Counts consecutive completed days ending today."""
    streak = 0
    current_day = date.today()

    while True:
        prog = HabitProgress.query.filter_by(
            habit_id=habit.id, day=current_day, completed=True
        ).first()
        if prog:
            streak += 1
            current_day -= timedelta(days=1)
        else:
            break

    return streak

def reward_for_completion(streak):
    """
    MVP reward rule:
    - Base coins every completion = 5
    - Bonus = +5 coins for every 3-day streak milestone
      (3, 6, 9, ...)
    """
    base = 5
    bonus = (streak // 3) * 5
    return base + bonus
