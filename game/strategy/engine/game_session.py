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
