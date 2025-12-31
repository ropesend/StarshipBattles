from test_framework.scenario import CombatScenario
from components import create_component, LayerType
import pygame
import pygame

import os

class GunAccuracyTest(CombatScenario):
    def __init__(self):
        super().__init__()
        self.name = "Gun Accuracy Test"
        self.description = "Verifies 100% accuracy and fixed damage at 10%, 50%, and 90% ranges."
        self.max_ticks = 1000 # 10 seconds (Approx 10 shots)
        
        # Setup Test Data Paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(base_dir, "tests", "data")
        
        self.components_path = os.path.join(self.data_dir, "test_components.json")
        self.vehicle_classes_path = os.path.join(self.data_dir, "test_classes.json")
        self.modifiers_path = os.path.join(self.data_dir, "test_modifiers.json")
        
    def setup(self, battle_engine):
        # Pairs of (Range, Y-Offset)
        # Range 1000. 10% = 100, 50% = 500, 90% = 900.
        configs = [
            (100, 0, "Range 10%"),
            (500, 2000, "Range 50%"),
            (900, 4000, "Range 90%")
        ]
        
        import json
        from ship import Ship
        
        # Helper to load ships from JSON
        ships_dir = os.path.join(self.data_dir, "ships")
        
        def load_test_ship(filename, name, team_id, x, y):
            path = os.path.join(ships_dir, filename)
            with open(path, 'r') as f:
                data = json.load(f)
            
            ship = Ship.from_dict(data)
            ship.name = name
            ship.team_id = team_id
            ship.start_pos = pygame.math.Vector2(x, y) # For reset
            ship.position = pygame.math.Vector2(x, y)
            ship.velocity = pygame.math.Vector2(0, 0)
            ship.ai_strategy = "idle" # Ensure idle
            ship.recalculate_stats()
            # ship.rect.center = ship.position # Not needed for headless/Ship object? 
            return ship

        attackers = []
        targets = []
        
        for r, y_offset, label in configs:
            attacker = load_test_ship(
                "Test_Attacker.json",
                f"Attacker_{label}",
                0,
                0, y_offset
            )
            attacker.angle = 0
            attackers.append(attacker)
            
            target = load_test_ship(
                "Test_Target.json",
                f"Target_{label}",
                1,
                r, y_offset
            )
            targets.append(target)
            
        self.targets = targets
        
        # Enable Logging
        battle_engine.logger.enabled = True
        battle_engine.logger.start_session()
        battle_engine.start(attackers, targets)
        
        # Store initial HPs and Positions
        self.initial_hps = {t: self.get_total_hp(t) for t in self.targets}
        self.initial_positions = {s: pygame.math.Vector2(s.position) for s in battle_engine.ships}
        
    def get_total_hp(self, ship, debug=False):
        total = 0
        for l_type, layer in ship.layers.items():
            for c in layer['components']:
                total += c.current_hp
                if debug:
                    print(f"  [{l_type.name}] {c.name}: {c.current_hp}/{c.max_hp}")
        return total

    def update(self, battle_engine):
        # Force stationary by resetting position
        for s in battle_engine.ships:
            if s in self.initial_positions:
                s.position = pygame.math.Vector2(self.initial_positions[s])
                s.velocity.update(0, 0)
        
        if battle_engine.tick_counter % 10 == 0:
            print(f"--- Tick {battle_engine.tick_counter} ---")
            for s in battle_engine.ships:
                shots = s.total_shots_fired if hasattr(s, 'total_shots_fired') else 0
                debug = False
                if "Target_Range 10%" in s.name:
                    debug = True
                    # print(f"Debgging {s.name}:")
                
                hp = self.get_total_hp(s, debug=debug)
                print(f"{s.name}: HP={hp} Derelict={getattr(s, 'is_derelict', False)} Shots={shots} Pos={s.position} Rad={s.radius}")
            
            # Projectile Debug
            projs = battle_engine.projectile_manager.projectiles
            print(f"Active Projectiles: {len(projs)}")
            for i, p in enumerate(projs[:5]): # First 5
                print(f"  P{i}: Pos={p.position} Vel={p.velocity} Owner={p.owner.name}")

    def verify(self, battle_engine):
        success = True
        
        for target in self.targets:
            start_hp = self.initial_hps[target]
            # Recalculate end HP manually
            end_hp = self.get_total_hp(target)
            damage_taken = start_hp - end_hp
            
            print(f"{target.name}: StartHP={start_hp}, EndHP={end_hp}, Dmg={damage_taken}")
            
            # 1. Verify Damage is multiple of 50
            if damage_taken % 50 != 0:
                print(f"FAILURE: {target.name} damage taken ({damage_taken}) is not multiple of 50.")
                success = False
                
            # 2. Verify some damage was taken (it fired)
            if damage_taken == 0:
                print(f"FAILURE: {target.name} took NO damage.")
                success = False
                
            # 3. Verify Hits (Approximate)
            # 1000 ticks / 100 reload = 10 shots.
            # Allow +/- 1 for timing variations
            expected_min = 450 # 9 shots
            expected_max = 550 # 11 shots
            
            if not (expected_min <= damage_taken <= expected_max):
                print(f"FAILURE: {target.name} damage {damage_taken} out of expected range [{expected_min}-{expected_max}]")
                success = False
                
        return success
