"""Galaxy system generation module.

Extracted from Galaxy as part of PROJ-173 Phase 2 (internal delegation pattern).
This module handles star system placement, planet generation, and storm generation.
"""
import random
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.star_system import StarSystem
    from game.strategy.generation.placement_strategies import ISystemPlacementStrategy
    from game.strategy.generation.star_generator import StarGenerator
    from game.strategy.data.planet_gen import PlanetGenerator
    from game.strategy.data.naming import NameRegistry
    from game.strategy.generation.planet_image_registry import PlanetImageRegistry
    from game.strategy.generation.storm_generator import StormGenerator


class GalaxySystemGenerator:
    """System and planet generator for Galaxy.

    Handles:
    - Star system placement using configurable strategies
    - Planet generation for newly created systems
    - Storm generation for environmental hazards (PROJ-189)
    - Spatial index management for efficient distance checks
    """

    def __init__(
        self,
        star_generator: 'StarGenerator',
        planet_generator: 'PlanetGenerator',
        naming: 'NameRegistry',
        image_registry: 'PlanetImageRegistry',
        storm_generator: Optional['StormGenerator'] = None
    ):
        """Initialize the system generator.

        Args:
            star_generator: Generator for creating stars.
            planet_generator: Generator for creating planets.
            naming: Name registry for system names.
            image_registry: Registry for planet images.
            storm_generator: Optional generator for environmental storms (PROJ-189).
        """
        self._star_gen = star_generator
        self._planet_gen = planet_generator
        self._naming = naming
        self._image_registry = image_registry
        self._storm_gen = storm_generator

    def generate_planets(
        self,
        galaxy: 'Galaxy',
        system: 'StarSystem',
        rng: Optional[random.Random] = None,
        physics_rng: Optional[random.Random] = None,
        image_rng: Optional[random.Random] = None,
    ) -> None:
        """Generate planets for a system based on its star type.

        Args:
            galaxy: Galaxy instance for planet registration.
            system: StarSystem to generate planets for.
            rng: Optional seeded RNG for deterministic intrinsic ability
                rolls (PROJ-301/302, S3). When None, uses unseeded Random()
                (back-compat with existing callers).
            physics_rng: PROJ-473 H7 S5 — planet physics stream. When None,
                physics draws fall back to module-level random.
            image_rng: PROJ-473 H7 S7 — separate image stream. When None, the
                image registry uses unseeded Random().
        """
        if not system.stars:
            return

        # PROJ-473 Task 3.3: physics_rng=None -> a fresh per-instance Random()
        # (NOT module-level random). The public Galaxy facade normalizes None at
        # a single site; this internal fallback keeps direct callers off global
        # state too (non-reproducible but no module-RNG leak).
        body_rng = physics_rng if physics_rng is not None else random.Random()
        system.planets = self._planet_gen.generate_system_bodies(
            system.name, system.stars, rng=body_rng, image_rng=image_rng,
        )

        # Sort by distance, then mass (descending) for consistent ordering
        system.planets.sort(key=lambda p: (p.orbit_distance, -p.mass))

        # PROJ-301: roll planet-intrinsic abilities from data/planet_types.json.
        _apply_planet_intrinsic_abilities(system.planets, rng=rng)
        # PROJ-302: roll star-intrinsic abilities from data/star_types.json.
        _apply_star_intrinsic_abilities(system.stars, rng=rng)

        # Register all planets with the galaxy
        for planet in system.planets:
            galaxy.register_planet(system, planet)

    def generate_storms(
        self,
        system: 'StarSystem',
        blueprint_config: Dict[str, Any],
        rng: random.Random
    ) -> None:
        """Generate storms for a system based on blueprint configuration.

        Args:
            system: StarSystem to generate storms for.
            blueprint_config: Blueprint configuration with storms section.
            rng: Random number generator.
        """
        if self._storm_gen is None:
            return

        storms = self._storm_gen.generate_storms(system, blueprint_config, rng)
        system.storms = storms

    def generate_systems(
        self,
        galaxy: 'Galaxy',
        count: int,
        min_dist: int = 10,
        placement_strategy: Optional['ISystemPlacementStrategy'] = None,
        rng: Optional[random.Random] = None,
        storm_blueprint_config: Optional[Dict[str, Any]] = None,
        physics_rng: Optional[random.Random] = None,
        image_rng: Optional[random.Random] = None,
    ) -> List['StarSystem']:
        """Generate star systems ensuring minimum distance and assigning Star Types.

        Args:
            galaxy: Galaxy instance to add systems to.
            count: Number of systems to generate.
            min_dist: Minimum distance between systems in hex units.
            placement_strategy: Strategy for placing systems. If None, uses
                RandomPlacementStrategy for uniform random placement.
            rng: Random number generator for deterministic generation (S1
                placement; also yields the S2/S3 child-stream seeds).
                If None, uses global random state.
            storm_blueprint_config: Optional blueprint config for storm generation.
                If None and storm_generator is set, uses default config.
            physics_rng: PROJ-473 H7 S4/S5 — dedicated star/planet physics
                stream, a SEPARATE instance from ``rng`` (seeded with the same
                galaxy_seed at the composition root). Threaded into the
                star/planet pipeline. When None the physics draws fall back to
                module-level random (pre-Phase-3 behavior).
            image_rng: PROJ-473 H7 S6/S7 — SEPARATE seeded stream for star +
                planet image_id / image_rotation, an INDEPENDENT instance (NOT
                derived from physics_rng — pulling a seed from physics_rng
                would consume a physics draw and shift the physics + S9 warp
                geometry sequence off the golden baseline; verified). Kept
                distinct so inserting image draws never perturbs class-(a).
                When None the registries use unseeded Random().

        Returns:
            List of generated StarSystem objects.
        """
        # Import here to avoid circular dependency
        from game.strategy.generation.placement_strategies import RandomPlacementStrategy
        from game.strategy.data.spatial_index import SpatialIndex
        from game.strategy.data.star_system import StarSystem
        if placement_strategy is None:
            placement_strategy = RandomPlacementStrategy()

        # Default storm blueprint config if storm generator exists but no config given
        if storm_blueprint_config is None and self._storm_gen is not None:
            storm_blueprint_config = {
                "storms": {
                    "count": {"min": 0, "max": 2}
                    # No allowed_types = use all types (handled by storm_generator)
                }
            }

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

        # Create separate RNGs for storms + intrinsic-ability rolls to avoid
        # consuming main RNG state. This preserves determinism of system
        # placement while threading a seeded RNG through PROJ-301/302/303/304
        # intrinsic-ability rolls.
        if rng is not None:
            storm_seed = rng.randint(0, 2**32 - 1)
            intrinsic_seed = rng.randint(0, 2**32 - 1)
            storm_rng = random.Random(storm_seed)
            intrinsic_rng = random.Random(intrinsic_seed)
        else:
            storm_rng = random.Random()
            intrinsic_rng = random.Random()

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

            # Create the system. PROJ-473: physics_rng drives star+planet
            # PHYSICS (H7 S4/S5, star-then-planet order preserved); image_rng
            # is a separate stream for image_id/rotation (H7 S6/S7).
            name = self._naming.get_system_name()
            stars = self._star_gen.generate_system_stars(
                name, rng=physics_rng, image_rng=image_rng
            )

            sys = StarSystem(name, coord, stars=stars)
            # PROJ-301/302: intrinsic_rng for ability rolls (S3, distinct
            # stream); physics_rng/image_rng for planet physics + images.
            self.generate_planets(
                galaxy, sys, rng=intrinsic_rng,
                physics_rng=physics_rng, image_rng=image_rng,
            )

            # Generate storms after planets (PROJ-189)
            if storm_blueprint_config is not None:
                self.generate_storms(sys, storm_blueprint_config, storm_rng)

            # PROJ-304: roll system archetype + intrinsic abilities (~15% by default).
            # Uses intrinsic_rng (separate stream from storm_rng) so storm
            # generation parameters don't shift archetype roll sequence.
            _apply_system_archetype(sys, intrinsic_rng)

            galaxy.add_system(sys)
            generated.append(sys)

            # Update spatial index and existing coords incrementally
            spatial_index.add(coord, None)
            existing_coords.add(coord)

        return generated


