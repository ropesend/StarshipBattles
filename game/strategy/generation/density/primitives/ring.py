"""
Ring density primitive.

Creates a ring-shaped density field with high density at a specific radius
from the center, falling off both inward and outward.
"""

import math
from dataclasses import dataclass

from game.strategy.generation.density.primitives.density_primitive import clamp_density


@dataclass
class RingPrimitive:
    """Ring-shaped density field.

    Creates a density field with maximum density at a specific radius,
    decreasing both toward and away from the center.

    Attributes:
        center_q: Center q coordinate
        center_r: Center r coordinate
        radius: Distance from center where density is highest
        width: Width of the ring (controls falloff rate)
        peak_density: Maximum density at the ring (default 1.0)
    """

    center_q: float = 0.0
    center_r: float = 0.0
    radius: float = 500.0
    width: float = 100.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Density is highest at the ring radius, falling off with distance
        from the ring using a Gaussian profile.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        # Calculate distance from center
        dq = q - self.center_q
        dr = r - self.center_r
        distance_sq = dq * dq + dr * dr + dq * dr
        distance = math.sqrt(max(0.0, distance_sq))

        if self.width <= 0:
            # Point ring - only exactly at radius
            return clamp_density(self.peak_density if abs(distance - self.radius) < 1.0 else 0.0)

        # Gaussian falloff from the ring radius
        distance_from_ring = distance - self.radius
        width_sq = self.width * self.width
        raw_density = self.peak_density * math.exp(-(distance_from_ring ** 2) / (2.0 * width_sq))

        return clamp_density(raw_density)
