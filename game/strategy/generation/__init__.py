"""
Galaxy generation module.

This module provides data-driven galaxy generation using composite density fields.
"""

from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.placement_strategies import (
    ISystemPlacementStrategy,
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)

__all__ = [
    'DensityMap',
    'ISystemPlacementStrategy',
    'RandomPlacementStrategy',
    'DensityBasedPlacementStrategy',
]
