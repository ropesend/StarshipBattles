from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from game.core.hex_math import HexCoord, hex_to_dict, hex_from_dict
from game.core.validation_helpers import require_keys, validate_positive
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
from game.strategy.data.naming import NameRegistry
from game.strategy.data.planet import Planet
from game.strategy.data.planet_gen import PlanetGenerator
from game.strategy.data.galaxy_state import GalaxyState
from game.strategy.generation.planet_image_registry import PlanetImageRegistry
from game.strategy.generation.star_image_registry import StarImageRegistry
from game.strategy.generation.storm_generator import StormGenerator
from game.strategy.generation.star_generator import StarGenerator
from game.strategy.data.galaxy_warp_generator import GalaxyWarpGenerator
from game.strategy.data.galaxy_system_generator import GalaxySystemGenerator
from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry
from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex
from game.core.json_utils import load_json
from game.core.paths import Paths

if TYPE_CHECKING:
    from game.strategy.generation.placement_strategies import ISystemPlacementStrategy
    from game.strategy.generation.region_classifier import RegionClassifier
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.star_system import StarSystem, WarpPoint


class Galaxy:
    """Facade over `GalaxyState` + entity / spatial / generation services.

    PROJ-372 Phase 3: state extracted to ``GalaxyState``; the four
    PROJ-173-Phase-2 delegates take ``self._state`` rather than
    ``self`` back-reference. Public attribute reads (``galaxy.systems``
    etc.) are preserved via ``@property`` forwarders.
    """

    def __init__(self, radius: int = 100, name_rng: Optional[random.Random] = None):
        """Initialize a galaxy.

        Args:
            radius: Galaxy radius in hex units.
            name_rng: Optional seeded RNG for the load-time system-name
                shuffle (PROJ-473 S8). Supplied here because the shuffle fires
                inside ``NameRegistry`` at construction (hazard H1); the
                composition root builds it from ``galaxy_seed``. When ``None``
                the shuffle uses an unseeded ``Random()`` without touching
                global module state.
        """
        self._state = GalaxyState(radius=radius)

        # Naming + image registries (heavy data loads — same as PROJ-173).
        self.naming = NameRegistry(Paths.STAR_SYSTEM_NAMES_FILE, rng=name_rng)
        self.star_image_registry = StarImageRegistry()
        self.star_generator = StarGenerator(image_registry=self.star_image_registry)
        self.image_registry = PlanetImageRegistry()
        self.planet_generator = PlanetGenerator(self.image_registry)

        storm_defs = load_json(Paths.STORMS_FILE, default={})
        self.storm_generator = StormGenerator(storm_defs) if storm_defs else None

        # Service delegates (PROJ-173 Phase 2 + PROJ-372 Phase 3-4).
        from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService
        from game.strategy.services.intercept_calculator import InterceptCalculator
        self._warp_gen = GalaxyWarpGenerator()
        self._sys_gen = GalaxySystemGenerator(
            self.star_generator, self.planet_generator, self.naming, self.image_registry,
            storm_generator=self.storm_generator,
        )
        self._registry = GalaxyEntityRegistry(self._state)
        self._spatial = GalaxySpatialIndex(self._state)
        self._pathfinder = GalaxyPathfindingService(self)

    # --- State property forwarders (public read-only access to GalaxyState) ---
    # PROJ-394 removed the 5 spatial private forwarders; new readers use ``Galaxy.state``.

    @property
    def state(self) -> GalaxyState:
        """Public access to the underlying ``GalaxyState``. Use this instead of ``_state`` for cross-module reads."""
        return self._state

    @property
    def radius(self) -> int:
        return self._state.radius

    @radius.setter
    def radius(self, value: int) -> None:
        self._state.radius = value

    @property
    def systems(self) -> Dict[HexCoord, 'StarSystem']:
        return self._state.systems

    @property
    def name_map(self) -> Dict[str, 'StarSystem']:
        return self._state.name_map

    @property
    def planets_by_id(self) -> Dict[int, 'Planet']:
        return self._state.planets_by_id

    @property
    def fleets_by_id(self) -> Dict[int, 'Fleet']:
        return self._state.fleets_by_id

    @property
    def _next_planet_id(self) -> int:
        return self._state.next_planet_id

    @_next_planet_id.setter
    def _next_planet_id(self, value: int) -> None:
        self._state.next_planet_id = value

    @property
    def _next_fleet_id(self) -> int:
        return self._state.next_fleet_id

    @_next_fleet_id.setter
    def _next_fleet_id(self, value: int) -> None:
        self._state.next_fleet_id = value

    # --- Public facade methods (1-line delegations) ---

    def add_system(self, system: 'StarSystem') -> None:
        """Add a system to the galaxy map (delegates to entity registry)."""
        self._registry.add_system(system)

    def get_system_by_name(self, name: str) -> Optional['StarSystem']:
        """O(1) name-keyed system lookup."""
        return self._state.name_map.get(name)

    def get_system_of_object(self, obj: Any) -> Optional['StarSystem']:
        """Find the system containing an object with a global location."""
        return self._spatial.get_system_of_object(obj)

    def register_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
        """Register a planet, assigning ID and updating indexes."""
        self._registry.register_planet(system, planet)

    def get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """O(1) lookup of planet by ID."""
        return self._registry.get_planet_by_id(planet_id)

    def get_system_of_planet(self, planet: 'Planet') -> Optional['StarSystem']:
        """O(1) reverse lookup: Planet -> StarSystem."""
        return self._spatial.get_system_of_planet(planet)

    def get_planets_at_global_hex(self, global_hex: 'HexCoord') -> List['Planet']:
        """O(1) spatial lookup: planets at a global hex."""
        return self._spatial.get_planets_at_global_hex(global_hex)

    def get_planet_global_hex(self, planet: 'Planet') -> Optional['HexCoord']:
        """O(1) lookup: planet's global hex coordinate."""
        return self._spatial.get_planet_global_hex(planet)

    def register_zone(self, system: 'StarSystem', obj) -> None:
        """Register a multi-hex zone object (PROJ-139)."""
        self._registry.register_zone(system, obj)

    def unregister_zone(self, system: 'StarSystem', obj) -> None:
        """Remove a multi-hex zone object."""
        self._registry.unregister_zone(system, obj)

    def get_zones_at_global_hex(self, global_hex: 'HexCoord') -> list:
        """O(1) spatial lookup: zones at a global hex."""
        return self._spatial.get_zones_at_global_hex(global_hex)

    def get_next_fleet_id(self) -> int:
        """Generate globally unique sequential fleet ID."""
        return self._registry.get_next_fleet_id()

    def register_fleet(self, fleet: 'Fleet') -> None:
        """Register a fleet for O(1) lookup by ID."""
        self._registry.register_fleet(fleet)

    def unregister_fleet(self, fleet: 'Fleet') -> None:
        """Remove a fleet from the registry."""
        self._registry.unregister_fleet(fleet)

    def get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """O(1) lookup of fleet by ID."""
        return self._registry.get_fleet_by_id(fleet_id)

    def unregister_planet(self, planet: 'Planet') -> None:
        """Remove a planet from all galaxy indexes and its parent system."""
        self._registry.unregister_planet(planet)

    def remove_warp_link(self, system_a_name: str, system_b_name: str) -> None:
        """Remove warp points connecting two systems. Handles missing systems."""
        system_a = self._state.name_map.get(system_a_name)
        system_b = self._state.name_map.get(system_b_name)

        if system_a is not None:
            for wp in system_a.warp_points:
                if wp.destination_id == system_b_name:
                    self._state.global_hex_warp_points.pop(
                        system_a.global_location + wp.location, None,
                    )
            system_a.warp_points = [
                wp for wp in system_a.warp_points if wp.destination_id != system_b_name
            ]

        if system_b is not None:
            for wp in system_b.warp_points:
                if wp.destination_id == system_a_name:
                    self._state.global_hex_warp_points.pop(
                        system_b.global_location + wp.location, None,
                    )
            system_b.warp_points = [
                wp for wp in system_b.warp_points if wp.destination_id != system_a_name
            ]

    def get_system_at_location(self, location: 'HexCoord') -> Optional['StarSystem']:
        """Find the star system containing a given global hex location (O(1))."""
        return self._spatial.get_system_at_location(location)

    def get_all_fleets_in_system(self, system: 'StarSystem', empires: List) -> List[tuple]:
        """All (empire, fleet) at any hex within `system`."""
        return self._spatial.get_all_fleets_in_system(system, empires)

    def generate_planets(
        self, system: 'StarSystem',
        rng: Optional[random.Random] = None,
        physics_rng: Optional[random.Random] = None,
        image_rng: Optional[random.Random] = None,
    ) -> None:
        """Generate planets for `system` based on its star type.

        PROJ-473 Task 3.3: backward-compatible facade — any ``None`` stream is
        normalized to a fresh per-instance ``Random()`` so the generation path
        never reads module-level ``random`` (no-rng callers are non-reproducible
        but never touch global state).
        """
        rng, physics_rng, image_rng = self._normalize_gen_rng(
            rng, physics_rng, image_rng
        )
        self._sys_gen.generate_planets(
            self, system, rng=rng, physics_rng=physics_rng, image_rng=image_rng,
        )

    @staticmethod
    def _normalize_gen_rng(
        rng: Optional[random.Random],
        physics_rng: Optional[random.Random],
        image_rng: Optional[random.Random],
    ) -> tuple[random.Random, random.Random, random.Random]:
        """PROJ-473 Task 3.3 single composition site: fill any missing seeded
        stream with a fresh per-instance ``Random()`` (distinct instances so
        they stay independent, mirroring the seeded production topology). The
        generation path therefore never falls back to module-level ``random``.
        """
        return (
            rng if rng is not None else random.Random(),
            physics_rng if physics_rng is not None else random.Random(),
            image_rng if image_rng is not None else random.Random(),
        )

    def generate_systems(
        self, count: int, min_dist: int = 10,
        placement_strategy: Optional['ISystemPlacementStrategy'] = None,
        rng: Optional[random.Random] = None,
        physics_rng: Optional[random.Random] = None,
        image_rng: Optional[random.Random] = None,
    ) -> List['StarSystem']:
        """Generate `count` systems with min hex distance, returns the list.

        PROJ-473: ``physics_rng`` is the dedicated star/planet physics stream
        (H7 S4/S5), distinct from placement ``rng`` (S1); ``image_rng`` is a
        separate image_id/rotation stream (H7 S6/S7) — NOT derived from
        physics_rng (that would shift the physics + S9 sequence). Task 3.3:
        ``None`` streams are normalized to fresh per-instance ``Random()`` at
        this single site so the generation path never reads module ``random``.
        """
        rng, physics_rng, image_rng = self._normalize_gen_rng(
            rng, physics_rng, image_rng
        )
        return self._sys_gen.generate_systems(
            self, count, min_dist, placement_strategy, rng,
            physics_rng=physics_rng, image_rng=image_rng,
        )

    def create_vars_link(self, sys_a: 'StarSystem', sys_b: 'StarSystem') -> None:
        """Create a warp link between two systems and index any new warp points."""
        wp_count_a = len(sys_a.warp_points)
        wp_count_b = len(sys_b.warp_points)

        # PROJ-473: runtime single-link seam (not the seeded generation path);
        # an independent unseeded Random() is correct here.
        self._warp_gen.create_warp_link(sys_a, sys_b, random.Random())

        # PROJ-179: index any newly created warp points.
        if len(sys_a.warp_points) > wp_count_a:
            wp = sys_a.warp_points[-1]
            self._state.global_hex_warp_points[sys_a.global_location + wp.location] = sys_a
        if len(sys_b.warp_points) > wp_count_b:
            wp = sys_b.warp_points[-1]
            self._state.global_hex_warp_points[sys_b.global_location + wp.location] = sys_b

    def add_warp_point(self, system: 'StarSystem', wp: 'WarpPoint') -> None:
        """Append a warp point at runtime and keep the global hex index in sync.

        Canonical seam for handlers that mutate the warp graph (#31). Mirrors
        the ``remove_warp_link`` pattern: list-append plus index update in a
        single call. Use this instead of writing ``system.warp_points.append(wp)``
        directly, otherwise consumers of ``state.global_hex_warp_points`` (warp
        validation, warp pathfinding, hex outline rendering, spatial index)
        silently misbehave around the new point.
        """
        system.warp_points.append(wp)
        self._state.global_hex_warp_points[system.global_location + wp.location] = system

    def generate_warp_lanes(
        self,
        region_classifier: 'Optional[RegionClassifier]' = None,
        inter_region_mode: str = 'normal',
        rng: Optional[random.Random] = None,
    ) -> None:
        """Generate warp lanes ensuring connectivity (MST) and adding density.

        PROJ-473 H7 S9/S10: ``rng`` is the CONTINUED ``physics_rng`` (the same
        instance threaded through stars/planets) so warp geometry (S9) stays
        byte-for-byte identical to the golden baseline and warp type/intrinsics
        (S10) become deterministic. Roots pass ``physics_rng`` — NOT a fresh
        warp rng. ``rng=None`` is normalized inside the warp generator.
        """
        self._warp_gen.generate_warp_lanes(
            self,
            region_classifier=region_classifier,
            inter_region_mode=inter_region_mode,
            rng=rng,
        )
        # PROJ-204: rebuild warp point index after bulk generation.
        self._registry.rebuild_all_warp_point_indices()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Galaxy to dict."""
        systems_list = [
            {'coord': hex_to_dict(coord), 'system': system.to_dict()}
            for coord, system in self._state.systems.items()
        ]
        return {
            'radius': self._state.radius,
            'systems': systems_list,
            '_next_planet_id': self._state.next_planet_id,
            '_next_fleet_id': self._state.next_fleet_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Galaxy':
        """Deserialize Galaxy from dict.

        Raises:
            PersistenceException: required key missing or radius non-positive,
            or any system entry corrupt (PROJ-251 strict).
        """
        # Local import: ``StarSystem`` lives in ``star_system`` (PROJ-372
        # Phase 3). Avoids module-level reference now that the re-export is
        # gone.
        from game.strategy.data.star_system import StarSystem

        require_keys(data, ['radius'], 'Galaxy')
        validate_positive(data['radius'], 'radius', 'Galaxy')

        galaxy = cls(radius=data['radius'])
        galaxy.state.next_planet_id = data.get('_next_planet_id', 1)
        galaxy.state.next_fleet_id = data.get('_next_fleet_id', 1)

        for i, sys_entry in enumerate(data.get('systems', [])):
            try:
                if 'coord' not in sys_entry:
                    raise PersistenceException(
                        f"Galaxy: system entry {i} missing 'coord'",
                        code=ErrorCode.CORRUPT_DATA.value,
                        context={"source": "Galaxy", "index": i, "missing_key": "coord"},
                    )
                if 'system' not in sys_entry:
                    raise PersistenceException(
                        f"Galaxy: system entry {i} missing 'system'",
                        code=ErrorCode.CORRUPT_DATA.value,
                        context={"source": "Galaxy", "index": i, "missing_key": "system"},
                    )

                coord = hex_from_dict(sys_entry['coord'])
                system = StarSystem.from_dict(sys_entry['system'])
            except (PersistenceException, KeyError, TypeError, ValueError) as e:
                raise PersistenceException(
                    f"Corrupt system data at index {i} in galaxy",
                    code=ErrorCode.CORRUPT_DATA.value,
                    context={"system_index": i, "original_error": str(e)},
                ) from e

            # PROJ-372 review MAJ-002: route through `add_system` (owns
            # state + zone + warp-point index rebuild) — keeps
            # `from_dict` from drifting if the registration block grows.
            assert system.global_location == coord, (
                f"system entry {i} coord/global_location mismatch"
            )
            galaxy._registry.add_system(system)

            for planet in system.planets:
                galaxy._registry.restore_planet(system, planet)

        return galaxy
