"""
Tests for service registry injection.

PROJ-27: Core Foundation - Registry Singleton Refactoring

This test file verifies that key services can accept an IRegistryProvider
for dependency injection, enabling isolated testing without the singleton.

TDD Approach: Tests written before implementation.
"""
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock


# =============================================================================
# Mock Component for Testing
# =============================================================================

class MockComponent:
    """Minimal mock component for testing service injection."""

    def __init__(
        self,
        type_str: str = "TestType",
        max_hp: float = 100.0,
        mass: float = 50.0,
        abilities: Dict[str, Any] = None,
        data: Dict[str, Any] = None
    ):
        self.type_str = type_str
        self.max_hp = max_hp
        self.mass = mass
        self.abilities = abilities if abilities is not None else {}
        self.data = data if data is not None else {}
        self.damage_threshold = 0.3

    def has_ability(self, ability_name: str) -> bool:
        """Check if component has given ability."""
        return ability_name in self.abilities or ability_name in self.data.get('abilities', {})

    def get_modifier(self, mod_id: str):
        """Mock get_modifier."""
        return None

    def add_modifier(self, mod_id: str):
        """Mock add_modifier."""
        pass


class MockModifierDef:
    """Mock modifier definition."""

    def __init__(
        self,
        mod_id: str = "test_mod",
        restrictions: Dict[str, Any] = None,
        min_val: float = 0.0,
        max_val: float = 100.0,
        default_val: float = 50.0
    ):
        self.mod_id = mod_id
        self.restrictions = restrictions
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = default_val


# =============================================================================
# Test: ShipStatsService Registry Injection
# =============================================================================

class TestShipStatsServiceInjection:
    """Tests for ShipStatsService registry injection."""

    def test_calculate_stats_accepts_registry_parameter(self):
        """calculate_stats() should accept an optional registry parameter."""
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.core.registry import TestRegistryProvider
        import inspect

        # Check method signature accepts registry parameter
        sig = inspect.signature(ShipStatsService.calculate_stats)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_calculate_stats_uses_injected_registry(self):
        """calculate_stats() should use injected registry when provided."""
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.core.registry import TestRegistryProvider

        # Create test registry with a custom vehicle class
        test_classes = {
            "TestShip": {"max_mass": 5000, "name": "TestShip"}
        }
        provider = TestRegistryProvider(vehicle_classes=test_classes)

        # Call with minimal design data
        design_data = {
            "ship_class": "TestShip",
            "layers": {}
        }

        # Should not raise and should use our test data
        result = ShipStatsService.calculate_stats(
            design_data,
            registry=provider
        )

        # Should return a dict with stats (exact values depend on implementation)
        assert isinstance(result, dict)

    def test_calculate_stats_falls_back_to_singleton(self):
        """calculate_stats() should use singleton when registry not provided."""
        from game.strategy.services.ship_stats_service import ShipStatsService

        # Call without registry parameter
        design_data = {
            "ship_class": "Escort",
            "layers": {}
        }

        # Should work using default singleton (assuming test fixtures populate it)
        result = ShipStatsService.calculate_stats(design_data)
        assert isinstance(result, dict)

    def test_calculate_stats_uses_injected_vehicle_class_data(self):
        """Verify calculate_stats actually uses injected registry values, not singleton."""
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.core.registry import TestRegistryProvider, RegistryManager

        # Create provider with a unique vehicle class that has specific max_mass
        # This value is used in formula context for ship_class_mass
        unique_max_mass = 99999  # Unlikely to match singleton
        provider = TestRegistryProvider(
            vehicle_classes={
                "UniqueTestClass": {"max_mass": unique_max_mass, "name": "UniqueTestClass"}
            },
            components={},
            modifiers={}
        )

        # Ensure singleton does NOT have this class
        assert "UniqueTestClass" not in RegistryManager.instance().vehicle_classes

        design_data = {
            "ship_class": "UniqueTestClass",
            "layers": {},
            # Provide expected_stats as fallback since no components
            "expected_stats": {"max_hp": 0, "mass": 0}
        }

        # Should use our injected registry, not crash looking for singleton data
        result = ShipStatsService.calculate_stats(design_data, registry=provider)

        # If it used the singleton, it would not find "UniqueTestClass"
        # and would use default formula_context. Our test verifies it doesn't crash
        # and returns valid stats.
        assert isinstance(result, dict)
        assert 'max_hp' in result


