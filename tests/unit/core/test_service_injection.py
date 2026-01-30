"""
Tests for service registry injection.

PROJ-27: Core Foundation - Registry Singleton Refactoring
PROJ-42: Updated for instance-only method patterns (removed static calling support)

This test file verifies that key services can accept registries
via constructor for dependency injection, enabling isolated testing.
"""
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock

from game.core.registry import GameRegistries


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
# Test: ShipStatsCalculator Registry Injection
# =============================================================================

class TestShipStatsCalculatorInjection:
    """Tests for ShipStatsCalculator constructor injection.

    PROJ-42: Updated to use instance-only patterns.
    """

    def test_constructor_accepts_registries_parameter(self):
        """ShipStatsCalculator constructor should accept registries parameter."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        import inspect

        # Check constructor signature accepts registries parameter
        sig = inspect.signature(ShipStatsCalculator.__init__)
        param_names = list(sig.parameters.keys())
        assert 'registries' in param_names

    def test_calculate_stats_uses_injected_registries(self):
        """calculate_stats() should use injected registries when provided."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # Create test registries with a custom vehicle class
        test_classes = {
            "TestShip": {"max_mass": 5000, "name": "TestShip"}
        }
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes=test_classes,
            resources={}
        )

        service = ShipStatsCalculator(registries=registries)

        # Call with minimal design data
        design_data = {
            "ship_class": "TestShip",
            "layers": {}
        }

        result = service.calculate_stats(design_data)

        # Should return a dict with stats
        assert isinstance(result, dict)
        assert 'max_hp' in result

    def test_constructor_requires_registries(self):
        """ShipStatsCalculator should require registries (strict DI)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        # PROJ-50: Should raise TypeError when registries is None
        with pytest.raises(TypeError) as exc_info:
            ShipStatsCalculator(registries=None)
        assert "registries is required" in str(exc_info.value)

    def test_calculate_stats_uses_injected_vehicle_class_data(self):
        """Verify calculate_stats actually uses injected registry values."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
        from game.core.registry import RegistryManager

        # Create registries with a unique vehicle class
        unique_max_mass = 99999
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes={
                "UniqueTestClass": {"max_mass": unique_max_mass, "name": "UniqueTestClass"}
            },
            resources={}
        )

        service = ShipStatsCalculator(registries=registries)

        # Ensure singleton does NOT have this class
        assert "UniqueTestClass" not in RegistryManager.instance().vehicle_classes

        design_data = {
            "ship_class": "UniqueTestClass",
            "layers": {},
            "expected_stats": {"max_hp": 0, "mass": 0}
        }

        # Should use our injected registry, not crash
        result = service.calculate_stats(design_data)

        assert isinstance(result, dict)
        assert 'max_hp' in result


# =============================================================================
# Test: ModifierService Registry Injection
# =============================================================================

