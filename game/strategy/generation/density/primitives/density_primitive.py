"""
Base protocol for density primitives.

All density primitives must implement the DensityPrimitive protocol,
providing an evaluate() method that returns density values in [0.0, 1.0].
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class DensityPrimitive(Protocol):
    """Protocol for density field primitives.

    Density primitives compute a density value at any hex coordinate.
    The returned value must be in the range [0.0, 1.0], where:
    - 0.0 = no density (no stars here)
    - 1.0 = maximum density (high probability of stars)

    Implementations should handle negative coordinates correctly.
    """

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate density at the given hex coordinate.

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        ...


def clamp_density(value: float) -> float:
    """Clamp a density value to the valid [0.0, 1.0] range.

    Args:
        value: Raw density value

    Returns:
        Clamped value in [0.0, 1.0]
    """
    return max(0.0, min(1.0, value))
