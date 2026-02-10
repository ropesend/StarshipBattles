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
    - IssueBuildShipCommand → _handle_build_ship_command

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
import os
import random
import warnings
from typing import Optional
from game.core.logger import log_info, log_debug, log_warning, set_event_handler
from game.core.validation import validation_result
from game.strategy.events import Event, EventLog
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.command_handlers import create_default_registry
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
from game.strategy.data.planet import SpeciesPopulation

class GameSession:
    """
    Manages the lifecycle and state of a single game session.
    Owns the Galaxy, Empires, and the Turn Engine.
    Running completely decoupled from the UI/Rendering layer.
    """
    def __init__(self, config: GameConfig = None, galaxy_radius: int = None, system_count: int = None):
        # Use provided config or create default
        if config is None:
            config = GameConfig()

        # Deprecation warning for legacy parameters (PROJ-22)
        # These parameters override config values, which violates config immutability.
        # Use GameConfig(galaxy_radius=X, system_count=Y) instead.
        if galaxy_radius is not None:
            warnings.warn(
                "galaxy_radius parameter is deprecated. "
                "Use GameConfig(galaxy_radius=...) instead.",
                DeprecationWarning,
                stacklevel=2
            )
            config.galaxy_radius = galaxy_radius
        if system_count is not None:
            warnings.warn(
                "system_count parameter is deprecated. "
                "Use GameConfig(system_count=...) instead.",
                DeprecationWarning,
                stacklevel=2
            )
            config.system_count = system_count

        self.config = config
        self.turn_number = 1
        self.save_path = None  # Set when save game is created/loaded (Phase 3)

        # Event log (PROJ-77)
        self._event_log = EventLog()
        set_event_handler(self._create_event_handler())

        # Engine
        self.turn_engine = TurnEngine()
        self._command_registry = create_default_registry()

        # Create empires dynamically from config.players
        self.empires = []
        for i, player_cfg in enumerate(config.players):
            theme_path = config.get_player_theme_path(i)
            log_info(f"GameSession: Creating empire {i} with theme={player_cfg.theme}, theme_path={theme_path}")
            empire = Empire(
                empire_id=i,
                name=player_cfg.name,
                color=player_cfg.color,
                theme_path=theme_path,
                empire_theme_id=player_cfg.theme,
                flag_id=player_cfg.flag_id,
                portrait_id=player_cfg.portrait_id,
                race_config=player_cfg.race_config
            )
            self.empires.append(empire)

        # Human player IDs based on is_human flag
        self.human_player_ids = [
            i for i, p in enumerate(config.players) if p.is_human
        ]

        # Convenience references for backward compatibility
        self.player_empire = self.empires[0] if len(self.empires) > 0 else None
        self.enemy_empire = self.empires[1] if len(self.empires) > 1 else None

        # Galaxy
        self.galaxy = Galaxy(radius=config.galaxy_radius)
        self.systems = []

        # Initialization
        self._initialize_galaxy(config.system_count)
        self._setup_initial_scenario()

    def _initialize_galaxy(self, count):
        """Initialize the galaxy with systems and warp lanes.

        Uses the galaxy_type and galaxy_seed from config to determine
        placement strategy. If galaxy_type is "random", uses uniform random
        placement. Otherwise, loads the density-based layout from
        galaxy_layouts.json.

        Args:
            count: Number of systems to generate
        """
        galaxy_type = self.config.galaxy_type
        galaxy_seed = self.config.galaxy_seed

        log_info(f"GameSession: Generating Galaxy (type={galaxy_type}, seed={galaxy_seed})...")

        # Set up RNG for deterministic generation
        rng: Optional[random.Random] = None
        if galaxy_seed is not None:
            rng = random.Random(galaxy_seed)
            # Also seed global random for star/planet generation
            random.seed(galaxy_seed)

        # Create placement strategy based on galaxy type
        if galaxy_type == "random":
            strategy = RandomPlacementStrategy()
        else:
            # Load layout configuration
            loader = GalaxyLayoutsLoader()
            layout_config = loader.load_and_scale(galaxy_type, self.galaxy.radius)

            # Create density map from config
            density_map = DensityMap.from_config(layout_config, self.galaxy.radius)
            strategy = DensityBasedPlacementStrategy(density_map)

        # Generate systems using the strategy
        self.systems = self.galaxy.generate_systems(
            count=count,
            min_dist=400,
            placement_strategy=strategy,
            rng=rng
        )
        self.galaxy.generate_warp_lanes()

        log_info(f"GameSession: Generated {len(self.systems)} systems.")

    def _setup_initial_scenario(self):
        """Set up starting colonies and fleets for all empires."""
        if not self.systems:
            return

        num_empires = len(self.empires)
        num_systems = len(self.systems)

        # Distribute starting colonies across the galaxy
        # Use evenly spaced system indices to spread empires apart
        if num_empires == 1:
            # Single player gets first system
            home_indices = [0]
        elif num_empires == 2:
            # Two players get first and last systems (opposite ends)
            home_indices = [0, num_systems - 1]
        elif num_empires == 3:
            # Three players: first, middle, last
            mid = num_systems // 2
            home_indices = [0, mid, num_systems - 1]
        else:  # 4 players
            # Four players: distribute evenly
            step = max(1, num_systems // 4)
            home_indices = [0, step, step * 2, num_systems - 1]

        # Assign home systems to empires
        for i, empire in enumerate(self.empires):
            if i < len(home_indices) and home_indices[i] < num_systems:
                home_sys = self.systems[home_indices[i]]
                if home_sys.planets:
                    # Assign first planet as home colony
                    home_planet = home_sys.planets[0]

                    # Adjust planet conditions to match species preferences (BUG-63)
                    if empire.race_config is not None:
                        self._adjust_homeworld_to_race(home_planet, empire.race_config)

                    empire.add_colony(home_planet)

                    # Seed initial population if empire has race_config
                    if empire.race_config is not None:
                        initial_pop = SpeciesPopulation(
                            race_id=empire.race_config.race_id,
                            count=10000,  # 10 million people
                            happiness=0.7
                        )
                        home_planet.populations.append(initial_pop)
                        log_info(f"GameSession: Seeded {initial_pop.count} population on {home_planet.name}")

                    log_info(f"GameSession: Empire '{empire.name}' home at system {home_indices[i]}")

    @property
    def event_log(self) -> EventLog:
        """The session's event log for recording game events."""
        return self._event_log

    def _create_event_handler(self):
        """Create a callback for the global log_event() system.

        Returns a closure that captures this session, creating Event objects
        from structured kwargs and appending them to the session's EventLog.
        """
        def handler(event_type: str, **kwargs):
            category = kwargs.pop('category', 'other')
            message = kwargs.pop('message', '')
            empire_id = kwargs.pop('empire_id', -1)
            # Coerce enum values to their string representation
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

    def _find_colony_at_fleet(self, fleet):
        """Find an empire colony at the fleet's current location (BUG-70)."""
        if not hasattr(self.galaxy, 'get_system_of_object'):
            return None
        for empire in self.empires:
            if any(f.id == fleet.id for f in empire.fleets):
                system = self.galaxy.get_system_of_object(fleet)
                if system:
                    for planet in system.planets:
                        if planet.owner_id == empire.id:
                            return planet
                break
        return None

    @staticmethod
    def _adjust_homeworld_to_race(planet, race_config):
        """Adjust a starting planet's conditions to match species ideal environment (BUG-63)."""
        from game.strategy.data.planet import PlanetType

        # Set planet type from homeworld type
        if race_config.homeworld_type:
            try:
                planet.planet_type = PlanetType[race_config.homeworld_type]
            except KeyError:
                pass  # Keep existing type if invalid

        # Set surface conditions to species ideals
        planet.surface_gravity = race_config.gravity_ideal * 9.81
        planet.surface_temperature = race_config.temperature_ideal
        planet.surface_water = race_config.water_ideal

        # Build atmosphere from preferences (positive preferences = present gases)
        # Use 1 ATM total pressure, distributed by positive preference weights
        atm_prefs = race_config.atmosphere_preferences
        positive_gases = {gas: val for gas, val in atm_prefs.items() if val > 0}

        if positive_gases:
            total_weight = sum(positive_gases.values())
            one_atm = 101325.0  # Pa
            planet.atmosphere = {}
            for gas, val in positive_gases.items():
                planet.atmosphere[gas] = (val / total_weight) * one_atm
            planet.surface_pressure = one_atm
        else:
            # No positive gas preferences - minimal atmosphere
            planet.atmosphere = {}
            planet.surface_pressure = 0.0

        log_info(f"GameSession: Adjusted {planet.name} to match species preferences "
                 f"(type={planet.planet_type.name}, gravity={planet.surface_gravity/9.81:.1f}g, "
                 f"temp={planet.surface_temperature:.0f}K, water={planet.surface_water:.0%})")

    def process_turn(self):
        """Advance the game simulation by one full turn."""
        log_info(f"GameSession: Processing Turn {self.turn_number}...")
        self.turn_engine.process_turn(self.empires, self.galaxy, self.save_path)
        self.turn_number += 1

    def get_current_player_empire(self, player_index):
        """Get the empire object for the current human player index."""
        if 0 <= player_index < len(self.human_player_ids):
            p_id = self.human_player_ids[player_index]
            return next((e for e in self.empires if e.id == p_id), None)
        return None

    def preview_fleet_path(self, fleet, target_hex):
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
        from game.strategy.data.pathfinding import find_hybrid_path

        # Log warp capability for debugging navigation issues (BUG-45)
        can_warp = fleet.can_use_warp() if hasattr(fleet, 'can_use_warp') else 'N/A'
        log_debug(f"preview_fleet_path: fleet={fleet.id}, can_use_warp={can_warp}, target={target_hex}")

        path = find_hybrid_path(self.galaxy, fleet.location, target_hex, fleet=fleet)

        # Consistent with Engine: remove start hex if it matches current location
        if path and path[0] == fleet.location:
             return path[1:]
        return path

    def get_fleet_path_projection(self, fleet, max_turns=50):
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
        Find fleet by ID across all empires.

        PROJ-40/NEW-STRAT-009: Reviewed and kept - used 7 times for command validation.
        Iterates all empires since fleets belong to empires but commands reference
        fleets by global ID.

        Args:
            fleet_id: Fleet ID to find.

        Returns:
            Fleet if found, None otherwise.
        """
        for emp in self.empires:
            for f in emp.fleets:
                if f.id == fleet_id:
                    return f
        return None

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

    def to_dict(self) -> dict:
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
    def from_dict(cls, data: dict) -> 'GameSession':
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
            KeyError: If required fields (config, galaxy, empires) are missing.
            TypeError: If data structures are invalid.
        """
        from game.core.exceptions import PersistenceException
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
                code="P001",
                context={"section": "config", "missing_field": str(e)}
            ) from e

        session.turn_number = data.get('turn_number', 1)
        session.save_path = data.get('save_path')

        # Initialize turn engine and command registry
        session.turn_engine = TurnEngine()
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
                code="P002",
                context={"section": "galaxy", "missing_field": str(e)}
            ) from e
        session.systems = list(session.galaxy.systems.values())

        # Step 2: Load Empires (resolves planet references via galaxy)
        try:
            session.empires = [
                Empire.from_dict(emp_data, galaxy=session.galaxy)
                for emp_data in data.get('empires', [])
            ]
        except KeyError as e:
            raise PersistenceException(
                f"Missing required empire field: {e}",
                code="P003",
                context={"section": "empires", "missing_field": str(e)}
            ) from e

        # Restore human player IDs
        session.human_player_ids = data.get('human_player_ids', [0, 1])

        # Set convenience references
        session.player_empire = session.empires[0] if len(session.empires) > 0 else None
        session.enemy_empire = session.empires[1] if len(session.empires) > 1 else None

        return session
