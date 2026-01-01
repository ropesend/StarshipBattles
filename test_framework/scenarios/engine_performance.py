from test_framework.scenario import CombatScenario
import math

class EnginePerformanceTest(CombatScenario):
    def __init__(self):
        super().__init__()
        self.name = "Engine Performance"
        self.description = "Tests acceleration, top speed, and fuel consumption across different mass/thrust profiles."
        self.max_ticks = 1000
        
        # Setup Test Data Paths
        import os
        # Base dir is Starship Battles root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "tests", "data")
        
        self.components_path = os.path.join(data_dir, "test_components.json")
        self.vehicle_classes_path = os.path.join(data_dir, "test_vehicleclasses.json")
        self.modifiers_path = os.path.join(data_dir, "test_modifiers.json")
        
    def setup(self, battle_engine):
        # 1. Light Scout (High Thrust/Mass Ratio)
        # 1 Engine (10), 1 Bridge (10), Hull (50) = 70 Mass
        # 1 Engine (10), Hull (50) = 60 Mass
        # Thrust 500. Expected Max Speed = (500 * 25) / 60 = 208.33
        engines = ["test_engine_infinite"] * 4 # Defined here for interceptor, but used in the edit for scout
        self.scout = self.create_ship(
            name="Scout",
            team_id=0,
            x=0, y=100,
            ship_class="TestShip_S_2L",
            components=["test_engine_infinite"]
        )
        self.scout.angle = 0
        
        # 2. Heavy Hauler (Low Thrust/Mass Ratio)
        # 1 Engine (10), 1 Bridge (10), Hull (50), 10 Armor (200) = 270 Mass
        armor_list = ["test_armor_std"] * 10
        self.hauler = self.create_ship(
            name="Hauler",
            team_id=0,
            x=0, y=200,
            ship_class="TestShip_S_2L",
            components=["test_engine_infinite"] + armor_list
        )
        self.hauler.angle = 0
        
        # 3. Interceptor (High Thrust, Medium Mass)
        # 4 Engines (40), 1 Bridge (10), Hull (50) = 100 Mass
        # Thrust 2000. Expected Max Speed = (2000 * 25) / 100 = 500.0
        engines = ["test_engine_infinite"] * 4
        self.interceptor = self.create_ship(
            name="Interceptor",
            team_id=0,
            x=0, y=300,
            ship_class="TestShip_S_2L",
            components=engines
        )
        self.interceptor.angle = 0
        
        # 4. Dummy Target (Required to keep battle active)
        dummy = self.create_ship(
            name="Monitor",
            team_id=1,
            x=10000, y=0,
            ship_class="TestShip_Target",
            components=["test_armor_std", "test_engine_infinite"] # Minimal Setup
        )
        
        battle_engine.start([self.scout, self.hauler, self.interceptor], [dummy])
        
    def update(self, battle_engine):
        # Force all ships to thrust forward
        for ship in [self.scout, self.hauler, self.interceptor]:
            ship.engine_throttle = 1.0
            ship.thrust_forward() # Consumes fuel (0), sets flag
            
            # Print stats every 50 ticks
            if battle_engine.tick_counter % 50 == 0:
                 print(f"Tick {battle_engine.tick_counter} [{ship.name}]: Spd={ship.current_speed:.1f}/{ship.max_speed:.1f} Acc={ship.acceleration_rate:.1f}")

    def verify(self, battle_engine):
        success = True
        
        for ship in [self.scout, self.hauler, self.interceptor]:
            # 1. Check Max Speed Reached
            if not math.isclose(ship.current_speed, ship.max_speed, rel_tol=0.01):
                print(f"FAILURE: {ship.name} did not reach max speed. Got {ship.current_speed}, Expected {ship.max_speed}")
                success = False
                
            # 2. Verify Calculated Stats match expected physics formulas locally
            expected_speed = (ship.total_thrust * 25.0) / ship.mass
            if not math.isclose(ship.max_speed, expected_speed, rel_tol=0.01):
                 print(f"FAILURE: {ship.name} stats mismatch. Calc MaxSpeed {ship.max_speed} != Expected {expected_speed}")
                 success = False

        return success
