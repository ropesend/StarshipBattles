"""
Geometric density primitive.

Creates density based on geometric shapes with angular constraints,
useful for diamond-shaped or polygonal galaxy layouts.
"""

import math
from dataclasses import dataclass

from game.core.hex_math import hex_axial_to_cartesian
from game.strategy.generation.density.primitives.density_primitive import clamp_density


@dataclass
class GeometricPrimitive:
    """Polygonal geometric density field.

    Creates density inside a regular polygon shape, with optional
    falloff at edges.

    Attributes:
        center_q: Center q coordinate
        center_r: Center r coordinate
        sides: Number of polygon sides (3=triangle, 4=diamond, 6=hexagon)
        radius: Distance from center to vertices
        rotation: Rotation angle in radians
        edge_falloff: Width of edge falloff (0 = hard edge)
        peak_density: Maximum density inside shape (default 1.0)
    """

    center_q: float = 0.0
    center_r: float = 0.0
    sides: int = 4
    radius: float = 500.0
    rotation: float = 0.0
    edge_falloff: float = 50.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Calculates whether point is inside the polygon and applies
        edge falloff if near boundaries.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        # Convert hex axial to Cartesian relative to center
        x, y = hex_axial_to_cartesian(q, r, self.center_q, self.center_r)

        # Get distance and angle
        distance = math.sqrt(x * x + y * y)
        if distance < 0.001:
            # At center
            return clamp_density(self.peak_density)

        angle = math.atan2(y, x) - self.rotation

        # For a regular polygon, the distance from center to edge varies with angle
        # Edge distance = r * cos(pi/n) / cos(theta mod (2pi/n) - pi/n)
        if self.sides < 3:
            # Fallback to circle
            edge_distance = self.radius
        else:
            # Angle within one sector
            sector_angle = 2.0 * math.pi / self.sides
            angle_in_sector = (angle % sector_angle) - sector_angle / 2.0

            # Distance to edge at this angle
            cos_half = math.cos(math.pi / self.sides)
            cos_sector = math.cos(angle_in_sector)
            if cos_sector > 0.001:
                edge_distance = self.radius * cos_half / cos_sector
            else:
                edge_distance = self.radius

        # Calculate how far inside/outside the polygon
        distance_from_edge = edge_distance - distance

        if distance_from_edge < 0:
            # Outside polygon
            if self.edge_falloff <= 0:
                return 0.0
            # Falloff outside
            falloff_factor = math.exp(-(distance_from_edge ** 2) / (2.0 * self.edge_falloff ** 2))
            return clamp_density(self.peak_density * falloff_factor)
        else:
            # Inside polygon
            if self.edge_falloff <= 0:
                return clamp_density(self.peak_density)
            # Slight falloff near edges
            if distance_from_edge < self.edge_falloff:
                # Smooth transition near edge
                t = distance_from_edge / self.edge_falloff
                return clamp_density(self.peak_density * (0.5 + 0.5 * t))
            return clamp_density(self.peak_density)
