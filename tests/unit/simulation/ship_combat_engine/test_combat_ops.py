"""
Tests for ShipCombatEngine combat operations.

Tests fire_weapons, take_damage, and integration with real ships.
"""

import pytest
from unittest.mock import MagicMock

from game.core.math import Vector2
from game.core.constants import LayerType


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
        proj_ab.endurance = 2.0  # PROJ-45: Required for projectile validation

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
        """take_damage reduces overflow damage by emissive armor amount."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 5
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields so emissive is tested
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: MagicMock(
                radius_pct=0.8,
                components=[]
            )
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)

        # Pipeline: shields=0 (skip), emissive reduces 10-5=5, SRA=0 (skip)
        # 5 remaining passes through empty layer
        engine.take_damage(10)

        # Damage was processed (5 remaining < 10 original)
        # PROJ-253: damage_calculator now uses recalculate_stats_if_dirty()
        ship.recalculate_stats_if_dirty.assert_called_once()
        ship.update_derelict_status.assert_called_once()

    def test_take_damage_emissive_armor_blocks_all_when_damage_less_than_armor(self):
        """take_damage with emissive armor blocking all overflow skips processing."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10  # Armor greater than damage
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields so emissive is tested
        ship.max_shields = 0
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)

        # Pipeline: shields=0 (skip), emissive blocks all 5 (10>5), early return
        engine.take_damage(5)

        # No damage reached hull, so these should NOT be called
        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()
        # Shields should remain unchanged
        assert ship.current_shields == 0

    def test_take_damage_applies_shield_regenerating_armor(self):
        """take_damage applies shield regenerating armor absorption and shield recharge."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 10
        ship.current_shields = 5  # Low shields so damage overflows to SRA
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Shields absorb 5: remaining=15, shields=0
        # Emissive=0 (skip)
        # SRA absorbs min(10,15)=10: remaining=5, shields+=10 -> shields=10
        # No hull layers, remaining=5
        # Callbacks called (5 < 20)
        assert ship.current_shields == 10
        # PROJ-253: damage_calculator now uses recalculate_stats_if_dirty()
        ship.recalculate_stats_if_dirty.assert_called_once()
        ship.update_derelict_status.assert_called_once()

    def test_take_damage_shields_absorb_before_layers(self):
        """take_damage shields absorb damage before hull layers."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
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
