"""Tests for ComponentResourceManager - extracted from Component god class.

PROJ-118 Phase 2: Tests resource activation cost management.

ComponentResourceManager handles:
- can_afford_activation: Check if resources available
- consume_activation: Consume activation-triggered resources
- try_activate: Atomic check-and-consume operation
- get_resource_cost: Calculate resource costs with formulas/multipliers
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.simulation.components.component import create_component, Component
from game.simulation.components.component_resource_manager import ComponentResourceManager


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_component():
    """Create a minimal mock component for testing."""
    component = MagicMock(spec=Component)
    component.ability_instances = []
    component.get_abilities = MagicMock(return_value=[])
    component.data = {}
    component.ship = None
    component.stats = {}
    return component


@pytest.fixture
def mock_resource_consumption_ability():
    """Create a mock ResourceConsumption ability with activation trigger."""
    ability = MagicMock()
    ability.trigger = 'activation'
    ability.check_available = MagicMock(return_value=True)
    ability.check_and_consume = MagicMock()
    return ability


@pytest.fixture
def mock_constant_consumption_ability():
    """Create a mock ResourceConsumption ability with constant trigger."""
    ability = MagicMock()
    ability.trigger = 'constant'
    ability.check_available = MagicMock(return_value=True)
    ability.check_and_consume = MagicMock()
    return ability


# =============================================================================
# Test can_afford_activation
# =============================================================================

class TestCanAffordActivation:
    """Test can_afford_activation method."""

    def test_returns_true_when_no_abilities(self, mock_component):
        """can_afford_activation should return True when component has no abilities."""
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is True

    def test_returns_true_when_all_activation_abilities_affordable(
        self, mock_component, mock_resource_consumption_ability
    ):
        """can_afford_activation should return True when all activation costs affordable."""
        mock_resource_consumption_ability.check_available.return_value = True
        mock_component.get_abilities = MagicMock(return_value=[mock_resource_consumption_ability])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is True
        mock_component.get_abilities.assert_called_once_with('ResourceConsumption')
        mock_resource_consumption_ability.check_available.assert_called_once()

    def test_returns_false_when_activation_ability_not_affordable(
        self, mock_component, mock_resource_consumption_ability
    ):
        """can_afford_activation should return False when activation cost not affordable."""
        mock_resource_consumption_ability.check_available.return_value = False
        mock_component.get_abilities = MagicMock(return_value=[mock_resource_consumption_ability])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is False

    def test_ignores_constant_trigger_abilities(
        self, mock_component, mock_constant_consumption_ability
    ):
        """can_afford_activation should ignore constant trigger abilities."""
        # Even if check_available returns False, it shouldn't matter
        mock_constant_consumption_ability.check_available.return_value = False
        mock_component.get_abilities = MagicMock(return_value=[mock_constant_consumption_ability])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is True
        # check_available should not be called since trigger is 'constant'
        mock_constant_consumption_ability.check_available.assert_not_called()

    def test_ignores_abilities_without_activation_trigger(self, mock_component):
        """can_afford_activation should ignore abilities without activation trigger."""
        ability = MagicMock()
        ability.trigger = 'per_turn'  # Non-activation trigger
        ability.check_available = MagicMock(return_value=False)
        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is True
        ability.check_available.assert_not_called()

    def test_multiple_activation_abilities_all_affordable(self, mock_component):
        """can_afford_activation should check all activation abilities."""
        ability1 = MagicMock()
        ability1.trigger = 'activation'
        ability1.check_available = MagicMock(return_value=True)

        ability2 = MagicMock()
        ability2.trigger = 'activation'
        ability2.check_available = MagicMock(return_value=True)

        mock_component.get_abilities = MagicMock(return_value=[ability1, ability2])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is True
        ability1.check_available.assert_called_once()
        ability2.check_available.assert_called_once()

    def test_multiple_activation_abilities_one_not_affordable(self, mock_component):
        """can_afford_activation should return False if any ability is not affordable."""
        ability1 = MagicMock()
        ability1.trigger = 'activation'
        ability1.check_available = MagicMock(return_value=True)

        ability2 = MagicMock()
        ability2.trigger = 'activation'
        ability2.check_available = MagicMock(return_value=False)

        mock_component.get_abilities = MagicMock(return_value=[ability1, ability2])
        manager = ComponentResourceManager(mock_component)

        assert manager.can_afford_activation() is False


# =============================================================================
# Test consume_activation
# =============================================================================

class TestConsumeActivation:
    """Test consume_activation method."""

    def test_calls_check_and_consume_on_activation_abilities(self, mock_component):
        """consume_activation should call check_and_consume on activation abilities."""
        ability = MagicMock()
        ability.trigger = 'activation'
        ability.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        manager.consume_activation()

        mock_component.get_abilities.assert_called_once_with('ResourceConsumption')
        ability.check_and_consume.assert_called_once()

    def test_does_not_consume_constant_abilities(self, mock_component):
        """consume_activation should not consume constant trigger abilities."""
        ability = MagicMock()
        ability.trigger = 'constant'
        ability.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        manager.consume_activation()

        ability.check_and_consume.assert_not_called()

    def test_consumes_multiple_activation_abilities(self, mock_component):
        """consume_activation should consume all activation abilities."""
        ability1 = MagicMock()
        ability1.trigger = 'activation'
        ability1.check_and_consume = MagicMock()

        ability2 = MagicMock()
        ability2.trigger = 'activation'
        ability2.check_and_consume = MagicMock()

        ability3 = MagicMock()
        ability3.trigger = 'constant'  # Should be skipped
        ability3.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[ability1, ability2, ability3])
        manager = ComponentResourceManager(mock_component)

        manager.consume_activation()

        ability1.check_and_consume.assert_called_once()
        ability2.check_and_consume.assert_called_once()
        ability3.check_and_consume.assert_not_called()

    def test_no_abilities_does_not_raise(self, mock_component):
        """consume_activation should handle empty ability list gracefully."""
        mock_component.get_abilities = MagicMock(return_value=[])
        manager = ComponentResourceManager(mock_component)

        # Should not raise
        manager.consume_activation()


# =============================================================================
# Test try_activate
# =============================================================================

class TestTryActivate:
    """Test try_activate method - atomic check-and-consume."""

    def test_returns_true_and_consumes_when_affordable(self, mock_component):
        """try_activate should return True and consume when affordable."""
        ability = MagicMock()
        ability.trigger = 'activation'
        ability.check_available = MagicMock(return_value=True)
        ability.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        result = manager.try_activate()

        assert result is True
        ability.check_and_consume.assert_called_once()

    def test_returns_false_and_does_not_consume_when_not_affordable(self, mock_component):
        """try_activate should return False and not consume when not affordable."""
        ability = MagicMock()
        ability.trigger = 'activation'
        ability.check_available = MagicMock(return_value=False)
        ability.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        result = manager.try_activate()

        assert result is False
        ability.check_and_consume.assert_not_called()

    def test_returns_true_when_no_abilities(self, mock_component):
        """try_activate should return True when no abilities to check."""
        mock_component.get_abilities = MagicMock(return_value=[])
        manager = ComponentResourceManager(mock_component)

        result = manager.try_activate()

        assert result is True


# =============================================================================
# Test get_resource_cost
# =============================================================================

class TestGetResourceCost:
    """Test get_resource_cost method - cost calculation with formulas/multipliers."""

    def test_returns_empty_dict_when_no_costs(self, mock_component):
        """get_resource_cost should return empty dict when no resource costs."""
        mock_component.data = {}
        mock_component.stats = {}
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {}

    def test_returns_base_costs_without_multiplier(self, mock_component):
        """get_resource_cost should return base costs when no multiplier."""
        mock_component.data = {'resource_cost': {'fuel': 10, 'energy': 5}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 10, 'energy': 5}

    def test_applies_cost_multiplier(self, mock_component):
        """get_resource_cost should apply cost_mult from stats."""
        mock_component.data = {'resource_cost': {'fuel': 10, 'energy': 6}}
        mock_component.stats = {'cost_mult': 2.0}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 20, 'energy': 12}

    def test_uses_evaluated_resource_cost_when_available(self, mock_component):
        """get_resource_cost should prefer evaluated_resource_cost over data."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.evaluated_resource_cost = {'fuel': 15, 'ammo': 3}
        mock_component.stats = {}
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 15, 'ammo': 3}

    def test_returns_integer_costs(self, mock_component):
        """get_resource_cost should return integer costs."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.stats = {'cost_mult': 1.5}  # Would give 15.0
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 15}
        assert isinstance(result['fuel'], int)

    def test_evaluates_formula_costs(self, mock_component):
        """get_resource_cost should evaluate formula costs (prefixed with '=')."""
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        # Explicit context required — there is no longer a silent default
        # for ship_class_mass. Formulas referencing it without a ship or
        # context now raise FormulaException loudly.
        result = manager.get_resource_cost(context={'ship_class_mass': 1000})

        assert result == {'fuel': 10}  # 1000 * 0.01 = 10

    def test_uses_context_ship_class_mass(self, mock_component):
        """get_resource_cost should use context ship_class_mass for formulas."""
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost(context={'ship_class_mass': 2000})

        assert result == {'fuel': 20}  # 2000 * 0.01 = 20

    def test_uses_ship_reference_for_mass_context(self, mock_component):
        """get_resource_cost should use ship.max_mass_budget when no context provided."""
        mock_ship = MagicMock()
        mock_ship.max_mass_budget = 3000

        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        mock_component.ship = mock_ship
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 30}  # 3000 * 0.01 = 30

    def test_context_takes_priority_over_ship_reference(self, mock_component):
        """get_resource_cost should prefer explicit context over ship reference."""
        mock_ship = MagicMock()
        mock_ship.max_mass_budget = 3000

        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        mock_component.ship = mock_ship
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost(context={'ship_class_mass': 5000})

        assert result == {'fuel': 50}  # Uses context 5000, not ship 3000

    def test_formula_with_multiplier(self, mock_component):
        """get_resource_cost should apply multiplier to formula results."""
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {'cost_mult': 2.0}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost(context={'ship_class_mass': 1000})

        assert result == {'fuel': 20}  # (1000 * 0.01) * 2.0 = 20

    def test_mixed_formula_and_numeric_costs(self, mock_component):
        """get_resource_cost should handle mix of formula and numeric costs."""
        mock_component.data = {
            'resource_cost': {
                'fuel': '=ship_class_mass * 0.01',
                'energy': 5
            }
        }
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost(context={'ship_class_mass': 1000})

        assert result == {'fuel': 10, 'energy': 5}

    def test_zero_resource_cost(self, mock_component):
        """get_resource_cost should handle zero costs."""
        mock_component.data = {'resource_cost': {'fuel': 0}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 0}


# =============================================================================
# Integration Tests with Real Components
# =============================================================================

class TestResourceManagerIntegration:
    """Integration tests using real component data."""

    def test_component_resource_manager_accessible_via_property(self, fresh_registries):
        """Component.resource_manager should return ComponentResourceManager."""
        railgun = create_component('railgun', registries=fresh_registries)

        manager = railgun.resource_manager

        assert isinstance(manager, ComponentResourceManager)
        assert manager._component is railgun

    def test_resource_manager_is_lazily_initialized(self, fresh_registries):
        """Resource manager should be created on first access."""
        railgun = create_component('railgun', registries=fresh_registries)

        # Initially None
        assert railgun._resource_mgr is None

        # Access creates it
        _ = railgun.resource_manager

        assert railgun._resource_mgr is not None

    def test_resource_manager_is_cached(self, fresh_registries):
        """Resource manager should return same instance on repeated access."""
        railgun = create_component('railgun', registries=fresh_registries)

        manager1 = railgun.resource_manager
        manager2 = railgun.resource_manager

        assert manager1 is manager2

    def test_component_delegates_can_afford_activation(self, fresh_registries):
        """Component.can_afford_activation should delegate to resource_manager."""
        railgun = create_component('railgun', registries=fresh_registries)

        # Should return same result as calling manager directly
        assert railgun.can_afford_activation() == railgun.resource_manager.can_afford_activation()

    def test_component_delegates_try_activate(self, fresh_registries):
        """Component.try_activate should delegate to resource_manager."""
        railgun = create_component('railgun', registries=fresh_registries)

        # Without ship resources, activation depends on ability setup
        result = railgun.try_activate()

        # Should succeed if no activation-triggered resource consumption
        assert isinstance(result, bool)

    def test_component_delegates_get_resource_cost(self, fresh_registries):
        """Component.get_resource_cost should delegate to resource_manager."""
        railgun = create_component('railgun', registries=fresh_registries)

        result1 = railgun.get_resource_cost()
        result2 = railgun.resource_manager.get_resource_cost()

        assert result1 == result2


# =============================================================================
# Edge Cases
# =============================================================================

class TestResourceManagerEdgeCases:
    """Edge cases for resource management."""

    def test_slots_optimization(self, mock_component):
        """ComponentResourceManager should use __slots__ for memory efficiency."""
        manager = ComponentResourceManager(mock_component)

        assert hasattr(ComponentResourceManager, '__slots__')
        assert '_component' in ComponentResourceManager.__slots__

        # Should not have __dict__ due to __slots__
        assert not hasattr(manager, '__dict__')

    def test_handles_none_trigger_gracefully(self, mock_component):
        """Should handle abilities with None trigger."""
        ability = MagicMock()
        ability.trigger = None
        ability.check_available = MagicMock(return_value=False)
        mock_component.get_abilities = MagicMock(return_value=[ability])
        manager = ComponentResourceManager(mock_component)

        # Should not raise, and should return True since trigger != 'activation'
        result = manager.can_afford_activation()

        assert result is True
        ability.check_available.assert_not_called()

    def test_default_multiplier_is_one(self, mock_component):
        """Default cost multiplier should be 1.0 when not in stats."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.stats = {}  # No cost_mult
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 10}

    def test_fractional_multiplier_truncates_to_int(self, mock_component):
        """Fractional costs should be truncated to integers."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.stats = {'cost_mult': 1.3}  # Would give 13.0
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 13}
        assert isinstance(result['fuel'], int)

    def test_formula_default_on_error(self, mock_component):
        """Formula evaluation should use default=0 on error."""
        mock_component.data = {'resource_cost': {'fuel': '=invalid_variable'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        # Should use default of 0 for failed formula
        assert result == {'fuel': 0}

    def test_negative_multiplier_produces_negative_cost(self, mock_component):
        """Negative cost_mult produces negative costs (edge case)."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.stats = {'cost_mult': -1.0}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': -10}

    def test_very_large_multiplier(self, mock_component):
        """Very large cost_mult is handled correctly."""
        mock_component.data = {'resource_cost': {'fuel': 10}}
        mock_component.stats = {'cost_mult': 1000000.0}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 10000000}

    def test_empty_resource_cost_dict(self, mock_component):
        """Empty resource_cost dict returns empty dict."""
        mock_component.data = {'resource_cost': {}}
        mock_component.stats = {'cost_mult': 2.0}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {}

    def test_formula_with_zero_ship_mass(self, mock_component):
        """Formula with ship_class_mass=0 evaluates correctly."""
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mock_component.stats = {}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost(context={'ship_class_mass': 0})

        assert result == {'fuel': 0}

    def test_multiple_resource_types(self, mock_component):
        """Multiple resource types are all calculated correctly."""
        mock_component.data = {
            'resource_cost': {
                'fuel': 10,
                'energy': 20,
                'ammo': 5,
                'coolant': 15
            }
        }
        mock_component.stats = {'cost_mult': 1.5}
        mock_component.evaluated_resource_cost = None
        manager = ComponentResourceManager(mock_component)

        result = manager.get_resource_cost()

        assert result == {'fuel': 15, 'energy': 30, 'ammo': 7, 'coolant': 22}


# =============================================================================
# Test Early Return Behavior
# =============================================================================

class TestCanAffordActivationEarlyReturn:
    """Test early return behavior in can_afford_activation."""

    def test_early_return_on_first_unaffordable(self, mock_component):
        """can_afford_activation returns False on first unaffordable ability."""
        ability1 = MagicMock()
        ability1.trigger = 'activation'
        ability1.check_available = MagicMock(return_value=False)

        ability2 = MagicMock()
        ability2.trigger = 'activation'
        ability2.check_available = MagicMock(return_value=True)

        mock_component.get_abilities = MagicMock(return_value=[ability1, ability2])
        manager = ComponentResourceManager(mock_component)

        result = manager.can_afford_activation()

        assert result is False
        # First ability checked, returns False early
        ability1.check_available.assert_called_once()
        # Second ability should not be checked due to early return
        ability2.check_available.assert_not_called()
