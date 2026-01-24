"""
Core utilities package for Starship Battles.

Provides framework-agnostic utilities including math, logging, and configuration.
"""
from game.core.math import Vector2, clamp, lerp, angle_diff

__all__ = ['Vector2', 'clamp', 'lerp', 'angle_diff']