# PROJ-319 (DUP-X-11): shared lazy JSON loader for the three module-level
# caches below. Returns the parsed JSON (optionally narrowed to a sub-key) or
# an empty dict if the file is missing.
def _load_json_or_empty(path_value: Any, dict_key: Optional[str] = None) -> Dict[str, Any]:
    # PROJ-381 Phase 3 (ERR-04-003 + ERR-04-008): route through
    # canonical json_utils so missing-file / corrupt-JSON / OSError
    # all collapse into the same default-{} graceful-degradation
    # contract. Drops the manual `path.exists()` guard since
    # `load_json` already handles missing files.
    from game.core.json_utils import load_json

    data = load_json(path_value, default={})
    if dict_key is None:
        return data
    return data.get(dict_key, {})


# PROJ-301 — module-level helper. Loads planet_types.json once on first call
# and rolls each planet's intrinsic abilities according to its planet_type.
_PLANET_TYPES_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def _reset_galaxy_generator_caches() -> None:
    """Drop the three JSON-backed caches in this module.

    Wired into `game.data_loader` so a mod that ships its own
    planet_types.json / star_types.json / system_archetypes.json takes
    effect after a data-set switch.
    """
    global _PLANET_TYPES_CACHE, _STAR_TYPES_CACHE, _SYSTEM_ARCHETYPES_CACHE
    _PLANET_TYPES_CACHE = None
    _STAR_TYPES_CACHE = None
    _SYSTEM_ARCHETYPES_CACHE = None


