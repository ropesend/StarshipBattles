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
from game.strategy.generation.planet_image_registry import PlanetImageRegistry
from game.strategy.generation.star_image_registry import StarImageRegistry

__all__ = [
    'DensityMap',
    'ISystemPlacementStrategy',
    'RandomPlacementStrategy',
    'DensityBasedPlacementStrategy',
    'PlanetImageRegistry',
    'StarImageRegistry',
]
