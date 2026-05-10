"""
Tests for IRegistryProvider Protocol and implementations.

PROJ-27: Core Foundation - Registry Singleton Refactoring

This test file covers:
- IRegistryProvider Protocol definition and runtime checkability
- DefaultRegistryProvider (singleton-backed implementation)
- TestRegistryProvider (isolated implementation for testing)
- get_default_registry_provider() factory function

TDD Approach: Tests written before implementation.
"""
import pytest
from typing import Dict, Any


# =============================================================================
# Test: IRegistryProvider Protocol Definition
# =============================================================================

class TestIRegistryProviderProtocol:
    """Tests for IRegistryProvider Protocol existence and interface."""

    def test_protocol_exists(self):
        """IRegistryProvider Protocol should exist in game.core.protocols."""
        from game.core.protocols import IRegistryProvider
        assert IRegistryProvider is not None

    def test_protocol_is_runtime_checkable(self):
        """IRegistryProvider should be decorated with @runtime_checkable."""
        from typing import runtime_checkable, Protocol
        from game.core.protocols import IRegistryProvider

        # runtime_checkable protocols can be used with isinstance()
        # We'll verify by creating a simple class that implements the protocol
        class MockProvider:
            def get_components(self) -> Dict[str, Any]:
                return {}
            def get_modifiers(self) -> Dict[str, Any]:
                return {}
            def get_vehicle_classes(self) -> Dict[str, Any]:
                return {}
            def get_resources(self) -> Dict[str, Any]:
                return {}

        # This should work without error if protocol is runtime_checkable
        assert isinstance(MockProvider(), IRegistryProvider)

    def test_protocol_requires_get_components(self):
        """IRegistryProvider should require get_components() method."""
        from game.core.protocols import IRegistryProvider

        # A class missing get_components should not satisfy the protocol
        class IncompleteProvider:
            def get_modifiers(self) -> Dict[str, Any]:
                return {}
            def get_vehicle_classes(self) -> Dict[str, Any]:
                return {}

        assert not isinstance(IncompleteProvider(), IRegistryProvider)

    def test_protocol_requires_get_modifiers(self):
        """IRegistryProvider should require get_modifiers() method."""
        from game.core.protocols import IRegistryProvider

        class IncompleteProvider:
            def get_components(self) -> Dict[str, Any]:
                return {}
            def get_vehicle_classes(self) -> Dict[str, Any]:
                return {}

        assert not isinstance(IncompleteProvider(), IRegistryProvider)

    def test_protocol_requires_get_vehicle_classes(self):
        """IRegistryProvider should require get_vehicle_classes() method."""
        from game.core.protocols import IRegistryProvider

        class IncompleteProvider:
            def get_components(self) -> Dict[str, Any]:
                return {}
            def get_modifiers(self) -> Dict[str, Any]:
                return {}

        assert not isinstance(IncompleteProvider(), IRegistryProvider)


# =============================================================================
# Test: DefaultRegistryProvider Implementation
# =============================================================================

