"""
Tests for PROJ-38 Phase 6 registry DI fixtures.

Tests that the new DI fixtures work correctly:
- session_registries: Session-scoped loaded once
- fresh_registries: Function-scoped with deep copies
- minimal_registries: Empty registries for isolated tests
"""
import pytest
from unittest.mock import Mock, patch


class TestSessionRegistriesFixture:
    """Tests for the session_registries fixture."""

    def test_session_registries_returns_game_registries(self, session_registries):
        """session_registries should return a GameRegistries instance."""
        from game.core.registry import GameRegistries
        assert isinstance(session_registries, GameRegistries)

    def test_session_registries_has_components(self, session_registries):
        """session_registries should have loaded components."""
        assert session_registries.components is not None
        assert isinstance(session_registries.components, dict)
        # Should have actual game components loaded
        assert len(session_registries.components) > 0

    def test_session_registries_has_modifiers(self, session_registries):
        """session_registries should have loaded modifiers."""
        assert session_registries.modifiers is not None
        assert isinstance(session_registries.modifiers, dict)
        assert len(session_registries.modifiers) > 0

    def test_session_registries_has_vehicle_classes(self, session_registries):
        """session_registries should have loaded vehicle classes."""
        assert session_registries.vehicle_classes is not None
        assert isinstance(session_registries.vehicle_classes, dict)
        assert len(session_registries.vehicle_classes) > 0

    def test_session_registries_has_resources(self, session_registries):
        """session_registries should have loaded resources."""
        assert session_registries.resources is not None
        assert isinstance(session_registries.resources, dict)


class TestFreshRegistriesFixture:
    """Tests for the fresh_registries fixture."""

    def test_fresh_registries_returns_game_registries(self, fresh_registries):
        """fresh_registries should return a GameRegistries instance."""
        from game.core.registry import GameRegistries
        assert isinstance(fresh_registries, GameRegistries)

    def test_fresh_registries_has_data(self, fresh_registries):
        """fresh_registries should have all registry data."""
        assert len(fresh_registries.components) > 0
        assert len(fresh_registries.modifiers) > 0
        assert len(fresh_registries.vehicle_classes) > 0

    def test_fresh_registries_are_independent_copies(self, session_registries, fresh_registries):
        """fresh_registries should be independent deep copies."""
        # Add a new key to fresh copy (components may be Component objects, not dicts)
        fresh_registries.components["_test_isolation_marker"] = {"test": True}

        # Session registries should NOT have the modification
        assert "_test_isolation_marker" not in session_registries.components

    def test_fresh_registries_are_per_function(self, fresh_registries):
        """Each call to fresh_registries should provide independent data."""
        # Add a marker to verify isolation
        fresh_registries.components["_isolation_test"] = {"test": True}
        # This test passes if subsequent tests don't see this marker
        # (The fixture is function-scoped, so it gets reset each call)


class TestMinimalRegistriesFixture:
    """Tests for the minimal_registries fixture."""

    def test_minimal_registries_returns_game_registries(self, minimal_registries):
        """minimal_registries should return a GameRegistries instance."""
        from game.core.registry import GameRegistries
        assert isinstance(minimal_registries, GameRegistries)

    def test_minimal_registries_is_empty(self, minimal_registries):
        """minimal_registries should have empty dictionaries."""
        assert minimal_registries.components == {}
        assert minimal_registries.modifiers == {}
        assert minimal_registries.vehicle_classes == {}
        assert minimal_registries.resources == {}

    def test_minimal_registries_allows_custom_data(self, minimal_registries):
        """minimal_registries can be modified for test-specific data."""
        # Add test data
        minimal_registries.components["test_component"] = {"id": "test_component"}

        # Should be present
        assert "test_component" in minimal_registries.components


class TestFixtureIsolation:
    """Tests verifying fixture isolation properties."""

    def test_session_registries_same_instance_in_session(self, request):
        """session_registries should return same instance across tests in same session."""
        # Get the fixture twice
        session_reg_1 = request.getfixturevalue("session_registries")
        session_reg_2 = request.getfixturevalue("session_registries")

        # Should be the exact same object (session-scoped)
        assert session_reg_1 is session_reg_2

    def test_fresh_registries_different_dicts_from_session(self, session_registries, fresh_registries):
        """fresh_registries dicts should be different objects from session_registries."""
        # The dictionaries themselves should be different objects
        assert fresh_registries.components is not session_registries.components
        assert fresh_registries.modifiers is not session_registries.modifiers
        assert fresh_registries.vehicle_classes is not session_registries.vehicle_classes

    def test_fresh_registries_has_same_content_initially(self, session_registries, fresh_registries):
        """fresh_registries should have the same content as session_registries initially."""
        assert set(fresh_registries.components.keys()) == set(session_registries.components.keys())
        assert set(fresh_registries.modifiers.keys()) == set(session_registries.modifiers.keys())
        assert set(fresh_registries.vehicle_classes.keys()) == set(session_registries.vehicle_classes.keys())
