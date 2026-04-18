"""
Strategy layer formulas and calculations.

This package contains pure functions for game mechanics calculations
like habitability scoring, population growth, etc.
"""
from game.strategy.formulas.habitability import (
    calculate_habitability,
    score_planet_for_race,
)

__all__ = [
    'calculate_habitability',
    'score_planet_for_race',
]
