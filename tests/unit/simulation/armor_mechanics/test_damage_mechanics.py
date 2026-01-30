"""Tests for damage mechanics beyond armor reduction.

Covers:
- Shield interaction with armor
- Edge cases: zero damage, dead ships, extreme values
- Emissive Armor ability class
- Layer damage distribution
- Shield regeneration with combat cooldowns
"""
import pytest
from unittest.mock import MagicMock


def create_mock_component(hp=100):
    """Create a mock component that can absorb damage."""
    comp = MagicMock()
    comp.current_hp = hp
    comp.take_damage = MagicMock(
        side_effect=lambda d: setattr(comp, 'current_hp', comp.current_hp - d)
    )
    return comp


# =============================================================================
# Test: Shield Interaction
# =============================================================================


class TestShieldInteraction:
    """Tests for armor/shield interaction."""

    def test_shields_absorb_after_armor(self):
        """Shields should absorb remaining damage after armor."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(30)

        # All 30 damage to shields -> 20
        assert ship.current_shields == 20
        assert ship.hp == 100

    def test_shields_overflow_to_hp(self):
        """Damage exceeding shields should flow to HP."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 20
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Create mock component to absorb damage
        mock_comp = create_mock_component()
        ship.layers['ARMOR']['components'].append(mock_comp)

        engine = ShipCombatEngine(ship)
        engine.take_damage(50)

        # 20 to shields, 30 overflow to component
        assert ship.current_shields == 0
        assert mock_comp.current_hp == 70


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestArmorEdgeCases:
    """Edge cases for armor mechanics."""

    def test_zero_damage(self):
        """Zero damage should not affect ship."""
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
        engine.take_damage(0)

        assert ship.current_shields == 50
        assert ship.hp == 100

    def test_dead_ship_ignores_damage(self):
        """Dead ship should not process damage."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = False  # Dead
        ship.emissive_armor = 10
        ship.crystalline_armor = 10
        ship.current_shields = 50
        ship.max_shields = 100
        ship.hp = 100
        ship.layers = {}

        engine = ShipCombatEngine(ship)
        engine.take_damage(100)

        # Should return early, no changes
        assert ship.hp == 100

    def test_very_high_armor_values(self):
        """Extremely high armor should handle edge values."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 1000000
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(999999)

        # All blocked
        assert ship.hp == 100

    def test_negative_armor_handling(self):
        """Negative armor values are ignored (ea > 0 check)."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = -10  # Invalid value - skipped by ea > 0 check
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Create mock component to absorb damage
        mock_comp = create_mock_component()
        ship.layers['ARMOR']['components'].append(mock_comp)

        engine = ShipCombatEngine(ship)
        engine.take_damage(20)

        # Negative armor is skipped (ea > 0 check fails), full 20 damage passes
        assert mock_comp.current_hp == 80


# =============================================================================
# Test: Emissive Armor Ability
# =============================================================================


class TestEmissiveArmorAbility:
    """Tests for EmissiveArmor ability class."""

    def test_ability_initialization(self):
        """EmissiveArmor ability should initialize with value."""
        from game.simulation.components.abilities.defense import EmissiveArmor

        component = MagicMock()
        data = {'value': 15}

        ability = EmissiveArmor(component, data)

        assert ability.amount == 15
        assert ability._base_amount == 15

    def test_ability_simple_value(self):
        """EmissiveArmor should accept simple numeric value."""
        from game.simulation.components.abilities.defense import EmissiveArmor

        component = MagicMock()
        data = 20  # Simple int value

        ability = EmissiveArmor(component, data)

        assert ability.amount == 20

    def test_ability_ui_rows(self):
        """EmissiveArmor should provide UI rows."""
        from game.simulation.components.abilities.defense import EmissiveArmor

        component = MagicMock()
        ability = EmissiveArmor(component, 25)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert rows[0]['label'] == 'Dmg Ignore'
        assert rows[0]['value'] == '25'

    def test_ability_primary_value(self):
        """EmissiveArmor primary value should be amount."""
        from game.simulation.components.abilities.defense import EmissiveArmor

        component = MagicMock()
        ability = EmissiveArmor(component, 30)

        assert ability.get_primary_value() == 30.0


# =============================================================================
# Test: Layer Damage Distribution
# =============================================================================


class TestLayerDamageDistribution:
    """Tests for damage distribution to layers after armor."""

    def test_damage_to_outer_layer_first(self):
        """Damage should hit outer layers (higher radius_pct) first."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        damage_order = []

        # Create mock components for each layer that track damage order
        def create_layer_comp(layer_name, hp=100):
            comp = MagicMock()
            comp.current_hp = hp
            def take_damage(d):
                damage_order.append(layer_name)
                comp.current_hp = max(0, comp.current_hp - d)
            comp.take_damage = take_damage
            return comp

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {
            'OUTER': {'radius_pct': 1.0, 'components': [create_layer_comp('OUTER', 10)]},
            'INNER': {'radius_pct': 0.5, 'components': [create_layer_comp('INNER', 10)]},
            'CORE': {'radius_pct': 0.2, 'components': [create_layer_comp('CORE', 10)]},
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(30)

        # Should process in order: OUTER (1.0), INNER (0.5), CORE (0.2)
        assert damage_order == ['OUTER', 'INNER', 'CORE']

    def test_damage_stopped_when_exhausted(self):
        """Layer damage should stop when damage is exhausted."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        damage_count = [0]

        # Create a component that absorbs all damage
        comp = MagicMock()
        comp.current_hp = 100
        def take_damage(d):
            damage_count[0] += 1
            comp.current_hp = max(0, comp.current_hp - d)
        comp.take_damage = take_damage

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {
            'OUTER': {'radius_pct': 1.0, 'components': [comp]},
            'INNER': {'radius_pct': 0.5, 'components': []},
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        engine = ShipCombatEngine(ship)
        engine.take_damage(30)

        # Should only hit first layer (OUTER) since it absorbs all
        assert damage_count[0] == 1


# =============================================================================
# Test: Shield Regeneration with Combat Cooldowns
# =============================================================================


class TestShieldRegeneration:
    """Tests for shield regeneration during combat cooldowns."""

    def test_shield_regen_applies(self):
        """Shield regen should increase shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 10  # 10 per second
        ship.shield_regen_cost = 0  # Free regen
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Regen = 10 / 100 = 0.1 per tick
        assert ship.current_shields == 50.1

    def test_shield_regen_capped(self):
        """Shield regen should not exceed max_shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 99.5
        ship.max_shields = 100
        ship.shield_regen_rate = 100  # High regen
        ship.shield_regen_cost = 0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should cap at 100
        assert ship.current_shields == 100

    def test_shield_regen_requires_energy(self):
        """Shield regen should consume energy resource if cost > 0."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 10
        ship.shield_regen_cost = 5  # 5 energy per second
        ship.repair_rate = 0

        # Mock resource system
        energy_res = MagicMock()
        energy_res.current_value = 10  # Enough energy
        energy_res.consume = MagicMock()
        ship.resources = MagicMock()
        ship.resources.get_resource.return_value = energy_res

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Energy should be consumed
        energy_res.consume.assert_called_with(0.05)  # 5/100
        assert ship.current_shields == 50.1

    def test_no_regen_without_energy(self):
        """Shield regen should stop if no energy."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 10
        ship.shield_regen_cost = 5
        ship.repair_rate = 0

        energy_res = MagicMock()
        energy_res.current_value = 0  # No energy
        ship.resources = MagicMock()
        ship.resources.get_resource.return_value = energy_res

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # No regen
        assert ship.current_shields == 50

    def test_dead_ship_no_regen(self):
        """Dead ship should not regenerate shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = False  # Dead
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 10
        ship.shield_regen_cost = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # No change
        assert ship.current_shields == 50
