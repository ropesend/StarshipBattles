"""Tests for armor mechanics.

Covers:
- Crystalline Armor: Damage absorption and shield regeneration
- Emissive Armor: Flat damage reduction (ablative)
- Damage reduction calculations
- Armor degradation via component damage
- Edge cases: zero armor, combined armor types, extreme values
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pygame.math import Vector2


# =============================================================================
# Test: Emissive Armor Behavior
# =============================================================================


class TestEmissiveArmorBehavior:
    """Tests for Emissive Armor damage reduction."""

    @pytest.fixture
    def mock_ship_with_emissive(self):
        """Create a mock ship with emissive armor."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 15  # Ignores first 15 damage
        ship.crystalline_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.hp = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()
        return ship

    def test_emissive_blocks_low_damage(self, mock_ship_with_emissive):
        """Emissive armor should completely block damage below threshold."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        # Call take_damage with ship that has emissive_armor=15
        # Damage 10 < 15 should be fully absorbed
        initial_hp = mock_ship_with_emissive.hp

        # Create a real call context - the mixin reads from self
        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self, ship_mock):
                self.is_alive = ship_mock.is_alive
                self.emissive_armor = ship_mock.emissive_armor
                self.crystalline_armor = ship_mock.crystalline_armor
                self.current_shields = ship_mock.current_shields
                self.max_shields = ship_mock.max_shields
                self.hp = ship_mock.hp
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin(mock_ship_with_emissive)
        test_ship.take_damage(10)

        # HP should be unchanged
        assert test_ship.hp == initial_hp

    def test_emissive_reduces_high_damage(self, mock_ship_with_emissive):
        """Emissive armor should reduce damage above threshold."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self, ship_mock):
                self.is_alive = ship_mock.is_alive
                self.emissive_armor = ship_mock.emissive_armor
                self.crystalline_armor = ship_mock.crystalline_armor
                self.current_shields = ship_mock.current_shields
                self.max_shields = ship_mock.max_shields
                self.hp = ship_mock.hp
                self.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.hp -= damage
                return 0

        test_ship = MockShipWithMixin(mock_ship_with_emissive)
        test_ship.take_damage(25)

        # 25 - 15 = 10 damage should pass through
        assert test_ship.hp == 90

    def test_emissive_exact_threshold(self, mock_ship_with_emissive):
        """Damage exactly at threshold should be fully absorbed."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self, ship_mock):
                self.is_alive = True
                self.emissive_armor = 15
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin(mock_ship_with_emissive)
        test_ship.take_damage(15)

        # 15 - 15 = 0 damage
        assert test_ship.hp == 100

    def test_emissive_zero_value(self):
        """Zero emissive armor should not reduce damage."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0  # No armor
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.hp -= damage
                return 0

        test_ship = MockShipWithMixin()
        test_ship.take_damage(20)

        # Full 20 damage passes
        assert test_ship.hp == 80


# =============================================================================
# Test: Crystalline Armor Behavior
# =============================================================================


class TestCrystallineArmorBehavior:
    """Tests for Crystalline Armor absorption and shield regen."""

    def test_crystalline_absorbs_and_regens_shields(self):
        """Crystalline armor should absorb damage and regenerate shields."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 10
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(20)

        # Absorb 10, shields +10 = 60, then shields take remaining 10
        # Final shields = 50
        assert test_ship.current_shields == 50
        assert test_ship.hp == 100

    def test_crystalline_full_absorption(self):
        """Crystalline armor absorbing more than damage does not go negative."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 20  # High absorption
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(10)

        # Absorb 10 (min of 20, 10), shields +10 = 60, no remaining damage
        assert test_ship.current_shields == 60
        assert test_ship.hp == 100

    def test_crystalline_no_shields_no_regen(self):
        """Crystalline should not regen if max_shields is 0."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 10
                self.current_shields = 0
                self.max_shields = 0  # No shield system
                self.hp = 100
                self.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.hp -= damage
                return 0

        test_ship = MockShipWithMixin()
        test_ship.take_damage(20)

        # Absorb 10, but can't regen shields (max_shields=0)
        # Remaining 10 damage goes to HP
        assert test_ship.current_shields == 0
        assert test_ship.hp == 90

    def test_crystalline_shield_cap(self):
        """Shield regen should not exceed max_shields."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 100  # High absorption
                self.current_shields = 95
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(50)

        # Absorb 50, shields +50 would be 145, capped at 100
        # No remaining damage
        assert test_ship.current_shields == 100


