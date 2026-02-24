"""Galaxy system generation module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles star system placement and planet generation.
"""
import random
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.generation.placement_strategies import ISystemPlacementStrategy
    from game.strategy.data.stars import StarGenerator
    from game.strategy.data.planet_gen import PlanetGenerator
    from game.strategy.data.naming import NameRegistry
    from game.strategy.generation.planet_image_registry import PlanetImageRegistry


class GalaxySystemGenerator:
    """System and planet generator for Galaxy.

    Handles:
    - Star system placement using configurable strategies
    - Planet generation for newly created systems
    - Spatial index management for efficient distance checks
    """

    def __init__(
        self,
        star_generator: 'StarGenerator',
        planet_generator: 'PlanetGenerator',
        naming: 'NameRegistry',
        image_registry: 'PlanetImageRegistry'
    ):
        """Initialize the system generator.

        Args:
            star_generator: Generator for creating stars.
            planet_generator: Generator for creating planets.
            naming: Name registry for system names.
            image_registry: Registry for planet images.
        """
        self._star_gen = star_generator
        self._planet_gen = planet_generator
        self._naming = naming
        self._image_registry = image_registry

    def generate_planets(self, galaxy: 'Galaxy', system: 'StarSystem') -> None:
        """Generate planets for a system based on its star type.

        Args:
            galaxy: Galaxy instance for planet registration.
            system: StarSystem to generate planets for.
        """
        if not system.stars:
            return

        system.planets = self._planet_gen.generate_system_bodies(system.name, system.stars)

        # Sort by distance, then mass (descending) for consistent ordering
        system.planets.sort(key=lambda p: (p.orbit_distance, -p.mass))

        # Register all planets with the galaxy
        for planet in system.planets:
            galaxy.register_planet(system, planet)

    def generate_systems(
        self,
        galaxy: 'Galaxy',
        count: int,
        min_dist: int = 10,
        placement_strategy: Optional['ISystemPlacementStrategy'] = None,
        rng: Optional[random.Random] = None
    ) -> List['StarSystem']:
        """Generate star systems ensuring minimum distance and assigning Star Types.

        Args:
            galaxy: Galaxy instance to add systems to.
            count: Number of systems to generate.
            min_dist: Minimum distance between systems in hex units.
            placement_strategy: Strategy for placing systems. If None, uses
                RandomPlacementStrategy for uniform random placement.
            rng: Random number generator for deterministic generation.
                If None, uses global random state.

        Returns:
            List of generated StarSystem objects.
        """
        # Import here to avoid circular dependency
        from game.strategy.generation.placement_strategies import RandomPlacementStrategy
        from game.strategy.data.spatial_index import SpatialIndex
        from game.strategy.data.galaxy import StarSystem

        if placement_strategy is None:
            placement_strategy = RandomPlacementStrategy()

        generated: List['StarSystem'] = []

        # Build spatial index ONCE for efficient distance checks
        # This avoids O(n²) complexity from rebuilding on every placement
        spatial_index = SpatialIndex(cell_size=max(min_dist, 500))
        existing_coords = set(galaxy.systems.keys())
        for coord in existing_coords:
            spatial_index.add(coord, None)

        # Track consecutive failures to detect saturation
        consecutive_failures = 0
        max_consecutive_failures = 10  # Stop after 10 consecutive failed placements

        while len(generated) < count:
            # Use strategy to sample a valid location
            coord = placement_strategy.sample_location(
                radius=galaxy.radius,
                existing_systems=existing_coords,
                min_dist=min_dist,
                rng=rng,
                spatial_index=spatial_index
            )

            if coord is None:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    # Galaxy is saturated, can't place more systems
                    break
                continue

            # Reset failure counter on success
            consecutive_failures = 0

            # Create the system
            name = self._naming.get_system_name()
            stars = self._star_gen.generate_system_stars(name)

            sys = StarSystem(name, coord, stars=stars)
            self.generate_planets(galaxy, sys)
            galaxy.add_system(sys)
            generated.append(sys)

            # Update spatial index and existing coords incrementally
            spatial_index.add(coord, None)
            existing_coords.add(coord)

        return generated
