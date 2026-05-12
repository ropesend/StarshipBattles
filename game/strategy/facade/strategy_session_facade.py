"""Strategy Session Facade.

Provides a strict facade for UI-to-engine communication using CQRS-lite
pattern. All state mutations go through Commands, all reads return immutable
DTOs.

PROJ-309 sub-phase 3.7: this file is the **composer** for a set of internal
slice classes living in :mod:`game.strategy.facade.slices`. The composer keeps
the original public surface of `StrategySessionFacade` (53 public methods plus
the underscore-prefixed members downstream tests reach into) — every public
method is a one-line forwarder to the appropriate slice. Slices share a
`FacadeSessionState` and never reach into each other.

Callers MUST NOT depend on the slice layout — slices are an implementation
detail.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import (
    BuildQueueSourceDTO,
    ColonyDemographicView,
    ColonySummary,
    EmpireInfo,
    FleetInfo,
    FleetSummary,
    PlanetInfo,
    StarInfo,
    SystemInfo,
)
from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.strategy.facade.slices.command_dispatch_slice import CommandDispatchSlice
from game.strategy.facade.slices.economy_slice import EconomySlice
from game.strategy.facade.slices.empire_slice import EmpireSlice
from game.strategy.facade.slices.event_slice import EventSlice
from game.strategy.facade.slices.fleet_slice import FleetSlice
from game.strategy.facade.slices.planet_slice import PlanetSlice
from game.strategy.facade.slices.system_slice import SystemSlice

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.engine.commands import Command
    from game.strategy.engine.game_session import GameSession
    from game.core.registry import GameRegistries


class StrategySessionFacade:
    """Facade for UI interaction with the strategy game session.

    This facade provides the single point of access for all UI-to-engine
    communication, implementing a CQRS-lite pattern:

    - Commands (writes): state mutations via :meth:`handle_command` and the
      28 ``dispatch_*`` helpers.
    - Queries (reads): return immutable DTOs, never domain objects.

    The UI layer should never access GameSession internals directly. All
    domain objects are converted to DTOs before being returned.

    Internally the facade composes seven slices (PROJ-309 sub-phase 3.7):
    command-dispatch, fleet, planet, system, empire, economy, and event.
    The slices share a :class:`FacadeSessionState` that owns the per-turn
    caches and the cached id-lookup helpers. Public methods on this class
    are one-line forwarders to the appropriate slice — the public API is
    unchanged from the pre-split monolithic facade.

    Tests asserting on private cache attributes (``_planet_index``,
    ``_fleets_by_hex_cache``, ``_all_stars_cache``, ``_race_registry``)
    continue to work via @property forwarders that read/write the same
    fields on :class:`FacadeSessionState`.
    """

    def __init__(self, session: "GameSession") -> None:
        """Initialize the facade with a GameSession.

        Args:
            session: The GameSession instance to wrap.
        """
        self._session = session
        self._state = FacadeSessionState(session)
        # Slice construction order is irrelevant — every slice depends only
        # on the shared `_state`.
        self._command_slice = CommandDispatchSlice(
            self._state,
            handle_command=lambda cmd: self.handle_command(cmd),
        )
        self._fleet_slice = FleetSlice(self._state)
        self._planet_slice = PlanetSlice(self._state)
        self._system_slice = SystemSlice(self._state)
        self._empire_slice = EmpireSlice(self._state)
        self._economy_slice = EconomySlice(self._state)
        self._event_slice = EventSlice(self._state)

    @property
    def facade_state(self) -> FacadeSessionState:
        """PROJ-411 Phase 1: public accessor for the per-turn cache holder.

        UI-side callers (Build Queue, Workshop, etc.) can pass this into
        ``DesignLibrary(facade_state=...)`` and similar collaborators so
        their per-turn caches are shared across opens within one turn.
        Engine-side code (turn engines, order processors) should NOT use
        this — it runs inside the turn loop where the cache is irrelevant
        and may even mask state-mutation bugs.
        """
        return self._state

    # =========================================================================
    # Cache attribute forwarders (read+write) — preserved for legacy tests
    # =========================================================================

    @property
    def _planet_index(self) -> Optional[dict]:
        return self._state.planet_index

    @_planet_index.setter
    def _planet_index(self, value: Optional[dict]) -> None:
        self._state.planet_index = value

    @property
    def _all_stars_cache(self) -> Optional[List[StarInfo]]:
        return self._state.all_stars_cache

    @_all_stars_cache.setter
    def _all_stars_cache(self, value: Optional[List[StarInfo]]) -> None:
        self._state.all_stars_cache = value

    @property
    def _all_stars_cache_turn(self) -> int:
        return self._state.all_stars_cache_turn

    @_all_stars_cache_turn.setter
    def _all_stars_cache_turn(self, value: int) -> None:
        self._state.all_stars_cache_turn = value

    @property
    def _fleets_by_hex_cache(self) -> Optional[dict]:
        return self._state.fleets_by_hex_cache

    @_fleets_by_hex_cache.setter
    def _fleets_by_hex_cache(self, value: Optional[dict]) -> None:
        self._state.fleets_by_hex_cache = value

    @property
    def _fleets_by_hex_turn(self) -> int:
        return self._state.fleets_by_hex_turn

    @_fleets_by_hex_turn.setter
    def _fleets_by_hex_turn(self, value: int) -> None:
        self._state.fleets_by_hex_turn = value

    @property
    def _race_registry(self) -> Optional["IRaceRegistry"]:
        return self._state.race_registry

    @_race_registry.setter
    def _race_registry(self, value: Optional["IRaceRegistry"]) -> None:
        self._state.race_registry = value

    # =========================================================================
    # COMMANDS (Write Path)
    # =========================================================================

    def handle_command(self, command: "Command") -> ValidationResult:
        """Execute a command against the game session.

        All state mutations should go through this method. The command is
        validated and executed by the underlying GameSession.
        """
        return self._session.handle_command(command)

    def process_turn(
        self,
        *,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """Process the current turn.

        Advances the game state by one turn, executing all queued orders,
        resolving movement, and processing AI actions. PROJ-254: invalidates
        every per-turn cache after the session advances.

        PROJ-381 Phase 3 (B-4): catches the domain-engine
        :class:`EnginePhaseError` and re-raises as a facade-level
        :class:`TurnFailedError` so the UI never has to import a
        sub-engine exception type. The original error is preserved on
        ``__cause__`` and the same context dict travels through.

        Args:
            progress_callback: Issue #7 — optional per-tick callback
                ``(current_tick, total_ticks)`` forwarded to the underlying
                ``GameSession.process_turn`` so the strategy screen can
                repaint the "PROCESSING TURN..." overlay between ticks.

        Raises:
            TurnFailedError: If a sub-engine phase failure escaped the
                rollback boundary in ``GameSession.process_turn``.
        """
        from game.core.exceptions import EnginePhaseError, TurnFailedError

        try:
            self._session.process_turn(progress_callback=progress_callback)
        except EnginePhaseError as e:
            raise TurnFailedError(
                message=str(e),
                code=e.code,
                context=dict(e.context or {}),
            ) from e
        self._state.invalidate_all()

    # --- Command dispatch helpers ---
    #
    # PROJ-371 Phase 2: 31 hand-written ``dispatch_*`` forwarders
    # (~150 LOC) collapsed to a class-level loop that derives one bound
    # method per ``CommandSpec.facade_helper_name`` from
    # ``command_registry``. The loop runs once at module import (see
    # ``_install_dispatch_forwarders`` below) so the methods exist on
    # ``StrategySessionFacade`` itself — ``hasattr(class, name)`` and
    # ``inspect.getmembers`` both see them, and tests can monkey-patch
    # ``facade.dispatch_X = MagicMock(...)`` at instance scope.

    # =========================================================================
    # QUERIES (Read Path) — Return DTOs only, never domain objects
    # =========================================================================

    # --- Internal id-lookup helpers (consumed by tests) ---

    def _get_fleet_by_id(self, fleet_id: int) -> Optional["Fleet"]:
        """Internal helper to get a fleet by ID across all empires.

        Delegates to ``GameSession._get_fleet_by_id()`` for O(1) lookup with
        fallback.
        """
        return self._state.get_fleet_by_id(fleet_id)

    def _get_empire_by_id(self, empire_id: int) -> Optional["Empire"]:
        """Internal helper to get an empire by ID."""
        return self._state.get_empire_by_id(empire_id)

    def _get_planet_by_id(self, planet_id: int) -> Optional["Planet"]:
        """Internal helper to get a planet by ID using index (PROJ-254)."""
        return self._state.get_planet_by_id(planet_id)

    def _build_planet_index(self) -> dict:
        """Build planet ID -> Planet lookup dict (PROJ-254)."""
        return self._state.build_planet_index()

    def _build_fleet_hex_index(self) -> dict:
        """Build HexCoord -> [Fleet] lookup dict (PROJ-254)."""
        return self._fleet_slice.build_fleet_hex_index()

    # --- Fleet queries ---

    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]:
        """Get fleet information by ID."""
        return self._fleet_slice.get_fleet(fleet_id)

    def get_fleets_at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]:
        """Get all fleets at a specific hex coordinate."""
        return self._fleet_slice.get_fleets_at_hex(hex_coord)

    def get_fleet_path_preview(
        self, fleet_id: int, target_hex: HexCoord
    ) -> Optional[List[HexCoord]]:
        """Calculate a path preview for a fleet to a target."""
        return self._fleet_slice.get_fleet_path_preview(fleet_id, target_hex)

    def get_fleet_path_projection(
        self, fleet_id: int, max_turns: int = 50
    ) -> List[dict]:
        """Get turn-by-turn path projection for a fleet."""
        return self._fleet_slice.get_fleet_path_projection(fleet_id, max_turns)

    def get_fleet_remaining_pods(self, fleet_id: int) -> dict:
        """Get remaining colony pods for a fleet (available minus committed)."""
        return self._fleet_slice.get_fleet_remaining_pods(fleet_id)

    # --- System / star / map queries ---

    def get_all_systems(self) -> List[SystemInfo]:
        """Get information about all star systems."""
        return self._system_slice.get_all_systems()

    def get_all_stars(self) -> List[StarInfo]:
        """Get information about all stars in the galaxy."""
        return self._system_slice.get_all_stars()

    def get_system_at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]:
        """Get the system at a specific hex coordinate."""
        return self._system_slice.get_system_at_hex(hex_coord)

    def get_system_containing_fleet(self, fleet_id: int) -> Optional[SystemInfo]:
        """Get the system containing (or closest to) the fleet."""
        return self._system_slice.get_system_containing_fleet(fleet_id)

    def get_system_near_hex(
        self, hex_coord: HexCoord, max_dist: int = 8
    ) -> Optional[SystemInfo]:
        """Get the system at or near the given hex coordinate."""
        return self._system_slice.get_system_near_hex(hex_coord, max_dist)

    def get_storm_names_at_hex(self, hex_coord: HexCoord) -> List[str]:
        """Get storm names affecting a global hex coordinate."""
        return self._system_slice.get_storm_names_at_hex(hex_coord)

    # --- Planet queries ---

    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID."""
        return self._planet_slice.get_planet(planet_id)

    def get_planets_at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position exactly matches the given hex."""
        return self._planet_slice.get_planets_at_hex(hex_coord)

    # --- Empire queries ---

    def get_all_empires(self) -> List[EmpireInfo]:
        """Get information about all empires."""
        return self._empire_slice.get_all_empires()

    def get_empire(self, empire_id: int) -> Optional[EmpireInfo]:
        """Get empire information by ID."""
        return self._empire_slice.get_empire(empire_id)

    def get_empire_colonies(self, empire_id: int) -> List[ColonySummary]:
        """Get colony summaries for an empire."""
        return self._empire_slice.get_empire_colonies(empire_id)

    def get_empire_fleets(self, empire_id: int) -> List[FleetSummary]:
        """Get fleet summaries for an empire."""
        return self._empire_slice.get_empire_fleets(empire_id)

    def get_empire_build_queues(self, empire_id: int) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources for an empire."""
        return self._empire_slice.get_empire_build_queues(empire_id)

    def get_hex_build_queues(
        self, empire_id: int, hex_coord: HexCoord
    ) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources at a hex for a specific empire."""
        return self._empire_slice.get_hex_build_queues(empire_id, hex_coord)

    # --- Game state queries ---

    def get_human_player_ids(self) -> List[int]:
        """Get the empire IDs of human players."""
        return self._event_slice.get_human_player_ids()

    def get_turn_number(self) -> int:
        """Get the current turn number (1-indexed)."""
        return self._event_slice.get_turn_number()

    def get_save_path(self) -> Optional[str]:
        """Get the current save game file path, or None if not yet saved."""
        return self._event_slice.get_save_path()

    # --- Demographics / economy / races ---

    def get_colony_demographic_view(
        self, planet_id: int
    ) -> Optional[ColonyDemographicView]:
        """One-shot snapshot of a colony's per-species + per-resource state."""
        return self._economy_slice.get_colony_demographic_view(planet_id)

    def _resolve_economy_config(self):  # pragma: no cover — internal helper
        """Pull the active EconomyConfig from the session (legacy alias)."""
        return self._economy_slice.resolve_economy_config()

    def get_race_registry(self) -> "IRaceRegistry":
        """Get the session-scoped race registry (PROJ-287)."""
        return self._economy_slice.get_race_registry()

    def get_registries(self) -> "GameRegistries":
        """Get the session-scoped game registries (PROJ-382 Phase 1).

        UI screens that need to call helpers expecting ``registries=`` (e.g.
        ``collect_build_queues_at_hex``) pull the bundle through the facade
        rather than reaching into ``session.registries`` directly.  Read-only
        access — callers must not mutate the returned object.
        """
        return self._session.registries

    # --- Event log queries (PROJ-77; BUG-123 per-empire scoping) ---

    def get_turn_events(
        self, turn: Optional[int] = None, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Get events for a specific turn (or current turn if None).

        ``empire_id`` (BUG-123): when not None, scope to that empire's
        view; global events (``empire_id == -1``) are included.
        """
        return self._event_slice.get_turn_events(turn, empire_id=empire_id)

    def get_all_events(self, *, empire_id: Optional[int] = None) -> List[dict]:
        """Get all events from the event log.

        ``empire_id`` (BUG-123): see :meth:`get_turn_events`.
        """
        return self._event_slice.get_all_events(empire_id=empire_id)

    def get_events_by_category(
        self, category: str, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Get events filtered by category.

        ``empire_id`` (BUG-123): see :meth:`get_turn_events`.
        """
        return self._event_slice.get_events_by_category(
            category, empire_id=empire_id
        )

    # --- Validation queries ---

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet (validation only)."""
        return self._planet_slice.can_colonize(fleet_id, planet_id)

    def can_move_to(self, fleet_id: int, target_hex: HexCoord) -> ValidationResult:
        """Check if a fleet can move to a target hex by previewing a path."""
        return self._fleet_slice.can_move_to(fleet_id, target_hex)


# ---------------------------------------------------------------------------
# PROJ-371 Phase 2 — auto-install ``dispatch_*`` forwarders on the class.
# ---------------------------------------------------------------------------
#
# Each spec's ``facade_helper_name`` becomes a bound method that proxies to
# the same name on ``self._command_slice``. The slice's ``__getattr__``
# resolver looks the spec up in ``command_registry.specs_by_facade_helper()``
# and returns a closure that instantiates the Command DTO from kwargs and
# forwards to ``handle_command``.
#
# Defining the methods on the class (not via ``__getattr__``) keeps them
# visible to ``hasattr(StrategySessionFacade, name)``, ``inspect.getmembers``,
# and the public-API contract test in
# ``tests/unit/strategy/facade/test_strategy_session_facade_public_api.py``.

def _install_dispatch_forwarders() -> None:
    from game.strategy.engine.commands.registry import (
        command_registry,
        seed_default_commands,
    )

    if len(command_registry) == 0:
        seed_default_commands(command_registry)

    def _make_forwarder(helper_name: str):
        def _dispatch(self, **kwargs) -> ValidationResult:
            return getattr(self._command_slice, helper_name)(**kwargs)

        _dispatch.__name__ = helper_name
        _dispatch.__qualname__ = f"StrategySessionFacade.{helper_name}"
        _dispatch.__doc__ = (
            f"Helper to dispatch the Command associated with "
            f"facade_helper_name={helper_name!r} (PROJ-371)."
        )
        return _dispatch

    for spec in command_registry.all():
        helper = spec.facade_helper_name
        if helper is None:
            continue
        if not hasattr(StrategySessionFacade, helper):
            setattr(StrategySessionFacade, helper, _make_forwarder(helper))


_install_dispatch_forwarders()