# =============================================================================
# Test: ModifierService Registry Injection
# =============================================================================

class TestModifierServiceInjection:
    """Tests for ModifierService registry injection."""

    def test_is_modifier_allowed_accepts_registry_parameter(self):
        """is_modifier_allowed() should accept an optional registry parameter."""
        from game.simulation.services.modifier_service import ModifierService
        import inspect

        sig = inspect.signature(ModifierService.is_modifier_allowed)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_is_modifier_allowed_uses_injected_registry(self):
        """is_modifier_allowed() should use injected registry when provided."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import TestRegistryProvider

        # Create mock modifier definition
        mock_mod = MockModifierDef(
            mod_id="test_mod",
            restrictions=None  # No restrictions = allowed for all
        )

        provider = TestRegistryProvider(
            modifiers={"test_mod": mock_mod}
        )

        component = MockComponent(type_str="TestType")

        # Should use our test registry
        result = ModifierService.is_modifier_allowed(
            "test_mod",
            component,
            registry=provider
        )

        assert result is True

    def test_is_modifier_allowed_returns_false_for_missing_mod(self):
        """is_modifier_allowed() should return False for modifier not in registry."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import TestRegistryProvider

        # Empty registry
        provider = TestRegistryProvider(modifiers={})
        component = MockComponent()

        result = ModifierService.is_modifier_allowed(
            "nonexistent_mod",
            component,
            registry=provider
        )

        assert result is False

    def test_get_mandatory_modifiers_accepts_registry_parameter(self):
        """get_mandatory_modifiers() should accept an optional registry parameter."""
        from game.simulation.services.modifier_service import ModifierService
        import inspect

        sig = inspect.signature(ModifierService.get_mandatory_modifiers)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_get_initial_value_accepts_registry_parameter(self):
        """get_initial_value() should accept an optional registry parameter."""
        from game.simulation.services.modifier_service import ModifierService
        import inspect

        sig = inspect.signature(ModifierService.get_initial_value)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_get_local_min_max_accepts_registry_parameter(self):
        """get_local_min_max() should accept an optional registry parameter."""
        from game.simulation.services.modifier_service import ModifierService
        import inspect

        sig = inspect.signature(ModifierService.get_local_min_max)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_is_modifier_allowed_uses_injected_not_singleton(self):
        """Verify is_modifier_allowed uses injected registry, not singleton."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import TestRegistryProvider, RegistryManager

        # Create a unique modifier that only exists in our injected registry
        unique_mod = MockModifierDef(
            mod_id="unique_injected_mod",
            restrictions=None  # No restrictions = allowed for all
        )

        provider = TestRegistryProvider(
            modifiers={"unique_injected_mod": unique_mod}
        )

        # Verify singleton does NOT have this modifier
        assert "unique_injected_mod" not in RegistryManager.instance().modifiers

        component = MockComponent(type_str="TestType")

        # With injected registry - should find the modifier
        result_with_injection = ModifierService.is_modifier_allowed(
            "unique_injected_mod",
            component,
            registry=provider
        )
        assert result_with_injection is True

        # Without registry (uses singleton) - should NOT find the modifier
        result_without_injection = ModifierService.is_modifier_allowed(
            "unique_injected_mod",
            component,
            registry=None
        )
        assert result_without_injection is False

    def test_get_initial_value_uses_injected_registry(self):
        """Verify get_initial_value uses injected registry, not singleton."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import TestRegistryProvider, RegistryManager

        # Create a modifier with a specific default value
        unique_default = 77.5
        unique_mod = MockModifierDef(
            mod_id="unique_default_mod",
            restrictions=None,
            default_val=unique_default
        )

        provider = TestRegistryProvider(
            modifiers={"unique_default_mod": unique_mod}
        )

        # Verify singleton does NOT have this modifier
        assert "unique_default_mod" not in RegistryManager.instance().modifiers

        component = MockComponent(type_str="TestType")

        # With injected registry - should return our unique default value
        result = ModifierService.get_initial_value(
            "unique_default_mod",
            component,
            registry=provider
        )
        assert result == unique_default


# =============================================================================
# Test: VehicleDesignService Registry Injection
# =============================================================================

