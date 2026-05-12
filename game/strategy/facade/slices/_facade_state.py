"""Shared mutable state for `StrategySessionFacade` slices (PROJ-309 sub-phase 3.7).

`FacadeSessionState` holds the session reference and the per-turn caches that
multiple slices need to share. Slices receive a `FacadeSessionState` at
construction and never reach across to each other — all cross-domain lookups
funnel through this object.

The `_get_<X>_by_id` helpers also live here because (a) several slices need
them and (b) the planet-id lookup owns the `_planet_index` cache that
`tests/unit/strategy/facade/test_facade_indices.py` asserts on.

The composer (`StrategySessionFacade`) exposes the cache attributes
(`_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache`, `_race_registry`)
via property forwarders so existing tests that read/write them on the facade
keep working.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.data.design_metadata import DesignMetadata
    from game.strategy.engine.game_session import GameSession
    from game.strategy.facade.dto import StarInfo


class FacadeSessionState:
    """Shared mutable state injected into every facade slice.

    Owns the session reference plus the four per-turn caches that the
    pre-split monolithic facade kept as instance attributes:
    `_planet_index`, `_all_stars_cache` (+ its turn stamp),
    `_fleets_by_hex_cache` (+ its turn stamp), and the lazily-built
    `_race_registry`.

    The cache fields here use the same names as the pre-split facade
    attributes (with a leading underscore) so slice code reads natural,
    even though the composer's @property forwarders are what tests touch
    when they assign `facade._planet_index = {...}`.
    """

    def __init__(self, session: "GameSession") -> None:
        self.session = session
        # PROJ-254: lazy index caches for O(1) lookups.
        self.planet_index: Optional[dict] = None  # id -> Planet
        self.all_stars_cache: Optional[List["StarInfo"]] = None
        self.all_stars_cache_turn: int = -1
        self.fleets_by_hex_cache: Optional[dict] = None  # HexCoord -> [Fleet]
        self.fleets_by_hex_turn: int = -1
        # PROJ-287: lazy-init session-scoped race registry.
        self.race_registry: Optional["IRaceRegistry"] = None
        # PROJ-411 Phase 1: per-turn UI caches. Cleared by invalidate_all()
        # at every turn boundary. Caches by empire_id where applicable.
        # DesignLibrary.scan_designs results, keyed by empire_id.
        self.designs_by_empire: Dict[int, List["DesignMetadata"]] = {}
        # gather_planets() result, keyed by empire_id (different empires may
        # see different filter views — keep per-empire to be safe).
        self.planets_for_empire_cache: Dict[int, list] = {}
        # gather_stars() raw star list. Galaxy-wide; not per-empire.
        # Distinct from `all_stars_cache` which holds DTO objects.
        self.stars_cache_new: Optional[list] = None
        # EmpireEconomyService.get_snapshot() result, keyed by empire_id.
        self.empire_economy_snapshot: Dict[int, Any] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def invalidate_all(self) -> None:
        """Clear every per-turn cache. Called by `process_turn`."""
        self.fleets_by_hex_cache = None
        self.planet_index = None
        self.all_stars_cache = None
        # PROJ-411 Phase 1 per-turn UI caches.
        self.designs_by_empire.clear()
        self.planets_for_empire_cache.clear()
        self.stars_cache_new = None
        self.empire_economy_snapshot.clear()

    # ------------------------------------------------------------------
    # ID lookups (cache-owning)
    # ------------------------------------------------------------------

    def get_fleet_by_id(self, fleet_id: int) -> Optional["Fleet"]:
        """Look up a fleet by ID across all empires.

        Delegates to `GameSession._get_fleet_by_id()` for O(1) lookup with
        fallback.
        """
        return self.session._get_fleet_by_id(fleet_id)

    def get_empire_by_id(self, empire_id: int) -> Optional["Empire"]:
        """Look up an empire by ID via linear scan."""
        for empire in self.session.empires:
            if empire.id == empire_id:
                return empire
        return None

    def build_planet_index(self) -> dict:
        """Build planet-id -> Planet lookup dict (PROJ-254)."""
        index: dict = {}
        for system in self.session.galaxy.systems.values():
            for planet in system.planets:
                index[planet.id] = planet
        return index

    def get_planet_by_id(self, planet_id: int) -> Optional["Planet"]:
        """Look up a planet by ID using the lazy index (PROJ-254)."""
        if self.planet_index is None:
            self.planet_index = self.build_planet_index()
        return self.planet_index.get(planet_id)
