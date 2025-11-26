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
    - Base coins: 5
    - Bonus: +5 every 3-day streak milestone (3, 6, 9, ...)
    """
    base = 5
    bonus = (streak // 3) * 5
    return base + bonus

# ---------- Level & XP helpers ----------

def get_level(xp: int) -> int:
    """Level starts at 1 and increases every 100 XP."""
    if xp < 0:
        xp = 0
    return xp // 100 + 1

def get_xp_progress(xp: int) -> dict:
    """
    Returns:
      {
        'level': int,
        'current_xp': int,     # xp into current level
        'needed_xp': int,      # xp needed to reach next level
        'percent': int,        # 0-100
        'next_level_xp': int,  # absolute xp threshold
      }
    """
    if xp < 0:
        xp = 0

    level = get_level(xp)
    current_level_floor = (level - 1) * 100
    next_level_xp = level * 100

    current_xp = xp - current_level_floor
    needed_xp = next_level_xp - current_level_floor

    if needed_xp <= 0:
        percent = 100
    else:
        percent = int((current_xp / needed_xp) * 100)
        percent = max(0, min(100, percent))

    return {
        "level": level,
        "current_xp": current_xp,
        "needed_xp": needed_xp,
        "percent": percent,
        "next_level_xp": next_level_xp,
    }