def _load_planet_types() -> Dict[str, Dict[str, Any]]:
    global _PLANET_TYPES_CACHE
    if _PLANET_TYPES_CACHE is None:
        from game.core.paths import Paths
        _PLANET_TYPES_CACHE = _load_json_or_empty(Paths.PLANET_TYPES_FILE, 'planet_types')
    return _PLANET_TYPES_CACHE


def _apply_intrinsic_abilities(
    entities: List[Any],
    types_data: Dict[str, Dict[str, Any]],
    get_type_key: Any,
    rng: Optional[random.Random] = None,
) -> None:
    """Shared roller for intrinsic abilities (DUP-X-12 consolidation).

    Idempotent: entities with non-empty `intrinsic_abilities` are left alone
    (e.g. for hand-crafted scenario entities). Caller-supplied seeded RNG
    threads determinism through galaxy generation; defaults to an unseeded
    `Random()` for back-compat.
    """
    from game.strategy.services.ability_sources import roll_intrinsic_abilities

    if not types_data:
        return
    if rng is None:
        rng = random.Random()
    for entity in entities:
        if entity.intrinsic_abilities:
            continue
        type_key = get_type_key(entity)
        template = types_data.get(type_key, {}).get('abilities', {})
        if not template:
            continue
        entity.intrinsic_abilities = roll_intrinsic_abilities(template, rng)


def _apply_planet_intrinsic_abilities(
    planets: List['Planet'],
    rng: Optional[random.Random] = None,
) -> None:
    """Roll intrinsic abilities for each planet from data/planet_types.json (PROJ-301).

    Thin wrapper over `_apply_intrinsic_abilities`.
    """
    _apply_intrinsic_abilities(
        planets, _load_planet_types(), lambda p: p.planet_type.name, rng,
    )


# PROJ-302 — module-level star intrinsics helper.
_STAR_TYPES_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def _load_star_types() -> Dict[str, Dict[str, Any]]:
    global _STAR_TYPES_CACHE
    if _STAR_TYPES_CACHE is None:
        from game.core.paths import Paths
        _STAR_TYPES_CACHE = _load_json_or_empty(Paths.STAR_TYPES_FILE, 'star_types')
    return _STAR_TYPES_CACHE


def _apply_star_intrinsic_abilities(
    stars: List[Any],
    rng: Optional[random.Random] = None,
) -> None:
    """PROJ-302: roll intrinsic abilities for each star from data/star_types.json.

    Thin wrapper over `_apply_intrinsic_abilities`.
    """
    _apply_intrinsic_abilities(
        stars, _load_star_types(), lambda s: s.star_type.name, rng,
    )


# PROJ-304 — module-level system archetype helper.
_SYSTEM_ARCHETYPES_CACHE: Optional[Dict[str, Any]] = None


def _load_system_archetypes() -> Dict[str, Any]:
    global _SYSTEM_ARCHETYPES_CACHE
    if _SYSTEM_ARCHETYPES_CACHE is None:
        from game.core.paths import Paths
        _SYSTEM_ARCHETYPES_CACHE = _load_json_or_empty(Paths.SYSTEM_ARCHETYPES_FILE)
    return _SYSTEM_ARCHETYPES_CACHE


def _apply_system_archetype(system: Any, rng: random.Random) -> None:
    """PROJ-304: roll a system archetype with ~15% probability."""
    from game.strategy.services.ability_sources import roll_intrinsic_abilities

    data = _load_system_archetypes()
    if not data:
        return

    chance = float(data.get('archetype_chance', 0.15))
    archetypes = data.get('archetypes', {})
    if not archetypes:
        return

    # Idempotent: respect pre-set archetype from scenarios.
    if system.archetype is not None:
        return
    if rng.random() > chance:
        return

    # Uniform random pick (no weighting). Skip 'void' which is intentionally empty.
    keys = [k for k in archetypes.keys() if k != 'void']
    if not keys:
        return
    pick = rng.choice(keys)
    system.archetype = pick
    template = archetypes[pick].get('abilities', {})
    if template:
        system.intrinsic_abilities = roll_intrinsic_abilities(template, rng)


# Self-register the cache reset with the data lifecycle (mode-scoped
# data-set switches reset planet/star/archetype JSON caches).
from game.data_loader import register_data_cache_invalidator as _register_data_cache_invalidator
_register_data_cache_invalidator(_reset_galaxy_generator_caches)
