"""
Density field module for galaxy generation.

Provides density primitives and composition for creating galaxy layouts.
"""

from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.density.primitives import (
    DensityPrimitive,
    RadialPrimitive,
    RingPrimitive,
    SpiralArmPrimitive,
    LinearPrimitive,
    NoisePrimitive,
    GeometricPrimitive,
)

__all__ = [
    'DensityMap',
    'DensityPrimitive',
    'RadialPrimitive',
    'RingPrimitive',
    'SpiralArmPrimitive',
    'LinearPrimitive',
    'NoisePrimitive',
    'GeometricPrimitive',
]
