"""
Tests for PROJ-38 Phase 6 registry deprecation warnings.

Tests that the legacy accessor functions emit DeprecationWarnings
to encourage migration to GameRegistries DI pattern.
"""
import pytest
import warnings


class TestAccessorDeprecationWarnings:
    """Tests that legacy accessor functions emit deprecation warnings."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we catch deprecation warnings."""
        # Store original warning filters
        original_filters = warnings.filters.copy()
        yield
        # Restore original filters
        warnings.filters = original_filters

    def test_get_component_registry_warns(self):
        """get_component_registry() should emit DeprecationWarning."""
        from game.core.registry import get_component_registry

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_component_registry()

            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)
            assert any("deprecated" in str(warning.message).lower() for warning in w)

    def test_get_modifier_registry_warns(self):
        """get_modifier_registry() should emit DeprecationWarning."""
        from game.core.registry import get_modifier_registry

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_modifier_registry()

            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)

    def test_get_vehicle_classes_warns(self):
        """get_vehicle_classes() should emit DeprecationWarning."""
        from game.core.registry import get_vehicle_classes

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_vehicle_classes()

            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)

    def test_get_resource_registry_warns(self):
        """get_resource_registry() should emit DeprecationWarning."""
        from game.core.registry import get_resource_registry

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_resource_registry()

            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)

    def test_get_validator_warns(self):
        """get_validator() should emit DeprecationWarning."""
        from game.core.registry import get_validator

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_validator()

            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)


class TestDeprecationWarningContent:
    """Tests for the content of deprecation warnings."""

    def test_warning_mentions_game_registries(self):
        """Deprecation warning should mention GameRegistries as alternative."""
        from game.core.registry import get_component_registry

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = get_component_registry()

            # Find the deprecation warning
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1

            # Check that it mentions the alternative
            warning_text = str(deprecation_warnings[0].message)
            assert "GameRegistries" in warning_text
