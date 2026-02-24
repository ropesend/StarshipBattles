"""
Spiral arm density primitive.

Creates a logarithmic spiral pattern for spiral galaxy arms.
"""

import math
from dataclasses import dataclass

from game.core.hex_math import hex_axial_to_cartesian
from game.strategy.generation.density.primitives.density_primitive import clamp_density


@dataclass
class SpiralArmPrimitive:
    """Logarithmic spiral arm density field.

    Creates density along spiral arms emanating from the center.
    Uses a logarithmic spiral: r = a * e^(b * theta)

    Attributes:
        center_q: Center q coordinate
        center_r: Center r coordinate
        arm_count: Number of spiral arms (default 2)
        pitch_angle: Pitch angle in degrees (controls tightness, default 20)
        arm_width: Width of each arm in hex units (default 100)
        rotation: Initial rotation offset in radians (default 0)
        peak_density: Maximum density along arm (default 1.0)
    """

    center_q: float = 0.0
    center_r: float = 0.0
    arm_count: int = 2
    pitch_angle: float = 20.0
    arm_width: float = 100.0
    rotation: float = 0.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Calculates distance to nearest spiral arm and returns
        density based on that distance.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        # Convert hex axial to Cartesian
        x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)

        # Get polar coordinates
        distance = math.sqrt(x * x + y * y)
        if distance < 1.0:
            # At center - high density
            return clamp_density(self.peak_density)

        angle = math.atan2(y, x)

        # Logarithmic spiral: r = a * e^(b * theta)
        # Rearranged: theta = ln(r/a) / b
        # For a given r, the arm is at theta = ln(r) / b + offset
        # b = tan(pitch_angle)
        pitch_rad = math.radians(self.pitch_angle)
        if abs(pitch_rad) < 0.001:
            # Nearly radial - fallback to ring-like behavior
            return clamp_density(0.0)

        b = 1.0 / math.tan(pitch_rad)

        # Calculate expected angle for this distance
        expected_angle = math.log(max(1.0, distance)) * b + self.rotation

        # Find minimum angular distance to any arm
        min_angular_distance = float('inf')
        arm_spacing = 2.0 * math.pi / max(1, self.arm_count)

        for arm in range(self.arm_count):
            arm_angle = expected_angle + arm * arm_spacing
            # Angular distance
            diff = angle - arm_angle
            # Normalize to [-pi, pi]
            while diff > math.pi:
                diff -= 2.0 * math.pi
            while diff < -math.pi:
                diff += 2.0 * math.pi

            # Convert angular distance to linear distance at this radius
            linear_distance = abs(diff) * distance
            if linear_distance < min_angular_distance:
                min_angular_distance = linear_distance

        # Gaussian falloff from arm
        if self.arm_width <= 0:
            return clamp_density(self.peak_density if min_angular_distance < 1.0 else 0.0)

        width_sq = self.arm_width * self.arm_width
        raw_density = self.peak_density * math.exp(-(min_angular_distance ** 2) / (2.0 * width_sq))

        return clamp_density(raw_density)
