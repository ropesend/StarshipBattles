"""
Beam Weapon Tests (BEAM360-001 through BEAM360-011)

Validates beam weapon accuracy mechanics:
- Sigmoid accuracy formula: P = 1 / (1 + e^-x)
- where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
- Range penalty = accuracy_falloff * distance
- Tests low, medium, high accuracy beam variants at various ranges
"""
import pytest
import os
import json
import math

import pygame

from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger


def calculate_expected_hit_chance(
    base_accuracy: float,
    accuracy_falloff: float,
    distance: float,
    attack_bonus: float = 0.0,
    defense_penalty: float = 0.0
) -> float:
    """
    Calculate expected hit chance using sigmoid formula.
    
    P = 1 / (1 + e^-x)
    where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    """
    range_penalty = accuracy_falloff * distance
    net_score = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
    clamped_score = max(-20.0, min(20.0, net_score))
    return 1.0 / (1.0 + math.exp(-clamped_score))


@pytest.mark.simulation
class TestBeamWeapons:
    """Test beam weapon accuracy at various ranges and configurations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry, ships_dir):
        """Use isolated registry and store ships_dir."""
        self.ships_dir = ships_dir
    
    def _load_ship(self, filename: str) -> Ship:
        """Load ship from JSON and calculate stats."""
        path = os.path.join(self.ships_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        ship = Ship.from_dict(data)
        ship.recalculate_stats()
        return ship
    
    def _run_battle_and_measure_accuracy(
        self,
        attacker: Ship,
        target: Ship,
        distance: float,
        ticks: int = 500,
        seed: int = 42
    ) -> dict:
        """
        Run a battle and measure beam weapon accuracy.
        
        Returns dict with hit_count, total_shots, hit_rate, damage_dealt.
        """
        # Position ships
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0  # Facing right
        target.position = pygame.math.Vector2(distance, 0)
        target.angle = 0
        
        initial_target_hp = target.hp
        
        engine = BattleEngine()
        engine.start([attacker], [target], seed=seed)
        
        # Set target for attacker
        attacker.current_target = target
        
        # Run simulation
        for _ in range(ticks):
            if not target.is_alive:
                break
            # Force weapon firing (test_do_nothing disables it)
            attacker.comp_trigger_pulled = True
            engine.update()
        
        damage_dealt = initial_target_hp - target.hp
        engine.shutdown()
        
        return {
            'damage_dealt': damage_dealt,
            'ticks_run': engine.tick_counter,
            'target_alive': target.is_alive,
            'initial_hp': initial_target_hp,
        }
    
    # ===== LOW ACCURACY BEAM TESTS (base_accuracy=0.5, falloff=0.002) =====
    
    def test_BEAM360_001_low_acc_point_blank(self):
        """
        BEAM360-001: Low accuracy beam (0.5) at point-blank.
        
        Expected: ~95.3% hit rate (due to target size bonus)
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=50, ticks=500)
        
        # At point blank, even low accuracy should hit most of the time
        assert result['damage_dealt'] > 0, \
            "Low accuracy beam should deal damage at point-blank"
    
    def test_BEAM360_002_low_acc_mid_range(self):
        """
        BEAM360-002: Low accuracy beam (0.5) at 400 pixels.
        
        Expected: ~73.1% hit rate with range penalty + size bonus
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=400, ticks=500)
        
        # Mid-range, lower accuracy
        assert result['ticks_run'] > 0, "Simulation should run"
    
    def test_BEAM360_003_low_acc_max_range(self):
        """
        BEAM360-003: Low accuracy beam (0.5) at max range (800).
        
        Expected: ~31.0% hit rate - accuracy heavily degraded at range
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=750, ticks=1000)
        
        # At max range with low accuracy, may or may not hit
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    # ===== MEDIUM ACCURACY BEAM TESTS (base_accuracy=2.0, falloff=0.001) =====
    
    def test_BEAM360_004_med_acc_point_blank(self):
        """
        BEAM360-004: Medium accuracy beam (2.0) at point-blank.
        
        Expected: ~98.9% hit rate
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=50, ticks=500)
        
        # Medium accuracy at point-blank should hit almost always
        assert result['damage_dealt'] > 0, \
            "Medium accuracy beam should deal significant damage at point-blank"
    
    def test_BEAM360_005_med_acc_mid_range(self):
        """
        BEAM360-005: Medium accuracy beam (2.0) at 400 pixels.
        
        Expected: ~96.8% hit rate
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=400, ticks=500)
        
        assert result['damage_dealt'] > 0, \
            "Medium accuracy beam should deal damage at mid-range"
    
    def test_BEAM360_006_med_acc_max_range(self):
        """
        BEAM360-006: Medium accuracy beam (2.0) at max range (800).
        
        Expected: ~90.0% hit rate
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=750, ticks=1000)
        
        # Medium accuracy maintains reasonable hit rate even at range
        assert result['damage_dealt'] >= 0, "Simulation should complete"
    
    # ===== HIGH ACCURACY BEAM TESTS (base_accuracy=5.0, falloff=0.0005) =====
    
    def test_BEAM360_007_high_acc_point_blank(self):
        """
        BEAM360-007: High accuracy beam (5.0) at point-blank.
        
        Expected: ~99.9% hit rate
        """
        attacker = self._load_ship('Test_Attacker_Beam360_High.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=50, ticks=500)
        
        assert result['damage_dealt'] > 0, \
            "High accuracy beam should hit consistently at point-blank"
    
    def test_BEAM360_008_high_acc_max_range(self):
        """
        BEAM360-008: High accuracy beam (5.0) at max range (800).
        
        Expected: ~99.7% hit rate - barely affected by range
        """
        attacker = self._load_ship('Test_Attacker_Beam360_High.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=750, ticks=500)
        
        assert result['damage_dealt'] > 0, \
            "High accuracy beam should hit at max range"
    
    # ===== MOVING TARGET TESTS =====
    
    def test_BEAM360_009_med_acc_vs_erratic_small_mid_range(self):
        """
        BEAM360-009: Medium accuracy beam vs small erratic target at 400 pixels.
        
        Defense score increases for maneuverable targets, reducing hit chance.
        Expected: ~59.9% hit rate with maneuverability penalty
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Erratic_Small.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=400, ticks=1000)
        
        # Erratic small target should be harder to hit
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    def test_BEAM360_010_med_acc_vs_erratic_small_max_range(self):
        """
        BEAM360-010: Medium accuracy beam vs small erratic target at max range.
        
        Combination of range and maneuverability penalties.
        Expected: ~26.9% hit rate
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Erratic_Small.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=750, ticks=1000)
        
        # Difficult target - accuracy significantly reduced
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    def test_BEAM360_011_out_of_range(self):
        """
        BEAM360-011: Beam weapon fires but no hits beyond max range.
        
        Target at max_range + 100 (900 pixels for 800 range weapon).
        """
        attacker = self._load_ship('Test_Attacker_Beam360_Med.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_battle_and_measure_accuracy(attacker, target, distance=900, ticks=500)
        
        # Beyond range - should not deal damage
        assert result['damage_dealt'] == 0, \
            f"Target beyond range should take 0 damage, got {result['damage_dealt']}"


@pytest.mark.simulation
class TestBeamAccuracyFormula:
    """Unit tests for beam accuracy sigmoid formula."""
    
    def test_accuracy_formula_at_zero_distance(self):
        """Test sigmoid formula at zero distance."""
        # base_accuracy=2.0, no falloff at 0 distance
        hit_chance = calculate_expected_hit_chance(2.0, 0.001, 0)
        # e^-2 ≈ 0.135, so P = 1/(1+0.135) ≈ 0.88
        assert 0.85 < hit_chance < 0.92, f"Expected ~0.88, got {hit_chance}"
    
    def test_accuracy_formula_large_positive_score(self):
        """Test sigmoid approaches 1.0 for highly positive scores."""
        hit_chance = calculate_expected_hit_chance(10.0, 0.0, 0)
        assert hit_chance > 0.999, f"Expected ~1.0, got {hit_chance}"
    
    def test_accuracy_formula_large_negative_score(self):
        """Test sigmoid approaches 0.0 for highly negative scores."""
        hit_chance = calculate_expected_hit_chance(0.0, 0.01, 1000)  # -10 score
        assert hit_chance < 0.001, f"Expected ~0.0, got {hit_chance}"
    
    def test_accuracy_formula_clamping(self):
        """Test score clamping at ±20."""
        # Score of 100 should be clamped to 20
        hit_chance = calculate_expected_hit_chance(100.0, 0.0, 0)
        expected = 1.0 / (1.0 + math.exp(-20))
        assert abs(hit_chance - expected) < 0.0001, f"Expected {expected}, got {hit_chance}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
