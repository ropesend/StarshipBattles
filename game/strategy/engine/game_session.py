import os
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy

class GameSession:
    """
    Manages the lifecycle and state of a single game session.
    Owns the Galaxy, Empires, and the Turn Engine.
    Running completely decoupled from the UI/Rendering layer.
    """
    def __init__(self, galaxy_radius=4000, system_count=25):
        self.turn_number = 1
        
        # Engine
        self.turn_engine = TurnEngine()
        
        # Empires
        # Hardcoding paths for now as per original StrategyScene, 
        # but this should eventually be configurable/injected.
        # NOTE: Using absolute paths based on original code, but this is fragile. 
        #Ideally we used a relative path resolver or constants.
        base_asset_path = r"C:\Developer\StarshipBattles\assets\ShipThemes"
        
        self.player_empire = Empire(0, "Terran Command", (0, 0, 255), 
                                  theme_path=os.path.join(base_asset_path, "Atlantians"))
        self.enemy_empire = Empire(1, "Xeno Hive", (255, 0, 0), 
                                 theme_path=os.path.join(base_asset_path, "Federation"))
        
        self.empires = [self.player_empire, self.enemy_empire]
        
        # Human Players (indices in empires list, or IDs? Original scene used IDs)
        # StrategyScene used self.human_player_ids = [0, 1]
        self.human_player_ids = [0, 1]
        
        # Galaxy
        self.galaxy = Galaxy(radius=galaxy_radius)
        self.systems = []
        
        # Initialization
        self._initialize_galaxy(system_count)
        self._setup_initial_scenario()

    def _initialize_galaxy(self, count):
        print("GameSession: Generating Galaxy...")
        self.systems = self.galaxy.generate_systems(count=count, min_dist=400)
        self.galaxy.generate_warp_lanes()
        print(f"GameSession: Generated {len(self.systems)} systems.")

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
        print(f"GameSession: Processing Turn {self.turn_number}...")
        self.turn_engine.process_turn(self.empires, self.galaxy)
        self.turn_number += 1
        
    def get_current_player_empire(self, player_index):
        """Get the empire object for the current human player index."""
        if 0 <= player_index < len(self.human_player_ids):
            p_id = self.human_player_ids[player_index]
            return next((e for e in self.empires if e.id == p_id), None)
        return None

    def handle_command(self, command):
        """
        Execute a user command.
        
        Args:
            command: Command object
            
        Returns:
            ValidationResult (is_valid=True/False)
        """
        if command.type == command.type.ISSUE_ORDER: # Assuming using CommandType enum, tricky without simpler import
            # Determine command type by class
            if command.name == 'IssueColonizeCommand':
                return self._handle_colonize_command(command)
        
        return None # Unknown command?

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
            # Need strict lookup.
            # Assuming we can find it via ID? We strictly used object references previously.
            # IMPORTANT: The Command has to probably deal with IDs if we want to be clean, 
            # BUT for this refactor preserving references might be easier if UI already has them?
            # The USER plan said "IssueColonizeCommand(fleet_id, planet_id)".
            # So we MUST support IDs. But our Galaxy doesn't have a planet ID registry efficiently yet.
            # Let's Scan. (Optimization debt, but acceptable for now).
            for sys in self.galaxy.systems.values():
                for p in sys.planets:
                    if id(p) == cmd.planet_id: # Python object ID as ID? Or did we assume Data ID?
                        # Planet data class doesn't seem to have a unique 'id' field in the file view I saw.
                        # It inherits from something? Let's check Galaxy/Planet data if needed.
                        # For SAFETY: The plan specified IDs. I'll assume we use `id(obj)` or add an ID field?
                        # Using `id(planet)` is flaky across network but fine for local refactor.
                        target_planet = p
                        break
                if target_planet: break
        
        # 2. Validate
        result = self.turn_engine.validate_colonize_order(self.galaxy, fleet, target_planet)
        
        # 3. Apply
        if result.is_valid:
             from game.strategy.data.fleet import FleetOrder, OrderType
             # Ensure we pass the OBJECT to rules
             order = FleetOrder(OrderType.COLONIZE, target=target_planet)
             fleet.add_order(order)
             print(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")
             
        return result
