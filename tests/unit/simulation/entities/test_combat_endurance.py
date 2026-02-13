"""Unit tests for combat_endurance.py module.

PROJ-118 Phase 2: Tests for CombatEndurance calculations.

Tests focus on behavior verification with mocked dependencies:
- Endurance calculation methods
- Resource consumption tracking
- Boundary conditions (zero, max values)
- Edge cases
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.simulation.entities.combat_endurance import (
    calculate_combat_endurance,
    _calculate_cached_summary,
)
from game.core.constants import ResourceType


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_resource():
    """Create a mock resource with configurable properties."""
    def _create(max_value=1000, regen_rate=0):
        resource = MagicMock()
        resource.max_value = max_value
        resource.regen_rate = regen_rate
        return resource
    return _create


@pytest.fixture
def mock_resource_registry(mock_resource):
    """Create a mock resource registry with configurable resources."""
    def _create(fuel_max=1000, ammo_max=500, energy_max=2000, energy_regen=50):
        registry = MagicMock()

        # get_max_value returns max for each resource type
        def get_max_value(resource_type):
            if resource_type == ResourceType.FUEL:
                return fuel_max
            elif resource_type == ResourceType.AMMO:
                return ammo_max
            elif resource_type == ResourceType.ENERGY:
                return energy_max
            return 0

        registry.get_max_value = MagicMock(side_effect=get_max_value)

        # get_resource returns a resource object with regen_rate
        def get_resource(resource_type):
            if resource_type == ResourceType.ENERGY:
                return mock_resource(energy_max, energy_regen)
            return None

        registry.get_resource = MagicMock(side_effect=get_resource)

        return registry
    return _create


@pytest.fixture
def mock_ship(mock_resource_registry):
    """Create a mock ship with configurable resources."""
    def _create(fuel_max=1000, ammo_max=500, energy_max=2000, energy_regen=50):
        ship = MagicMock()
        ship.resources = mock_resource_registry(fuel_max, ammo_max, energy_max, energy_regen)

        # Initialize attributes that will be set by calculate_combat_endurance
        ship.fuel_consumption = 0.0
        ship.ammo_consumption = 0.0
        ship.energy_consumption = 0.0
        ship.potential_fuel_consumption = 0.0
        ship.potential_ammo_consumption = 0.0
        ship.potential_energy_consumption = 0.0
        ship.fuel_endurance = 0.0
        ship.ammo_endurance = 0.0
        ship.energy_endurance = 0.0
        ship.energy_net = 0.0
        ship.energy_recharge = 0.0
        ship._cached_summary = {}

        # For _calculate_cached_summary
        ship.mass = 1000
        ship.max_hp = 500
        ship.max_speed = 100
        ship.turn_speed = 10
        ship.max_shields = 200
        ship.max_weapon_range = 1000
        ship.get_all_components = MagicMock(return_value=[])

        return ship
    return _create


@pytest.fixture
def mock_component():
    """Create a mock component with configurable abilities."""
    def _create(is_active=True, abilities=None):
        component = MagicMock()
        component.is_active = is_active
        component.ability_instances = abilities or []
        return component
    return _create


@pytest.fixture
def mock_resource_consumption_ability():
    """Create a mock ResourceConsumption ability."""
    def _create(resource_name, amount, trigger='constant'):
        ability = MagicMock()
        ability.__class__.__name__ = 'ResourceConsumption'
        ability.resource_type = resource_name
        ability.amount = amount
        ability.trigger = trigger
        return ability
    return _create


@pytest.fixture
def mock_weapon_ability():
    """Create a mock WeaponAbility."""
    def _create(reload_time=1.0, damage=100):
        ability = MagicMock()
        ability.__class__.__name__ = 'WeaponAbility'
        ability.reload_time = reload_time
        ability.damage = damage
        return ability
    return _create


# ============================================================================
# Test: Basic Fuel Endurance
# ============================================================================

class TestFuelEnduranceCalculation:
    """Tests for fuel endurance calculations."""

    def test_fuel_endurance_basic(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Fuel endurance = max_fuel / fuel_consumption."""
        ship = mock_ship(fuel_max=1000)

        # Component with constant fuel consumption of 10/s
        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 10.0
        assert ship.fuel_endurance == 100.0  # 1000 / 10

    def test_fuel_endurance_multiple_consumers(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Fuel endurance sums consumption from all active components."""
        ship = mock_ship(fuel_max=1000)

        # Two engines consuming fuel
        fuel1 = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        fuel2 = mock_resource_consumption_ability(ResourceType.FUEL, 15.0, 'constant')

        comp1 = mock_component(is_active=True, abilities=[fuel1])
        comp2 = mock_component(is_active=True, abilities=[fuel2])

        calculate_combat_endurance(ship, [comp1, comp2])

        assert ship.fuel_consumption == 25.0
        assert ship.fuel_endurance == 40.0  # 1000 / 25

    def test_fuel_endurance_zero_consumption(self, mock_ship, mock_component):
        """Zero fuel consumption results in infinite endurance."""
        ship = mock_ship(fuel_max=1000)
        component = mock_component(is_active=True, abilities=[])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 0.0
        assert ship.fuel_endurance == float('inf')

    def test_fuel_endurance_inactive_component(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Inactive components contribute to potential but not actual consumption."""
        ship = mock_ship(fuel_max=1000)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        component = mock_component(is_active=False, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        # Actual consumption is 0, potential is 10
        assert ship.fuel_consumption == 0.0
        assert ship.potential_fuel_consumption == 10.0
        # Endurance uses potential when actual is 0
        assert ship.fuel_endurance == 100.0  # 1000 / 10 (potential)


# ============================================================================
# Test: Ammo Endurance
# ============================================================================

class TestAmmoEnduranceCalculation:
    """Tests for ammo endurance calculations."""

    def test_ammo_endurance_constant_consumption(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Ammo endurance with constant consumption trigger."""
        ship = mock_ship(ammo_max=500)

        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 5.0, 'constant')
        component = mock_component(is_active=True, abilities=[ammo_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.ammo_consumption == 5.0
        assert ship.ammo_endurance == 100.0  # 500 / 5

    def test_ammo_endurance_activation_trigger_with_weapon(
        self, mock_ship, mock_component, mock_resource_consumption_ability, mock_weapon_ability
    ):
        """Ammo activation consumption converts to rate using weapon reload time."""
        ship = mock_ship(ammo_max=500)

        # Weapon with 2s reload time
        weapon = mock_weapon_ability(reload_time=2.0)
        # Activation cost of 10 ammo per shot = 5 ammo/s
        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'activation')

        component = mock_component(is_active=True, abilities=[weapon, ammo_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.ammo_consumption == 5.0  # 10 / 2 = 5 per second
        assert ship.ammo_endurance == 100.0  # 500 / 5

    def test_ammo_endurance_zero_consumption(self, mock_ship, mock_component):
        """Zero ammo consumption results in infinite endurance."""
        ship = mock_ship(ammo_max=500)
        component = mock_component(is_active=True, abilities=[])

        calculate_combat_endurance(ship, [component])

        assert ship.ammo_consumption == 0.0
        assert ship.ammo_endurance == float('inf')


# ============================================================================
# Test: Energy Endurance
# ============================================================================

class TestEnergyEnduranceCalculation:
    """Tests for energy endurance calculations."""

    def test_energy_endurance_drain(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Energy endurance when consumption exceeds generation (draining)."""
        # 50 regen, 100 consumption = -50 net = drain 1000 in 20s
        ship = mock_ship(energy_max=1000, energy_regen=50)

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 100.0, 'constant')
        component = mock_component(is_active=True, abilities=[energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_consumption == 100.0
        assert ship.energy_net == -50.0  # 50 gen - 100 consumption
        assert ship.energy_endurance == 20.0  # 1000 / 50 drain rate

    def test_energy_endurance_sustainable(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Energy endurance is infinite when generation meets/exceeds consumption."""
        # 50 regen, 25 consumption = +25 net = sustainable
        ship = mock_ship(energy_max=1000, energy_regen=50)

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 25.0, 'constant')
        component = mock_component(is_active=True, abilities=[energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_consumption == 25.0
        assert ship.energy_net == 25.0  # 50 gen - 25 consumption
        assert ship.energy_endurance == float('inf')

    def test_energy_endurance_balanced(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Energy endurance is infinite when generation equals consumption."""
        # 50 regen, 50 consumption = 0 net = sustainable (no drain)
        ship = mock_ship(energy_max=1000, energy_regen=50)

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 50.0, 'constant')
        component = mock_component(is_active=True, abilities=[energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_consumption == 50.0
        assert ship.energy_net == 0.0
        assert ship.energy_endurance == float('inf')

    def test_energy_recharge_time(self, mock_ship, mock_component):
        """Energy recharge time = max_energy / gen_rate."""
        ship = mock_ship(energy_max=2000, energy_regen=100)
        component = mock_component(is_active=True, abilities=[])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_recharge == 20.0  # 2000 / 100

    def test_energy_recharge_zero_generation(self, mock_ship, mock_component):
        """Energy recharge is infinite when no generation."""
        ship = mock_ship(energy_max=2000, energy_regen=0)
        component = mock_component(is_active=True, abilities=[])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_recharge == float('inf')


# ============================================================================
# Test: Activation Trigger Handling
# ============================================================================

class TestActivationTriggerHandling:
    """Tests for activation trigger to rate conversion."""

    def test_activation_energy_converts_to_rate(
        self, mock_ship, mock_component, mock_resource_consumption_ability, mock_weapon_ability
    ):
        """Activation-triggered energy consumption converts to rate."""
        ship = mock_ship(energy_max=1000, energy_regen=0)

        # Weapon with 0.5s reload = 2 shots per second
        weapon = mock_weapon_ability(reload_time=0.5)
        # 20 energy per shot = 40 energy/s
        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 20.0, 'activation')

        component = mock_component(is_active=True, abilities=[weapon, energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_consumption == 40.0  # 20 / 0.5 = 40 per second

    def test_activation_uses_default_reload_without_weapon(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Activation without weapon ability uses default reload time of 1.0."""
        ship = mock_ship(ammo_max=500)

        # No weapon ability, activation cost of 10
        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'activation')
        component = mock_component(is_active=True, abilities=[ammo_ability])

        calculate_combat_endurance(ship, [component])

        # Default reload time is 1.0, so rate = 10 / 1 = 10
        assert ship.ammo_consumption == 10.0

    def test_activation_zero_reload_time_skipped(
        self, mock_ship, mock_component, mock_resource_consumption_ability, mock_weapon_ability
    ):
        """Zero reload time should not cause division by zero."""
        ship = mock_ship(ammo_max=500)

        # Weapon with 0 reload time (edge case)
        weapon = mock_weapon_ability(reload_time=0)
        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'activation')

        component = mock_component(is_active=True, abilities=[weapon, ammo_ability])

        calculate_combat_endurance(ship, [component])

        # Zero reload time prevents rate calculation
        assert ship.ammo_consumption == 0.0


# ============================================================================
# Test: Potential vs Actual Consumption
# ============================================================================

class TestPotentialConsumption:
    """Tests for potential consumption tracking."""

    def test_potential_tracks_inactive_components(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Potential consumption includes inactive components."""
        ship = mock_ship(fuel_max=1000)

        fuel1 = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        fuel2 = mock_resource_consumption_ability(ResourceType.FUEL, 15.0, 'constant')

        active_comp = mock_component(is_active=True, abilities=[fuel1])
        inactive_comp = mock_component(is_active=False, abilities=[fuel2])

        calculate_combat_endurance(ship, [active_comp, inactive_comp])

        assert ship.fuel_consumption == 10.0  # Only active
        assert ship.potential_fuel_consumption == 25.0  # All components

    def test_all_resource_potentials_tracked(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """All resource types track potential consumption."""
        ship = mock_ship()

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 5.0, 'constant')
        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 3.0, 'constant')
        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 10.0, 'constant')

        component = mock_component(is_active=False, abilities=[fuel_ability, ammo_ability, energy_ability])

        calculate_combat_endurance(ship, [component])

        # Actual should be 0 (inactive)
        assert ship.fuel_consumption == 0.0
        assert ship.ammo_consumption == 0.0
        assert ship.energy_consumption == 0.0

        # Potential should have values
        assert ship.potential_fuel_consumption == 5.0
        assert ship.potential_ammo_consumption == 3.0
        assert ship.potential_energy_consumption == 10.0


# ============================================================================
# Test: Cached Summary Calculation
# ============================================================================

class TestCachedSummaryCalculation:
    """Tests for _calculate_cached_summary."""

    def test_cached_summary_basic_stats(self, mock_ship):
        """Cached summary includes basic ship stats."""
        ship = mock_ship()
        ship.mass = 1500
        ship.max_hp = 750
        ship.max_speed = 120
        ship.turn_speed = 15
        ship.max_shields = 300
        ship.max_weapon_range = 1200

        _calculate_cached_summary(ship)

        assert ship._cached_summary['mass'] == 1500
        assert ship._cached_summary['max_hp'] == 750
        assert ship._cached_summary['speed'] == 120
        assert ship._cached_summary['turn'] == 15
        assert ship._cached_summary['shield'] == 300
        assert ship._cached_summary['range'] == 1200

    def test_cached_summary_dps_calculation(self, mock_ship, mock_weapon_ability):
        """Cached summary calculates DPS from weapon abilities."""
        ship = mock_ship()

        # Weapon: 100 damage, 2s reload = 50 DPS
        weapon = mock_weapon_ability(reload_time=2.0, damage=100)

        mock_component = MagicMock()
        mock_component.get_abilities = MagicMock(return_value=[weapon])

        ship.get_all_components = MagicMock(return_value=[mock_component])

        _calculate_cached_summary(ship)

        assert ship._cached_summary['dps'] == 50.0  # 100 / 2

    def test_cached_summary_multiple_weapons_dps(self, mock_ship, mock_weapon_ability):
        """DPS sums from multiple weapons."""
        ship = mock_ship()

        # Two weapons: 100/2 = 50 DPS + 60/1.5 = 40 DPS = 90 total
        weapon1 = mock_weapon_ability(reload_time=2.0, damage=100)
        weapon2 = mock_weapon_ability(reload_time=1.5, damage=60)

        mock_comp1 = MagicMock()
        mock_comp1.get_abilities = MagicMock(return_value=[weapon1])

        mock_comp2 = MagicMock()
        mock_comp2.get_abilities = MagicMock(return_value=[weapon2])

        ship.get_all_components = MagicMock(return_value=[mock_comp1, mock_comp2])

        _calculate_cached_summary(ship)

        assert ship._cached_summary['dps'] == 90.0

    def test_cached_summary_no_weapons(self, mock_ship):
        """DPS is 0 when no weapons."""
        ship = mock_ship()

        mock_component = MagicMock()
        mock_component.get_abilities = MagicMock(return_value=[])

        ship.get_all_components = MagicMock(return_value=[mock_component])

        _calculate_cached_summary(ship)

        assert ship._cached_summary['dps'] == 0

    def test_cached_summary_zero_reload_weapon(self, mock_ship, mock_weapon_ability):
        """Zero reload time weapon does not contribute to DPS (avoids division by zero)."""
        ship = mock_ship()

        # Weapon with 0 reload time
        weapon = mock_weapon_ability(reload_time=0, damage=100)

        mock_component = MagicMock()
        mock_component.get_abilities = MagicMock(return_value=[weapon])

        ship.get_all_components = MagicMock(return_value=[mock_component])

        _calculate_cached_summary(ship)

        # Should not crash, DPS stays 0
        assert ship._cached_summary['dps'] == 0


# ============================================================================
# Test: Boundary Conditions
# ============================================================================

class TestBoundaryConditions:
    """Tests for boundary conditions and edge cases."""

    def test_empty_component_pool(self, mock_ship):
        """Empty component pool results in zero consumption and infinite endurance."""
        ship = mock_ship()

        calculate_combat_endurance(ship, [])

        assert ship.fuel_consumption == 0.0
        assert ship.ammo_consumption == 0.0
        assert ship.energy_consumption == 0.0
        assert ship.fuel_endurance == float('inf')
        assert ship.ammo_endurance == float('inf')
        assert ship.energy_endurance == float('inf')

    def test_component_without_ability_instances(self, mock_ship):
        """Component without ability_instances attribute is handled gracefully."""
        ship = mock_ship()

        component = MagicMock(spec=['is_active'])  # No ability_instances
        component.is_active = True

        # Should not crash
        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 0.0

    def test_very_small_consumption_rate(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Very small consumption rates produce very large endurance."""
        ship = mock_ship(fuel_max=1000)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 0.001, 'constant')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 0.001
        assert ship.fuel_endurance == 1000000.0  # 1000 / 0.001

    def test_very_high_consumption_rate(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Very high consumption rates produce very small endurance."""
        ship = mock_ship(fuel_max=1000)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10000.0, 'constant')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 10000.0
        assert ship.fuel_endurance == 0.1  # 1000 / 10000

    def test_zero_max_resource(self, mock_ship, mock_component, mock_resource_consumption_ability):
        """Zero max resource capacity results in zero endurance."""
        ship = mock_ship(fuel_max=0)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_endurance == 0.0  # 0 / 10


# ============================================================================
# Test: Weapon Ability Type Detection
# ============================================================================

class TestWeaponAbilityTypeDetection:
    """Tests for detecting different weapon ability types for reload time."""

    def test_projectile_weapon_ability_detected(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """ProjectileWeaponAbility reload time is used for rate conversion."""
        ship = mock_ship(ammo_max=500)

        weapon = MagicMock()
        weapon.__class__.__name__ = 'ProjectileWeaponAbility'
        weapon.reload_time = 2.0

        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'activation')
        component = mock_component(is_active=True, abilities=[weapon, ammo_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.ammo_consumption == 5.0  # 10 / 2

    def test_beam_weapon_ability_detected(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """BeamWeaponAbility reload time is used for rate conversion."""
        ship = mock_ship(energy_max=1000, energy_regen=0)

        weapon = MagicMock()
        weapon.__class__.__name__ = 'BeamWeaponAbility'
        weapon.reload_time = 0.5

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 25.0, 'activation')
        component = mock_component(is_active=True, abilities=[weapon, energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_consumption == 50.0  # 25 / 0.5

    def test_seeker_weapon_ability_detected(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """SeekerWeaponAbility reload time is used for rate conversion."""
        ship = mock_ship(ammo_max=500)

        weapon = MagicMock()
        weapon.__class__.__name__ = 'SeekerWeaponAbility'
        weapon.reload_time = 4.0

        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 20.0, 'activation')
        component = mock_component(is_active=True, abilities=[weapon, ammo_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.ammo_consumption == 5.0  # 20 / 4


# ============================================================================
# Test: Mixed Component Scenarios
# ============================================================================

class TestMixedComponentScenarios:
    """Tests for realistic mixed component scenarios."""

    def test_mixed_active_inactive_components(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Mixed active/inactive components track both actual and potential."""
        ship = mock_ship(fuel_max=1000, ammo_max=500, energy_max=2000, energy_regen=100)

        # Active engine with fuel consumption
        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 20.0, 'constant')
        engine = mock_component(is_active=True, abilities=[fuel_ability])

        # Active weapon with energy consumption
        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 50.0, 'constant')
        weapon = mock_component(is_active=True, abilities=[energy_ability])

        # Inactive secondary weapon with ammo consumption
        ammo_ability = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'constant')
        inactive_weapon = mock_component(is_active=False, abilities=[ammo_ability])

        calculate_combat_endurance(ship, [engine, weapon, inactive_weapon])

        # Actual values (only active)
        assert ship.fuel_consumption == 20.0
        assert ship.energy_consumption == 50.0
        assert ship.ammo_consumption == 0.0

        # Potential values (all)
        assert ship.potential_fuel_consumption == 20.0
        assert ship.potential_energy_consumption == 50.0
        assert ship.potential_ammo_consumption == 10.0

        # Endurance calculations
        assert ship.fuel_endurance == 50.0  # 1000 / 20
        assert ship.energy_endurance == float('inf')  # 100 - 50 = +50 net
        assert ship.ammo_endurance == float('inf')  # 0 consumption

    def test_component_with_multiple_resource_consumptions(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Single component can have multiple resource consumptions."""
        ship = mock_ship(fuel_max=1000, energy_max=1000, energy_regen=0)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 20.0, 'constant')

        component = mock_component(is_active=True, abilities=[fuel_ability, energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 10.0
        assert ship.energy_consumption == 20.0
        assert ship.fuel_endurance == 100.0  # 1000 / 10
        assert ship.energy_endurance == 50.0  # 1000 / 20 drain


# ============================================================================
# Test: Additional Edge Cases (PROJ-118 Phase 2)
# ============================================================================

class TestAdditionalCombatEnduranceEdgeCases:
    """Additional edge case tests for combat_endurance module."""

    def test_resource_consumption_with_unknown_trigger(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Unknown trigger type does not contribute to consumption."""
        ship = mock_ship(fuel_max=1000)

        # Unknown trigger type (not 'constant' or 'activation')
        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'unknown_trigger')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        # Should not add to consumption since trigger is unknown
        assert ship.fuel_consumption == 0.0

    def test_non_resource_consumption_ability_ignored(self, mock_ship, mock_component):
        """Non-ResourceConsumption abilities are ignored in consumption calc."""
        ship = mock_ship(fuel_max=1000)

        # Create a non-ResourceConsumption ability
        other_ability = MagicMock()
        other_ability.__class__.__name__ = 'ThrustAbility'
        other_ability.thrust = 100

        component = mock_component(is_active=True, abilities=[other_ability])

        calculate_combat_endurance(ship, [component])

        # No consumption added
        assert ship.fuel_consumption == 0.0
        assert ship.ammo_consumption == 0.0
        assert ship.energy_consumption == 0.0

    def test_multiple_weapons_with_different_reload_times(
        self, mock_ship, mock_component, mock_resource_consumption_ability, mock_weapon_ability
    ):
        """Multiple weapons with different reload times convert correctly."""
        ship = mock_ship(ammo_max=1000, energy_max=1000, energy_regen=0)

        # First weapon: 1s reload, 10 ammo per shot = 10 ammo/s
        weapon1 = mock_weapon_ability(reload_time=1.0)
        ammo1 = mock_resource_consumption_ability(ResourceType.AMMO, 10.0, 'activation')

        # Second weapon: 2s reload, 20 energy per shot = 10 energy/s
        weapon2 = mock_weapon_ability(reload_time=2.0)
        energy2 = mock_resource_consumption_ability(ResourceType.ENERGY, 20.0, 'activation')

        comp1 = mock_component(is_active=True, abilities=[weapon1, ammo1])
        comp2 = mock_component(is_active=True, abilities=[weapon2, energy2])

        calculate_combat_endurance(ship, [comp1, comp2])

        assert ship.ammo_consumption == 10.0  # 10 / 1
        assert ship.energy_consumption == 10.0  # 20 / 2

    def test_cached_summary_called_by_calculate_combat_endurance(self, mock_ship):
        """calculate_combat_endurance calls _calculate_cached_summary."""
        ship = mock_ship()

        calculate_combat_endurance(ship, [])

        # Should have populated _cached_summary
        assert ship._cached_summary is not None
        assert 'dps' in ship._cached_summary

    def test_negative_energy_net_when_draining(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """energy_net is negative when consumption exceeds generation."""
        ship = mock_ship(energy_max=1000, energy_regen=30)

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 80.0, 'constant')
        component = mock_component(is_active=True, abilities=[energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_net == -50.0  # 30 - 80 = -50
        assert ship.energy_endurance == 20.0  # 1000 / 50 drain

    def test_positive_energy_net_when_sustainable(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """energy_net is positive when generation exceeds consumption."""
        ship = mock_ship(energy_max=1000, energy_regen=100)

        energy_ability = mock_resource_consumption_ability(ResourceType.ENERGY, 40.0, 'constant')
        component = mock_component(is_active=True, abilities=[energy_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.energy_net == 60.0  # 100 - 40 = 60
        assert ship.energy_endurance == float('inf')

    def test_fuel_endurance_uses_potential_when_all_inactive(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """When all components inactive, fuel endurance uses potential consumption."""
        ship = mock_ship(fuel_max=500)

        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 25.0, 'constant')
        inactive_comp = mock_component(is_active=False, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [inactive_comp])

        # Actual is 0, potential is 25
        assert ship.fuel_consumption == 0.0
        assert ship.potential_fuel_consumption == 25.0
        # Endurance uses potential
        assert ship.fuel_endurance == 20.0  # 500 / 25

    def test_all_components_inactive_still_calculates_potential(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """All inactive components still contribute to potential consumption."""
        ship = mock_ship(fuel_max=1000, ammo_max=500, energy_max=2000, energy_regen=0)

        fuel_ab = mock_resource_consumption_ability(ResourceType.FUEL, 10.0, 'constant')
        ammo_ab = mock_resource_consumption_ability(ResourceType.AMMO, 5.0, 'constant')
        energy_ab = mock_resource_consumption_ability(ResourceType.ENERGY, 20.0, 'constant')

        comp = mock_component(is_active=False, abilities=[fuel_ab, ammo_ab, energy_ab])

        calculate_combat_endurance(ship, [comp])

        # Actual all 0
        assert ship.fuel_consumption == 0.0
        assert ship.ammo_consumption == 0.0
        assert ship.energy_consumption == 0.0

        # Potential all set
        assert ship.potential_fuel_consumption == 10.0
        assert ship.potential_ammo_consumption == 5.0
        assert ship.potential_energy_consumption == 20.0

    def test_calculate_cached_summary_with_empty_components(self, mock_ship):
        """_calculate_cached_summary handles ship with no components."""
        ship = mock_ship()
        ship.get_all_components = MagicMock(return_value=[])

        _calculate_cached_summary(ship)

        assert ship._cached_summary['dps'] == 0

    def test_dps_from_multiple_abilities_on_same_component(self, mock_ship, mock_weapon_ability):
        """DPS accumulates from multiple weapon abilities on same component."""
        ship = mock_ship()

        # Two weapons on same component
        weapon1 = mock_weapon_ability(reload_time=1.0, damage=50)  # 50 DPS
        weapon2 = mock_weapon_ability(reload_time=2.0, damage=100)  # 50 DPS

        mock_comp = MagicMock()
        mock_comp.get_abilities = MagicMock(return_value=[weapon1, weapon2])

        ship.get_all_components = MagicMock(return_value=[mock_comp])

        _calculate_cached_summary(ship)

        assert ship._cached_summary['dps'] == 100.0  # 50 + 50

    def test_energy_resource_none_returns_zero_regen(self, mock_ship, mock_component):
        """When get_resource returns None, energy_gen_rate is 0."""
        ship = mock_ship()
        # Override to return None for energy
        ship.resources.get_resource = MagicMock(return_value=None)

        calculate_combat_endurance(ship, [])

        # With no regen, recharge should be infinite
        assert ship.energy_recharge == float('inf')

    def test_fractional_consumption_values(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Fractional consumption values are handled correctly."""
        ship = mock_ship(fuel_max=100)

        # Very precise fractional consumption
        fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 0.333, 'constant')
        component = mock_component(is_active=True, abilities=[fuel_ability])

        calculate_combat_endurance(ship, [component])

        assert ship.fuel_consumption == 0.333
        # 100 / 0.333 ~ 300.3
        assert abs(ship.fuel_endurance - 300.3003003) < 0.001

    def test_large_number_of_components(
        self, mock_ship, mock_component, mock_resource_consumption_ability
    ):
        """Handles large number of components efficiently."""
        ship = mock_ship(fuel_max=10000)

        # Create 100 components each consuming 1 fuel
        components = []
        for _ in range(100):
            fuel_ability = mock_resource_consumption_ability(ResourceType.FUEL, 1.0, 'constant')
            comp = mock_component(is_active=True, abilities=[fuel_ability])
            components.append(comp)

        calculate_combat_endurance(ship, components)

        assert ship.fuel_consumption == 100.0
        assert ship.fuel_endurance == 100.0  # 10000 / 100
