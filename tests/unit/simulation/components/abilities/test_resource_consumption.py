"""
Unit tests for resource consumption during ability activation.

Tests ResourceConsumption ability behavior including:
- Resource consumption when abilities activate
- Insufficient resources handling
- Multiple resource types
- Edge cases (zero cost, negative amounts)
- Different trigger types (constant, activation, strategic_per_hex)
- Modifier effects on consumption amounts
"""
import pytest
from unittest.mock import MagicMock, Mock

from game.simulation.components.abilities.resources import (
    ResourceConsumption,
    ResourceStorage,
    ResourceGeneration,
)
from game.simulation.systems.resource_manager import ResourceRegistry, ResourceState
from game.core.config import PhysicsConfig
from game.simulation.components.abilities.ui_colors import (
    HINT_RANGE,
    HINT_WARP_ENERGY,
    HINT_PROJECTILE_SPEED,
    HINT_DEFAULT,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_component():
    """Create a mock component for ability testing."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    component.ship = None
    return component


@pytest.fixture
def mock_component_with_ship():
    """Create a mock component with a ship that has a resource registry."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    component.ship = MagicMock()
    component.ship.resources = ResourceRegistry()
    return component


@pytest.fixture
def resource_registry():
    """Create a resource registry with common resources."""
    registry = ResourceRegistry()
    # Register storage and set initial values
    registry.register_storage('fuel', 100.0)
    registry.set_value('fuel', 100.0)
    registry.register_storage('energy', 50.0)
    registry.set_value('energy', 50.0)
    registry.register_storage('ammo', 20.0)
    registry.set_value('ammo', 20.0)
    return registry


# =============================================================================
# ResourceConsumption Initialization Tests
# =============================================================================


class TestResourceConsumptionInit:
    """Tests for ResourceConsumption initialization."""

    def test_init_with_full_data(self, mock_component):
        """Initialize with complete data dict."""
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        assert ability.resource_type == 'fuel'
        assert ability.amount == 10.0
        assert ability._base_amount == 10.0
        assert ability.trigger == 'activation'

    def test_init_defaults(self, mock_component):
        """Initialize with minimal data uses defaults."""
        data = {}
        ability = ResourceConsumption(mock_component, data)

        assert ability.resource_type == ''
        assert ability.amount == 0.0
        assert ability.trigger == 'constant'

    def test_init_with_constant_trigger(self, mock_component):
        """Initialize with constant trigger type."""
        data = {
            'resource': 'energy',
            'amount': 5.0,
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component, data)

        assert ability.trigger == 'constant'

    def test_init_with_strategic_trigger(self, mock_component):
        """Initialize with strategic_per_hex trigger type."""
        data = {
            'resource': 'fuel',
            'amount': 1.0,
            'trigger': 'strategic_per_hex'
        }
        ability = ResourceConsumption(mock_component, data)

        assert ability.trigger == 'strategic_per_hex'


# =============================================================================
# Activation Trigger Tests
# =============================================================================


class TestActivationTriggerConsumption:
    """Tests for activation-triggered resource consumption."""

    def test_check_and_consume_success(self, mock_component_with_ship, resource_registry):
        """check_and_consume returns True and consumes resource when available."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('fuel') == initial_fuel - 10.0

    def test_check_and_consume_insufficient_resources(self, mock_component_with_ship, resource_registry):
        """check_and_consume returns False when insufficient resources."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 150.0,  # More than available (100)
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.check_and_consume()

        assert result is False
        assert resource_registry.get_value('fuel') == initial_fuel  # Unchanged

    def test_check_and_consume_exact_amount(self, mock_component_with_ship, resource_registry):
        """check_and_consume succeeds when consuming exact available amount."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 100.0,  # Exact amount available
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('fuel') == 0.0

    def test_check_and_consume_with_external_registry(self, mock_component):
        """check_and_consume works with externally provided registry."""
        registry = ResourceRegistry()
        registry.register_storage('ammo', 50.0)
        registry.set_value('ammo', 50.0)

        data = {
            'resource': 'ammo',
            'amount': 5.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        result = ability.check_and_consume(resources=registry)

        assert result is True
        assert registry.get_value('ammo') == 45.0

    def test_check_available_without_consuming(self, mock_component_with_ship, resource_registry):
        """check_available returns True without consuming resources."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.check_available()

        assert result is True
        assert resource_registry.get_value('fuel') == initial_fuel  # Unchanged

    def test_check_available_insufficient(self, mock_component_with_ship, resource_registry):
        """check_available returns False when insufficient resources."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 150.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_available()

        assert result is False


# =============================================================================
# Constant Trigger Tests
# =============================================================================


class TestConstantTriggerConsumption:
    """Tests for constant (per-tick) resource consumption."""

    def test_update_consumes_per_tick_amount(self, mock_component_with_ship, resource_registry):
        """update() consumes amount scaled by TICK_RATE for constant trigger."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'energy',
            'amount': 10.0,  # 10 per second
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_energy = resource_registry.get_value('energy')
        result = ability.update()

        expected_consumption = 10.0 * PhysicsConfig.TICK_RATE
        assert result is True
        assert abs(resource_registry.get_value('energy') - (initial_energy - expected_consumption)) < 0.001

    def test_update_returns_false_on_starvation(self, mock_component_with_ship, resource_registry):
        """update() returns False when resources depleted (starvation)."""
        mock_component_with_ship.ship.resources = resource_registry
        # Set energy to very low value
        resource_registry.set_value('energy', 0.001)

        data = {
            'resource': 'energy',
            'amount': 100.0,  # Will consume more than available per tick
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.update()

        assert result is False

    def test_update_with_external_registry(self, mock_component):
        """update() works with externally provided registry."""
        registry = ResourceRegistry()
        registry.register_storage('fuel', 100.0)
        registry.set_value('fuel', 100.0)

        data = {
            'resource': 'fuel',
            'amount': 20.0,
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component, data)

        initial_fuel = registry.get_value('fuel')
        result = ability.update(resources=registry)

        expected_consumption = 20.0 * PhysicsConfig.TICK_RATE
        assert result is True
        assert abs(registry.get_value('fuel') - (initial_fuel - expected_consumption)) < 0.001

    def test_update_non_constant_trigger_no_consumption(self, mock_component_with_ship, resource_registry):
        """update() does not consume for activation trigger."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'  # Not constant
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.update()

        assert result is True
        assert resource_registry.get_value('fuel') == initial_fuel  # Unchanged


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestResourceConsumptionEdgeCases:
    """Tests for edge cases in resource consumption."""

    def test_zero_cost_activation(self, mock_component_with_ship, resource_registry):
        """Zero cost activation always succeeds."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 0.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('fuel') == initial_fuel

    def test_zero_cost_check_available(self, mock_component_with_ship, resource_registry):
        """Zero cost check_available always returns True."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 0.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_available()

        assert result is True

    def test_nonexistent_resource_with_positive_cost(self, mock_component_with_ship, resource_registry):
        """Attempting to consume nonexistent resource fails if cost > 0."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'nonexistent_resource',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is False

    def test_nonexistent_resource_with_zero_cost(self, mock_component_with_ship, resource_registry):
        """Zero cost for nonexistent resource succeeds."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'nonexistent_resource',
            'amount': 0.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is True

    def test_nonexistent_resource_check_available_zero_cost(self, mock_component_with_ship, resource_registry):
        """Zero cost check_available for nonexistent resource returns True."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'nonexistent_resource',
            'amount': 0.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_available()

        assert result is True

    def test_constant_trigger_nonexistent_resource_positive_cost_fails(self, mock_component_with_ship, resource_registry):
        """Constant trigger with nonexistent resource and positive cost returns False."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'nonexistent_resource',
            'amount': 10.0,
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.update()

        assert result is False

    def test_no_ship_reference(self, mock_component):
        """Consumption fails gracefully when no ship reference."""
        mock_component.ship = None
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        result = ability.check_and_consume()

        assert result is False

    def test_no_resources_on_ship(self, mock_component):
        """Consumption fails gracefully when ship has no resources."""
        mock_component.ship = MagicMock()
        mock_component.ship.resources = None
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        result = ability.check_and_consume()

        assert result is False


# =============================================================================
# Multiple Resource Types Tests
# =============================================================================


class TestMultipleResourceTypes:
    """Tests for handling different resource types."""

    def test_fuel_consumption(self, mock_component_with_ship, resource_registry):
        """Test consuming fuel resource."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 25.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('fuel') == 75.0

    def test_energy_consumption(self, mock_component_with_ship, resource_registry):
        """Test consuming energy resource."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'energy',
            'amount': 30.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('energy') == 20.0

    def test_ammo_consumption(self, mock_component_with_ship, resource_registry):
        """Test consuming ammo resource."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'ammo',
            'amount': 5.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('ammo') == 15.0

    def test_multiple_consumptions_different_resources(self, mock_component_with_ship, resource_registry):
        """Test multiple abilities consuming different resources."""
        mock_component_with_ship.ship.resources = resource_registry

        fuel_ability = ResourceConsumption(mock_component_with_ship, {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        })
        energy_ability = ResourceConsumption(mock_component_with_ship, {
            'resource': 'energy',
            'amount': 5.0,
            'trigger': 'activation'
        })

        fuel_result = fuel_ability.check_and_consume()
        energy_result = energy_ability.check_and_consume()

        assert fuel_result is True
        assert energy_result is True
        assert resource_registry.get_value('fuel') == 90.0
        assert resource_registry.get_value('energy') == 45.0


# =============================================================================
# Strategic Movement Cost Tests
# =============================================================================


class TestStrategicMovementCost:
    """Tests for strategic_per_hex trigger type."""

    def test_get_strategic_cost_returns_amount(self, mock_component):
        """get_strategic_cost returns amount for strategic_per_hex trigger."""
        data = {
            'resource': 'fuel',
            'amount': 5.0,
            'trigger': 'strategic_per_hex'
        }
        ability = ResourceConsumption(mock_component, data)

        cost = ability.get_strategic_cost()

        assert cost == 5.0

    def test_get_strategic_cost_returns_zero_for_other_triggers(self, mock_component):
        """get_strategic_cost returns 0 for non-strategic triggers."""
        data = {
            'resource': 'fuel',
            'amount': 5.0,
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component, data)

        cost = ability.get_strategic_cost()

        assert cost == 0.0

    def test_get_strategic_cost_activation_trigger(self, mock_component):
        """get_strategic_cost returns 0 for activation trigger."""
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        cost = ability.get_strategic_cost()

        assert cost == 0.0


# =============================================================================
# Modifier Effects Tests
# =============================================================================


class TestConsumptionModifierEffects:
    """Tests for modifier effects on consumption amounts."""

    def test_recalculate_applies_consumption_mult(self, mock_component):
        """recalculate() applies consumption_mult modifier."""
        mock_component.stats = {'consumption_mult': 1.5}
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        ability.recalculate()

        assert ability.amount == 15.0  # 10.0 * 1.5
        assert ability._base_amount == 10.0  # Base unchanged

    def test_recalculate_with_zero_mult(self, mock_component):
        """recalculate() with zero multiplier results in zero consumption."""
        mock_component.stats = {'consumption_mult': 0.0}
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        ability.recalculate()

        assert ability.amount == 0.0

    def test_recalculate_with_reduction_mult(self, mock_component):
        """recalculate() with reduction multiplier decreases consumption."""
        mock_component.stats = {'consumption_mult': 0.5}
        data = {
            'resource': 'energy',
            'amount': 20.0,
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component, data)

        ability.recalculate()

        assert ability.amount == 10.0  # 20.0 * 0.5

    def test_recalculate_uses_default_mult_when_not_set(self, mock_component):
        """recalculate() uses 1.0 as default multiplier."""
        mock_component.stats = {}  # No consumption_mult
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        ability.recalculate()

        assert ability.amount == 10.0  # Unchanged

    def test_modified_consumption_affects_check_and_consume(self, mock_component_with_ship, resource_registry):
        """Modified consumption amount is used in check_and_consume."""
        mock_component_with_ship.ship.resources = resource_registry
        mock_component_with_ship.stats = {'consumption_mult': 2.0}
        data = {
            'resource': 'fuel',
            'amount': 10.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)
        ability.recalculate()

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.check_and_consume()

        assert result is True
        assert resource_registry.get_value('fuel') == initial_fuel - 20.0  # 10 * 2.0


# =============================================================================
# Sync Data Tests
# =============================================================================


class TestSyncData:
    """Tests for sync_data method."""

    def test_sync_data_updates_resource_name(self, mock_component):
        """sync_data updates resource_name from new data."""
        data = {'resource': 'fuel', 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        ability.sync_data({'resource': 'energy', 'amount': 5.0, 'trigger': 'constant'})

        assert ability.resource_type == 'energy'
        assert ability.amount == 5.0
        assert ability.trigger == 'constant'

    def test_sync_data_with_numeric_shortcut(self, mock_component):
        """sync_data handles numeric shortcut (int/float instead of dict)."""
        data = {'resource': 'fuel', 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        ability.sync_data(15.0)

        assert ability.amount == 15.0
        assert ability._base_amount == 15.0
        assert ability.trigger == 'constant'  # Default for shortcut

    def test_sync_data_preserves_resource_name_with_partial_update(self, mock_component):
        """sync_data preserves resource_name if not provided in new data."""
        data = {'resource': 'fuel', 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        ability.sync_data({'amount': 20.0})

        assert ability.resource_type == 'fuel'  # Preserved
        assert ability.amount == 20.0


# =============================================================================
# UI Rows Tests
# =============================================================================


class TestResourceConsumptionUIRows:
    """Tests for get_ui_rows method."""

    def test_ui_rows_constant_trigger(self, mock_component):
        """get_ui_rows shows /s suffix for constant trigger."""
        data = {'resource': 'fuel', 'amount': 10.0, 'trigger': 'constant'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert '10.0/s' in rows[0]['value']
        assert 'Use' in rows[0]['label']

    def test_ui_rows_activation_trigger(self, mock_component):
        """get_ui_rows shows /use suffix for activation trigger."""
        data = {'resource': 'fuel', 'amount': 5.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert '5.0/use' in rows[0]['value']
        assert 'Cost' in rows[0]['label']

    def test_ui_rows_strategic_trigger(self, mock_component):
        """get_ui_rows shows /hex suffix for strategic_per_hex trigger."""
        data = {'resource': 'fuel', 'amount': 2.0, 'trigger': 'strategic_per_hex'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()

        assert len(rows) == 1
        assert '2.0/hex' in rows[0]['value']


# =============================================================================
# Primary Value Tests
# =============================================================================


class TestResourceConsumptionPrimaryValue:
    """Tests for get_primary_value method."""

    def test_primary_value_returns_amount(self, mock_component):
        """get_primary_value returns the consumption amount."""
        data = {'resource': 'fuel', 'amount': 15.5, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        value = ability.get_primary_value()

        assert value == 15.5

    def test_primary_value_reflects_modifier(self, mock_component):
        """get_primary_value returns modified amount after recalculate."""
        mock_component.stats = {'consumption_mult': 2.0}
        data = {'resource': 'fuel', 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)
        ability.recalculate()

        value = ability.get_primary_value()

        assert value == 20.0


# =============================================================================
# ResourceStorage Tests (Brief coverage for completeness)
# =============================================================================


class TestResourceStorage:
    """Basic tests for ResourceStorage ability."""

    def test_storage_init(self, mock_component):
        """ResourceStorage initializes with resource type and max amount."""
        data = {'resource': 'fuel', 'amount': 100.0}
        ability = ResourceStorage(mock_component, data)

        assert ability.resource_type == 'fuel'
        assert ability.max_amount == 100.0
        assert ability._base_max_amount == 100.0

    def test_storage_recalculate_with_capacity_mult(self, mock_component):
        """ResourceStorage recalculate applies capacity_mult."""
        mock_component.stats = {'capacity_mult': 1.5}
        data = {'resource': 'fuel', 'amount': 100.0}
        ability = ResourceStorage(mock_component, data)

        ability.recalculate()

        assert ability.max_amount == 150.0

    def test_storage_primary_value(self, mock_component):
        """ResourceStorage get_primary_value returns max_amount."""
        data = {'resource': 'fuel', 'amount': 100.0}
        ability = ResourceStorage(mock_component, data)

        assert ability.get_primary_value() == 100.0


# =============================================================================
# ResourceGeneration Tests (Brief coverage for completeness)
# =============================================================================


class TestResourceGeneration:
    """Basic tests for ResourceGeneration ability."""

    def test_generation_init(self, mock_component):
        """ResourceGeneration initializes with resource type and rate."""
        data = {'resource': 'energy', 'amount': 10.0}
        ability = ResourceGeneration(mock_component, data)

        assert ability.resource_type == 'energy'
        assert ability.rate == 10.0
        assert ability._base_rate == 10.0

    def test_generation_recalculate_with_energy_gen_mult(self, mock_component):
        """ResourceGeneration recalculate applies energy_gen_mult."""
        mock_component.stats = {'energy_gen_mult': 2.0}
        data = {'resource': 'energy', 'amount': 10.0}
        ability = ResourceGeneration(mock_component, data)

        ability.recalculate()

        assert ability.rate == 20.0

    def test_generation_primary_value(self, mock_component):
        """ResourceGeneration get_primary_value returns rate."""
        data = {'resource': 'energy', 'amount': 10.0}
        ability = ResourceGeneration(mock_component, data)

        assert ability.get_primary_value() == 10.0


# =============================================================================
# Additional Edge Case and Boundary Tests
# =============================================================================


class TestResourceConsumptionStatBindings:
    """Tests for ResourceConsumption STAT_BINDINGS."""

    def test_stat_bindings_defined(self, mock_component):
        """ResourceConsumption has correct STAT_BINDINGS."""
        from game.simulation.components.abilities.stat_keys import StatKey

        bindings = ResourceConsumption.STAT_BINDINGS
        assert len(bindings) == 1
        assert bindings[0].stat_key == StatKey.CONSUMPTION_MULT
        assert bindings[0].attribute_name == 'amount'
        assert bindings[0].operation == 'multiply'

    def test_get_consumed_stats_returns_consumption_mult(self, mock_component):
        """get_consumed_stats returns CONSUMPTION_MULT."""
        from game.simulation.components.abilities.stat_keys import StatKey

        stats = ResourceConsumption.get_consumed_stats()
        assert StatKey.CONSUMPTION_MULT in stats


class TestResourceStorageStatBindings:
    """Tests for ResourceStorage STAT_BINDINGS."""

    def test_stat_bindings_defined(self, mock_component):
        """ResourceStorage has correct STAT_BINDINGS."""
        from game.simulation.components.abilities.stat_keys import StatKey

        bindings = ResourceStorage.STAT_BINDINGS
        assert len(bindings) == 1
        assert bindings[0].stat_key == StatKey.CAPACITY_MULT
        assert bindings[0].attribute_name == 'max_amount'

    def test_sync_data_with_numeric_shortcut(self, mock_component):
        """ResourceStorage sync_data handles numeric shortcut."""
        data = {'resource': 'fuel', 'amount': 100.0}
        ability = ResourceStorage(mock_component, data)

        ability.sync_data(200.0)

        assert ability.max_amount == 200.0
        assert ability._base_max_amount == 200.0


class TestResourceGenerationStatBindings:
    """Tests for ResourceGeneration STAT_BINDINGS."""

    def test_stat_bindings_defined(self, mock_component):
        """ResourceGeneration has correct STAT_BINDINGS."""
        from game.simulation.components.abilities.stat_keys import StatKey

        bindings = ResourceGeneration.STAT_BINDINGS
        assert len(bindings) == 1
        assert bindings[0].stat_key == StatKey.ENERGY_GEN_MULT
        assert bindings[0].attribute_name == 'rate'

    def test_sync_data_with_numeric_shortcut(self, mock_component):
        """ResourceGeneration sync_data handles numeric shortcut."""
        data = {'resource': 'energy', 'amount': 10.0}
        ability = ResourceGeneration(mock_component, data)

        ability.sync_data(25.0)

        assert ability.rate == 25.0
        assert ability._base_rate == 25.0


class TestResourceConsumptionFloatPrecision:
    """Tests for float precision in resource consumption."""

    def test_very_small_constant_consumption(self, mock_component_with_ship, resource_registry):
        """Very small constant consumption amounts work correctly."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 0.001,  # Very small rate
            'trigger': 'constant'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        initial_fuel = resource_registry.get_value('fuel')
        result = ability.update()

        expected_consumption = 0.001 * PhysicsConfig.TICK_RATE
        assert result is True
        assert resource_registry.get_value('fuel') < initial_fuel

    def test_large_consumption_amount(self, mock_component_with_ship, resource_registry):
        """Large consumption amounts that exceed resources fail."""
        mock_component_with_ship.ship.resources = resource_registry
        data = {
            'resource': 'fuel',
            'amount': 1000.0,  # More than max storage
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        result = ability.check_and_consume()

        assert result is False

    def test_repeated_consumption_until_depleted(self, mock_component_with_ship, resource_registry):
        """Repeated consumption eventually depletes resources."""
        mock_component_with_ship.ship.resources = resource_registry
        resource_registry.set_value('ammo', 10.0)

        data = {
            'resource': 'ammo',
            'amount': 3.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        # First 3 consumptions should succeed
        assert ability.check_and_consume() is True  # 7 remaining
        assert ability.check_and_consume() is True  # 4 remaining
        assert ability.check_and_consume() is True  # 1 remaining

        # Fourth should fail
        assert ability.check_and_consume() is False


class TestResourceConsumptionUIColors:
    """Tests for UI color hints in resource consumption."""

    def test_fuel_resource_has_orange_color(self, mock_component):
        """Fuel resource shows orange color hint."""
        from game.core.constants import ResourceType

        data = {'resource': ResourceType.FUEL, 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()
        assert rows[0]['color_hint'] == HINT_RANGE  # Orange

    def test_energy_resource_has_blue_color(self, mock_component):
        """Energy resource shows light blue color hint."""
        from game.core.constants import ResourceType

        data = {'resource': ResourceType.ENERGY, 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()
        assert rows[0]['color_hint'] == HINT_WARP_ENERGY  # Light Blue

    def test_ammo_resource_has_yellow_color(self, mock_component):
        """Ammo resource shows dirty yellow color hint."""
        from game.core.constants import ResourceType

        data = {'resource': ResourceType.AMMO, 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()
        assert rows[0]['color_hint'] == HINT_PROJECTILE_SPEED  # Dirty Yellow

    def test_unknown_resource_has_white_color(self, mock_component):
        """Unknown resource shows white color hint."""
        data = {'resource': 'unknown_resource', 'amount': 10.0, 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()
        assert rows[0]['color_hint'] == HINT_DEFAULT  # White


class TestResourceConsumptionStringAmounts:
    """Tests for handling string/formula amounts."""

    def test_ui_rows_with_string_amount(self, mock_component):
        """UI rows handle string amounts (formulas) correctly."""
        data = {'resource': 'fuel', 'amount': '2*size', 'trigger': 'activation'}
        ability = ResourceConsumption(mock_component, data)

        rows = ability.get_ui_rows()
        assert '2*size/use' in rows[0]['value']


class TestResourceRegistryFallback:
    """Tests for resource registry fallback behavior."""

    def test_external_registry_takes_precedence(self, mock_component_with_ship, resource_registry):
        """External registry parameter takes precedence over ship.resources."""
        mock_component_with_ship.ship.resources = resource_registry

        # Create a different registry
        external_registry = ResourceRegistry()
        external_registry.register_storage('fuel', 500.0)
        external_registry.set_value('fuel', 500.0)

        data = {
            'resource': 'fuel',
            'amount': 100.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component_with_ship, data)

        # Use external registry
        result = ability.check_and_consume(resources=external_registry)

        assert result is True
        assert external_registry.get_value('fuel') == 400.0
        # Ship's resources should be unchanged
        assert resource_registry.get_value('fuel') == 100.0

    def test_check_available_with_external_registry(self, mock_component):
        """check_available works with external registry."""
        registry = ResourceRegistry()
        registry.register_storage('energy', 100.0)
        registry.set_value('energy', 50.0)

        data = {
            'resource': 'energy',
            'amount': 30.0,
            'trigger': 'activation'
        }
        ability = ResourceConsumption(mock_component, data)

        assert ability.check_available(resources=registry) is True

        # Set energy too low
        registry.set_value('energy', 10.0)
        assert ability.check_available(resources=registry) is False
