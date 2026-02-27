"""
DensityMap - Composite density field for galaxy generation.

Combines multiple density primitives with weights to create
complex galaxy layouts.
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.core.hex_math import HexCoord
from game.strategy.generation.density.primitives.density_primitive import (
    DensityPrimitive,
    clamp_density,
)
from game.strategy.generation.density.primitives.radial import RadialPrimitive
from game.strategy.generation.density.primitives.ring import RingPrimitive
from game.strategy.generation.density.primitives.spiral_arm import SpiralArmPrimitive
from game.strategy.generation.density.primitives.linear import LinearPrimitive
from game.strategy.generation.density.primitives.noise import NoisePrimitive
from game.strategy.generation.density.primitives.geometric import GeometricPrimitive

logger = logging.getLogger(__name__)


# Mapping from primitive type names to classes
PRIMITIVE_REGISTRY: Dict[str, type] = {
    'radial': RadialPrimitive,
    'ring': RingPrimitive,
    'spiral_arm': SpiralArmPrimitive,
    'linear': LinearPrimitive,
    'noise': NoisePrimitive,
    'geometric': GeometricPrimitive,
}


@dataclass
class DensityMap:
    """Composite density field combining multiple primitives.

    DensityMap manages a collection of density primitives, each with
    an associated weight. The total density at any point is the
    weighted sum of all primitive contributions, clamped to [0, 1].

    Attributes:
        radius: The radius of the galaxy in hex units
        normalize: Whether to normalize weights to sum to 1.0
    """

    radius: int = 1000
    normalize: bool = True
    _primitives: List[Tuple[DensityPrimitive, float]] = field(default_factory=list)
    _total_weight: float = field(default=0.0, init=False)

    def add_primitive(self, primitive: DensityPrimitive, weight: float = 1.0) -> None:
        """Add a density primitive with the given weight.

        Args:
            primitive: The density primitive to add
            weight: Weight for this primitive (default 1.0)
        """
        if weight <= 0:
            logger.warning(f"Ignoring primitive with non-positive weight: {weight}")
            return
        self._primitives.append((primitive, weight))
        self._total_weight += weight

    def evaluate(self, q: int, r: int) -> float:
        """Evaluate total density at the given hex coordinate.

        Returns the weighted sum of all primitive densities,
        optionally normalized and clamped to [0, 1].

        Args:
            q: Axial q coordinate
            r: Axial r coordinate

        Returns:
            Density value in range [0.0, 1.0]
        """
        if not self._primitives:
            return 0.0

        total = 0.0
        for primitive, weight in self._primitives:
            density = primitive.evaluate(q, r)
            total += density * weight

        # Normalize if requested
        if self.normalize and self._total_weight > 0:
            total /= self._total_weight

        return clamp_density(total)

    def sample(self, rng: Optional[random.Random] = None, max_attempts: int = 1000) -> Optional[HexCoord]:
        """Sample a random coordinate weighted by density.

        Uses rejection sampling: generates random points and accepts
        them with probability proportional to their density.

        Args:
            rng: Random number generator (uses global random if None)
            max_attempts: Maximum sampling attempts before giving up

        Returns:
            HexCoord in high-density region, or None if sampling fails

        Raises:
            ValidationException: If no primitives have been added
        """
        if not self._primitives:
            raise ValidationException(
                "Cannot sample from empty density map",
                code=ErrorCode.NOT_INITIALIZED.value,
                context={"reason": "no_primitives_added"}
            )

        if rng is None:
            rng = random.Random()

        for _ in range(max_attempts):
            # Generate random point within radius
            # Use rejection sampling for uniform hex distribution
            q = rng.randint(-self.radius, self.radius)
            r = rng.randint(-self.radius, self.radius)

            # Check if within hex radius
            # In axial coordinates, valid hexes satisfy: |q| + |r| + |q+r| <= 2*radius
            # Simplified: max(|q|, |r|, |q+r|) <= radius
            if max(abs(q), abs(r), abs(q + r)) > self.radius:
                continue

            # Evaluate density and accept/reject
            density = self.evaluate(q, r)
            if rng.random() < density:
                return HexCoord(q, r)

        logger.warning(f"DensityMap.sample() failed after {max_attempts} attempts")
        return None

    def get_coverage_estimate(self, sample_count: int = 1000, rng: Optional[random.Random] = None) -> float:
        """Estimate the fraction of the area with significant density.

        Useful for validating that a density map isn't too sparse.

        Args:
            sample_count: Number of random points to sample
            rng: Random number generator (uses global random if None)

        Returns:
            Fraction of sampled points with density > 0.1
        """
        if rng is None:
            rng = random.Random()

        significant = 0
        sampled = 0

        for _ in range(sample_count):
            q = rng.randint(-self.radius, self.radius)
            r = rng.randint(-self.radius, self.radius)

            if max(abs(q), abs(r), abs(q + r)) > self.radius:
                continue

            sampled += 1
            if self.evaluate(q, r) > 0.1:
                significant += 1

        return significant / max(1, sampled)

    @classmethod
    def from_config(cls, layout_config: Dict[str, Any], radius: int) -> 'DensityMap':
        """Create a DensityMap from a layout configuration dict.

        Args:
            layout_config: Configuration dict with 'primitives' list
            radius: Galaxy radius in hex units

        Returns:
            Configured DensityMap instance

        Raises:
            ValidationException: If configuration is invalid
        """
        density_map = cls(radius=radius)

        primitives_config = layout_config.get('primitives', [])
        if not primitives_config:
            raise ValidationException(
                "Layout config must contain 'primitives' list",
                code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                context={"missing_key": "primitives"}
            )

        for prim_config in primitives_config:
            primitive_type = prim_config.get('type')
            if not primitive_type:
                raise ValidationException(
                    "Each primitive must have a 'type' field",
                    code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                    context={"primitive_config": prim_config}
                )

            if primitive_type not in PRIMITIVE_REGISTRY:
                raise ValidationException(
                    f"Unknown primitive type: {primitive_type}",
                    code=ErrorCode.MISSING_ENTITY.value,
                    context={"primitive_type": primitive_type, "valid_types": list(PRIMITIVE_REGISTRY.keys())}
                )

            # Extract weight (default 1.0)
            weight = prim_config.get('weight', 1.0)

            # Build kwargs for primitive, excluding 'type', 'weight', and underscore-prefixed keys (comments)
            kwargs = {k: v for k, v in prim_config.items()
                      if k not in ('type', 'weight') and not k.startswith('_')}

            # Create primitive instance
            primitive_class = PRIMITIVE_REGISTRY[primitive_type]
            try:
                primitive = primitive_class(**kwargs)
            except TypeError as e:
                raise ValidationException(
                    f"Invalid parameters for {primitive_type}",
                    code=ErrorCode.VALIDATION_FAILED.value,
                    context={"primitive_type": primitive_type, "kwargs": kwargs}
                ) from e

            density_map.add_primitive(primitive, weight)

        logger.info(f"Created DensityMap with {len(density_map._primitives)} primitives")
        return density_map

    def __len__(self) -> int:
        """Return the number of primitives in this map."""
        return len(self._primitives)
