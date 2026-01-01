import os
import pygame
from test_framework.scenario import CombatScenario
from ship import Ship

class SimpleDuel(CombatScenario):
    """
    A simple 1v1 duel between a Gun Ship and a Target Dummy.
    Tests basic firing, damage application, and destruction.
    """
    def __init__(self):
        super().__init__()
        self.name = "Simple Duel"
        self.description = "A basic 1v1 duel to verify combat mechanics."
        self.max_ticks = 1200 # Increased for lower damage weapons
        
        # Setup Test Data Paths
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "tests", "data")
        
        self.components_path = os.path.join(data_dir, "test_components.json")
        self.vehicle_classes_path = os.path.join(data_dir, "test_vehicleclasses.json")
        self.modifiers_path = os.path.join(data_dir, "test_modifiers.json")
        
    def setup(self, battle_engine):
        # 1. Attacker (Team 0)
        attacker = self.create_ship(
            name="Attacker", 
            team_id=0, 
            x=0, y=0, 
            ship_class="TestShip_S_2L",
            components=[
                "test_engine_infinite", "test_weapon_proj_omni", "test_storage_fuel"
            ]
        )

        # Manually orient to face target (Target is at 0, 500)
        attacker.angle = 0 # Face Right
        
        # 2. Target (Team 1)
        # Reduced HP to ensure kill before potential collision
        target = self.create_ship(
            name="Target",
            team_id=1,
            x=800, y=0,
            ship_class="TestShip_Target",
            components=["test_thruster_std", "test_engine_std", "test_storage_fuel"]
        )
        
        battle_engine.start([attacker], [target])

    def verify(self, battle_engine):
        # We expect the Target to be destroyed
        attacker = battle_engine.ships[0]
        target = battle_engine.ships[1]
        
        self.results['attacker_hp'] = attacker.hp
        self.results['target_hp'] = target.hp
        
        if not target.is_alive:
            print("Target destroyed successfully.")
            return True
        else:
            print(f"Target survived with {target.hp} HP.")
            return False
