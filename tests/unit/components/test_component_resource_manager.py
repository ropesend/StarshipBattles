"""Tests for ComponentResourceManager."""
import pytest
from unittest.mock import MagicMock, patch


class TestComponentResourceManager:
    """Tests for ComponentResourceManager extracted from Component."""

    @pytest.fixture
    def mock_component(self):
        """Create a mock component for testing."""
        component = MagicMock()
        component.ability_instances = []
        component.abilities = {}
        component.stats = {'cost_mult': 1.0}
        component.data = {'resource_cost': {'fuel': 10, 'energy': 5}}
        component.ship = None
        component.evaluated_resource_cost = None
        return component

    @pytest.fixture
    def mock_resource_ability(self):
        """Create a mock resource consumption ability."""
        ability = MagicMock()
        ability.trigger = 'activation'
        ability.check_available = MagicMock(return_value=True)
        ability.check_and_consume = MagicMock()
        return ability

    @pytest.fixture
    def mock_resource_ability_depleted(self):
        """Create a mock resource consumption ability with no resources."""
        ability = MagicMock()
        ability.trigger = 'activation'
        ability.check_available = MagicMock(return_value=False)
        ability.check_and_consume = MagicMock()
        return ability

    # === can_afford_activation tests ===

    def test_can_afford_activation_returns_true_when_resources_available(self, mock_component, mock_resource_ability):
        """Test can_afford_activation returns True when all resources are available."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ability_instances = [mock_resource_ability]
        mgr = ComponentResourceManager(mock_component)

        result = mgr.can_afford_activation()

        assert result is True
        mock_resource_ability.check_available.assert_called_once()

    def test_can_afford_activation_returns_false_when_resources_depleted(self, mock_component, mock_resource_ability_depleted):
        """Test can_afford_activation returns False when resources are depleted."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ability_instances = [mock_resource_ability_depleted]
        mgr = ComponentResourceManager(mock_component)

        result = mgr.can_afford_activation()

        assert result is False

    def test_can_afford_activation_ignores_non_activation_triggers(self, mock_component):
        """Test can_afford_activation ignores abilities with non-activation triggers."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        constant_ability = MagicMock()
        constant_ability.trigger = 'constant'
        constant_ability.check_available = MagicMock(return_value=False)
        mock_component.ability_instances = [constant_ability]
        mgr = ComponentResourceManager(mock_component)

        result = mgr.can_afford_activation()

        assert result is True  # Should pass - constant trigger is ignored

    def test_can_afford_activation_with_no_abilities(self, mock_component):
        """Test can_afford_activation returns True with no abilities."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ability_instances = []
        mgr = ComponentResourceManager(mock_component)

        result = mgr.can_afford_activation()

        assert result is True

    # === try_activate tests ===

    def test_try_activate_returns_true_and_consumes_on_success(self, mock_component, mock_resource_ability):
        """Test try_activate returns True and consumes resources on success."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ability_instances = [mock_resource_ability]
        mock_component.get_abilities = MagicMock(return_value=[mock_resource_ability])
        mgr = ComponentResourceManager(mock_component)

        result = mgr.try_activate()

        assert result is True
        mock_resource_ability.check_and_consume.assert_called_once()

    def test_try_activate_returns_false_and_preserves_on_failure(self, mock_component, mock_resource_ability_depleted):
        """Test try_activate returns False and does not consume resources on failure."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ability_instances = [mock_resource_ability_depleted]
        mock_component.get_abilities = MagicMock(return_value=[mock_resource_ability_depleted])
        mgr = ComponentResourceManager(mock_component)

        result = mgr.try_activate()

        assert result is False
        mock_resource_ability_depleted.check_and_consume.assert_not_called()

    # === consume_activation tests ===

    def test_consume_activation_only_consumes_activation_triggered(self, mock_component, mock_resource_ability):
        """Test consume_activation only consumes activation-triggered resources."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        constant_ability = MagicMock()
        constant_ability.trigger = 'constant'
        constant_ability.check_and_consume = MagicMock()

        mock_component.get_abilities = MagicMock(return_value=[mock_resource_ability, constant_ability])
        mgr = ComponentResourceManager(mock_component)

        mgr.consume_activation()

        mock_resource_ability.check_and_consume.assert_called_once()
        constant_ability.check_and_consume.assert_not_called()

    # === get_resource_cost tests ===

    def test_get_resource_cost_returns_correct_costs_with_multiplier(self, mock_component):
        """Test get_resource_cost returns correct costs with multiplier."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.stats = {'cost_mult': 2.0}
        mock_component.data = {'resource_cost': {'fuel': 10, 'energy': 5}}
        mgr = ComponentResourceManager(mock_component)

        result = mgr.get_resource_cost()

        assert result == {'fuel': 20, 'energy': 10}

    def test_get_resource_cost_evaluates_formulas(self, mock_component):
        """Test get_resource_cost evaluates formula strings correctly."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.stats = {'cost_mult': 1.0}
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mgr = ComponentResourceManager(mock_component)

        result = mgr.get_resource_cost({'ship_class_mass': 1000})

        assert result == {'fuel': 10}

    def test_get_resource_cost_uses_ship_context_fallback(self, mock_component):
        """Test get_resource_cost falls back to ship context when no explicit context."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_ship = MagicMock()
        mock_ship.max_mass_budget = 2000
        mock_component.ship = mock_ship
        mock_component.stats = {'cost_mult': 1.0}
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mgr = ComponentResourceManager(mock_component)

        result = mgr.get_resource_cost()

        assert result == {'fuel': 20}

    def test_get_resource_cost_uses_default_context(self, mock_component):
        """Test get_resource_cost uses default context when no ship."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.ship = None
        mock_component.stats = {'cost_mult': 1.0}
        mock_component.data = {'resource_cost': {'fuel': '=ship_class_mass * 0.01'}}
        mgr = ComponentResourceManager(mock_component)

        result = mgr.get_resource_cost()

        # Default ship_class_mass is 1000
        assert result == {'fuel': 10}

    def test_get_resource_cost_uses_evaluated_resource_cost(self, mock_component):
        """Test get_resource_cost prefers evaluated_resource_cost over data."""
        from game.simulation.components.component_resource_manager import ComponentResourceManager

        mock_component.evaluated_resource_cost = {'fuel': 100}
        mock_component.stats = {'cost_mult': 1.0}
        mgr = ComponentResourceManager(mock_component)

        result = mgr.get_resource_cost()

        assert result == {'fuel': 100}
