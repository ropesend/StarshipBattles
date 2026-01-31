"""
System placement strategies for galaxy generation.

Provides different algorithms for placing star systems in a galaxy:
- RandomPlacementStrategy: Uniform random placement (original behavior)
- DensityBasedPlacementStrategy: Placement guided by density fields
"""

import logging
import random
from typing import Protocol, Set, Optional, runtime_checkable

from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.generation.density.density_map import DensityMap


log = logging.getLogger(__name__)


@runtime_checkable
class ISystemPlacementStrategy(Protocol):
    """Protocol for system placement strategies.

    Placement strategies determine where to place star systems in a galaxy.
    Each strategy may use different algorithms but must respect the
    minimum distance constraint between systems.
    """

    def sample_location(
        self,
        radius: int,
        existing_systems: Set[HexCoord],
        min_dist: int,
        rng: Optional[random.Random] = None,
        max_attempts: int = 1000
    ) -> Optional[HexCoord]:
        """Sample a valid location for a new star system.

        Args:
            radius: Galaxy radius in hex units
            existing_systems: Set of existing system coordinates to avoid
            min_dist: Minimum distance from existing systems
            rng: Random number generator (uses global random if None)
            max_attempts: Maximum sampling attempts before giving up

        Returns:
            HexCoord for new system, or None if no valid location found
        """
        ...


class RandomPlacementStrategy:
    """Uniform random placement strategy.

    Places systems uniformly at random within the galaxy radius,
    respecting minimum distance constraints. This replicates the
    original galaxy generation behavior.
    """

    def sample_location(
        self,
        radius: int,
        existing_systems: Set[HexCoord],
        min_dist: int,
        rng: Optional[random.Random] = None,
        max_attempts: int = 1000
    ) -> Optional[HexCoord]:
        """Sample a random valid location for a new star system.

        Uses uniform random sampling within hex radius bounds,
        rejecting candidates too close to existing systems.

        Args:
            radius: Galaxy radius in hex units
            existing_systems: Set of existing system coordinates to avoid
            min_dist: Minimum distance from existing systems
            rng: Random number generator (uses global random if None)
            max_attempts: Maximum sampling attempts before giving up

        Returns:
            HexCoord for new system, or None if no valid location found
        """
        if rng is None:
            rng = random.Random()

        for _ in range(max_attempts):
            # Generate random hex within radius (same logic as original)
            q = rng.randint(-radius, radius)
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            r = rng.randint(r1, r2)

            coord = HexCoord(q, r)

            # Check not already occupied
            if coord in existing_systems:
                continue

            # Check minimum distance from all existing systems
            valid = True
            for other in existing_systems:
                if hex_distance(coord, other) < min_dist:
                    valid = False
                    break

            if valid:
                return coord

        log.debug(f"RandomPlacementStrategy failed after {max_attempts} attempts")
        return None


class DensityBasedPlacementStrategy:
    """Density field-guided placement strategy.

    Places systems preferentially in high-density regions as defined
    by a DensityMap, while still respecting minimum distance constraints.
    """

    def __init__(self, density_map: DensityMap):
        """Initialize with a density map.

        Args:
            density_map: DensityMap defining probability distribution for placement
        """
        self._density_map = density_map

    def sample_location(
        self,
        radius: int,
        existing_systems: Set[HexCoord],
        min_dist: int,
        rng: Optional[random.Random] = None,
        max_attempts: int = 1000
    ) -> Optional[HexCoord]:
        """Sample a density-weighted valid location for a new star system.

        Uses rejection sampling with the density map to prefer high-density
        regions, rejecting candidates too close to existing systems.

        Args:
            radius: Galaxy radius in hex units (may differ from density map radius)
            existing_systems: Set of existing system coordinates to avoid
            min_dist: Minimum distance from existing systems
            rng: Random number generator (uses global random if None)
            max_attempts: Maximum sampling attempts before giving up

        Returns:
            HexCoord for new system, or None if no valid location found
        """
        if rng is None:
            rng = random.Random()

        # Use the smaller of provided radius and density map radius
        effective_radius = min(radius, self._density_map.radius)

        for _ in range(max_attempts):
            # Generate random hex within radius
            q = rng.randint(-effective_radius, effective_radius)
            r = rng.randint(-effective_radius, effective_radius)

            # Check if within hex radius constraint
            if max(abs(q), abs(r), abs(q + r)) > effective_radius:
                continue

            coord = HexCoord(q, r)

            # Check not already occupied
            if coord in existing_systems:
                continue

            # Check minimum distance from all existing systems
            valid = True
            for other in existing_systems:
                if hex_distance(coord, other) < min_dist:
                    valid = False
                    break

            if not valid:
                continue

            # Accept/reject based on density (rejection sampling)
            density = self._density_map.evaluate(q, r)
            if rng.random() < density:
                return coord

        log.debug(f"DensityBasedPlacementStrategy failed after {max_attempts} attempts")
        return None
