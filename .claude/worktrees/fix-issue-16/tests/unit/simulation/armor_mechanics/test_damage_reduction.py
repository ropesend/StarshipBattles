"""Tests for armor damage reduction mechanics.

Covers:
- Emissive Armor: Flat damage reduction (ablative)
- Shield Regenerating Armor: Damage absorption and shield regeneration
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
        ship.shield_regenerating_armor = 0
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
# Test: Shield Regenerating Armor Behavior
# =============================================================================


class TestShieldRegeneratingArmorBehavior:
    """Tests for Shield Regenerating Armor absorption and shield regen."""

    def test_crystalline_absorbs_and_regens_shields(self):
        """Crystalline armor should absorb overflow and regenerate shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 10
        ship.current_shields = 5  # Low shields so damage overflows to SRA
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Shields absorb 5: remaining=15, shields=0
        # SRA absorbs min(10,15)=10: remaining=5, shields+=10 -> shields=10
        # No hull layers
        assert ship.current_shields == 10
        assert ship.hp == 100

    def test_crystalline_full_absorption(self):
        """Crystalline armor absorbing more than overflow does not go negative."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 20  # High absorption
        ship.current_shields = 0  # No shields so damage reaches SRA
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(10)

        # Shields=0 (skip), emissive=0 (skip)
        # SRA absorbs min(20,10)=10: remaining=0, shields+=10 -> shields=10
        assert ship.current_shields == 10
        assert ship.hp == 100

    def test_crystalline_no_shields_no_regen(self):
        """Crystalline should not regen if max_shields is 0."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 10
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

    def test_sra_shield_cap(self):
        """Shield regen should not exceed max_shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 100  # High absorption
        ship.current_shields = 5  # Low shields so damage overflows to SRA
        ship.max_shields = 20  # Low max to test cap
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(50)

        # Shields absorb 5: remaining=45, shields=0
        # SRA absorbs min(100,45)=45: remaining=0, shields+=45 -> 45, capped at 20
        assert ship.current_shields == 20


# =============================================================================
# Test: Combined Armor Types
# =============================================================================


class TestCombinedArmor:
    """Tests for combined emissive and shield regenerating armor."""

    def test_shields_then_emissive_then_crystalline(self):
        """Shields absorb first, then emissive reduces, then SRA absorbs overflow."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10
        ship.shield_regenerating_armor = 10
        ship.current_shields = 5  # Low shields so damage overflows
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(25)

        # Shields absorb 5: remaining=20, shields=0
        # Emissive: 20 - 10 = 10
        # SRA: absorb min(10,10)=10, remaining=0, shields+=10 -> shields=10
        assert ship.current_shields == 10
        assert ship.hp == 100

    def test_both_armor_types_block_completely(self):
        """Both armor types together can fully block overflow damage."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10
        ship.shield_regenerating_armor = 10
        ship.current_shields = 0  # No shields so armor is tested
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(15)

        # Shields=0 (skip)
        # Emissive: 15 - 10 = 5 remaining
        # SRA: absorb min(10,5)=5, remaining=0, shields+=5 -> shields=5
        assert ship.current_shields == 5
        assert ship.hp == 100
