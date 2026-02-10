"""
System placement strategies for galaxy generation.

Provides different algorithms for placing star systems in a galaxy:
- RandomPlacementStrategy: Uniform random placement (original behavior)
- DensityBasedPlacementStrategy: Placement guided by density fields
"""

import logging
import random
from typing import Protocol, Set, Optional, runtime_checkable

from game.core.hex_math import HexCoord
from game.strategy.data.spatial_index import SpatialIndex
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
        max_attempts: int = 1000,
        spatial_index: Optional[SpatialIndex] = None
    ) -> Optional[HexCoord]:
        """Sample a valid location for a new star system.

        Args:
            radius: Galaxy radius in hex units
            existing_systems: Set of existing system coordinates to avoid
            min_dist: Minimum distance from existing systems
            rng: Random number generator (uses global random if None)
            max_attempts: Maximum sampling attempts before giving up
            spatial_index: Pre-built spatial index for distance checks.
                If provided, avoids rebuilding index on each call.
                Caller is responsible for keeping it in sync with existing_systems.

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
        max_attempts: int = 1000,
        spatial_index: Optional[SpatialIndex] = None
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
            spatial_index: Pre-built spatial index for distance checks.
                If provided, avoids rebuilding index on each call.

        Returns:
            HexCoord for new system, or None if no valid location found
        """
        if rng is None:
            rng = random.Random()

        # Use provided spatial index or build one
        if spatial_index is None:
            spatial_index = SpatialIndex(cell_size=max(min_dist, 500))
            for coord in existing_systems:
                spatial_index.add(coord, None)

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

            # Check minimum distance using spatial index (O(1) average case)
            if spatial_index.has_neighbor_within_distance(coord, min_dist):
                continue

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
        max_attempts: int = 1000,
        spatial_index: Optional[SpatialIndex] = None
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
            spatial_index: Pre-built spatial index for distance checks.
                If provided, avoids rebuilding index on each call.

        Returns:
            HexCoord for new system, or None if no valid location found
        """
        if rng is None:
            rng = random.Random()

        # Use the smaller of provided radius and density map radius
        effective_radius = min(radius, self._density_map.radius)

        # Minimum density threshold for fast rejection of empty areas
        density_threshold = 0.01

        # Use provided spatial index or build one
        if spatial_index is None:
            spatial_index = SpatialIndex(cell_size=max(min_dist, 500))
            for coord in existing_systems:
                spatial_index.add(coord, None)

        for _ in range(max_attempts):
            # Generate random hex within radius
            q = rng.randint(-effective_radius, effective_radius)
            r = rng.randint(-effective_radius, effective_radius)

            # Check if within hex radius constraint
            if max(abs(q), abs(r), abs(q + r)) > effective_radius:
                continue

            # Check density FIRST (fast rejection for low-density areas)
            density = self._density_map.evaluate(q, r)
            if density < density_threshold:
                continue

            # Probabilistic acceptance based on density
            # Higher density = higher chance of acceptance
            if rng.random() > density:
                continue

            coord = HexCoord(q, r)

            # Check not already occupied
            if coord in existing_systems:
                continue

            # Check minimum distance using spatial index (O(1) average case)
            if spatial_index.has_neighbor_within_distance(coord, min_dist):
                continue

            return coord

        log.debug(f"DensityBasedPlacementStrategy failed after {max_attempts} attempts")
        return None
