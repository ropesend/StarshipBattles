"""
Tests for ShipCombatEngine - extracted combat logic from Ship class.

Follows TDD: Tests written first, then implementation.
This module tests the ShipCombatEngine class which handles:
- Firing weapons
- Target selection
- Lead calculation
- Damage application
- Projectile creation
"""
import pytest
import math
from unittest.mock import MagicMock, patch

from game.core.math import Vector2
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType, create_component
from game.core.constants import AttackType


class TestShipCombatEngineCreation:
    """Tests for ShipCombatEngine instantiation."""

    def test_combat_engine_can_be_created(self):
        """ShipCombatEngine can be instantiated with a ship."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)
        assert engine is not None
        assert engine._ship is ship

    def test_combat_engine_stores_ship_reference(self):
        """ShipCombatEngine stores reference to its ship."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)
        assert engine._ship is ship


class TestSolveLeadCalculation:
    """Tests for lead/interception calculation."""

    def test_solve_lead_stationary_target(self):
        """Lead calculation for stationary target returns direct time-to-target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target at (100, 0), stationary, projectile speed 10
        target_pos = Vector2(100, 0)
        target_vel = Vector2(0, 0)
        proj_speed = 10.0

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        # Time should be distance / speed = 100 / 10 = 10
        assert abs(t - 10.0) < 0.1

    def test_solve_lead_moving_target(self):
        """Lead calculation for moving target returns intercept time."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target moving right at 10 u/s at (100, 0)
        target_pos = Vector2(100, 0)
        target_vel = Vector2(10, 0)
        proj_speed = 20.0

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        # t should be ~10.0 based on quadratic solution
        assert t > 0
        assert abs(t - 10.0) < 0.5

    def test_solve_lead_no_solution(self):
        """Lead calculation returns 0 when target cannot be intercepted."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Target moving away faster than projectile
        target_pos = Vector2(100, 0)
        target_vel = Vector2(100, 0)  # Moving away at 100 u/s
        proj_speed = 10.0  # Only 10 u/s

        t = engine.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)

        assert t == 0


class TestTargetSelection:
    """Tests for target selection logic."""

    def test_select_target_returns_valid_enemy(self):
        """select_target returns an enemy ship from candidates."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create enemy candidate
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(100, 0)

        target = engine.select_target([enemy])
        assert target is enemy

    def test_select_target_excludes_friendlies(self):
        """select_target does not return friendly ships."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create friendly ship
        friendly = MagicMock()
        friendly.is_alive = True
        friendly.team_id = 0  # Same team

        target = engine.select_target([friendly])
        assert target is None

    def test_select_target_excludes_dead_ships(self):
        """select_target does not return dead ships."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create dead enemy
        dead_enemy = MagicMock()
        dead_enemy.is_alive = False
        dead_enemy.team_id = 1

        target = engine.select_target([dead_enemy])
        assert target is None

    def test_select_target_returns_closest_enemy(self):
        """select_target returns the closest valid enemy."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create multiple enemies at different distances
        far_enemy = MagicMock()
        far_enemy.is_alive = True
        far_enemy.team_id = 1
        far_enemy.position = Vector2(200, 0)

        close_enemy = MagicMock()
        close_enemy.is_alive = True
        close_enemy.team_id = 1
        close_enemy.position = Vector2(50, 0)

        target = engine.select_target([far_enemy, close_enemy])
        assert target is close_enemy


class TestFiringSolutionCalculation:
    """Tests for firing solution calculation."""

    def test_calculate_firing_solution_beam_weapon(self):
        """Firing solution for beam weapon aims directly at target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create target
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)

        # Create beam weapon component
        comp = MagicMock()
        comp.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
        comp.get_ability = MagicMock(return_value=None)

        aim_pos, aim_vec = engine.calculate_firing_solution(comp, target)

        assert aim_pos.x == 100
        assert aim_pos.y == 0
        assert aim_vec.x == 100
        assert aim_vec.y == 0

    def test_calculate_firing_solution_projectile_weapon(self):
        """Firing solution for projectile weapon leads the target."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        engine = ShipCombatEngine(ship)

        # Create moving target
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(10, 0)  # Moving right

        # Create projectile weapon component
        proj_ability = MagicMock()
        proj_ability.projectile_speed = 500  # 500 units/tick * 100 = 5 units/tick

        comp = MagicMock()
        comp.has_ability = lambda name: name == 'ProjectileWeaponAbility'
        comp.get_ability = lambda name: proj_ability if name == 'ProjectileWeaponAbility' else None

        aim_pos, aim_vec = engine.calculate_firing_solution(comp, target)

        # Aim position should be ahead of current position (leading target)
        assert aim_pos.x >= target.position.x


class TestFireWeapons:
    """Tests for the main fire_weapons method."""

    def test_fire_weapons_returns_empty_when_dead(self):
        """fire_weapons returns empty list when ship is dead."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = False
        ship.is_derelict = False

        engine = ShipCombatEngine(ship)
        attacks = engine.fire_weapons()

        assert attacks == []

    def test_fire_weapons_returns_empty_when_derelict(self):
        """fire_weapons returns empty list when ship is derelict."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = True

        engine = ShipCombatEngine(ship)
        attacks = engine.fire_weapons()

        assert attacks == []

    def test_fire_weapons_returns_empty_when_no_weapons(self):
        """fire_weapons returns empty list when ship has no weapons."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.iter_components = MagicMock(return_value=[])

        engine = ShipCombatEngine(ship)
        attacks = engine.fire_weapons()

        assert attacks == []

    def test_fire_weapons_creates_projectile_for_ready_weapon(self):
        """fire_weapons creates projectile when weapon is ready and target valid."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        # Create ship with projectile weapon
        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0
        ship.total_shots_fired = 0

        # Create weapon ability
        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 10
        weapon_ab.range = 1000
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500
        proj_ab.damage = 10
        proj_ab.range = 1000

        # Create weapon component
        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else proj_ab
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)
        weapon.facing_angle = 0
        weapon.shots_fired = 0

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        # Create target
        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)
        target.type = 'ship'

        ship.current_target = target
        ship.secondary_targets = []
        ship.max_targets = 1

        engine = ShipCombatEngine(ship)
        attacks = engine.fire_weapons()

        # Should have created 1 projectile
        assert len(attacks) == 1
        assert weapon_ab.fire.called


class TestDamageApplication:
    """Tests for take_damage method."""

    def test_take_damage_does_nothing_when_dead(self):
        """take_damage does nothing if ship is already dead."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = False
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(100)

        # Ship methods should NOT be called since ship is dead
        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()

    def test_take_damage_applies_emissive_armor_reduction(self):
        """take_damage reduces damage by emissive armor amount."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 5
        ship.crystalline_armor = 0
        ship.current_shields = 100  # Give shields so damage can be absorbed
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)

        # With 5 emissive armor, 10 damage becomes 5.
        # Shields absorb the remaining 5 damage: 100 - 5 = 95
        engine.take_damage(10)

        # Verify shields absorbed damage (emissive armor reduced it)
        assert ship.current_shields == 95
        # Verify damage was processed
        ship.recalculate_stats.assert_called_once()
        ship.update_derelict_status.assert_called_once()

    def test_take_damage_emissive_armor_blocks_all_when_damage_less_than_armor(self):
        """take_damage with emissive armor blocking all damage skips processing."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10  # Armor greater than damage
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)

        # 5 damage is completely absorbed by 10 emissive armor
        engine.take_damage(5)

        # No damage reached the ship, so these should NOT be called
        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()
        # Shields should remain unchanged
        assert ship.current_shields == 100

    def test_take_damage_applies_crystalline_armor(self):
        """take_damage applies crystalline armor absorption and shield recharge."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Crystalline armor absorbs min(10, 20) = 10 damage
        # Shields recharge by 10: 50 + 10 = 60
        # Remaining damage: 20 - 10 = 10
        # Shields absorb 10: 60 - 10 = 50
        # Final shields: 50
        assert ship.current_shields == 50
        ship.recalculate_stats.assert_called_once()
        ship.update_derelict_status.assert_called_once()

    def test_take_damage_shields_absorb_before_layers(self):
        """take_damage shields absorb damage before hull layers."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(50)

        # Shields should have absorbed 50 damage
        assert ship.current_shields == 50


class TestCombatEngineIntegration:
    """Integration tests with real Ship objects."""

    def test_engine_works_with_real_ship(self, armed_ship):
        """ShipCombatEngine works with actual Ship instance."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        engine = ShipCombatEngine(armed_ship)
        assert engine is not None
        assert engine._ship is armed_ship

    def test_engine_fire_weapons_no_target(self, armed_ship):
        """fire_weapons returns empty when no target set."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        armed_ship.current_target = None
        engine = ShipCombatEngine(armed_ship)
        attacks = engine.fire_weapons()

        assert attacks == []


# Fixtures
@pytest.fixture
def armed_ship():
    """Create an armed ship for testing."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="TestShip",
        x=0, y=0,
        team_id=0,
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
    )
