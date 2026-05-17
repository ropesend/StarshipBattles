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
    from game.core.hex_math import HexCoord
    from game.core.protocols import IRaceRegistry
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.engine.session.runtime_services import (
        SessionBootstrapState,
    )

import logging

from game.core.event_logging import EventBus
from game.core.registry import GameRegistries, get_default_registry_provider
from game.strategy.events import Event, EventLog

logger = logging.getLogger(__name__)
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.turn_engine_config import TurnEngineConfig
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.handlers import create_default_registry
from game.strategy.engine.session.runtime_services import (
    SessionRuntimeServices,
)
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy

class GameSession:
    """
    Manages the lifecycle and state of a single game session.
    Owns the Galaxy, Empires, and the Turn Engine.
    Running completely decoupled from the UI/Rendering layer.
    """
    def __init__(self, config: Optional[GameConfig] = None, ai_factory: Optional[Any] = None):
        # Use provided config or create default
        if config is None:
            config = GameConfig()

        self.turn_number = 1
        self.save_path = None  # Set when save game is created/loaded (Phase 3)

        # PROJ-291 C3: race registry stays lazy on GameSession (see the
        # `race_registry` property). The bootstrap's
        # `race_registry_provider` callback resolves through that property
        # so the cached instance is the same one engines see.
        self._race_registry: Optional['IRaceRegistry'] = None

        # PROJ-423 Phase 2: route construction through SessionBootstrap so
        # the wired-service bag has a single canonical assembly point
        # (eliminates the PROJ-396 CRIT-002 drift surface). Phase 4
        # collapses this into the canonical `_apply_bootstrap_state(...)`
        # method.
        #
        # PROJ-381 Phase 2 (B-11): SessionInitializationError null-object
        # substitution is still applied at the `self` boundary so the
        # partially-constructed session a caller sees lands in a
        # deterministic null-object state. The bootstrap re-raises the
        # typed error; this catch only sets the visible null-object slots
        # on `self` before propagating.
        from game.core.exceptions import SessionInitializationError
        from game.strategy.engine.session.bootstrap import SessionBootstrap
        try:
            state = SessionBootstrap.new_game_state(
                config,
                ai_factory=ai_factory,
                race_registry_provider=lambda: self.race_registry,
                event_handler_factory=lambda log: self._build_event_handler(log),
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
        self._apply_provisional_state(state)

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
        return self._event_log

    @property
    def registries(self) -> GameRegistries:
        """The session's game registries for DI to sub-systems."""
        return self._registries

    @property
    def fleet_mutator(self):  # type: ignore[no-untyped-def]
        """The session's IFleetMutator (PROJ-370).

        Routed through ``FleetWriteService`` (composed with
        ``FleetNavigationService``). Command handlers pull this to mutate
        Fleet state without bypassing the AST-guarded boundary.
        """
        return self._fleet_mutator

    @property
    def planet_mutator(self):  # type: ignore[no-untyped-def]
        """The session's IPlanetMutator (PROJ-370)."""
        return self._planet_mutator

    @property
    def empire_mutator(self):  # type: ignore[no-untyped-def]
        """The session's IEmpireMutator (PROJ-370)."""
        return self._empire_mutator

    @property
    def ship_mutator(self):  # type: ignore[no-untyped-def]
        """The session's IShipInstanceMutator (PROJ-370)."""
        return self._ship_mutator

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

    def _create_event_handler(self) -> Callable[..., None]:
        """Backwards-compatible event-handler factory.

        Captures `self._event_log` implicitly via `self._build_event_handler`.
        Kept for any direct callers; production paths now route through the
        SessionBootstrap event-handler factory which also stamps the current
        `self.turn_number` onto each event.
        """
        return self._build_event_handler(self._event_log)

    def _build_event_handler(self, event_log: EventLog) -> Callable[..., None]:
        """Create the closure handler the global log_event() system calls.

        Capturing `event_log` as a parameter (rather than implicitly via
        `self._event_log`) lets `SessionBootstrap._build_services(...)`
        construct the EventBus *before* `self._event_log` is set during
        rehydration. Turn stamping still reads `self.turn_number`.
        """

        def handler(event_type: str, **kwargs) -> None:
            category = kwargs.pop('category', 'other')
            message = kwargs.pop('message', '')
            empire_id = kwargs.pop('empire_id', -1)
            # Coerce enum values to string (hasattr checks if Enum or str)
            cat_value = category.value if hasattr(category, 'value') else category
            etype_value = event_type.value if hasattr(event_type, 'value') else event_type
            event = Event(
                event_type=etype_value,
                category=cat_value,
                turn=self.turn_number,
                empire_id=empire_id,
                message=message,
                details=kwargs,
            )
            event_log.append(event)
        return handler

    def _apply_provisional_state(self, state: 'SessionBootstrapState') -> None:
        """Copy a SessionBootstrapState onto self (PROJ-423 Phase 2 / 3).

        Provisional assignment path used by `__init__` and `from_dict`
        until Phase 4 introduces the canonical `_apply_bootstrap_state(...)`.
        Sets `self.config`, the session-scoped service attribute set, the
        `self._services` bag, owned domain state, and the
        `active_empire` / `enemy_empire` seed (BUG-125).
        """
        self.config = state.config
        self._registries = state.services.registries
        self._event_log = state.services.event_log
        self._event_bus = state.services.event_bus
        self._fleet_mutator = state.services.fleet_mutator
        self._planet_mutator = state.services.planet_mutator
        self._empire_mutator = state.services.empire_mutator
        self._ship_mutator = state.services.ship_mutator
        self.turn_engine = state.services.turn_engine
        self._command_registry = state.services.command_registry
        self._services = state.services

        self.turn_number = state.turn_number
        self.save_path = state.save_path
        self.galaxy = state.galaxy
        self.empires = state.empires
        self.human_player_ids = list(state.human_player_ids)
        self.systems = (
            list(state.galaxy.systems.values()) if state.galaxy is not None else []
        )
        # BUG-125: see __init__ for `active_empire` contract.
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

    def handle_command(self, command: Any) -> Any:
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
        """
        Serialize GameSession to dict for save system.

        Returns complete game state including config, galaxy, empires, and turn data.
        """
        return {
            'turn_number': self.turn_number,
            'save_path': self.save_path,
            'config': self.config.to_dict(),
            'galaxy': self.galaxy.to_dict(),
            'empires': [e.to_dict() for e in self.empires],
            'human_player_ids': self.human_player_ids.copy(),
            'event_log': self._event_log.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict, ai_factory=None) -> 'GameSession':
        """
        Deserialize GameSession from dict.

        Uses two-phase loading:
        1. Load galaxy (creates all planets with IDs)
        2. Load empires (resolves planet references via galaxy)

        Args:
            data: Saved game session data

        Returns:
            Reconstructed GameSession with all state restored

        Raises:
            PersistenceException: If required fields are missing or data structures are invalid.
        """
        from game.core.exceptions import PersistenceException
        from game.core.error_codes import ErrorCode
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.empire import Empire

        # Create empty session (bypass __init__ to avoid generating new galaxy)
        session = cls.__new__(cls)

        # Restore config with context on error
        try:
            session.config = GameConfig.from_dict(data['config'])
        except KeyError as e:
            raise PersistenceException(
                f"Missing required config field: {e}",
                code=ErrorCode.SAVE_FAILED.value,
                context={"section": "config", "missing_field": str(e)}
            ) from e

        session.turn_number = data.get('turn_number', 1)
        session.save_path = data.get('save_path')

        # PROJ-211: Resolve registries at init time, pass to TurnEngine
        session._registries = GameSession._resolve_registries()

        # PROJ-291 C3: race registry stays lazy on GameSession; the
        # bootstrap's `race_registry_provider` lambda routes to
        # `session.race_registry` so the cached instance is the same one
        # engines see post-load.
        session._race_registry = None

        # Restore event log (PROJ-77) — PROJ-252: session-scoped EventBus
        restored_event_log = EventLog.from_dict(
            data.get('event_log', {'events': []})
        )

        # PROJ-423 Phase 2: route service construction through the same
        # canonical wiring path as __init__. This is the structural fix
        # for the PROJ-396 CRIT-002 drift surface — no more hand-mirrored
        # service block in from_dict.
        from game.strategy.engine.session.bootstrap import SessionBootstrap
        services = SessionBootstrap._build_services(
            registries=session._registries,
            event_log=restored_event_log,
            ai_factory=ai_factory,
            race_registry_provider=lambda: session.race_registry,
            event_handler_factory=lambda log: session._build_event_handler(log),
        )
        session._event_log = services.event_log
        session._event_bus = services.event_bus
        session._fleet_mutator = services.fleet_mutator
        session._planet_mutator = services.planet_mutator
        session._empire_mutator = services.empire_mutator
        session._ship_mutator = services.ship_mutator
        session.turn_engine = services.turn_engine
        session._command_registry = services.command_registry
        session._services = services

        # Step 1: Load Galaxy (creates all planets with IDs)
        try:
            session.galaxy = Galaxy.from_dict(data['galaxy'])
        except KeyError as e:
            raise PersistenceException(
                f"Missing required galaxy field: {e}",
                code=ErrorCode.LOAD_FAILED.value,
                context={"section": "galaxy", "missing_field": str(e)}
            ) from e
        session.systems = list(session.galaxy.systems.values())

        # Step 2: Load Empires (resolves planet references via galaxy)
        try:
            session.empires = [
                Empire.from_dict(emp_data, galaxy=session.galaxy, registries=session._registries)
                for emp_data in data.get('empires', [])
            ]
        except KeyError as e:
            raise PersistenceException(
                f"Missing required empire field: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"section": "empires", "missing_field": str(e)}
            ) from e

        # Restore human player IDs
        session.human_player_ids = data.get('human_player_ids', [0, 1])

        # PROJ-219: Set galaxy back-references for auto fleet registration
        for empire in session.empires:
            empire.set_galaxy(session.galaxy)

        # PROJ-219: Register deserialized fleets with galaxy for O(1) lookup.
        # Deserialization bypasses add_fleet(), so explicit registration is needed.
        for empire in session.empires:
            for fleet in empire.fleets:
                session.galaxy.register_fleet(fleet)

        # Step 3: Resolve fleet order references (PROJ-207)
        # Fleet orders targeting other fleets or planets are stored as marker dicts
        # (_fleet_ref, _planet_ref) during deserialization. Now that all empires
        # and galaxy are loaded, resolve these to actual object references.
        for empire in session.empires:
            for fleet in empire.fleets:
                fleet.resolve_order_references(session.galaxy, session.empires)

        # PROJ-222: Rebuild pursuer tracker from resolved order references.
        # After resolve_order_references(), order targets are live Fleet objects.
        # Scan all orders and register pursuers with their targets.
        from game.strategy.data.order_types import OrderType
        for empire in session.empires:
            for fleet in empire.fleets:
                for order in fleet.orders:
                    if order.type in (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET):
                        if hasattr(order.target, 'pursuer_tracker'):
                            order.target.pursuer_tracker.add_pursuer(fleet)

        # BUG-125: see __init__ for `active_empire` contract.
        session.active_empire = session.empires[0] if len(session.empires) > 0 else None
        session.enemy_empire = session.empires[1] if len(session.empires) > 1 else None

        # PROJ-423 Phase 1: mirror __init__ in assembling the
        # SessionRuntimeServices bag from the already-constructed services.
        # Phase 2 collapses both wirings into a shared
        # SessionBootstrap._build_services(...) call.
        session._services = SessionRuntimeServices(
            registries=session._registries,
            event_log=session._event_log,
            event_bus=session._event_bus,
            fleet_mutator=session._fleet_mutator,
            planet_mutator=session._planet_mutator,
            empire_mutator=session._empire_mutator,
            ship_mutator=session._ship_mutator,
            turn_engine=session.turn_engine,
            command_registry=session._command_registry,
        )

        return session
