from test_framework.scenario import CombatScenario
import os
import pygame
import json
from game.simulation.entities.ship import Ship

class RangeTest(CombatScenario):
    def __init__(self):
        super().__init__()
        self.name = "Range Test"
        self.description = "Verifies maximum range limits (1000 units). Target at 990 should be hit, 1010 should be missed."
        self.max_ticks = 200 # Short test, just enough to fire once or twice
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(base_dir, "tests", "data")
        
        self.components_path = os.path.join(self.data_dir, "test_components.json")
        self.vehicle_classes_path = os.path.join(self.data_dir, "test_vehicleclasses.json")
        self.modifiers_path = os.path.join(self.data_dir, "test_modifiers.json")
        
    def setup(self, battle_engine):
        ships_dir = os.path.join(self.data_dir, "ships")
        
        def load_test_ship(filename, name, team_id, x, y):
            path = os.path.join(ships_dir, filename)
            with open(path, 'r') as f:
                data = json.load(f)
            
            ship = Ship.from_dict(data)
            ship.name = name
            ship.team_id = team_id
            ship.start_pos = pygame.math.Vector2(x, y)
            ship.position = pygame.math.Vector2(x, y)
            ship.velocity = pygame.math.Vector2(0, 0)
            ship.ai_strategy = "idle"
            ship.recalculate_stats()
            return ship

        # Range of Omni Railgun is 1000
        # Configs: (Distance, Expected Hit?)
        configs = [
            (950, True, "In_Range"),
            (1050, False, "Out_Range")
        ]
        
        attackers = []
        targets = []
        
        y_step = 2000
        
        for i, (dist, expect_hit, label) in enumerate(configs):
            y_pos = i * y_step
            
            p1 = load_test_ship("Test_Attacker.json", f"Attacker_{label}", 0, 0, y_pos)
            p2 = load_test_ship("Test_Target.json", f"Target_{label}", 1, dist, y_pos)
            
            attackers.append(p1)
            targets.append(p2)
            
        self.targets = targets
        self.expectations = {f"Target_{label}": expect_hit for _, expect_hit, label in configs}
        
        battle_engine.logger.enabled = True
        battle_engine.logger.start_session()
        battle_engine.start(attackers, targets)
        
        self.initial_hps = {t.name: self.get_total_hp(t) for t in self.targets}
        self.initial_positions = {s: pygame.math.Vector2(s.position) for s in battle_engine.ships}

    def get_total_hp(self, ship):
        total = 0
        for c in ship.get_all_components():
            total += c.current_hp
        return total

    def update(self, battle_engine):
        # Position Lock
        for s in battle_engine.ships:
            if s in self.initial_positions:
                s.position = pygame.math.Vector2(self.initial_positions[s])
                s.velocity.update(0, 0)
                
        if battle_engine.tick_counter % 50 == 0:
            print(f"--- Tick {battle_engine.tick_counter} ---")
            for s in self.targets:
                hp = self.get_total_hp(s)
                print(f"{s.name}: HP={hp}")

    def verify(self, battle_engine):
        success = True
        print("\n--- Verification ---")
        
        for target in self.targets:
            start_hp = self.initial_hps[target.name]
            end_hp = self.get_total_hp(target)
            damage = start_hp - end_hp
            should_hit = self.expectations[target.name]
            
            print(f"{target.name}: Dmg={damage}, ExpectedHit={should_hit}")
            
            if should_hit:
                if damage <= 0:
                    print(f"FAILURE: {target.name} should have been hit but took NO damage.")
                    success = False
            else:
                if damage > 0:
                    print(f"FAILURE: {target.name} should NOT have been hit but took {damage} damage.")
                    success = False
                    
        return success
