"""
Tests for DamageCalculator - extracted damage logic from ShipCombatEngine.

Follows TDD: Tests written first, then implementation.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.math import Vector2
from game.core.constants import LayerType


class TestDamageCalculatorCreation:
    """Tests for DamageCalculator instantiation."""

    def test_damage_calculator_can_be_created(self):
        """DamageCalculator can be instantiated."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()
        assert calculator is not None

    def test_damage_calculator_has_required_methods(self):
        """DamageCalculator has all required public methods."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()
        assert hasattr(calculator, 'apply_damage')


class TestEmissiveArmorReduction:
    """Tests for emissive armor damage reduction."""

    def test_emissive_armor_reduces_damage(self):
        """Emissive armor reduces incoming damage."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 5
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 10 damage - 5 emissive = 5 remaining
        # Shields absorb 5: 100 - 5 = 95
        calculator.apply_damage(ship, 10)

        assert ship.current_shields == 95

    def test_emissive_armor_blocks_all_when_greater(self):
        """Emissive armor blocks all damage when greater than damage."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 5 damage fully blocked by 10 emissive armor
        calculator.apply_damage(ship, 5)

        # No damage reached ship, methods not called
        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()
        assert ship.current_shields == 100


class TestCrystallineArmorAbsorption:
    """Tests for crystalline armor absorption and shield recharge."""

    def test_crystalline_armor_absorbs_and_recharges(self):
        """Crystalline armor absorbs damage and recharges shields."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 20 damage
        # Crystalline absorbs 10, recharges shields: 50 + 10 = 60
        # Remaining 10 damage absorbed by shields: 60 - 10 = 50
        calculator.apply_damage(ship, 20)

        assert ship.current_shields == 50

    def test_crystalline_armor_caps_shield_recharge(self):
        """Crystalline armor shield recharge is capped at max shields."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 20
        ship.current_shields = 95
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 30 damage
        # Crystalline absorbs 20, would recharge 20 but capped at max
        # Shields would go 95 + 20 = 115 -> capped at 100
        # Remaining 10 damage: 100 - 10 = 90
        calculator.apply_damage(ship, 30)

        assert ship.current_shields == 90


class TestShieldAbsorption:
    """Tests for shield damage absorption."""

    def test_shields_absorb_before_layers(self):
        """Shields absorb damage before hull layers."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 50)

        assert ship.current_shields == 50

    def test_shields_fully_depleted(self):
        """Shields can be fully depleted."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 30
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 50 damage, shields only 30
        calculator.apply_damage(ship, 50)

        assert ship.current_shields == 0


class TestLayerDamage:
    """Tests for hull layer damage application."""

    def test_damage_layers_by_radius(self):
        """Damage is applied to layers ordered by radius (outermost first)."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        # Create components with HP
        outer_comp = MagicMock()
        outer_comp.current_hp = 50
        outer_comp.max_hp = 50
        outer_comp.take_damage = MagicMock()

        inner_comp = MagicMock()
        inner_comp.current_hp = 50
        inner_comp.max_hp = 50
        inner_comp.take_damage = MagicMock()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 0  # No shields
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: {'radius_pct': 0.8, 'components': [outer_comp]},
            LayerType.INNER: {'radius_pct': 0.4, 'components': [inner_comp]},
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Apply 30 damage - should hit outer layer first
        calculator.apply_damage(ship, 30)

        # Outer component should have been damaged
        outer_comp.take_damage.assert_called()

    def test_damage_spreads_to_inner_layers(self):
        """Damage spreads to inner layers when outer is destroyed."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        # Outer component with low HP
        outer_comp = MagicMock()
        outer_comp.current_hp = 10
        outer_comp.max_hp = 50

        def outer_take_damage(amount):
            outer_comp.current_hp = max(0, outer_comp.current_hp - amount)

        outer_comp.take_damage = outer_take_damage

        # Inner component
        inner_comp = MagicMock()
        inner_comp.current_hp = 50
        inner_comp.max_hp = 50

        def inner_take_damage(amount):
            inner_comp.current_hp = max(0, inner_comp.current_hp - amount)

        inner_comp.take_damage = inner_take_damage

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: {'radius_pct': 0.8, 'components': [outer_comp]},
            LayerType.INNER: {'radius_pct': 0.4, 'components': [inner_comp]},
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Apply 30 damage
        # Outer has 10 HP, absorbs 10, leaving 20 damage
        # Inner absorbs remaining 20
        calculator.apply_damage(ship, 30)

        assert outer_comp.current_hp == 0
        assert inner_comp.current_hp == 30  # 50 - 20 = 30


class TestDeadShipHandling:
    """Tests for dead ship damage handling."""

    def test_damage_skipped_when_dead(self):
        """Damage is not applied to dead ships."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = False
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 100)

        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()


class TestDamageCallbacks:
    """Tests for post-damage callbacks."""

    def test_recalculate_stats_called_on_damage(self):
        """recalculate_stats is called when damage is applied."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 50)

        ship.recalculate_stats.assert_called_once()
        ship.update_derelict_status.assert_called_once()
