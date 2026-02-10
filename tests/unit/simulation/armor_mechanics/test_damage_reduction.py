"""Tests for armor damage reduction mechanics.

Covers:
- Emissive Armor: Flat damage reduction (ablative)
- Crystalline Armor: Damage absorption and shield regeneration
- Combined armor types

Note: These tests use ShipCombatEngine directly since Phase 1 converted
ShipCombatMixin to a thin facade. Testing combat logic should go through
the engine for accurate behavior testing.
"""
import pytest
from unittest.mock import MagicMock
from game.simulation.entities.layer_data import LayerData


def create_mock_component(hp=100):
    """Create a mock component that can absorb damage."""
    comp = MagicMock()
    comp.current_hp = hp
    comp.take_damage = MagicMock(
        side_effect=lambda d: setattr(comp, 'current_hp', comp.current_hp - d)
    )
    return comp


# =============================================================================
# Test: Emissive Armor Behavior
# =============================================================================


class TestEmissiveArmorBehavior:
    """Tests for Emissive Armor damage reduction."""

    def test_emissive_blocks_low_damage(self, mock_ship_with_emissive):
        """Emissive armor should completely block damage below threshold."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        # Call take_damage with ship that has emissive_armor=15
        # Damage 10 < 15 should be fully absorbed
        initial_hp = mock_ship_with_emissive.hp

        engine = ShipCombatEngine(mock_ship_with_emissive)
        engine.take_damage(10)

        # HP should be unchanged
        assert mock_ship_with_emissive.hp == initial_hp

    def test_emissive_reduces_high_damage(self, mock_ship_with_emissive):
        """Emissive armor should reduce damage above threshold."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        # Set up layers with components that can take damage
        mock_ship_with_emissive.layers = {'ARMOR': LayerData(radius_pct=1.0)}

        # Create a mock component that can absorb damage
        mock_comp = create_mock_component()
        mock_ship_with_emissive.layers['ARMOR'].components.append(mock_comp)

        engine = ShipCombatEngine(mock_ship_with_emissive)
        engine.take_damage(25)

        # 25 - 15 = 10 damage should pass through to components
        assert mock_comp.current_hp == 90

    def test_emissive_exact_threshold(self, mock_ship_with_emissive):
        """Damage exactly at threshold should be fully absorbed."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        mock_ship_with_emissive.emissive_armor = 15
        mock_ship_with_emissive.hp = 100

        engine = ShipCombatEngine(mock_ship_with_emissive)
        engine.take_damage(15)

        # 15 - 15 = 0 damage, HP unchanged
        assert mock_ship_with_emissive.hp == 100

    def test_emissive_zero_value(self):
        """Zero emissive armor should not reduce damage."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0  # No armor
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {'ARMOR': LayerData(radius_pct=1.0)}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Create mock component to absorb damage
        mock_comp = create_mock_component()
        ship.layers['ARMOR'].components.append(mock_comp)

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Full 20 damage passes to component
        assert mock_comp.current_hp == 80


# =============================================================================
# Test: Crystalline Armor Behavior
# =============================================================================


class TestCrystallineArmorBehavior:
    """Tests for Crystalline Armor absorption and shield regen."""

    def test_crystalline_absorbs_and_regens_shields(self):
        """Crystalline armor should absorb damage and regenerate shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Absorb 10, shields +10 = 60, then shields take remaining 10
        # Final shields = 50
        assert ship.current_shields == 50
        assert ship.hp == 100

    def test_crystalline_full_absorption(self):
        """Crystalline armor absorbing more than damage does not go negative."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 20  # High absorption
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(10)

        # Absorb 10 (min of 20, 10), shields +10 = 60, no remaining damage
        assert ship.current_shields == 60
        assert ship.hp == 100

    def test_crystalline_no_shields_no_regen(self):
        """Crystalline should not regen if max_shields is 0."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.current_shields = 0
        ship.max_shields = 0  # No shield system
        ship.hp = 100
        ship.layers = {'ARMOR': LayerData(radius_pct=1.0)}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Create mock component to absorb damage
        mock_comp = create_mock_component()
        ship.layers['ARMOR'].components.append(mock_comp)

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Absorb 10, but can't regen shields (max_shields=0)
        # Remaining 10 damage goes to component
        assert ship.current_shields == 0
        assert mock_comp.current_hp == 90

    def test_crystalline_shield_cap(self):
        """Shield regen should not exceed max_shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 100  # High absorption
        ship.current_shields = 95
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(50)

        # Absorb 50, shields +50 would be 145, capped at 100
        # No remaining damage
        assert ship.current_shields == 100


# =============================================================================
# Test: Combined Armor Types
# =============================================================================


class TestCombinedArmor:
    """Tests for combined emissive and crystalline armor."""

    def test_emissive_before_crystalline(self):
        """Emissive should apply before crystalline (order in code)."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(25)

        # Emissive: 25 - 10 = 15
        # Crystalline: absorb 10, shields +10 = 60
        # Remaining: 5 to shields -> 55
        assert ship.current_shields == 55
        assert ship.hp == 100

    def test_both_armor_types_block_completely(self):
        """Both armor types together can fully block damage."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 15
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(15)

        # Emissive blocks 15, 0 remaining
        assert ship.current_shields == 50
        assert ship.hp == 100
