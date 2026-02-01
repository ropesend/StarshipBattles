"""
Radial density primitive with Gaussian falloff.

Creates a circular density field centered on a point, with density
decreasing according to a Gaussian distribution.
"""

import math
from dataclasses import dataclass

from game.strategy.generation.density.primitives.density_primitive import clamp_density


@dataclass
class RadialPrimitive:
    """Radial density field with Gaussian falloff from center.

    The density decreases smoothly from center_q, center_r according to:
        density = peak_density * exp(-(distance^2) / (2 * sigma^2))

    Attributes:
        center_q: Center q coordinate
        center_r: Center r coordinate
        sigma: Standard deviation controlling falloff rate (in hex units)
        peak_density: Maximum density at center (default 1.0)
    """

    center_q: float = 0.0
    center_r: float = 0.0
    sigma: float = 100.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Uses Gaussian falloff from the center point.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        # Calculate distance from center using axial coordinates
        dq = q - self.center_q
        dr = r - self.center_r
        # Convert to cube coordinates for proper hex distance
        # In axial, distance = max(|dq|, |dr|, |dq + dr|)
        # But for smooth Gaussian we use Euclidean-like distance
        distance_sq = dq * dq + dr * dr + dq * dr

        # Gaussian falloff
        if self.sigma <= 0:
            # Avoid division by zero
            return clamp_density(self.peak_density if distance_sq == 0 else 0.0)

        sigma_sq = self.sigma * self.sigma
        raw_density = self.peak_density * math.exp(-distance_sq / (2.0 * sigma_sq))

        return clamp_density(raw_density)
