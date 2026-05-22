"""Shared mutable state for `StrategySessionFacade` slices (PROJ-309 sub-phase 3.7).

`FacadeSessionState` holds the session reference and the per-turn caches that
multiple slices need to share. Slices receive a `FacadeSessionState` at
construction and never reach across to each other — all cross-domain lookups
funnel through this object.

The `_get_<X>_by_id` helpers also live here because (a) several slices need
them and (b) the planet-id lookup owns the `_planet_index` cache that
`tests/unit/strategy/facade/test_facade_indices.py` asserts on.

PROJ-430 / TD-08: ``seed_*`` public helpers replace the legacy
``facade._planet_index = {...}`` write-through pattern. Tests call
``facade.facade_state.seed_planet_index({...})`` (or ``seed_race_registry(...)``)
to inject cache state explicitly. The ``seed_`` prefix makes the test-only
intent visible at the call site so the helpers aren't confused with
production seeding paths.
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
    from game.strategy.systems.design_catalog import DesignCatalog
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

    **Intentional performance boundary** (PROJ-438 Phase 2 — pinned by
    ``tests/unit/strategy/engine/test_game_session_projection_boundary.py
    ::TestFacadeCacheHolderIsDocumentedPerformanceBoundary``):

    This cache holder is NOT compensation debt for a missing query model;
    it is a kept-by-design performance boundary. The per-turn caches
    (``planet_index``, ``all_stars_cache``, ``fleets_by_hex_cache``, plus
    the per-empire caches added by PROJ-411) cut quadratic UI work to
    linear on hot paths like ``planet_list_window`` and
    ``fleet_report_ctrl``. ``invalidate_all`` clears every cache at each
    turn boundary, so freshness is bounded by one turn. Do not remove or
    inline these caches without an equivalent or better performance
    boundary in place.
    """

    def __init__(self, session: "GameSession") -> None:
        self.session = session
        # PROJ-254: lazy index caches for O(1) lookups.
        self.planet_index: Optional[dict] = None  # id -> Planet
        self.empire_index: Optional[Dict[int, "Empire"]] = None  # F-A-031
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
        self.empire_index = None
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
        """Look up an empire by ID using the lazy empire-index (F-A-031)."""
        if self.empire_index is None:
            self.empire_index = {e.id: e for e in self.session.empires}
        return self.empire_index.get(empire_id)

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

    # ------------------------------------------------------------------
    # Per-empire designs (PROJ-434 Phase 0)
    # ------------------------------------------------------------------

    def get_design_catalog_for_empire(self, empire_id: int) -> "Optional[DesignCatalog]":
        """Return the per-empire ``DesignCatalog`` object, or ``None``.

        PROJ-472 Phase 1C: UI callers (the build-queue manager) need the
        live ``DesignCatalog`` instance — not just its design list — because
        the build-queue screen writes through ``catalog.save_design`` and
        relies on the same instance's cache for the QA-Obs-3 contract.
        Routing through this accessor keeps the UI off the
        ``facade_state.session.services.design_catalogs_by_empire`` chain
        while preserving the exact object the prior bypass returned.
        Returns ``None`` when no catalog is wired for the empire (early
        bootstrap / tests).
        """
        services = getattr(self.session, "services", None)
        if services is None:
            return None
        catalogs = getattr(services, "design_catalogs_by_empire", None) or {}
        return catalogs.get(empire_id)

    def get_designs_for_empire(self, empire_id: int) -> List["DesignMetadata"]:
        """Return the per-empire ``DesignMetadata`` list via the session's
        ``DesignCatalog`` (PROJ-427 Phase 6 / PROJ-434 Phase 0).

        Routes through ``session.services.design_catalogs_by_empire[empire_id]``
        so workshop saves flowing through ``DesignCatalog.save_design``
        (which invalidates the catalog cache) are immediately visible to
        the same-empire viewer on the next read — the QA-Obs-3 cache
        contract. Returns ``[]`` when no catalog is wired for the
        requested empire (early bootstrap / tests).
        """
        services = getattr(self.session, "services", None)
        if services is None:
            return []
        catalogs = getattr(services, "design_catalogs_by_empire", None) or {}
        catalog = catalogs.get(empire_id)
        if catalog is None:
            return []
        return catalog.list_designs()

    # ------------------------------------------------------------------
    # Test-only seeding seam (PROJ-430 / TD-08 Phase 4)
    # ------------------------------------------------------------------
    #
    # The ``seed_*`` prefix is intentional: these methods are *only* for
    # tests that need to inject cache state without driving the full
    # production hydration path. Production code populates the same
    # caches through the slices' own lazy-init paths and must not call
    # these helpers.

    def seed_planet_index(self, mapping: dict) -> None:
        """Test-only: seed the planet-id -> Planet lookup cache.

        Replaces the legacy ``facade._planet_index = {...}`` write through
        path. Production code populates this cache via
        :meth:`get_planet_by_id` (lazy build); call sites of this helper
        should all be inside ``tests/``.
        """
        self.planet_index = mapping

    def seed_race_registry(self, registry: "IRaceRegistry") -> None:
        """Test-only: seed the session-scoped race registry.

        Replaces the legacy ``facade._race_registry = ...`` write-through
        path. Production code goes through
        :meth:`EconomySlice.get_race_registry` (lazy build of
        :class:`CachedRaceRegistry`); call sites of this helper should all
        be inside ``tests/``.
        """
        self.race_registry = registry
