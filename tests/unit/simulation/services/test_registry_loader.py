"""
Unit tests for registry_loader.py.

Tests the reload_registries_from_directory function which loads
components, modifiers, and vehicle classes from a data directory.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from game.simulation.services.registry_loader import reload_registries_from_directory
from game.core.exceptions import FrozenStateException


class TestReloadRegistriesFromDirectory:
    """Tests for reload_registries_from_directory function."""

    @pytest.fixture
    def mock_registry_manager(self):
        """Create a mock RegistryManager with required attributes."""
        manager = MagicMock()
        manager.components = {}
        manager.modifiers = {}
        manager.vehicle_classes = {}
        manager.resources = {}
        manager._validator = MagicMock()
        manager._check_frozen = MagicMock()
        return manager

    def test_reload_nonexistent_directory_returns_false(self, mock_registry_manager, tmp_path):
        """Non-existent directory returns False."""
        nonexistent = tmp_path / "does_not_exist"

        result = reload_registries_from_directory(mock_registry_manager, nonexistent)

        assert result is False

    def test_reload_clears_all_registries(self, mock_registry_manager, tmp_path):
        """All registries are cleared when reload is called."""
        # Pre-populate registries
        mock_registry_manager.components = {"old": "data"}
        mock_registry_manager.modifiers = {"old": "modifiers"}
        mock_registry_manager.vehicle_classes = {"old": "classes"}
        mock_registry_manager.resources = {"old": "resources"}
        mock_registry_manager._validator = MagicMock()

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True
        assert mock_registry_manager.components == {}
        assert mock_registry_manager.modifiers == {}
        assert mock_registry_manager.vehicle_classes == {}
        assert mock_registry_manager.resources == {}
        assert mock_registry_manager._validator is None

    def test_reload_loads_modifiers_first(self, mock_registry_manager, tmp_path):
        """Modifiers are loaded before components (dependency order)."""
        # Create modifiers file
        (tmp_path / "modifiers.json").write_text("{}")
        (tmp_path / "components.json").write_text("{}")

        call_order = []

        def track_modifiers(path):
            call_order.append("modifiers")

        def track_components(path):
            call_order.append("components")

        with patch('game.simulation.services.registry_loader.load_modifiers', side_effect=track_modifiers):
            with patch('game.simulation.services.registry_loader.load_components', side_effect=track_components):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert call_order.index("modifiers") < call_order.index("components")

    def test_reload_loads_components(self, mock_registry_manager, tmp_path):
        """load_components is called with correct path."""
        comp_file = tmp_path / "components.json"
        comp_file.write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components') as mock_load:
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    reload_registries_from_directory(mock_registry_manager, tmp_path)

        mock_load.assert_called_once_with(str(comp_file))

    def test_reload_loads_vehicle_classes(self, mock_registry_manager, tmp_path):
        """load_vehicle_classes is called when file exists."""
        vclass_file = tmp_path / "vehicleclasses.json"
        vclass_file.write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes') as mock_load:
                    reload_registries_from_directory(mock_registry_manager, tmp_path)

        mock_load.assert_called_once_with(str(vclass_file))

    def test_reload_with_layers_file(self, mock_registry_manager, tmp_path):
        """Passes layers_file_path when vehiclelayers.json exists."""
        vclass_file = tmp_path / "vehicleclasses.json"
        vlayer_file = tmp_path / "vehiclelayers.json"
        vclass_file.write_text("{}")
        vlayer_file.write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes') as mock_load:
                    reload_registries_from_directory(mock_registry_manager, tmp_path)

        mock_load.assert_called_once_with(str(vclass_file), layers_file_path=str(vlayer_file))

    def test_reload_test_prefix_fallback(self, mock_registry_manager, tmp_path):
        """test_components.json is preferred over components.json."""
        # Create both standard and test-prefixed files
        std_file = tmp_path / "components.json"
        test_file = tmp_path / "test_components.json"
        std_file.write_text('{"standard": true}')
        test_file.write_text('{"test": true}')

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components') as mock_load:
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    reload_registries_from_directory(mock_registry_manager, tmp_path)

        # Should use test_ prefixed version
        mock_load.assert_called_once_with(str(test_file))

    def test_reload_missing_modifiers_file_continues(self, mock_registry_manager, tmp_path):
        """No crash if modifiers.json is absent."""
        # Only create components file, no modifiers
        (tmp_path / "components.json").write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers') as mock_mod:
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True
        mock_mod.assert_not_called()  # No modifiers file to load

    def test_reload_missing_components_file_continues(self, mock_registry_manager, tmp_path):
        """No crash if components.json is absent."""
        # Only create modifiers file, no components
        (tmp_path / "modifiers.json").write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components') as mock_comp:
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True
        mock_comp.assert_not_called()  # No components file to load

    def test_reload_returns_true_even_if_some_files_missing(self, mock_registry_manager, tmp_path):
        """Returns True if directory exists, even with no data files."""
        # Empty directory - no json files
        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True

    def test_reload_frozen_registry_raises(self, mock_registry_manager, tmp_path):
        """FrozenStateException is raised when registry is frozen."""
        mock_registry_manager._check_frozen.side_effect = FrozenStateException("Registry is frozen")

        with pytest.raises(FrozenStateException):
            reload_registries_from_directory(mock_registry_manager, tmp_path)

    def test_reload_component_load_error_logged(self, mock_registry_manager, tmp_path, caplog):
        """JSONDecodeError in components is logged, not raised."""
        (tmp_path / "components.json").write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components',
                       side_effect=json.JSONDecodeError("test", "doc", 0)):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True  # Should not crash
        assert "Failed to load components" in caplog.text

    def test_reload_modifier_load_error_logged(self, mock_registry_manager, tmp_path, caplog):
        """TypeError in modifiers is logged, not raised."""
        (tmp_path / "modifiers.json").write_text("{}")

        with patch('game.simulation.services.registry_loader.load_modifiers',
                   side_effect=TypeError("test error")):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True  # Should not crash
        assert "Failed to load modifiers" in caplog.text


class TestReloadRegistriesPathHandling:
    """Tests for path handling in reload_registries_from_directory."""

    @pytest.fixture
    def mock_registry_manager(self):
        """Create a mock RegistryManager."""
        manager = MagicMock()
        manager.components = {}
        manager.modifiers = {}
        manager.vehicle_classes = {}
        manager.resources = {}
        manager._validator = MagicMock()
        manager._check_frozen = MagicMock()
        return manager

    def test_accepts_string_path(self, mock_registry_manager, tmp_path):
        """Accepts string path as data_dir argument."""
        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, str(tmp_path))

        assert result is True

    def test_accepts_path_object(self, mock_registry_manager, tmp_path):
        """Accepts Path object as data_dir argument."""
        with patch('game.simulation.services.registry_loader.load_modifiers'):
            with patch('game.simulation.services.registry_loader.load_components'):
                with patch('game.simulation.services.registry_loader.load_vehicle_classes'):
                    result = reload_registries_from_directory(mock_registry_manager, tmp_path)

        assert result is True

    def test_file_instead_of_directory_returns_false(self, mock_registry_manager, tmp_path):
        """Returns False if path is a file, not a directory."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("content")

        result = reload_registries_from_directory(mock_registry_manager, file_path)

        assert result is False
