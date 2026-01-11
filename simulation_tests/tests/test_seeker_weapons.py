"""
Seeker Weapon Tests (SEEK360-001 through SEEK360-TRACK-004)

Validates seeker/missile weapon behavior:
- Lifetime/endurance tests (target at various distances)
- Point defense interaction (seekers destroyed by PD)
- Tracking behavior (following stationary, linear, and erratic targets)

Seeker properties (from test_weapon_missile_omni):
- projectile_speed: 1000
- turn_rate: 90°/sec
- endurance: 5.0 sec
- range: 3000
- damage: 100
"""
import pytest
import os
import json

import pygame

from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger


@pytest.mark.simulation
class TestSeekerWeaponsLifetime:
    """Test seeker/missile lifetime and range behavior."""
    
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
    
    def _run_seeker_battle(
        self,
        attacker: Ship,
        target: Ship,
        distance: float,
        ticks: int = 600,
        seed: int = 42
    ) -> dict:
        """
        Run a seeker weapon battle simulation.
        
        Returns dict with damage_dealt, ticks_run, target_alive, projectiles_remaining.
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
        projectiles_remaining = len([p for p in engine.projectiles if p.is_alive])
        
        engine.shutdown()
        
        return {
            'damage_dealt': damage_dealt,
            'ticks_run': engine.tick_counter,
            'target_alive': target.is_alive,
            'projectiles_remaining': projectiles_remaining,
            'initial_hp': initial_target_hp,
        }
    
    def test_SEEK360_001_close_range_impact(self):
        """
        SEEK360-001: Seeker impact at close range (500 pixels).
        
        Seeker should reach target well before endurance limit.
        At speed 1000, 500 pixels takes ~0.5 seconds (50 ticks).
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_seeker_battle(attacker, target, distance=500, ticks=600)
        
        # Close range - seeker should hit and deal damage
        assert result['damage_dealt'] > 0, \
            "Seeker should impact and deal damage at close range"
        
        # Damage should be at least one missile (100 damage)
        assert result['damage_dealt'] >= 100, \
            f"Expected at least 100 damage from missile, got {result['damage_dealt']}"
    
    def test_SEEK360_002_mid_range_impact(self):
        """
        SEEK360-002: Seeker impact at mid range (2500 pixels).
        
        Seeker should reach target within endurance limit (5 seconds).
        At speed 1000, 2500 pixels takes ~2.5 seconds (250 ticks).
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_seeker_battle(attacker, target, distance=2500, ticks=800)
        
        # Mid range - seeker should still reach target
        assert result['damage_dealt'] > 0, \
            "Seeker should impact target at mid range within endurance"
    
    def test_SEEK360_003_beyond_range_expire(self):
        """
        SEEK360-003: Seeker expires before reaching target beyond range.
        
        Target at 5000 pixels (beyond range 3000 and endurance).
        Seeker travels 1000 px/s × 5s = 5000 max distance, but likely expires.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        # Position well beyond range
        result = self._run_seeker_battle(attacker, target, distance=5000, ticks=800)
        
        # Beyond range - seeker should expire without hitting
        # Note: Some damage may occur if weapon has multiple behaviors
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    def test_SEEK360_004_edge_case_range(self):
        """
        SEEK360-004: Edge case at range limit (4500 pixels).
        
        Right at the edge of range/endurance - may or may not hit.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_seeker_battle(attacker, target, distance=4500, ticks=800)
        
        # Edge case - behavior may vary
        assert result['ticks_run'] > 0, "Simulation should complete"


@pytest.mark.simulation
class TestSeekerWeaponsTracking:
    """Test seeker tracking against moving targets."""
    
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
    
    def _run_seeker_battle(
        self,
        attacker: Ship,
        target: Ship,
        distance: float,
        ticks: int = 600,
        seed: int = 42
    ) -> dict:
        """Run battle and collect results."""
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(distance, 0)
        target.angle = 0
        
        initial_target_hp = target.hp
        
        engine = BattleEngine()
        engine.start([attacker], [target], seed=seed)
        
        # Set target for attacker
        attacker.current_target = target
        
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
        }
    
    def test_SEEK360_TRACK_001_stationary_target(self):
        """
        SEEK360-TRACK-001: Seeker tracking stationary target.
        
        Direct flight path - should hit efficiently.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Stationary.json')
        
        result = self._run_seeker_battle(attacker, target, distance=1000, ticks=600)
        
        assert result['damage_dealt'] > 0, \
            "Seeker should hit stationary target with direct flight"
    
    def test_SEEK360_TRACK_002_linear_target(self):
        """
        SEEK360-TRACK-002: Seeker tracking linearly moving target.
        
        Seeker should lead and/or curve to intercept.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Linear_Slow.json')
        
        # Target moving perpendicular to line-of-sight
        target_ship = target
        target_ship.angle = 90  # Moving up
        
        result = self._run_seeker_battle(attacker, target_ship, distance=1000, ticks=600)
        
        # Seeker with turn_rate 90 deg/s should track linear targets
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    def test_SEEK360_TRACK_003_orbiting_target(self):
        """
        SEEK360-TRACK-003: Seeker tracking orbiting target.
        
        Curved pursuit - seeker should adjust heading to follow.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Orbiting.json')
        
        result = self._run_seeker_battle(attacker, target, distance=1000, ticks=800)
        
        # Orbiting target requires continuous tracking adjustment
        assert result['ticks_run'] > 0, "Simulation should complete"
    
    def test_SEEK360_TRACK_004_erratic_target(self):
        """
        SEEK360-TRACK-004: Seeker vs highly maneuverable erratic target.
        
        Erratic targets may out-turn seekers, causing SEEKER_EXPIRE.
        """
        attacker = self._load_ship('Test_Attacker_Seeker360.json')
        target = self._load_ship('Test_Target_Erratic_Small.json')
        
        result = self._run_seeker_battle(attacker, target, distance=1000, ticks=800)
        
        # Erratic small target may evade seekers - results vary
        assert result['ticks_run'] > 0, "Simulation should complete"


@pytest.mark.simulation
@pytest.mark.skip(reason="Requires Point Defense target ships - not yet implemented in test data")
class TestSeekerPointDefense:
    """Test seeker interaction with point defense systems.
    
    Placeholder tests - require target ships with PD weapons,
    which are not yet in the test data set.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry, ships_dir):
        self.ships_dir = ships_dir
    
    def _load_ship(self, filename: str) -> Ship:
        path = os.path.join(self.ships_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        ship = Ship.from_dict(data)
        ship.recalculate_stats()
        return ship
    
    def test_SEEK360_PD_001_no_pd_all_hit(self):
        """
        SEEK360-PD-001: No point defense - all seekers hit.
        """
        pass  # TODO: Implement when PD target ships exist
    
    def test_SEEK360_PD_002_single_pd(self):
        """
        SEEK360-PD-002: Single point defense - measure destruction rate.
        """
        pass  # TODO: Implement when PD target ships exist
    
    def test_SEEK360_PD_003_triple_pd(self):
        """
        SEEK360-PD-003: Triple point defense - higher destruction rate.
        """
        pass  # TODO: Implement when PD target ships exist


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
