"""
Noise density primitive.

Creates a procedural noise field for irregular density patterns.
Uses a simple value noise implementation (no external dependencies).
"""

import math
from dataclasses import dataclass, field

from game.strategy.generation.density.primitives.density_primitive import clamp_density


def _hash_coord(x: int, y: int, seed: int) -> int:
    """Simple hash function for coordinate-based noise."""
    # Simple hash combining coordinates with seed
    h = seed
    h = ((h ^ x) * 0x45d9f3b) & 0xFFFFFFFF
    h = ((h ^ y) * 0x45d9f3b) & 0xFFFFFFFF
    h = ((h >> 16) ^ h) & 0xFFFFFFFF
    return h


def _smooth_noise(x: float, y: float, seed: int) -> float:
    """Generate smooth value noise at a coordinate."""
    # Integer coordinates
    x0 = int(math.floor(x))
    y0 = int(math.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1

    # Fractional parts
    fx = x - x0
    fy = y - y0

    # Smoothstep interpolation
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)

    # Corner values (normalized to 0-1)
    n00 = (_hash_coord(x0, y0, seed) & 0xFFFF) / 0xFFFF
    n10 = (_hash_coord(x1, y0, seed) & 0xFFFF) / 0xFFFF
    n01 = (_hash_coord(x0, y1, seed) & 0xFFFF) / 0xFFFF
    n11 = (_hash_coord(x1, y1, seed) & 0xFFFF) / 0xFFFF

    # Bilinear interpolation
    nx0 = n00 * (1 - fx) + n10 * fx
    nx1 = n01 * (1 - fx) + n11 * fx
    return nx0 * (1 - fy) + nx1 * fy


@dataclass
class NoisePrimitive:
    """Procedural noise density field.

    Uses value noise with multiple octaves for natural-looking
    irregular patterns.

    Attributes:
        scale: Base scale of noise features (larger = bigger features)
        octaves: Number of noise octaves to combine (more = finer detail)
        persistence: Amplitude multiplier per octave (default 0.5)
        seed: Random seed for reproducible noise
        offset_q: Offset in q direction for noise sampling
        offset_r: Offset in r direction for noise sampling
        peak_density: Maximum density (default 1.0)
    """

    scale: float = 100.0
    octaves: int = 4
    persistence: float = 0.5
    seed: int = 0
    offset_q: float = 0.0
    offset_r: float = 0.0
    peak_density: float = 1.0

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate noise density at the given hex coordinate.

        Combines multiple octaves of value noise.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        if self.scale <= 0:
            return clamp_density(0.5 * self.peak_density)

        # Convert hex to approximate Cartesian for more uniform noise
        x = (q + self.offset_q + (r + self.offset_r) * 0.5) / self.scale
        y = ((r + self.offset_r) * math.sqrt(3.0) / 2.0) / self.scale

        # Sum octaves
        total = 0.0
        amplitude = 1.0
        max_amplitude = 0.0
        frequency = 1.0

        for octave in range(max(1, self.octaves)):
            octave_seed = self.seed + octave * 1000
            total += amplitude * _smooth_noise(x * frequency, y * frequency, octave_seed)
            max_amplitude += amplitude
            amplitude *= self.persistence
            frequency *= 2.0

        # Normalize to [0, 1]
        if max_amplitude > 0:
            normalized = total / max_amplitude
        else:
            normalized = 0.5

        return clamp_density(normalized * self.peak_density)
