"""
Tests for reload_registries_from_directory() functionality.

PROJ-44 Phase 2: Registry reload function for centralized data loading.
PROJ-90 Phase 2: Extracted to Simulation layer to fix Core -> Simulation violation.

Uses the project's existing reset_game_state fixture from conftest.py for
proper test isolation.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from game.core.registry import (
    get_default_registry_manager,
    get_default_registry_provider,
)
from game.core.exceptions import FrozenStateException
from game.simulation.services.registry_loader import reload_registries_from_directory


@pytest.fixture
def fresh_registry():
    """Get a fresh, cleared registry instance for reload testing.

    Unlike the default setup, this clears all existing data to test
    that reload_registries_from_directory properly populates empty registries.

    PROJ-195: Legitimate — testing reload_registries_from_directory on the
    default registry manager. The reload function is specifically designed
    to operate on the global registry.
    """
    reg = get_default_registry_manager()
    # Clear to test loading into empty registries
    reg.components.clear()
    reg.modifiers.clear()
    reg.vehicle_classes.clear()
    reg.resources.clear()
    return reg


@pytest.fixture
def default_provider():
    """The production registry provider — legal in test code (test layer
    is outside `game/simulation/`, so PROJ-252's prohibition doesn't apply).

    PROJ-306: required by `reload_registries_from_directory` since the
    fallback at line 91 was deleted.
    """
    return get_default_registry_provider()


class TestReloadAllFromDirectory:
    """Tests for reload_registries_from_directory() function."""

    def test_reload_clears_existing_data(self, fresh_registry):
        """reload_registries_from_directory() should clear existing registry data first."""
        # Pre-populate with some data
        fresh_registry.components["old_component"] = {"id": "old_component"}
        fresh_registry.modifiers["old_modifier"] = {"id": "old_modifier"}
        fresh_registry.vehicle_classes["OldClass"] = {"name": "OldClass"}

        # Use test data directory which has known content
        test_dir = Path(os.getcwd()) / "tests" / "unit" / "data"

        result = reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())

        assert result is True
        # Old data should be gone
        assert "old_component" not in fresh_registry.components
        assert "old_modifier" not in fresh_registry.modifiers
        assert "OldClass" not in fresh_registry.vehicle_classes

    def test_reload_loads_components(self, fresh_registry):
        """reload_registries_from_directory() should load components from directory."""
        test_dir = Path(os.getcwd()) / "tests" / "unit" / "data"

        result = reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())

        assert result is True
        # Should have loaded some components (test data has known components)
        assert len(fresh_registry.components) > 0

    def test_reload_loads_modifiers(self, fresh_registry):
        """reload_registries_from_directory() should load modifiers from standard data directory."""
        # Use standard data directory which has modifiers
        data_dir = Path(os.getcwd()) / "data"

        result = reload_registries_from_directory(fresh_registry, data_dir, registry_provider=get_default_registry_provider())

        assert result is True
        # Should have loaded some modifiers
        assert len(fresh_registry.modifiers) > 0

    @pytest.mark.use_custom_data
    def test_reload_loads_vehicle_classes(self, fresh_registry):
        """reload_registries_from_directory() should load vehicle classes from directory.

        Note: Uses use_custom_data marker to bypass the conftest monkeypatch
        that replaces load_vehicle_classes with a no-op. This test needs to
        call the real loader to verify reload_registries_from_directory works.
        """
        # Use standard data directory which has full vehicle classes
        data_dir = Path(os.getcwd()) / "data"

        result = reload_registries_from_directory(fresh_registry, data_dir, registry_provider=get_default_registry_provider())

        assert result is True
        # Should have loaded some vehicle classes
        assert len(fresh_registry.vehicle_classes) > 0

    def test_reload_returns_false_for_invalid_directory(self, fresh_registry):
        """reload_registries_from_directory() should return False for nonexistent directory."""
        invalid_dir = Path("/nonexistent/directory/path")

        result = reload_registries_from_directory(fresh_registry, invalid_dir, registry_provider=get_default_registry_provider())

        assert result is False

    def test_reload_raises_when_frozen(self, fresh_registry):
        """reload_registries_from_directory() should raise FrozenStateException when frozen."""
        fresh_registry.freeze()
        test_dir = Path(os.getcwd()) / "tests" / "unit" / "data"

        try:
            with pytest.raises(FrozenStateException, match="frozen"):
                reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())
        finally:
            # Clean up: unfreeze by resetting (registry fixture will restore)
            fresh_registry.unfreeze()

    def test_reload_accepts_string_path(self, fresh_registry):
        """reload_registries_from_directory() should accept string path as well as Path."""
        test_dir = os.path.join(os.getcwd(), "tests", "unit", "data")

        result = reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())

        assert result is True
        assert len(fresh_registry.components) > 0

    def test_reload_preserves_dict_identity(self, fresh_registry):
        """reload_registries_from_directory() should preserve dict identity (not replace dicts)."""
        components_id = id(fresh_registry.components)
        modifiers_id = id(fresh_registry.modifiers)
        vehicle_classes_id = id(fresh_registry.vehicle_classes)

        test_dir = Path(os.getcwd()) / "tests" / "unit" / "data"
        reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())

        # Same dict objects, just with new content
        assert id(fresh_registry.components) == components_id
        assert id(fresh_registry.modifiers) == modifiers_id
        assert id(fresh_registry.vehicle_classes) == vehicle_classes_id

    def test_reload_handles_missing_files_gracefully(self, fresh_registry, tmp_path):
        """reload_registries_from_directory() should handle missing files gracefully."""
        # Create an empty temp directory
        empty_dir = tmp_path / "empty_data"
        empty_dir.mkdir()

        # Should not raise, just log warnings
        result = reload_registries_from_directory(fresh_registry, empty_dir, registry_provider=get_default_registry_provider())

        # Returns True (directory exists) but registries may be empty
        assert result is True
        # Registries should be empty since no files found
        assert len(fresh_registry.components) == 0

    def test_reload_uses_test_prefix_files(self, fresh_registry):
        """reload_registries_from_directory() should prefer test_ prefixed files in test directories."""
        test_dir = Path(os.getcwd()) / "tests" / "unit" / "data"

        result = reload_registries_from_directory(fresh_registry, test_dir, registry_provider=get_default_registry_provider())

        assert result is True
        # Test data should have been loaded (test_components.json, etc.)
        assert len(fresh_registry.components) > 0


class TestReloadWithCustomFilenames:
    """Tests for reload with custom filename detection."""

    def test_reload_finds_components_json(self, fresh_registry):
        """reload should find components.json file."""
        data_dir = Path(os.getcwd()) / "data"

        result = reload_registries_from_directory(fresh_registry, data_dir, registry_provider=get_default_registry_provider())
        assert result is True
        # Standard data directory should have components
        assert len(fresh_registry.components) > 0

    @pytest.mark.use_custom_data
    def test_reload_finds_vehicleclasses_json(self, fresh_registry):
        """reload should find vehicleclasses.json file.

        Note: Uses use_custom_data marker to bypass the conftest monkeypatch
        that replaces load_vehicle_classes with a no-op.
        """
        data_dir = Path(os.getcwd()) / "data"

        result = reload_registries_from_directory(fresh_registry, data_dir, registry_provider=get_default_registry_provider())
        assert result is True
        # Standard data directory should have vehicle classes
        assert len(fresh_registry.vehicle_classes) > 0