class TestModifierServiceInjection:
    """Tests for ModifierService constructor injection.

    PROJ-42: Updated to use instance-only patterns.
    """

    def test_constructor_accepts_modifier_registry_parameter(self):
        """ModifierService constructor should accept modifier_registry parameter."""
        from game.simulation.services.modifier_service import ModifierService
        import inspect

        sig = inspect.signature(ModifierService.__init__)
        param_names = list(sig.parameters.keys())
        assert 'modifier_registry' in param_names

    def test_is_modifier_allowed_uses_injected_registry(self):
        """is_modifier_allowed() should use injected registry."""
        from game.simulation.services.modifier_service import ModifierService

        # Create mock modifier definition
        mock_mod = MockModifierDef(
            mod_id="test_mod",
            restrictions=None
        )

        service = ModifierService(modifier_registry={"test_mod": mock_mod})
        component = MockComponent(type_str="TestType")

        result = service.is_modifier_allowed("test_mod", component)
        assert result is True

    def test_is_modifier_allowed_returns_false_for_missing_mod(self):
        """is_modifier_allowed() should return False for modifier not in registry."""
        from game.simulation.services.modifier_service import ModifierService

        service = ModifierService(modifier_registry={})
        component = MockComponent()

        result = service.is_modifier_allowed("nonexistent_mod", component)
        assert result is False

    def test_is_modifier_allowed_uses_injected_not_singleton(self):
        """Verify is_modifier_allowed uses injected registry, not singleton."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import RegistryManager

        # Create a unique modifier that only exists in our injected registry
        unique_mod = MockModifierDef(
            mod_id="unique_injected_mod",
            restrictions=None
        )

        injected_service = ModifierService(modifier_registry={"unique_injected_mod": unique_mod})
        # PROJ-50: Singleton service now also requires registry injection
        singleton_modifiers = RegistryManager.instance().modifiers
        singleton_service = ModifierService(modifier_registry=singleton_modifiers)

        # Verify singleton does NOT have this modifier
        assert "unique_injected_mod" not in RegistryManager.instance().modifiers

        component = MockComponent(type_str="TestType")

        # With injected registry - should find the modifier
        result_with_injection = injected_service.is_modifier_allowed(
            "unique_injected_mod",
            component
        )
        assert result_with_injection is True

        # With singleton registry - should NOT find the modifier
        result_without_injection = singleton_service.is_modifier_allowed(
            "unique_injected_mod",
            component
        )
        assert result_without_injection is False

    def test_get_initial_value_uses_injected_registry(self):
        """Verify get_initial_value uses injected registry."""
        from game.simulation.services.modifier_service import ModifierService
        from game.core.registry import RegistryManager

        unique_default = 77.5
        unique_mod = MockModifierDef(
            mod_id="unique_default_mod",
            restrictions=None,
            default_val=unique_default
        )

        service = ModifierService(modifier_registry={"unique_default_mod": unique_mod})

        # Verify singleton does NOT have this modifier
        assert "unique_default_mod" not in RegistryManager.instance().modifiers

        component = MockComponent(type_str="TestType")

        result = service.get_initial_value("unique_default_mod", component)
        assert result == unique_default

    def test_get_local_min_max_uses_injected_registry(self):
        """Verify get_local_min_max uses injected registry."""
        from game.simulation.services.modifier_service import ModifierService

        unique_mod = MockModifierDef(
            mod_id="bounded_mod",
            restrictions=None,
            min_val=10.0,
            max_val=200.0
        )

        service = ModifierService(modifier_registry={"bounded_mod": unique_mod})
        component = MockComponent(type_str="TestType")

        min_val, max_val = service.get_local_min_max("bounded_mod", component)
        assert min_val == 10.0
        assert max_val == 200.0


# =============================================================================
# Test: VehicleDesignService Registry Injection
# =============================================================================

class TestVehicleDesignServiceInjection:
    """Tests for VehicleDesignService registry injection.

    PROJ-42: Updated to use GameRegistries instead of IRegistryProvider.
    """

    def test_constructor_accepts_registries_parameter(self):
        """VehicleDesignService constructor should accept optional registries."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService
        import inspect

        sig = inspect.signature(VehicleDesignService.__init__)
        param_names = list(sig.parameters.keys())
        assert 'registries' in param_names

    def test_create_ship_uses_injected_registries(self):
        """create_ship() should use injected registries for class validation."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService

        # Create test registries with custom vehicle class
        test_classes = {
            "CustomClass": {"max_mass": 1000, "name": "CustomClass"}
        }
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes=test_classes,
            resources={}
        )

        service = VehicleDesignService(registries=registries)

        # Should recognize our custom class without warning
        result = service.create_ship(
            name="TestShip",
            ship_class="CustomClass"
        )

        # Check no "Unknown ship class" warning
        unknown_warnings = [w for w in result.warnings if "Unknown ship class" in w]
        assert len(unknown_warnings) == 0

    def test_create_ship_warns_for_unknown_class(self):
        """create_ship() should warn for class not in injected registries."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService

        # Empty registries
        registries = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes={},
            resources={}
        )

        service = VehicleDesignService(registries=registries)

        result = service.create_ship(
            name="TestShip",
            ship_class="NonexistentClass"
        )

        # Should have warning about unknown class
        unknown_warnings = [w for w in result.warnings if "Unknown ship class" in w]
        assert len(unknown_warnings) > 0

    def test_constructor_without_registries_raises_type_error(self):
        """PROJ-50: VehicleDesignService() without registries should raise TypeError."""
        from game.simulation.services.vehicle_design_service import VehicleDesignService

        # Python raises TypeError for missing required keyword-only argument
        with pytest.raises(TypeError, match="registries"):
            VehicleDesignService()


# =============================================================================
# Test: Integration - Services Work with Injected Registries
# =============================================================================

class TestServiceIntegration:
    """Integration tests verifying services work with injected registries."""

    def test_isolated_service_testing(self):
        """Demonstrate isolated testing without singleton pollution."""
        from game.core.registry import RegistryManager

        # Create completely isolated registries
        isolated_registries = GameRegistries(
            components={"isolated_comp": {"id": "isolated_comp", "mass": 100}},
            modifiers={},
            vehicle_classes={"IsolatedClass": {"max_mass": 2000}},
            resources={}
        )

        # The singleton should NOT contain our isolated data
        singleton_components = RegistryManager.instance().components
        assert "isolated_comp" not in singleton_components

        # Our registries should have the isolated data
        assert "isolated_comp" in isolated_registries.components
