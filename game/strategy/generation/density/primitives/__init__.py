"""
Density primitives for galaxy layout generation.

Each primitive provides a density field that can be combined in a DensityMap.
"""

from game.strategy.generation.density.primitives.density_primitive import DensityPrimitive
from game.strategy.generation.density.primitives.radial import RadialPrimitive
from game.strategy.generation.density.primitives.ring import RingPrimitive
from game.strategy.generation.density.primitives.spiral_arm import SpiralArmPrimitive
from game.strategy.generation.density.primitives.linear import LinearPrimitive
from game.strategy.generation.density.primitives.noise import NoisePrimitive
from game.strategy.generation.density.primitives.geometric import GeometricPrimitive

__all__ = [
    'DensityPrimitive',
    'RadialPrimitive',
    'RingPrimitive',
    'SpiralArmPrimitive',
    'LinearPrimitive',
    'NoisePrimitive',
    'GeometricPrimitive',
]
