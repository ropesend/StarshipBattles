"""
Game Session - Strategy Game State Manager

This module contains GameSession, which manages the lifecycle and state of
a single strategy game. It owns the Galaxy, Empires, and TurnEngine, and
provides the interface for UI layers to interact with the game.

GameSession is designed to run headless (without UI) for testing and AI.

Responsibilities:
    - Galaxy generation and system initialization
    - Empire creation from game configuration
    - Turn processing via TurnEngine
    - Command dispatch (MOVE, COLONIZE, BUILD, etc.)
    - Pathfinding preview for UI
    - Serialization/deserialization for save/load

Command Dispatch:
    handle_command(cmd) routes commands to handlers based on type:
    - IssueColonizeCommand → _handle_colonize_command
    - IssueMoveCommand → _handle_move_command
    - AddToConstructionQueueCommand → AddToConstructionQueueCommandHandler

    Each handler:
    1. Resolves entity references (fleet, planet)
    2. Validates the action
    3. Applies the order if valid
    4. Returns ValidationResult

Save/Load:
    to_dict() → dict: Serialize full game state
    from_dict(data) → GameSession: Deserialize (two-phase loading)

Example:
    config = GameConfig(galaxy_radius=5000, system_count=20)
    session = GameSession(config=config)

    # Process a turn
    session.process_turn()

    # Issue a move command
    from game.strategy.commands import IssueMoveCommand
    cmd = IssueMoveCommand(fleet_id=fleet.id, target_hex=destination)
    result = session.handle_command(cmd)
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.event_logging import EventBus
    from game.core.hex_math import HexCoord
    from game.core.protocols import IRaceRegistry
    from game.core.protocols.strategy_mutators import IEmpireMutator, IFleetMutator, IPlanetMutator, IShipInstanceMutator
    from game.core.validation import ValidationResult
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.engine.commands.registry import CommandRegistry
    from game.strategy.engine.session.runtime_services import SessionBootstrapState

import logging

from game.core.registry import GameRegistries, get_default_registry_provider
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.session.bootstrap import (
    build_event_handler as _make_event_handler,
)
from game.strategy.engine.session.runtime_services import (
    SessionRuntimeServices,
)
from game.strategy.events import EventLog

logger = logging.getLogger(__name__)

class GameSession:
    """Manages the lifecycle and state of a single game session.

    Owns the Galaxy, Empires, and the Turn Engine. Headless-runnable
    (decoupled from UI/Rendering).

    PROJ-438 Phase 2 ownership categories (pinned by
    ``tests/unit/strategy/engine/test_game_session_projection_boundary.py``;
    holder-extraction sweep was rejected — 60+ caller files):

    - **Owned domain state**: ``config``, ``galaxy``, ``empires``,
      ``systems``, ``turn_engine``, ``turn_number``.
    - **Owned UI-rotation state**: ``active_empire`` / ``enemy_empire`` —
      mutable runtime state rotated by ``StrategyGameStateManager.
      advance_turn`` per BUG-125, NOT derivable projections.
    - **Owned UI configuration**: ``human_player_ids`` (hot-seat).
    - **Owned persistence metadata**: ``save_path``.
    - **Lazy-init owned services**: ``_race_registry`` via the
      ``race_registry`` property — chicken-and-egg with bootstrap closure.
    - **Service-bag delegation**: ``services`` property + per-service
      read-only properties forwarding to ``SessionRuntimeServices``.
    """
    def __init__(
        self,
        config: Optional[GameConfig] = None,
        ai_factory: Optional[Any] = None,
        *,
        _state: Optional['SessionBootstrapState'] = None,
    ) -> None:
        """Construct a GameSession.

        Two entry forms:

        - **New game** — `GameSession(config=..., ai_factory=...)` runs
          `SessionBootstrap.new_game_state(...)` and applies the
          resulting `SessionBootstrapState`. `SessionInitializationError`
          null-object substitution at the `self` boundary (PROJ-381) is
          preserved.
        - **Internal `_state=` form** — `GameSession.from_dict(...)` uses
          this with a pre-built `SessionBootstrapState`. Not part of the
          public API.

        Either way the single internal assignment path is
        `_apply_bootstrap_state(state)`.
        """
        # PROJ-291 C3: race registry stays lazy on GameSession (see the
        # `race_registry` property). Initialized here so the bootstrap's
        # `race_registry_provider` lambda can route through `self.race_registry`
        # before `_apply_bootstrap_state` runs.
        self._race_registry: Optional['IRaceRegistry'] = None

        if _state is not None:
            self._apply_bootstrap_state(_state)
            return

        # New-game path.
        if config is None:
            config = GameConfig()

        # PROJ-381 Phase 2 (B-11): wrap construction so the caller sees a
        # deterministic null-object partial session on init failure.
        from game.core.exceptions import SessionInitializationError
        from game.strategy.engine.session.bootstrap import SessionBootstrap
        try:
            state = SessionBootstrap.new_game_state(
                config,
                ai_factory=ai_factory,
                race_registry_provider=lambda: self.race_registry,
                event_handler_factory=lambda log: _make_event_handler(
                    log, lambda: self.turn_number
                ),
            )
        except SessionInitializationError:
            self.config = config
            self.galaxy = None
            self.empires = []
            self.systems = []
            self.human_player_ids = []
            self.active_empire = None
            self.enemy_empire = None
            raise
        self._apply_bootstrap_state(state)

    @staticmethod
    def _resolve_registries() -> GameRegistries:
        """Resolve game registries from the default provider.

        Shared by __init__ and from_dict to avoid duplicating the
        provider resolution and GameRegistries construction.
        """
        from game.core.resources import ResourceCatalog
        provider = get_default_registry_provider()
        return GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=ResourceCatalog.from_json(),
        )

    @property
    def services(self) -> SessionRuntimeServices:
        """The wired runtime-services bag (PROJ-423).

        Both `__init__` and `from_dict` populate `self._services` from the
        same set of constructed services. Phase 2 routes both paths
        through a shared `SessionBootstrap._build_services(...)` so the
        bag is the single source of truth and there is no drift surface.
        """
        return self._services

    @property
    def event_log(self) -> EventLog:
        """The session's event log for recording game events."""
        return self._services.event_log

    @property
    def _event_log(self) -> EventLog:
        """Backwards-compatible attribute alias.

        PROJ-423: ownership moved to `self._services.event_log`. The
        underscore alias is kept because save/load code and a small
        number of internal callers still read it directly; refactoring
        them is out of scope for the structural extraction.
        """
        return self._services.event_log

    @property
    def _event_bus(self) -> "EventBus":
        """Backwards-compatible attribute alias for `services.event_bus`."""
        return self._services.event_bus

    @property
    def registries(self) -> GameRegistries:
        """The session's game registries for DI to sub-systems."""
        return self._services.registries

    @property
    def _registries(self) -> GameRegistries:
        """Backwards-compatible alias for `services.registries`."""
        return self._services.registries

    @property
    def fleet_mutator(self) -> "IFleetMutator":
        """The session's IFleetMutator (PROJ-370).

        Routed through ``FleetWriteService`` (composed with
        ``FleetNavigationService``). Command handlers pull this to mutate
        Fleet state without bypassing the AST-guarded boundary.
        """
        return self._services.fleet_mutator

    @property
    def _fleet_mutator(self) -> "IFleetMutator":
        return self._services.fleet_mutator

    @property
    def planet_mutator(self) -> "IPlanetMutator":
        """The session's IPlanetMutator (PROJ-370)."""
        return self._services.planet_mutator

    @property
    def _planet_mutator(self) -> "IPlanetMutator":
        return self._services.planet_mutator

    @property
    def empire_mutator(self) -> "IEmpireMutator":
        """The session's IEmpireMutator (PROJ-370)."""
        return self._services.empire_mutator

    @property
    def _empire_mutator(self) -> "IEmpireMutator":
        return self._services.empire_mutator

    @property
    def ship_mutator(self) -> "IShipInstanceMutator":
        """The session's IShipInstanceMutator (PROJ-370)."""
        return self._services.ship_mutator

    @property
    def _ship_mutator(self) -> "IShipInstanceMutator":
        return self._services.ship_mutator

    @property
    def _command_registry(self) -> "CommandRegistry":
        return self._services.command_registry

    @property
    def race_registry(self) -> 'IRaceRegistry':
        """Session-scoped race registry (PROJ-291 C3).

        Lazy-creates a `CachedRaceRegistry` wrapping a `RaceLibrary` on
        first access and reuses it for the lifetime of the session.
        TurnEngine threads this into HappinessEngine + PopulationEngine
        so multi-species colonies resolve each species' `RaceConfig`
        correctly.

        Callers that mutate races (e.g. the race editor on save) must
        call `registry.invalidate(race_id)` to keep subsequent reads
        coherent.
        """
        if self._race_registry is None:
            from game.strategy.systems.race_library import (
                CachedRaceRegistry,
                RaceLibrary,
            )
            self._race_registry = CachedRaceRegistry(RaceLibrary())
        return self._race_registry

    def _apply_bootstrap_state(self, state: 'SessionBootstrapState') -> None:
        """Copy a SessionBootstrapState onto self (PROJ-423 Phase 4).

        Single canonical assignment path for both `__init__` (new-game)
        and `from_dict` (rehydrate). The categorical groupings below
        match the class docstring (PROJ-438 Phase 2 narrowing).

        Does NOT touch `self._race_registry` — that slot is set to None
        by `__init__` before this method runs and stays lazy via the
        `race_registry` property.
        """
        # Frozen config + the wired services bag.
        self.config = state.config
        self._services = state.services
        self.turn_engine = state.services.turn_engine

        # Owned persistence metadata.
        self.save_path = state.save_path

        # Owned execution-position counter (domain state).
        self.turn_number = state.turn_number

        # Owned domain state — the live mutable graph.
        self.galaxy = state.galaxy
        self.empires = state.empires
        self.systems = (
            list(state.galaxy.systems.values()) if state.galaxy is not None else []
        )

        # Owned UI configuration — hot-seat human player indices.
        self.human_player_ids = list(state.human_player_ids)

        # Owned UI-rotation state — BUG-125: `active_empire` is the empire
        # whose turn it currently is. Defaults to empires[0] at session
        # creation; rotated by `StrategyGameStateManager.advance_turn` on
        # each hot-seat turn change. Authorization gates in command
        # handlers read this — never the original session creator.
        # Save/load resets to empires[0]; the UI rotation index lives in
        # `StrategyScreen.current_player_index`.
        self.active_empire = (
            self.empires[0] if len(self.empires) > 0 else None
        )
        self.enemy_empire = (
            self.empires[1] if len(self.empires) > 1 else None
        )

    def process_turn(
        self,
        *,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """Advance the game simulation by one full turn.

        PROJ-251: On failure, state is rolled back via snapshot and
        EnginePhaseError is re-raised for UI layer to handle.
        turn_number is only incremented on success.

        Args:
            progress_callback: Issue #7 — optional per-tick callback
                ``(current_tick, total_ticks)`` forwarded to
                ``TurnEngine.process_turn`` so the UI can repaint the
                "PROCESSING TURN..." overlay between ticks.

        Raises:
            EnginePhaseError: If any sub-engine phase fails.
        """
        from game.core.exceptions import EnginePhaseError

        logger.info(f"GameSession: Processing Turn {self.turn_number}...")
        try:
            self.turn_engine.process_turn(
                self.empires, self.galaxy, self.save_path,
                session=self,
                progress_callback=progress_callback,
            )
            self.turn_number += 1
        except EnginePhaseError as e:
            # State already rolled back by TurnEngine
            logger.error(f"Turn {self.turn_number} failed: {e}")
            raise

    def preview_fleet_path(self, fleet: 'Fleet', target_hex: 'HexCoord') -> Optional[List['HexCoord']]:
        """
        Calculate and return the path a fleet would take to target_hex,
        without modifying the fleet's state.

        Args:
            fleet: Fleet object
            target_hex: HexCoord destination

        Returns:
            list[HexCoord] or None if no path found.
        """
        # Avoid circular imports if possible, or lazy import
        from game.strategy.services.galaxy_pathfinding_service import (
            GalaxyPathfindingService,
        )

        path = GalaxyPathfindingService(self.galaxy).find_hybrid_path(
            fleet.location, target_hex, fleet=fleet,
        )

        # PROJ-204: Consistent with Engine - remove start hex if it matches current location
        result = GalaxyPathfindingService.strip_start_hex(fleet.location, path)
        return result

    def get_fleet_path_projection(self, fleet: 'Fleet', max_turns: int = 50) -> List[Dict[str, Any]]:
        """
        Get the projected movement segments for a fleet (for UI visualization).

        Args:
            fleet: Fleet object
            max_turns: Limit projection

        Returns:
            list[dict] of segments
        """
        from game.strategy.services.intercept_calculator import project_fleet_path
        return project_fleet_path(fleet, self.galaxy, max_turns)

    def handle_command(self, command: Any) -> "ValidationResult":
        """
        Execute a user command via the command registry.

        Args:
            command: Command object

        Returns:
            ValidationResult (is_valid=True/False)
        """
        # PROJ-382 Phase 3 (Pattern #6): tautology guard removed.  Every
        # ``Command`` DTO sets ``type = CommandType.ISSUE_ORDER`` in
        # ``__post_init__``, so the conditional was unreachable.
        return self._command_registry.dispatch(command.name, self, command)

    def _get_fleet_by_id(self, fleet_id: int) -> Optional['Fleet']:
        """
        Find fleet by ID via Galaxy registry (O(1) lookup).

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        # O(1) Galaxy registry lookup
        return self.galaxy.get_fleet_by_id(fleet_id)

    def _get_planet_by_id(self, planet_id: int) -> Optional['Planet']:
        """
        Find planet by ID via Galaxy registry (O(1) lookup).

        PROJ-40/NEW-STRAT-009: Reviewed and kept - provides consistent API with
        _get_fleet_by_id and encapsulates galaxy dependency.

        Args:
            planet_id: Planet ID to find.

        Returns:
            Planet if found, None otherwise.
        """
        return self.galaxy.get_planet_by_id(planet_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize GameSession to dict for save system.

        PROJ-423: thin delegate to `SessionPersistenceAdapter.serialize`;
        save schema (`{turn_number, save_path, config, galaxy, empires,
        human_player_ids, event_log}`) is unchanged.
        """
        from game.strategy.engine.session.persistence_adapter import (
            SessionPersistenceAdapter,
        )
        return SessionPersistenceAdapter.serialize(self)

    @classmethod
    def from_dict(cls, data: dict, ai_factory: Any | None = None) -> 'GameSession':
        """Deserialize GameSession from dict.

        PROJ-423: thin delegate. `SessionPersistenceAdapter.rehydrate_state`
        performs the two-phase galaxy / empire load plus the four
        load-only operations (galaxy back-refs, fleet registration, order
        reference resolution, pursuer-tracker rebuild) and returns a
        `SessionBootstrapState`. The session is then assembled through
        the canonical `_apply_bootstrap_state(...)` path.

        Args:
            data: Saved game session data.
            ai_factory: Optional AI factory threaded to the TurnEngine.

        Returns:
            Reconstructed GameSession with all state restored.

        Raises:
            PersistenceException: If required fields are missing or data
                structures are invalid.
        """
        from game.strategy.engine.session.persistence_adapter import (
            SessionPersistenceAdapter,
        )

        # Bare session so the rehydrate path can reference `session.turn_number`
        # and `session.race_registry` through provider lambdas. The
        # closures see the values written by `_apply_bootstrap_state`
        # below.
        session = cls.__new__(cls)
        session._race_registry = None

        state = SessionPersistenceAdapter.rehydrate_state(
            data,
            ai_factory=ai_factory,
            turn_number_provider=lambda: session.turn_number,
            race_registry_provider=lambda: session.race_registry,
        )
        session._apply_bootstrap_state(state)
        return session
