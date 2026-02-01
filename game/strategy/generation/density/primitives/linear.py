"""
Linear density primitive.

Creates a bar/line-shaped density field, useful for barred spiral galaxy cores.
"""

import math
from dataclasses import dataclass

from game.strategy.generation.density.primitives.density_primitive import clamp_density


@dataclass
class LinearPrimitive:
    """Linear bar-shaped density field.

    Creates density along a line segment, with Gaussian falloff
    perpendicular to the line.

    Attributes:
        center_q: Center q coordinate of the bar
        center_r: Center r coordinate of the bar
        length: Total length of the bar in hex units
        width: Width of the bar (controls perpendicular falloff)
        rotation: Rotation angle in radians (0 = horizontal)
        peak_density: Maximum density along bar center (default 1.0)
    """

    center_q: float = 0.0
    center_r: float = 0.0
    length: float = 500.0
    width: float = 50.0
    rotation: float = 0.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Calculates distance to the bar line segment and returns
        density based on perpendicular distance.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        # Convert to Cartesian-like coordinates relative to center
        dq = q - self.center_q
        dr = r - self.center_r

        # Convert hex axial to approximate Cartesian
        x = dq + dr * 0.5
        y = dr * math.sqrt(3.0) / 2.0

        # Rotate point to align bar with x-axis
        cos_r = math.cos(-self.rotation)
        sin_r = math.sin(-self.rotation)
        x_rot = x * cos_r - y * sin_r
        y_rot = x * sin_r + y * cos_r

        # Now the bar extends along the x-axis from -length/2 to +length/2
        half_length = self.length / 2.0

        # Calculate distance along bar (parallel distance)
        parallel = x_rot
        # Clamp to bar ends
        parallel_clamped = max(-half_length, min(half_length, parallel))

        # Calculate perpendicular distance
        perpendicular = abs(y_rot)

        # Also account for distance past bar ends
        past_end_distance = abs(parallel) - half_length
        if past_end_distance > 0:
            # Point is past the bar end - combine perpendicular and past-end distance
            total_distance_sq = perpendicular ** 2 + past_end_distance ** 2
        else:
            # Point is alongside the bar - just perpendicular distance
            total_distance_sq = perpendicular ** 2

        # Gaussian falloff
        if self.width <= 0:
            return clamp_density(self.peak_density if total_distance_sq < 1.0 else 0.0)

        width_sq = self.width * self.width
        raw_density = self.peak_density * math.exp(-total_distance_sq / (2.0 * width_sq))

        return clamp_density(raw_density)