class TestDefaultRegistryProvider:
    """Tests for DefaultRegistryProvider (singleton-backed)."""

    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry state before and after each test."""
        from game.core.registry import RegistryManager, set_default_registry_manager
        set_default_registry_manager(RegistryManager())
        yield
        set_default_registry_manager(RegistryManager())

    def test_class_exists(self):
        """DefaultRegistryProvider class should exist in game.core.registry."""
        from game.core.registry import DefaultRegistryProvider
        assert DefaultRegistryProvider is not None

    def test_implements_protocol(self):
        """DefaultRegistryProvider should implement IRegistryProvider."""
        from game.core.protocols import IRegistryProvider
        from game.core.registry import DefaultRegistryProvider

        provider = DefaultRegistryProvider()
        assert isinstance(provider, IRegistryProvider)

    def test_get_components_returns_default_manager_components(self):
        """get_components() should return the default manager's components dict."""
        from game.core.registry import DefaultRegistryProvider, get_default_registry_manager

        # Add data to default manager
        get_default_registry_manager().components["test_comp"] = {"id": "test_comp"}

        provider = DefaultRegistryProvider()
        result = provider.get_components()

        assert "test_comp" in result
        assert result is get_default_registry_manager().components

    def test_get_modifiers_returns_default_manager_modifiers(self):
        """get_modifiers() should return the default manager's modifiers dict."""
        from game.core.registry import DefaultRegistryProvider, get_default_registry_manager

        get_default_registry_manager().modifiers["test_mod"] = {"id": "test_mod"}

        provider = DefaultRegistryProvider()
        result = provider.get_modifiers()

        assert "test_mod" in result
        assert result is get_default_registry_manager().modifiers

    def test_get_vehicle_classes_returns_default_manager_classes(self):
        """get_vehicle_classes() should return the default manager's vehicle_classes dict."""
        from game.core.registry import DefaultRegistryProvider, get_default_registry_manager

        get_default_registry_manager().vehicle_classes["Cruiser"] = {"name": "Cruiser"}

        provider = DefaultRegistryProvider()
        result = provider.get_vehicle_classes()

        assert "Cruiser" in result
        assert result is get_default_registry_manager().vehicle_classes

    def test_reflects_default_manager_changes(self):
        """Provider should reflect changes to the underlying default manager."""
        from game.core.registry import DefaultRegistryProvider, get_default_registry_manager

        provider = DefaultRegistryProvider()

        # Initially empty
        assert len(provider.get_components()) == 0

        # Add to default manager
        get_default_registry_manager().components["new"] = {"id": "new"}

        # Provider should see the change
        assert "new" in provider.get_components()


# =============================================================================
# Test: TestRegistryProvider Implementation
# =============================================================================

class TestTestRegistryProvider:
    """Tests for TestRegistryProvider (isolated implementation)."""

    def test_class_exists(self):
        """TestRegistryProvider class should exist in game.core.registry."""
        from game.core.registry import TestRegistryProvider
        assert TestRegistryProvider is not None

    def test_implements_protocol(self):
        """TestRegistryProvider should implement IRegistryProvider."""
        from game.core.protocols import IRegistryProvider
        from game.core.registry import TestRegistryProvider

        provider = TestRegistryProvider()
        assert isinstance(provider, IRegistryProvider)

    def test_default_empty_dicts(self):
        """Default constructor should provide empty dicts."""
        from game.core.registry import TestRegistryProvider

        provider = TestRegistryProvider()

        assert provider.get_components() == {}
        assert provider.get_modifiers() == {}
        assert provider.get_vehicle_classes() == {}

    def test_accepts_custom_components(self):
        """Constructor should accept custom components dict."""
        from game.core.registry import TestRegistryProvider

        custom_components = {"comp1": {"id": "comp1"}}
        provider = TestRegistryProvider(components=custom_components)

        assert provider.get_components() == custom_components
        assert "comp1" in provider.get_components()

    def test_accepts_custom_modifiers(self):
        """Constructor should accept custom modifiers dict."""
        from game.core.registry import TestRegistryProvider

        custom_modifiers = {"mod1": {"id": "mod1"}}
        provider = TestRegistryProvider(modifiers=custom_modifiers)

        assert provider.get_modifiers() == custom_modifiers

    def test_accepts_custom_vehicle_classes(self):
        """Constructor should accept custom vehicle_classes dict."""
        from game.core.registry import TestRegistryProvider

        custom_classes = {"Fighter": {"name": "Fighter"}}
        provider = TestRegistryProvider(vehicle_classes=custom_classes)

        assert provider.get_vehicle_classes() == custom_classes

    def test_isolated_from_default_manager(self):
        """TestRegistryProvider should be isolated from the default manager."""
        from game.core.registry import (
            TestRegistryProvider, RegistryManager,
            set_default_registry_manager, get_default_registry_manager,
        )

        # Reset default manager
        set_default_registry_manager(RegistryManager())

        # Add to default manager
        get_default_registry_manager().components["singleton_data"] = {"id": "singleton_data"}

        # Create isolated provider
        provider = TestRegistryProvider()

        # Provider should NOT see default manager data
        assert "singleton_data" not in provider.get_components()

    def test_multiple_providers_independent(self):
        """Multiple TestRegistryProvider instances should be independent."""
        from game.core.registry import TestRegistryProvider

        provider1 = TestRegistryProvider(components={"p1": {"id": "p1"}})
        provider2 = TestRegistryProvider(components={"p2": {"id": "p2"}})

        # Each should only see its own data
        assert "p1" in provider1.get_components()
        assert "p1" not in provider2.get_components()
        assert "p2" in provider2.get_components()
        assert "p2" not in provider1.get_components()

    def test_mutable_dicts_can_be_modified(self):
        """Returned dicts should be mutable for test setup."""
        from game.core.registry import TestRegistryProvider

        provider = TestRegistryProvider()
        provider.get_components()["added"] = {"id": "added"}

        # Should persist
        assert "added" in provider.get_components()


