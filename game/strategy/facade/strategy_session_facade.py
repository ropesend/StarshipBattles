"""Strategy Session Facade (PROJ-430 / TD-08 target shape).

Provides a strict facade for UI-to-engine communication using a CQRS-lite
pattern. All state mutations go through Commands, all reads return immutable
DTOs.

Post-TD-08 surface:

- 2 top-level callables: :meth:`handle_command`, :meth:`process_turn`.
- 1 public attribute for the per-turn cache holder:
  :attr:`facade_state`.
- 10 grouped namespace accessors, each returning a
  :class:`~game.strategy.facade.grouped_namespaces.*` wrapper around the
  corresponding slice: :attr:`commands`, :attr:`fleets`, :attr:`planets`,
  :attr:`systems`, :attr:`spatial`, :attr:`empires`, :attr:`events`,
  :attr:`session_meta`, :attr:`economy`, :attr:`validation`. (:attr:`spatial`
  is the PROJ-477 hex-contents read surface.)

The class composes eight slices (PROJ-309 sub-phase 3.7; PROJ-477 added the
spatial slice): command-dispatch, fleet, planet, system, spatial, empire,
economy, and event. The
slices share a :class:`FacadeSessionState` and never reach across to each
other. Callers MUST NOT depend on the slice layout — slices are an
implementation detail; the grouped namespace wrappers are the stable
boundary.

Cache state on :class:`FacadeSessionState` is private to the slices; tests
that need to inject cache state use the public ``seed_*`` helpers on the
session state (e.g. ``facade.facade_state.seed_planet_index({...})``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from game.core.validation import ValidationResult
from game.strategy.facade.grouped_namespaces import (
    FacadeCommands,
    FacadeEconomyQueries,
    FacadeEmpireQueries,
    FacadeEventQueries,
    FacadeFleetQueries,
    FacadePlanetQueries,
    FacadeSessionInfo,
    FacadeSpatialQueries,
    FacadeSystemQueries,
    FacadeValidation,
)
from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.strategy.facade.slices.command_dispatch_slice import CommandDispatchSlice
from game.strategy.facade.slices.economy_slice import EconomySlice
from game.strategy.facade.slices.empire_slice import EmpireSlice
from game.strategy.facade.slices.event_slice import EventSlice
from game.strategy.facade.slices.fleet_slice import FleetSlice
from game.strategy.facade.slices.planet_slice import PlanetSlice
from game.strategy.facade.slices.spatial_slice import SpatialSlice
from game.strategy.facade.slices.system_slice import SystemSlice

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.engine.commands import Command
    from game.strategy.engine.game_session import GameSession


class StrategySessionFacade:
    """Facade for UI interaction with the strategy game session.

    Post-TD-08 surface:
    - Two top-level write entry points: :meth:`handle_command` and
      :meth:`process_turn`.
    - Nine grouped namespace accessors (see module docstring) plus
      :attr:`facade_state`.

    Architectural invariant (TD-08): new methods land on a grouped
    namespace, not on this class. The two top-level callables are the only
    behavioral entry points that survive at the top level. Cache state on
    ``FacadeSessionState`` is private to the slices; tests use the public
    ``seed_*`` helpers there.
    """

    def __init__(self, session: "GameSession") -> None:
        """Initialize the facade with a GameSession.

        Args:
            session: The GameSession instance to wrap.
        """
        self._session = session
        self._state = FacadeSessionState(session)
        # Slice construction order is irrelevant — every slice depends only
        # on the shared ``_state``.
        self._command_slice = CommandDispatchSlice(
            self._state,
            handle_command=lambda cmd: self.handle_command(cmd),
        )
        self._fleet_slice = FleetSlice(self._state)
        self._planet_slice = PlanetSlice(self._state)
        self._system_slice = SystemSlice(self._state)
        self._spatial_slice = SpatialSlice(self._state)
        self._empire_slice = EmpireSlice(self._state)
        self._economy_slice = EconomySlice(self._state)
        self._event_slice = EventSlice(self._state)

        # PROJ-430 Phase 2: grouped namespace accessors. Each wraps the
        # corresponding slice and exposes the renamed, prefix-stripped
        # verb set. The legacy flat top-level helpers were root-cause
        # deleted in Phase 5.
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )

        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        helper_pairs = [
            (helper_name, spec.command_class)
            for helper_name, spec in command_registry.specs_by_facade_helper().items()
        ]

        self._commands = FacadeCommands(self._command_slice, helper_pairs)
        self._fleets = FacadeFleetQueries(self._fleet_slice)
        self._planets = FacadePlanetQueries(self._planet_slice)
        self._systems = FacadeSystemQueries(self._system_slice)
        self._spatial = FacadeSpatialQueries(self._spatial_slice)
        self._empires = FacadeEmpireQueries(self._empire_slice)
        self._events = FacadeEventQueries(self._event_slice)
        self._session_meta = FacadeSessionInfo(self._event_slice, session)
        self._economy = FacadeEconomyQueries(self._economy_slice)
        self._validation = FacadeValidation(self._fleet_slice, self._planet_slice)

    # =========================================================================
    # GROUPED NAMESPACE ACCESSORS (PROJ-430 / TD-08) — the only public read
    # surface. Each property returns the per-facade namespace wrapper
    # constructed in ``__init__``.
    # =========================================================================

    @property
    def commands(self) -> FacadeCommands:
        """Grouped command-dispatch surface (PROJ-430).

        Replaces the legacy top-level ``dispatch_*`` helpers; verbs are
        prefix-stripped (e.g. ``facade.commands.issue_move(...)``).
        """
        return self._commands

    @property
    def fleets(self) -> FacadeFleetQueries:
        """Grouped fleet read surface (PROJ-430)."""
        return self._fleets

    @property
    def planets(self) -> FacadePlanetQueries:
        """Grouped planet read surface (PROJ-430)."""
        return self._planets

    @property
    def systems(self) -> FacadeSystemQueries:
        """Grouped system / star / storm read surface (PROJ-430)."""
        return self._systems

    @property
    def spatial(self) -> FacadeSpatialQueries:
        """Grouped spatial / hex-contents read surface (PROJ-477 Phase 2)."""
        return self._spatial

    @property
    def empires(self) -> FacadeEmpireQueries:
        """Grouped empire read surface (PROJ-430)."""
        return self._empires

    @property
    def events(self) -> FacadeEventQueries:
        """Grouped event-log read surface (PROJ-430)."""
        return self._events

    @property
    def session_meta(self) -> FacadeSessionInfo:
        """Grouped session-metadata surface (turn, save path, humans)."""
        return self._session_meta

    @property
    def economy(self) -> FacadeEconomyQueries:
        """Grouped economy / demographics surface."""
        return self._economy

    @property
    def validation(self) -> FacadeValidation:
        """Grouped validation surface (PROJ-430)."""
        return self._validation

    @property
    def facade_state(self) -> FacadeSessionState:
        """PROJ-411 Phase 1: public accessor for the per-turn cache holder.

        UI-side callers (Build Queue, Workshop, etc.) can pass this into
        the per-empire ``DesignCatalog`` (PROJ-434 Phase 2) and similar
        collaborators so their per-turn caches are shared across opens
        within one turn.
        Engine-side code (turn engines, order processors) should NOT use
        this — it runs inside the turn loop where the cache is irrelevant
        and may even mask state-mutation bugs.

        Tests that need to inject cache state (e.g. seeding a planet
        index without driving the full hydration path) use the
        ``seed_*`` helpers on the returned state object — see
        ``FacadeSessionState.seed_planet_index`` / ``seed_race_registry``.
        """
        return self._state

    # =========================================================================
    # TOP-LEVEL ENTRY POINTS (the only callables that survive at the top
    # level after TD-08)
    # =========================================================================

    def handle_command(self, command: "Command") -> ValidationResult:
        """Execute a command against the game session.

        All state mutations should go through this method or the grouped
        ``commands`` namespace (which itself round-trips through this
        method). The command is validated and executed by the underlying
        GameSession.
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

    # =========================================================================
    # Internal id-lookup helpers (consumed by tests that go through
    # FacadeSessionState's caching path). These are underscore-prefixed
    # because they're internal — they survive Phase 5 because the
    # alternative (rewriting every test that calls ``facade._get_planet_by_id``
    # to construct a FacadeSessionState directly) would not collapse the
    # public surface any further. Tests that need to *write* to the
    # underlying caches use the public ``seed_*`` helpers on
    # ``FacadeSessionState``.
    # =========================================================================

    def _get_fleet_by_id(self, fleet_id: int) -> Optional["Fleet"]:
        """Internal helper: get a fleet by ID across all empires."""
        return self._state.get_fleet_by_id(fleet_id)

    def _get_empire_by_id(self, empire_id: int) -> Optional["Empire"]:
        """Internal helper: get an empire by ID."""
        return self._state.get_empire_by_id(empire_id)

    def _get_planet_by_id(self, planet_id: int) -> Optional["Planet"]:
        """Internal helper: get a planet by ID using the cached index."""
        return self._state.get_planet_by_id(planet_id)

    def _build_planet_index(self) -> dict:
        """Internal helper: build the planet-id -> Planet lookup dict."""
        return self._state.build_planet_index()

    def _build_fleet_hex_index(self) -> dict:
        """Internal helper: build the HexCoord -> [Fleet] lookup dict."""
        return self._fleet_slice.build_fleet_hex_index()
