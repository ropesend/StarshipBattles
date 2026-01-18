import os
from game.core.logger import log_info
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.game_config import GameConfig
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy

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
        
        # Allow legacy parameters to override config for backward compatibility
        if galaxy_radius is not None:
            config.galaxy_radius = galaxy_radius
        if system_count is not None:
            config.system_count = system_count
            
        self.config = config
        self.turn_number = 1
        self.save_path = None  # Set when save game is created/loaded (Phase 3)

        # Engine
        self.turn_engine = TurnEngine()
        
        # Empires - using config paths instead of hardcoded values
        self.player_empire = Empire(
            0, 
            config.player_name, 
            config.player_color, 
            theme_path=config.player_theme_path
        )
        self.enemy_empire = Empire(
            1, 
            config.enemy_name, 
            config.enemy_color, 
            theme_path=config.enemy_theme_path
        )
        
        self.empires = [self.player_empire, self.enemy_empire]
        
        # Human Players (indices in empires list)
        self.human_player_ids = [0, 1]
        
        # Galaxy
        self.galaxy = Galaxy(radius=config.galaxy_radius)
        self.systems = []
        
        # Initialization
        self._initialize_galaxy(config.system_count)
        self._setup_initial_scenario()

    def _initialize_galaxy(self, count):
        log_info("GameSession: Generating Galaxy...")
        self.systems = self.galaxy.generate_systems(count=count, min_dist=400)
        self.galaxy.generate_warp_lanes()
        log_info(f"GameSession: Generated {len(self.systems)} systems.")

    def _setup_initial_scenario(self):
        """Set up starting colonies and fleets."""
        if not self.systems:
            return

        # Player Home (Sys 0)
        p_home_sys = self.systems[0]
        if p_home_sys.planets:
            p_planet = p_home_sys.planets[0]
            self.player_empire.add_colony(p_planet)
            
            # Starting Fleet removed per original code request
            # f1 = Fleet(1, 0, p_home_sys.global_location)
            # f1.ships.append("Scout")
            # self.player_empire.add_fleet(f1)

        # Enemy Home (Last Sys)
        e_home_sys = self.systems[-1]
        if e_home_sys.planets:
            e_planet = e_home_sys.planets[0]
            self.enemy_empire.add_colony(e_planet)

    def process_turn(self):
        """Advance the game simulation by one full turn."""
        log_info(f"GameSession: Processing Turn {self.turn_number}...")
        self.turn_engine.process_turn(self.empires, self.galaxy)
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
        
        path = find_hybrid_path(self.galaxy, fleet.location, target_hex)
        
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
        
        return None # Warning/Error?

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
            from game.strategy.engine.turn_engine import ValidationResult
            return ValidationResult(False, "Fleet not found.")

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
            from game.strategy.engine.turn_engine import ValidationResult
            return ValidationResult(False, "Fleet not found.")
            
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
                 from game.strategy.engine.turn_engine import ValidationResult
                 # If path is None and locations differ, it's unreachable
                 return ValidationResult(False, "Target is unreachable or invalid.")
        
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

        from game.strategy.engine.turn_engine import ValidationResult
        return ValidationResult(True, "Move order issued.")

    def _handle_build_ship_command(self, cmd):
        """Handle IssueBuildShipCommand."""
        # 1. Resolve Planet
        planet = self._get_planet_by_id(cmd.planet_id)
        if not planet:
             from game.strategy.engine.turn_engine import ValidationResult
             return ValidationResult(False, "Planet not found.")
             
        # 2. Validate Ownership
        # Check if planet belongs to a known empire?
        # We generally trust the ID resolution, but logic should check.
        # For now, just executed.
        
        # 3. Apply
        # Standard build time = 1 turn for now? Logic was `add_production("Colony Ship", 1)`
        # We should probably look up design cost/time.
        # For now, hardcode 1 as per legacy.
        planet.add_production(cmd.design_name, 1)
        
        from game.strategy.engine.turn_engine import ValidationResult
        return ValidationResult(True, f"Started construction of {cmd.design_name}.")

    def _get_fleet_by_id(self, fleet_id):
        """Helper to find fleet."""
        for emp in self.empires:
             for f in emp.fleets:
                 if f.id == fleet_id: return f
        return None

    def _get_planet_by_id(self, planet_id):
        """Helper to find planet using Galaxy's O(1) registry."""
        return self.galaxy.get_planet_by_id(planet_id)
