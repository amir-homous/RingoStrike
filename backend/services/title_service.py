from __future__ import annotations


def evaluate_user_title(*, level: int, streak: int, total_xp: int, achievements_unlocked: int) -> dict:
    if streak >= 30 or level >= 12:
        return {"key": "relentless_striker", "label": "Relentless Striker"}
    if achievements_unlocked >= 10 or total_xp >= 1000:
        return {"key": "focus_vanguard", "label": "Focus Vanguard"}
    if level >= 8 or streak >= 14:
        return {"key": "discipline_architect", "label": "Discipline Architect"}
    if achievements_unlocked >= 5 or total_xp >= 500:
        return {"key": "momentum_builder", "label": "Momentum Builder"}
    if streak >= 3 or level >= 3:
        return {"key": "consistency_starter", "label": "Consistency Starter"}
    return {"key": "beginner", "label": "Beginner"}