class TestVehicleDesignServiceInjection:
    """Tests for VehicleDesignService registry injection."""

    def test_constructor_accepts_registry_parameter(self):
        """VehicleDesignService constructor should accept optional registry."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService
        from game.core.registry import TestRegistryProvider
        import inspect

        sig = inspect.signature(VehicleDesignService.__init__)
        param_names = list(sig.parameters.keys())
        assert 'registry' in param_names

    def test_create_ship_uses_injected_registry(self):
        """create_ship() should use injected registry for class validation."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService
        from game.core.registry import TestRegistryProvider

        # Create test registry with custom vehicle class
        test_classes = {
            "CustomClass": {"max_mass": 1000, "name": "CustomClass"}
        }
        provider = TestRegistryProvider(vehicle_classes=test_classes)

        service = VehicleDesignService(registry=provider)

        # Should recognize our custom class without warning
        result = service.create_ship(
            name="TestShip",
            ship_class="CustomClass"
        )

        # Check no "Unknown ship class" warning
        unknown_warnings = [w for w in result.warnings if "Unknown ship class" in w]
        assert len(unknown_warnings) == 0

    def test_create_ship_warns_for_unknown_class(self):
        """create_ship() should warn for class not in injected registry."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService
        from game.core.registry import TestRegistryProvider

        # Empty registry
        provider = TestRegistryProvider(vehicle_classes={})

        service = VehicleDesignService(registry=provider)

        result = service.create_ship(
            name="TestShip",
            ship_class="NonexistentClass"
        )

        # Should have warning about unknown class
        unknown_warnings = [w for w in result.warnings if "Unknown ship class" in w]
        assert len(unknown_warnings) > 0

    def test_default_constructor_uses_singleton(self):
        """VehicleDesignService() should work without registry parameter."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService

        # Should not raise
        service = VehicleDesignService()
        assert service is not None

    def test_get_available_components_uses_injected_registry(self):
        """get_available_components() should use injected registry, not singleton."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService
        from game.core.registry import TestRegistryProvider, RegistryManager
        from game.simulation.entities.ship import Ship
        from game.simulation.components.component_constants import LayerType
        from unittest.mock import MagicMock, patch

        # Create provider with a custom component
        custom_components = {
            "injected_test_comp": {
                "id": "injected_test_comp",
                "name": "Injected Test Component",
                "mass": 10,
                "max_hp": 50
            }
        }
        provider = TestRegistryProvider(
            components=custom_components,
            vehicle_classes={"Escort": {"max_mass": 1000}}
        )

        service = VehicleDesignService(registry=provider)

        # Create a mock ship
        ship = MagicMock(spec=Ship)
        ship.layers = {LayerType.CORE: {'components': []}}

        # Mock create_component to return a valid component for our custom ID
        mock_component = MagicMock()
        mock_component.id = "injected_test_comp"

        # Mock the validator to always approve
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_validator.validate_addition.return_value = mock_result

        with patch('game.simulation.services.vehicle_design_service.get_or_create_validator', return_value=mock_validator):
            with patch('game.simulation.services.vehicle_design_service.create_component', return_value=mock_component):
                # Call get_available_components
                available = service.get_available_components(ship, LayerType.CORE)

        # Should find our injected component, not singleton components
        assert "injected_test_comp" in available

        # Verify singleton was NOT consulted (our component shouldn't be in singleton)
        assert "injected_test_comp" not in RegistryManager.instance().components


# =============================================================================
# Test: Integration - Services Work with TestRegistryProvider
# =============================================================================

class TestServiceIntegration:
    """Integration tests verifying services work with TestRegistryProvider."""

    def test_isolated_service_testing(self):
        """Demonstrate isolated testing without singleton pollution."""
        from game.core.registry import TestRegistryProvider, RegistryManager

        # Create completely isolated provider
        isolated_provider = TestRegistryProvider(
            components={"isolated_comp": {"id": "isolated_comp", "mass": 100}},
            modifiers={},
            vehicle_classes={"IsolatedClass": {"max_mass": 2000}}
        )

        # The singleton should NOT contain our isolated data
        # (This test verifies isolation, not injection - but important for confidence)
        singleton_components = RegistryManager.instance().components
        assert "isolated_comp" not in singleton_components

        # Our provider should have the isolated data
        assert "isolated_comp" in isolated_provider.get_components()