# =============================================================================
# Test: get_default_registry_provider() Factory Function
# =============================================================================

class TestGetDefaultRegistryProvider:
    """Tests for get_default_registry_provider() factory function."""

    def test_function_exists(self):
        """get_default_registry_provider() should exist in game.core.registry."""
        from game.core.registry import get_default_registry_provider
        assert get_default_registry_provider is not None
        assert callable(get_default_registry_provider)

    def test_returns_default_provider(self):
        """Should return a DefaultRegistryProvider instance."""
        from game.core.registry import get_default_registry_provider, DefaultRegistryProvider

        result = get_default_registry_provider()
        assert isinstance(result, DefaultRegistryProvider)

    def test_returns_same_instance(self):
        """Should return the same instance on multiple calls (singleton)."""
        from game.core.registry import get_default_registry_provider

        provider1 = get_default_registry_provider()
        provider2 = get_default_registry_provider()

        assert provider1 is provider2

    def test_implements_protocol(self):
        """Returned provider should implement IRegistryProvider."""
        from game.core.protocols import IRegistryProvider
        from game.core.registry import get_default_registry_provider

        provider = get_default_registry_provider()
        assert isinstance(provider, IRegistryProvider)


# =============================================================================
# Test: get_resources() Method (PROJ-174)
# =============================================================================

class TestGetResourcesMethod:
    """Tests for get_resources() method on provider implementations."""

    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset registry state before and after each test."""
        from game.core.registry import RegistryManager, set_default_registry_manager
        set_default_registry_manager(RegistryManager())
        yield
        set_default_registry_manager(RegistryManager())

    def test_default_provider_get_resources_returns_registry_data(self):
        """DefaultRegistryProvider.get_resources() should return the default manager's resources."""
        from game.core.registry import DefaultRegistryProvider, get_default_registry_manager

        # Add data to default manager resources
        get_default_registry_manager().resources["fuel"] = {"id": "fuel", "max": 100}

        provider = DefaultRegistryProvider()
        result = provider.get_resources()

        assert "fuel" in result
        assert result is get_default_registry_manager().resources

    def test_test_provider_get_resources_returns_custom_data(self):
        """TestRegistryProvider(resources=...).get_resources() should return custom data."""
        from game.core.registry import TestRegistryProvider

        custom_resources = {"foo": "bar", "energy": {"id": "energy"}}
        provider = TestRegistryProvider(resources=custom_resources)

        result = provider.get_resources()

        assert result == custom_resources
        assert result["foo"] == "bar"

    def test_test_provider_get_resources_defaults_to_empty(self):
        """TestRegistryProvider().get_resources() should return empty dict by default."""
        from game.core.registry import TestRegistryProvider

        provider = TestRegistryProvider()
        result = provider.get_resources()

        assert result == {}

    def test_protocol_requires_get_resources(self):
        """IRegistryProvider should require get_resources() method."""
        from game.core.protocols import IRegistryProvider

        # A class missing get_resources should not satisfy the protocol
        class IncompleteProvider:
            def get_components(self) -> Dict[str, Any]:
                return {}
            def get_modifiers(self) -> Dict[str, Any]:
                return {}
            def get_vehicle_classes(self) -> Dict[str, Any]:
                return {}

        assert not isinstance(IncompleteProvider(), IRegistryProvider)