# =============================================================================
# Test: Combined Armor Types
# =============================================================================


class TestCombinedArmor:
    """Tests for combined emissive and crystalline armor."""

    def test_emissive_before_crystalline(self):
        """Emissive should apply before crystalline (order in code)."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 10
                self.crystalline_armor = 10
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(25)

        # Emissive: 25 - 10 = 15
        # Crystalline: absorb 10, shields +10 = 60
        # Remaining: 5 to shields -> 55
        assert test_ship.current_shields == 55
        assert test_ship.hp == 100

    def test_both_armor_types_block_completely(self):
        """Both armor types together can fully block damage."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 15
                self.crystalline_armor = 10
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(15)

        # Emissive blocks 15, 0 remaining
        assert test_ship.current_shields == 50
        assert test_ship.hp == 100


# =============================================================================
# Test: Shield Interaction
# =============================================================================


class TestShieldInteraction:
    """Tests for armor/shield interaction."""

    def test_shields_absorb_after_armor(self):
        """Shields should absorb remaining damage after armor."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 0
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(30)

        # All 30 damage to shields -> 20
        assert test_ship.current_shields == 20
        assert test_ship.hp == 100

    def test_shields_overflow_to_hp(self):
        """Damage exceeding shields should flow to HP."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 0
                self.current_shields = 20
                self.max_shields = 100
                self.hp = 100
                self.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.hp -= damage
                return 0

        test_ship = MockShipWithMixin()
        test_ship.take_damage(50)

        # 20 to shields, 30 overflow to HP
        assert test_ship.current_shields == 0
        assert test_ship.hp == 70


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestArmorEdgeCases:
    """Edge cases for armor mechanics."""

    def test_zero_damage(self):
        """Zero damage should not affect ship."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 10
                self.crystalline_armor = 10
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(0)

        assert test_ship.current_shields == 50
        assert test_ship.hp == 100

    def test_dead_ship_ignores_damage(self):
        """Dead ship should not process damage."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = False  # Dead
                self.emissive_armor = 10
                self.crystalline_armor = 10
                self.current_shields = 50
                self.max_shields = 100
                self.hp = 100
                self.layers = {}

        test_ship = MockShipWithMixin()
        test_ship.take_damage(100)

        # Should return early, no changes
        assert test_ship.hp == 100

    def test_very_high_armor_values(self):
        """Extremely high armor should handle edge values."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 1000000
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.layers = {}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

        test_ship = MockShipWithMixin()
        test_ship.take_damage(999999)

        # All blocked
        assert test_ship.hp == 100

    def test_negative_armor_handling(self):
        """Negative armor values are ignored (ea > 0 check)."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = -10  # Invalid value - skipped by ea > 0 check
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.layers = {'ARMOR': {'radius_pct': 1.0, 'components': []}}
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.hp -= damage
                return 0

        test_ship = MockShipWithMixin()
        test_ship.take_damage(20)

        # Negative armor is skipped (ea > 0 check fails), full 20 damage passes
        assert test_ship.hp == 80


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
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.damage_order = []

                # Create mock layers with different radius_pct
                self.layers = {
                    'OUTER': {'radius_pct': 1.0, 'components': []},
                    'INNER': {'radius_pct': 0.5, 'components': []},
                    'CORE': {'radius_pct': 0.2, 'components': []},
                }
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.damage_order.append(layer_type)
                return damage  # Pass through all damage

        test_ship = MockShipWithMixin()
        test_ship.take_damage(30)

        # Should process in order: OUTER (1.0), INNER (0.5), CORE (0.2)
        assert test_ship.damage_order == ['OUTER', 'INNER', 'CORE']

    def test_damage_stopped_when_exhausted(self):
        """Layer damage should stop when damage is exhausted."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.emissive_armor = 0
                self.crystalline_armor = 0
                self.current_shields = 0
                self.max_shields = 0
                self.hp = 100
                self.damage_count = 0

                self.layers = {
                    'OUTER': {'radius_pct': 1.0, 'components': []},
                    'INNER': {'radius_pct': 0.5, 'components': []},
                }
                self.recalculate_stats = lambda: None
                self.update_derelict_status = lambda: None

            def _damage_layer(self, layer_type, damage):
                self.damage_count += 1
                return 0  # All damage absorbed

        test_ship = MockShipWithMixin()
        test_ship.take_damage(30)

        # Should only hit first layer since it absorbs all
        assert test_ship.damage_count == 1


# =============================================================================
# Test: Shield Regeneration with Combat Cooldowns
# =============================================================================


class TestShieldRegeneration:
    """Tests for shield regeneration during combat cooldowns."""

    def test_shield_regen_applies(self):
        """Shield regen should increase shields."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.current_shields = 50
                self.max_shields = 100
                self.shield_regen_rate = 10  # 10 per second
                self.shield_regen_cost = 0  # Free regen
                self.repair_rate = 0

        test_ship = MockShipWithMixin()
        test_ship.update_combat_cooldowns()

        # Regen = 10 / 100 = 0.1 per tick
        assert test_ship.current_shields == 50.1

    def test_shield_regen_capped(self):
        """Shield regen should not exceed max_shields."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.current_shields = 99.5
                self.max_shields = 100
                self.shield_regen_rate = 100  # High regen
                self.shield_regen_cost = 0
                self.repair_rate = 0

        test_ship = MockShipWithMixin()
        test_ship.update_combat_cooldowns()

        # Should cap at 100
        assert test_ship.current_shields == 100

    def test_shield_regen_requires_energy(self):
        """Shield regen should consume energy resource if cost > 0."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.current_shields = 50
                self.max_shields = 100
                self.shield_regen_rate = 10
                self.shield_regen_cost = 5  # 5 energy per second
                self.repair_rate = 0

                # Mock resource system
                self.resources = MagicMock()
                energy_res = MagicMock()
                energy_res.current_value = 10  # Enough energy
                energy_res.consume = MagicMock()
                self.resources.get_resource.return_value = energy_res
                self._energy_res = energy_res

        test_ship = MockShipWithMixin()
        test_ship.update_combat_cooldowns()

        # Energy should be consumed
        test_ship._energy_res.consume.assert_called_with(0.05)  # 5/100
        assert test_ship.current_shields == 50.1

    def test_no_regen_without_energy(self):
        """Shield regen should stop if no energy."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = True
                self.current_shields = 50
                self.max_shields = 100
                self.shield_regen_rate = 10
                self.shield_regen_cost = 5
                self.repair_rate = 0

                self.resources = MagicMock()
                energy_res = MagicMock()
                energy_res.current_value = 0  # No energy
                self.resources.get_resource.return_value = energy_res

        test_ship = MockShipWithMixin()
        test_ship.update_combat_cooldowns()

        # No regen
        assert test_ship.current_shields == 50

    def test_dead_ship_no_regen(self):
        """Dead ship should not regenerate shields."""
        from game.simulation.entities.ship_combat import ShipCombatMixin

        class MockShipWithMixin(ShipCombatMixin):
            def __init__(self):
                self.is_alive = False  # Dead
                self.current_shields = 50
                self.max_shields = 100
                self.shield_regen_rate = 10
                self.shield_regen_cost = 0

        test_ship = MockShipWithMixin()
        test_ship.update_combat_cooldowns()

        # No change
        assert test_ship.current_shields == 50
