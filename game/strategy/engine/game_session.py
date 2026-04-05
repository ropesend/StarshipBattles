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
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.empire import Empire

import logging

from game.core.event_logging import set_event_handler
from game.core.registry import GameRegistries, get_default_registry_provider
from game.strategy.events import Event, EventLog

logger = logging.getLogger(__name__)
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.command_handlers import create_default_registry
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy

class GameSession:
    """
    Manages the lifecycle and state of a single game session.
    Owns the Galaxy, Empires, and the Turn Engine.
    Running completely decoupled from the UI/Rendering layer.
    """
    def __init__(self, config: GameConfig = None, ai_factory=None):
        # Use provided config or create default
        if config is None:
            config = GameConfig()

        self.config = config
        self.turn_number = 1
        self.save_path = None  # Set when save game is created/loaded (Phase 3)

        # Event log (PROJ-77)
        self._event_log = EventLog()
        set_event_handler(self._create_event_handler())

        # PROJ-211: Resolve registries at init time, pass to TurnEngine
        self._registries = self._resolve_registries()

        # Engine
        # PROJ-239: ai_factory is passed through to TurnEngine → SimulationBattleResolver.
        # Callers in the UI/app layer provide it; tests inject mocks.
        self.turn_engine = TurnEngine(registries=self._registries, ai_factory=ai_factory)
        self._command_registry = create_default_registry()

        # Initialization via GameInitializer (PROJ-87 Phase 6)
        from game.strategy.engine.game_initializer import GameInitializer
        self.galaxy, self.empires = GameInitializer.initialize(config)
        self.systems = list(self.galaxy.systems.values())

        # Human player IDs based on is_human flag
        self.human_player_ids = [
            i for i, p in enumerate(config.players) if p.is_human
        ]

        # Convenience references for common empires
        self.player_empire = self.empires[0] if len(self.empires) > 0 else None
        self.enemy_empire = self.empires[1] if len(self.empires) > 1 else None

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
    def event_log(self) -> EventLog:
        """The session's event log for recording game events."""
        return self._event_log

    @property
    def registries(self) -> GameRegistries:
        """The session's game registries for DI to sub-systems."""
        return self._registries

    def _create_event_handler(self):
        """Create a callback for the global log_event() system.

        Returns a closure that captures this session, creating Event objects
        from structured kwargs and appending them to the session's EventLog.
        """
        def handler(event_type: str, **kwargs):
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
            self._event_log.append(event)
        return handler

    def process_turn(self) -> None:
        """Advance the game simulation by one full turn."""
        logger.info(f"GameSession: Processing Turn {self.turn_number}...")
        self.turn_engine.process_turn(self.empires, self.galaxy, self.save_path)
        self.turn_number += 1

    def get_current_player_empire(self, player_index: int) -> Optional['Empire']:
        """Get the empire object for the current human player index."""
        if 0 <= player_index < len(self.human_player_ids):
            p_id = self.human_player_ids[player_index]
            return next((e for e in self.empires if e.id == p_id), None)
        return None

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
        from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex

        path = find_hybrid_path(self.galaxy, fleet.location, target_hex, fleet=fleet)

        # PROJ-204: Consistent with Engine - remove start hex if it matches current location
        result = strip_start_hex(fleet.location, path)
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
        from game.strategy.data.pathfinding import project_fleet_path
        return project_fleet_path(fleet, self.galaxy, max_turns)

    def handle_command(self, command):
        """
        Execute a user command via the command registry.

        Args:
            command: Command object

        Returns:
            ValidationResult (is_valid=True/False)
        """
        if command.type == command.type.ISSUE_ORDER:
            return self._command_registry.dispatch(command.name, self, command)
        return None

    def _get_fleet_by_id(self, fleet_id: int):
        """
        Find fleet by ID via Galaxy registry (O(1) lookup).

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        # O(1) Galaxy registry lookup
        return self.galaxy.get_fleet_by_id(fleet_id)

    def _get_planet_by_id(self, planet_id: int):
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

        # Initialize turn engine and command registry
        # PROJ-239: ai_factory=None is OK here — TurnEngine will raise if
        # a battle_resolver is needed but no ai_factory was provided. In practice,
        # the conflict_engine is lazy-initialized and will only need it during
        # actual combat. SaveGameService.load_game callers must provide ai_factory
        # or inject a battle_resolver if combat will occur.
        session.turn_engine = TurnEngine(registries=session._registries, ai_factory=ai_factory)
        session._command_registry = create_default_registry()

        # Restore event log (PROJ-77)
        session._event_log = EventLog.from_dict(data.get('event_log', {'events': []}))
        set_event_handler(session._create_event_handler())

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

        # Set convenience references
        session.player_empire = session.empires[0] if len(session.empires) > 0 else None
        session.enemy_empire = session.empires[1] if len(session.empires) > 1 else None

        return session
