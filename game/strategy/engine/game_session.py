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
from game.core.logger import log_info, log_debug, log_warning
from game.core.validation import validation_result
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.game_config import GameConfig
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader

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

        # Engine
        self.turn_engine = TurnEngine()

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
                    empire.add_colony(home_planet)
                    log_info(f"GameSession: Empire '{empire.name}' home at system {home_indices[i]}")

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
        Execute a user command.

        Args:
            command: Command object

        Returns:
            ValidationResult (is_valid=True/False)
        """
        if command.type == command.type.ISSUE_ORDER:
            # Determine command type by class
            cmd_name = command.name

            if cmd_name == 'IssueColonizeCommand':
                return self._handle_colonize_command(command)
            elif cmd_name == 'IssueMoveCommand':
                return self._handle_move_command(command)
            elif cmd_name == 'IssueBuildShipCommand':
                return self._handle_build_ship_command(command)
            elif cmd_name == 'IssueInterceptCommand':
                return self._handle_intercept_command(command)
            elif cmd_name == 'IssueJoinFleetCommand':
                return self._handle_join_command(command)
            elif cmd_name == 'QueueColonizeMissionCommand':
                return self._handle_colonize_mission_command(command)
            elif cmd_name == 'ClearFleetOrdersCommand':
                return self._handle_clear_orders_command(command)
            elif cmd_name == 'IssueTransferCommand':
                return self._handle_transfer_command(command)

        return None  # Warning/Error?

    def _handle_colonize_command(self, cmd):
        """Handle IssueColonizeCommand."""
        # 1. Resolve Data
        # We need fleet object and planet object
        # Searching fleets:
        fleet = None
        owning_empire = None

        for emp in self.empires:
             for f in emp.fleets:
                 if f.id == cmd.fleet_id:
                     fleet = f
                     owning_empire = emp
                     break
             if fleet: break

        if not fleet:
            return validation_result(False, "Fleet not found.")

        # Resolve Planet
        target_planet = None
        if cmd.planet_id:
            # Use galaxy's O(1) registry lookup instead of O(n²) scan with id()
            target_planet = self.galaxy.get_planet_by_id(cmd.planet_id)

        # 2. Validate
        result = self.turn_engine.validate_colonize_order(self.galaxy, fleet, target_planet)

        # 3. Apply
        if result.is_valid:
             from game.strategy.data.fleet import FleetOrder, OrderType
             # Ensure we pass the OBJECT to rules
             order = FleetOrder(OrderType.COLONIZE, target=target_planet)
             fleet.add_order(order)
             log_info(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")

        return result

    def _handle_move_command(self, cmd):
        """Handle IssueMoveCommand."""
        # 1. Resolve Fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Validation / Pathfinding
        # We validate by checking if a path exists.
        # Use preview_path (internal logic reuse)
        path = self.preview_fleet_path(fleet, cmd.target_hex)

        if not path:
             # Basic check: Is it already there?
             if fleet.location == cmd.target_hex:
                 # Move to self? Valid but no-op? Or invalid?
                 # Let's say valid but logs.
                 pass
             else:
                 # If path is None and locations differ, it's unreachable
                 return validation_result(False, "Target is unreachable or invalid.")

        # 3. Apply
        from game.strategy.data.fleet import FleetOrder, OrderType

        # Clear existing move orders? Or append? Standard RTS usually overrides current move.
        # But our system has an order queue.
        # UI usually clears queue for immediate move.
        # Let's assume this command appends for now, or we can make a flag.
        # For this refactor, let's Append (Queue) as per 'add_order' behavior in existing code.
        # BUT existing UI code did `fleet.orders = []` sometimes?
        # Let's stick to safe append. The user can clear orders via another command if needed.
        # Actually, standard RTS right-click usually clears previous move.
        # Let's simple append for safety in Phase 1.

        order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            fleet.path = path # Assign the calculated path

        return validation_result(True, "Move order issued.")

    def _handle_build_ship_command(self, cmd):
        """Handle IssueBuildShipCommand."""
        # 1. Resolve Planet
        planet = self._get_planet_by_id(cmd.planet_id)
        if not planet:
             return validation_result(False, "Planet not found.")

        # 2. Validate Ownership
        # Check if planet belongs to a known empire?
        # We generally trust the ID resolution, but logic should check.
        # For now, just executed.

        # 3. Apply
        # Standard build time = 1 turn for now? Logic was `add_production("Colony Ship", 1)`
        # We should probably look up design cost/time.
        # For now, hardcode 1 as per legacy.
        planet.add_production(cmd.design_name, 1)

        return validation_result(True, f"Started construction of {cmd.design_name}.")

    def _handle_intercept_command(self, cmd):
        """Handle IssueInterceptCommand.

        Creates a MOVE_TO_FLEET order targeting another fleet.
        """
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve target fleet
        target_fleet = self._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return validation_result(False, "Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        log_info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return validation_result(True, "Intercept order issued.")

    def _handle_join_command(self, cmd):
        """Handle IssueJoinFleetCommand.

        Creates MOVE_TO_FLEET and JOIN_FLEET orders to move to and merge with target.
        """
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve target fleet
        target_fleet = self._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return validation_result(False, "Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order first
        move_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 4. Then create JOIN_FLEET order
        join_order = FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        log_info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return validation_result(True, "Join fleet order issued.")

    def _handle_colonize_mission_command(self, cmd):
        """Handle QueueColonizeMissionCommand.

        Queues MOVE and COLONIZE orders. Calculates path from current location
        or last order's target hex if fleet has existing orders.

        If planet_id is None, queues a colonize order with target=None,
        meaning "colonize any available planet" when the fleet arrives.
        """
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.data.pathfinding import find_hybrid_path

        # 1. Resolve fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve planet (None is valid - means "any planet")
        planet = None
        if cmd.planet_id is not None:
            planet = self._get_planet_by_id(cmd.planet_id)
            if not planet:
                return validation_result(False, "Planet not found.")

        # 3. Determine start hex (current location or last order target)
        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

        # 4. Calculate path
        path = find_hybrid_path(self.galaxy, start_hex, cmd.target_hex)
        if not path:
            return validation_result(False, "No path found to target.")

        # 5. Queue MOVE order if not already at target
        if start_hex != cmd.target_hex:
            move_order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
            fleet.add_order(move_order)

            # Set path immediately if it's the active order
            if len(fleet.orders) == 1:
                # Remove start hex from path before assigning
                if path and path[0] == fleet.location:
                    path = path[1:]
                fleet.path = path

        # 6. Queue COLONIZE order (target=None means "any available planet")
        colonize_order = FleetOrder(OrderType.COLONIZE, target=planet)
        fleet.add_order(colonize_order)

        planet_name = planet.name if planet else "Any Planet"
        log_info(f"GameSession: Queued Colonize Mission for Fleet {fleet.id} -> {planet_name}")
        return validation_result(True, "Colonize mission queued.")

    def _handle_clear_orders_command(self, cmd):
        """Handle ClearFleetOrdersCommand.

        Clears all orders and the path from a fleet.
        """
        # 1. Resolve fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Clear orders and path
        fleet.orders = []
        fleet.path = []

        log_info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return validation_result(True, "Fleet orders cleared.")

    def _handle_transfer_command(self, cmd):
        """Handle IssueTransferCommand.

        Creates a TRANSFER order for cargo operations between fleet and colony.
        """
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.validation import TransferValidator

        # 1. Resolve fleet
        fleet = self._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Find owning empire
        owning_empire = None
        for emp in self.empires:
            if fleet in emp.fleets:
                owning_empire = emp
                break

        if not owning_empire:
            return validation_result(False, "Fleet owner not found.")

        # 3. Resolve planet
        planet = self._get_planet_by_id(cmd.planet_id)
        if not planet:
            return validation_result(False, "Planet not found.")

        # 4. Validate
        result = TransferValidator.validate(
            self.galaxy, fleet, planet, cmd.cargo_type, cmd.direction, cmd.amount
        )

        # 5. Apply
        if result.is_valid:
            # Create TRANSFER order with params dict
            transfer_params = {
                'direction': cmd.direction,
                'cargo_type': cmd.cargo_type,
                'amount': cmd.amount,
                'planet_id': cmd.planet_id
            }
            order = FleetOrder(OrderType.TRANSFER, target=transfer_params)
            fleet.add_order(order)
            log_info(f"GameSession: Issued TRANSFER order for Fleet {fleet.id}")

        return result

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
            'human_player_ids': self.human_player_ids.copy()
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

        # Initialize turn engine
        session.turn_engine = TurnEngine()

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
