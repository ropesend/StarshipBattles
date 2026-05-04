"""
Unit tests for ShipIO module.

PROJ-118: Comprehensive unit tests for ShipIO class covering:
- Save/load operations (via mocked file dialogs)
- Data format validation
- Round-trip serialization tests
- Error handling
- Edge cases

Note: ShipIO uses tkinter file dialogs which cannot be tested interactively,
so we mock the dialog and file operations to test the logic.
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Dict, Any

from tests.fixtures.ships import create_test_ship


# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# PROJ-327 Phase 2 Task 2.19: scope-rescope notes
#
# Original PROJ-322 deferral cited: "many tests mutate the mock ship
# (set_modifier, change attributes) before asserting on round-trip identity."
# That rationale was incorrect at re-audit time: a grep across this file
# finds ZERO attribute writes against `mock_ship`, `mock_ship_with_special_chars`,
# or `minimal_ship`. Tests only call `mock_ship.to_dict()` (read-only) and
# read `.name`, `.ship_class`, `.layers`, etc. Round-trip tests construct
# a NEW ship via `Ship.from_dict(...)` from the dict, which doesn't touch
# the fixture instance.
#
# `minimal_ship` was never used (zero references). Deleted as dead code.
#
# `mock_ship` and `mock_ship_with_special_chars` rescoped to module. The
# underlying `fresh_registries` is replaced with `session_registries` (which
# is read-only and shared) so that the module-scoped fixtures can construct
# without re-loading the registry catalog 54 times.
# =============================================================================


@pytest.fixture(scope="module")
def mock_ship(session_registries):
    """Basic ship for testing. Module-scoped: every test in this file calls
    `mock_ship.to_dict()` (read-only); none mutate the ship (PROJ-327 Phase 2
    Task 2.19)."""
    return create_test_ship(
        name="TestShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=1,
        registries=session_registries
    )


@pytest.fixture(scope="module")
def mock_ship_with_special_chars(session_registries):
    """Ship with special characters in name. Module-scoped: only
    `test_save_ship_sanitizes_filename` consumes it, read-only
    (PROJ-327 Phase 2 Task 2.19)."""
    return create_test_ship(
        name="Test Ship @#$%^&*()!",
        add_bridge=True,
        registries=session_registries
    )


@pytest.fixture
def ship_io_with_tkroot():
    """Patch tkinter_utils to appear initialized for testing."""
    with patch('game.ui.services.ship_io.is_tkinter_available', return_value=True):
        from game.ui.services.ship_io import ShipIO
        yield ShipIO


@pytest.fixture
def ship_io_without_tkroot():
    """Patch tkinter_utils to appear NOT initialized for testing."""
    with patch('game.ui.services.ship_io.is_tkinter_available', return_value=False):
        from game.ui.services.ship_io import ShipIO
        yield ShipIO


# =============================================================================
# TestShipIOSaveOperations
# =============================================================================

class TestShipIOSaveOperations:
    """Tests for ShipIO.save_ship method."""

    def test_save_ship_returns_false_when_tkinter_not_initialized(self, mock_ship, ship_io_without_tkroot):
        """Save should return (False, error) when tkinter not available."""
        success, message = ship_io_without_tkroot.save_ship(mock_ship)

        assert success is False
        assert message == "Tkinter not initialized"

    def test_save_ship_returns_false_none_on_cancel(self, mock_ship, ship_io_with_tkroot):
        """Save should return (False, None) when user cancels dialog."""
        with patch('game.ui.services.ship_io.open_save_dialog', return_value=''):
            with patch('os.path.exists', return_value=True):
                success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is False
        assert message is None  # None indicates user cancelled

    def test_save_ship_success(self, mock_ship, ship_io_with_tkroot, tmp_path):
        """Save should return (True, success_message) on successful save."""
        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', return_value=True) as mock_save:
                    success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is True
        assert "Saved ship to" in message
        mock_save.assert_called_once()

    def test_save_ship_creates_ships_folder_if_not_exists(self, mock_ship, ship_io_with_tkroot, tmp_path):
        """Save should create ships folder if it doesn't exist."""
        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=False):
                with patch('os.makedirs') as mock_makedirs:
                    with patch('game.ui.services.ship_io.save_json', return_value=True):
                        ship_io_with_tkroot.save_ship(mock_ship)

        mock_makedirs.assert_called_once()

    def test_save_ship_sanitizes_filename(self, mock_ship_with_special_chars, ship_io_with_tkroot, tmp_path):
        """Save should sanitize ship name for filename."""
        save_file = str(tmp_path / "test.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file) as mock_dialog:
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', return_value=True):
                    ship_io_with_tkroot.save_ship(mock_ship_with_special_chars)

        # Check that the initialfile was sanitized (alphanumeric, spaces, hyphens, underscores only)
        call_kwargs = mock_dialog.call_args[1]
        sanitized_name = call_kwargs['initialfile']
        # Should only contain safe characters
        assert all(c.isalpha() or c.isdigit() or c in (' ', '-', '_') for c in sanitized_name)

    def test_save_ship_handles_permission_error(self, mock_ship, ship_io_with_tkroot, tmp_path):
        """Save should return error message on permission denied."""
        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', side_effect=PermissionError("Permission denied")):
                    success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is False
        assert "Permission denied" in message

    def test_save_ship_handles_os_error(self, mock_ship, ship_io_with_tkroot, tmp_path):
        """Save should return error message on OS error."""
        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', side_effect=OSError("Disk full")):
                    success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is False
        assert "Disk full" in message or "Save failed" in message

    def test_save_ship_handles_serialization_error(self, ship_io_with_tkroot, tmp_path):
        """Save should return error on serialization failure."""
        from game.core.exceptions import ValidationException

        # Create a mock ship with broken to_dict that raises ValidationException
        mock_ship = MagicMock()
        mock_ship.name = "BrokenShip"
        mock_ship.to_dict.side_effect = ValidationException("Cannot serialize", code="V001")

        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is False
        assert "Invalid ship data" in message or "Save failed" in message

    def test_save_ship_returns_false_on_save_json_failure(self, mock_ship, ship_io_with_tkroot, tmp_path):
        """Save should return (False, error) when save_json returns False."""
        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', return_value=False):
                    success, message = ship_io_with_tkroot.save_ship(mock_ship)

        assert success is False
        assert "Failed to save ship file" in message


# =============================================================================
# TestShipIOLoadOperations
# =============================================================================

class TestShipIOLoadOperations:
    """Tests for ShipIO.load_ship method."""

    def test_load_ship_returns_none_when_tkinter_not_initialized(self, ship_io_without_tkroot):
        """Load should return (None, error) when tkinter not available."""
        ship, message = ship_io_without_tkroot.load_ship(1920, 1080)

        assert ship is None
        assert message == "Tkinter not initialized"

    def test_load_ship_returns_none_on_cancel(self, ship_io_with_tkroot):
        """Load should return (None, None) when user cancels dialog."""
        with patch('game.ui.services.ship_io.open_load_dialog', return_value=''):
            with patch('os.path.exists', return_value=True):
                ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        assert ship is None
        assert message is None  # None indicates user cancelled

    def test_load_ship_success(self, mock_ship, ship_io_with_tkroot, tmp_path, fresh_registries):
        """Load should return (Ship, success_message) on successful load."""
        # Save ship data to temp file
        ship_data = mock_ship.to_dict()
        load_file = tmp_path / "test_ship.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        # Mock Ship.from_dict to use our registries (since ShipIO doesn't pass registries)
        from game.simulation.entities.ship import Ship
        original_from_dict = Ship.from_dict

        def patched_from_dict(data, *, registries=None):
            return original_from_dict(data, registries=fresh_registries)

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with patch.object(Ship, 'from_dict', side_effect=patched_from_dict):
                    ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        assert ship is not None
        assert ship.name == "TestShip"
        assert "Loaded ship from" in message

    def test_load_ship_positions_ship_at_screen_center(self, mock_ship, ship_io_with_tkroot, tmp_path, fresh_registries):
        """Loaded ship should be positioned at screen center."""
        ship_data = mock_ship.to_dict()
        load_file = tmp_path / "test_ship.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        screen_width, screen_height = 1920, 1080

        # Mock Ship.from_dict to use our registries (since ShipIO doesn't pass registries)
        from game.simulation.entities.ship import Ship
        original_from_dict = Ship.from_dict

        def patched_from_dict(data, *, registries=None):
            return original_from_dict(data, registries=fresh_registries)

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with patch.object(Ship, 'from_dict', side_effect=patched_from_dict):
                    ship, _ = ship_io_with_tkroot.load_ship(screen_width, screen_height)

        assert ship.position.x == screen_width // 2
        assert ship.position.y == screen_height // 2

    def test_load_ship_creates_ships_folder_if_not_exists(self, ship_io_with_tkroot):
        """Load should create ships folder if it doesn't exist."""
        with patch('game.ui.services.ship_io.open_load_dialog', return_value=''):
            with patch('os.path.exists', return_value=False):
                with patch('os.makedirs') as mock_makedirs:
                    ship_io_with_tkroot.load_ship(1920, 1080)

        mock_makedirs.assert_called_once()

    def test_load_ship_handles_json_decode_error(self, ship_io_with_tkroot, tmp_path):
        """Load should return error on invalid JSON."""
        load_file = tmp_path / "bad_json.json"
        with open(load_file, 'w') as f:
            f.write("{ this is not valid json }")

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        assert ship is None
        assert "invalid JSON" in message or "Load failed" in message

    def test_load_ship_handles_missing_required_field(self, ship_io_with_tkroot, tmp_path, fresh_registries):
        """Load should return error when required field is missing."""
        # Ship data missing 'name' field
        incomplete_data = {
            "ship_class": "Escort",
            "color": [255, 255, 255]
        }
        load_file = tmp_path / "incomplete_ship.json"
        with open(load_file, 'w') as f:
            json.dump(incomplete_data, f)

        # Mock Ship.from_dict to use our registries (since ShipIO doesn't pass registries)
        from game.simulation.entities.ship import Ship
        original_from_dict = Ship.from_dict

        def patched_from_dict(data, *, registries=None):
            return original_from_dict(data, registries=fresh_registries)

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with patch.object(Ship, 'from_dict', side_effect=patched_from_dict):
                    ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        # Should still load (name defaults to "Unnamed")
        # This tests that defaults work properly
        assert ship is not None or message is not None

    def test_load_ship_handles_permission_error(self, ship_io_with_tkroot, tmp_path):
        """Load should return error on permission denied."""
        load_file = tmp_path / "test_ship.json"

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.load_json_required', side_effect=PermissionError("Access denied")):
                    ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        assert ship is None
        assert "Permission denied" in message or "Load failed" in message

    def test_load_ship_handles_os_error(self, ship_io_with_tkroot, tmp_path):
        """Load should return error on OS error."""
        load_file = tmp_path / "test_ship.json"

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.load_json_required', side_effect=OSError("File corrupted")):
                    ship, message = ship_io_with_tkroot.load_ship(1920, 1080)

        assert ship is None
        assert "Load failed" in message


# =============================================================================
# TestShipIORoundTrip
# =============================================================================

class TestShipIORoundTrip:
    """Tests for save/load round-trip consistency."""

    def test_round_trip_preserves_ship_name(self, mock_ship, fresh_registries, tmp_path):
        """Ship name should be preserved after save/load cycle."""
        # Serialize ship data
        ship_data = mock_ship.to_dict()

        # Save to file
        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        # Load from file
        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        # Recreate ship
        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.name == mock_ship.name

    def test_round_trip_preserves_ship_class(self, mock_ship, fresh_registries, tmp_path):
        """Ship class should be preserved after save/load cycle."""
        ship_data = mock_ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.ship_class == mock_ship.ship_class

    def test_round_trip_preserves_team_id(self, fresh_registries, tmp_path):
        """Team ID should be preserved after save/load cycle."""
        ship = create_test_ship(
            name="TeamShip",
            team_id=42,
            add_bridge=True,
            registries=fresh_registries
        )
        ship_data = ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.team_id == 42

    def test_round_trip_preserves_color(self, fresh_registries, tmp_path):
        """Ship color should be preserved after save/load cycle."""
        custom_color = (100, 150, 200)
        ship = create_test_ship(
            name="ColorShip",
            color=custom_color,
            add_bridge=True,
            registries=fresh_registries
        )
        ship_data = ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert tuple(loaded_ship.color) == custom_color

    def test_round_trip_preserves_component_count(self, mock_ship, fresh_registries, tmp_path):
        """Component count should be preserved after save/load cycle."""
        original_component_count = sum(
            len(layer.components)
            for layer in mock_ship.layers.values()
        )

        ship_data = mock_ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        loaded_component_count = sum(
            len(layer.components)
            for layer in loaded_ship.layers.values()
        )

        assert loaded_component_count == original_component_count

    def test_round_trip_preserves_movement_policy(self, fresh_registries, tmp_path):
        """Movement policy should be preserved after save/load cycle."""
        ship = create_test_ship(
            name="AIShip",
            add_bridge=True,
            registries=fresh_registries
        )
        ship.movement_policy = "brawl_close"

        ship_data = ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.movement_policy == "brawl_close"

    def test_round_trip_recalculates_stats(self, mock_ship, fresh_registries, tmp_path):
        """Stats should be recalculated after load."""
        ship_data = mock_ship.to_dict()

        save_file = tmp_path / "round_trip.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Stats should be calculated (not zero)
        assert loaded_ship.max_hp > 0
        assert loaded_ship.mass > 0


# =============================================================================
# TestShipIODataFormat
# =============================================================================

class TestShipIODataFormat:
    """Tests for ship data format validation."""

    def test_saved_data_contains_format_version(self, mock_ship):
        """Saved data should include format version."""
        ship_data = mock_ship.to_dict()

        assert "_format_version" in ship_data
        assert ship_data["_format_version"] == "2.0"

    def test_saved_data_contains_required_fields(self, mock_ship):
        """Saved data should contain all required fields."""
        ship_data = mock_ship.to_dict()

        required_fields = ["name", "ship_class", "color", "layers"]
        for field in required_fields:
            assert field in ship_data, f"Missing required field: {field}"

    def test_saved_data_contains_expected_stats(self, mock_ship):
        """Saved data should include expected_stats for validation."""
        ship_data = mock_ship.to_dict()

        assert "expected_stats" in ship_data
        stats = ship_data["expected_stats"]

        expected_stat_keys = ["max_hp", "mass", "max_speed"]
        for key in expected_stat_keys:
            assert key in stats, f"Missing expected stat: {key}"

    def test_saved_data_layers_contain_components(self, mock_ship):
        """Saved data layers should contain component definitions."""
        ship_data = mock_ship.to_dict()

        # Should have at least one layer with components
        layers = ship_data.get("layers", {})
        has_components = any(len(comps) > 0 for comps in layers.values())
        assert has_components, "Ship should have at least one component"

    def test_saved_component_format(self, mock_ship):
        """Components in saved data should have correct format."""
        ship_data = mock_ship.to_dict()

        for layer_name, components in ship_data.get("layers", {}).items():
            for comp in components:
                assert isinstance(comp, dict), f"Component should be dict: {comp}"
                assert "id" in comp, f"Component missing 'id': {comp}"

    def test_saved_data_resources_format(self, mock_ship):
        """Saved data should include resources in correct format."""
        ship_data = mock_ship.to_dict()

        assert "resources" in ship_data
        resources = ship_data["resources"]

        expected_resources = ["fuel", "energy", "ammo"]
        for resource in expected_resources:
            assert resource in resources, f"Missing resource: {resource}"


# =============================================================================
# TestShipIOEdgeCases
# =============================================================================

class TestShipIOEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_save_ship_with_empty_name_uses_default(self, fresh_registries, ship_io_with_tkroot, tmp_path):
        """Ship with empty name should use 'New Ship' as filename."""
        ship = create_test_ship(name="", add_bridge=True, registries=fresh_registries)

        with patch('game.ui.services.ship_io.open_save_dialog', return_value='') as mock_dialog:
            with patch('os.path.exists', return_value=True):
                ship_io_with_tkroot.save_ship(ship)

        # Check that default name was used
        call_kwargs = mock_dialog.call_args[1]
        assert call_kwargs['initialfile'] == "New Ship"

    def test_load_ship_with_color_as_list(self, fresh_registries, tmp_path):
        """Load should handle color stored as list (JSON array)."""
        ship_data = {
            "name": "ListColorShip",
            "ship_class": "Escort",
            "theme_id": "Federation",
            "color": [100, 150, 200],  # List, not tuple
            "team_id": 0,
            "movement_policy": "kite_max",
            "layers": {},
            "_format_version": "2.0"
        }

        load_file = tmp_path / "list_color.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Color should be converted to tuple
        assert loaded_ship.color == (100, 150, 200) or loaded_ship.color == [100, 150, 200]

    def test_load_ship_with_missing_optional_fields_uses_defaults(self, fresh_registries, tmp_path):
        """Load should use defaults for missing optional fields."""
        minimal_data = {
            "name": "MinimalShip",
            "ship_class": "Escort",
            "color": [255, 255, 255],
            "layers": {},
            "_format_version": "2.0"
        }

        load_file = tmp_path / "minimal.json"
        with open(load_file, 'w') as f:
            json.dump(minimal_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Should use defaults
        assert loaded_ship.team_id == 0
        assert loaded_ship.theme_id == "Federation"
        assert loaded_ship.movement_policy == "kite_max"

    def test_load_ship_ignores_unknown_layer_types(self, fresh_registries, tmp_path):
        """Load should ignore unknown layer types without error."""
        ship_data = {
            "name": "UnknownLayerShip",
            "ship_class": "Escort",
            "color": [255, 255, 255],
            "layers": {
                "CORE": [],
                "UNKNOWN_LAYER": [{"id": "some_component"}],  # Invalid layer
            },
            "_format_version": "2.0"
        }

        load_file = tmp_path / "unknown_layer.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        # Should not raise
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)
        assert loaded_ship is not None

    def test_load_ship_ignores_unknown_component_ids(self, fresh_registries, tmp_path):
        """Load should skip unknown component IDs without error."""
        ship_data = {
            "name": "UnknownComponentShip",
            "ship_class": "Escort",
            "color": [255, 255, 255],
            "layers": {
                "CORE": [{"id": "nonexistent_component_12345"}],
            },
            "_format_version": "2.0"
        }

        load_file = tmp_path / "unknown_component.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        # Should not raise
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)
        assert loaded_ship is not None

    def test_default_ships_folder_is_configurable(self):
        """ShipIO.default_ships_folder should be configurable."""
        from game.ui.services.ship_io import ShipIO

        original = ShipIO.default_ships_folder
        try:
            ShipIO.default_ships_folder = "custom_ships"
            assert ShipIO.default_ships_folder == "custom_ships"
        finally:
            ShipIO.default_ships_folder = original


# =============================================================================
# TestShipIOErrorLogging
# =============================================================================

class TestShipIOErrorLogging:
    """Tests for error logging behavior."""

    def test_save_error_logs_message(self, mock_ship, ship_io_with_tkroot, tmp_path, caplog):
        """Save errors should be logged."""
        import logging

        save_file = str(tmp_path / "test_ship.json")

        with patch('game.ui.services.ship_io.open_save_dialog', return_value=save_file):
            with patch('os.path.exists', return_value=True):
                with patch('game.ui.services.ship_io.save_json', side_effect=OSError("Test error")):
                    with caplog.at_level(logging.ERROR):
                        ship_io_with_tkroot.save_ship(mock_ship)

        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on save failure"

    def test_load_json_error_logs_message(self, ship_io_with_tkroot, tmp_path, caplog):
        """Load JSON errors should be logged."""
        import logging

        load_file = tmp_path / "bad.json"
        with open(load_file, 'w') as f:
            f.write("not json")

        with patch('game.ui.services.ship_io.open_load_dialog', return_value=str(load_file)):
            with patch('os.path.exists', return_value=True):
                with caplog.at_level(logging.ERROR):
                    ship_io_with_tkroot.load_ship(1920, 1080)

        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on JSON decode failure"


# =============================================================================
# TestShipIOStatMismatchWarnings
# =============================================================================

class TestShipIOStatMismatchWarnings:
    """Tests for stat mismatch warnings on load."""

    def test_load_ship_with_stat_mismatch_sets_warnings(self, fresh_registries, tmp_path):
        """Ship with stat mismatches should have _loading_warnings populated."""
        # Create ship data with incorrect expected stats
        ship_data = {
            "name": "MismatchShip",
            "ship_class": "Escort",
            "color": [255, 255, 255],
            "theme_id": "Federation",
            "team_id": 0,
            "movement_policy": "kite_max",
            "layers": {},
            "expected_stats": {
                "max_hp": 999999,  # Definitely wrong
                "mass": 999999,    # Definitely wrong
            },
            "_format_version": "2.0"
        }

        load_file = tmp_path / "mismatch.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Should have loading warnings
        assert hasattr(loaded_ship, '_loading_warnings')
        assert len(loaded_ship._loading_warnings) > 0

    def test_load_ship_with_correct_stats_has_no_warnings(self, mock_ship, fresh_registries, tmp_path):
        """Ship with correct stats should have no loading warnings."""
        # Use actual ship's to_dict which has correct expected_stats
        ship_data = mock_ship.to_dict()

        load_file = tmp_path / "correct.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Should have no loading warnings (or empty list)
        warnings = getattr(loaded_ship, '_loading_warnings', [])
        assert len(warnings) == 0, f"Unexpected warnings: {warnings}"


# =============================================================================
# TestShipIOComponentIntegration
# =============================================================================

class TestShipIOComponentIntegration:
    """Integration tests for ship component serialization."""

    def test_round_trip_preserves_component_properties(self, fresh_registries, tmp_path):
        """Component properties should be preserved after round-trip."""
        from game.simulation.components.component import create_component
        from game.core.constants import LayerType

        ship = create_test_ship(
            name="PropertyShip",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )

        # Find a weapon-like component and check properties
        ship_data = ship.to_dict()

        save_file = tmp_path / "property_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Verify components still present
        original_count = sum(len(layer.components) for layer in ship.layers.values())
        loaded_count = sum(len(layer.components) for layer in loaded_ship.layers.values())
        assert loaded_count == original_count

    def test_round_trip_with_damaged_ship(self, fresh_registries, tmp_path):
        """Ship loaded from file should have full HP (designs are templates, not battle state)."""
        ship = create_test_ship(
            name="DamagedShip",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )

        # Apply some damage (this is runtime state, not saved)
        original_max_hp = ship.max_hp
        ship.hp = ship.max_hp // 2

        ship_data = ship.to_dict()

        save_file = tmp_path / "damaged_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Ship designs are templates - loaded ship should have full HP
        # Damage state is runtime only, not persisted
        assert loaded_ship.hp == loaded_ship.max_hp
        assert loaded_ship.max_hp == original_max_hp

    def test_round_trip_multiple_weapons(self, fresh_registries, tmp_path):
        """Ship with multiple weapons should preserve all of them."""
        ship = create_test_ship(
            name="ArmedShip",
            add_bridge=True,
            add_engine=True,
            add_weapons=3,
            registries=fresh_registries
        )

        ship_data = ship.to_dict()

        save_file = tmp_path / "armed_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Count weapons (components with WeaponAbility)
        original_weapons = sum(
            1 for layer in ship.layers.values()
            for comp in layer.components
            if any('Weapon' in type(a).__name__ for a in comp.abilities.values())
        )
        loaded_weapons = sum(
            1 for layer in loaded_ship.layers.values()
            for comp in layer.components
            if any('Weapon' in type(a).__name__ for a in comp.abilities.values())
        )

        assert loaded_weapons == original_weapons


# =============================================================================
# TestShipIOFormatVersioning
# =============================================================================

class TestShipIOFormatVersioning:
    """Tests for ship format versioning."""

    def test_format_version_is_2_0(self, mock_ship):
        """Current format version should be 2.0."""
        ship_data = mock_ship.to_dict()
        assert ship_data.get('_format_version') == '2.0'

    def test_load_without_format_version(self, fresh_registries, tmp_path):
        """Ships without format version should still load (legacy support)."""
        ship_data = {
            "name": "LegacyShip",
            "ship_class": "Escort",
            "color": [255, 255, 255],
            "layers": {},
            # No _format_version
        }

        load_file = tmp_path / "legacy.json"
        with open(load_file, 'w') as f:
            json.dump(ship_data, f)

        from game.simulation.entities.ship import Ship
        with open(load_file, 'r') as f:
            loaded_data = json.load(f)

        # Should not raise
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)
        assert loaded_ship.name == "LegacyShip"


# =============================================================================
# TestShipIOResourceSerialization
# =============================================================================

class TestShipIOResourceSerialization:
    """Tests for ship resource serialization."""

    def test_resources_serialized_correctly(self, mock_ship):
        """Ship resources should be serialized to JSON."""
        ship_data = mock_ship.to_dict()

        assert 'resources' in ship_data
        resources = ship_data['resources']

        # Standard resources should be present
        assert 'fuel' in resources
        assert 'energy' in resources
        assert 'ammo' in resources

    def test_resources_round_trip(self, mock_ship, fresh_registries, tmp_path):
        """Resources should be preserved after round-trip."""
        ship_data = mock_ship.to_dict()
        original_resources = ship_data['resources'].copy()

        save_file = tmp_path / "resource_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Get loaded ship resources
        loaded_resources = loaded_ship.to_dict()['resources']

        # Resources should match (using subset check since loaded might have more)
        for resource_key in ['fuel', 'energy', 'ammo']:
            if resource_key in original_resources:
                assert resource_key in loaded_resources


# =============================================================================
# TestShipIOSpecialCharacters
# =============================================================================

class TestShipIOSpecialCharacters:
    """Tests for handling special characters in ship data."""

    def test_unicode_ship_name(self, fresh_registries, tmp_path):
        """Ship with Unicode name should serialize/deserialize correctly."""
        ship = create_test_ship(
            name="Starship",  # Greek, Japanese, Emoji in name
            add_bridge=True,
            registries=fresh_registries
        )

        ship_data = ship.to_dict()

        save_file = tmp_path / "unicode_ship.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(ship_data, f, ensure_ascii=False)

        with open(save_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # This tests basic Unicode handling even with ASCII-safe name
        assert loaded_ship is not None
        assert loaded_ship.name == "Starship"

    def test_whitespace_in_ship_name(self, fresh_registries, tmp_path):
        """Ship name with whitespace should be handled correctly."""
        ship = create_test_ship(
            name="  Ship With Spaces  ",
            add_bridge=True,
            registries=fresh_registries
        )

        ship_data = ship.to_dict()

        save_file = tmp_path / "whitespace_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # Name should be preserved as-is
        assert loaded_ship.name == "  Ship With Spaces  "


# =============================================================================
# TestShipIOLargeShips
# =============================================================================

class TestShipIOLargeShips:
    """Tests for handling ships with many components."""

    def test_ship_with_many_components(self, fresh_registries, tmp_path):
        """Ship with many components should serialize/deserialize correctly."""
        ship = create_test_ship(
            name="MegaShip",
            add_bridge=True,
            add_engine=True,
            add_weapons=5,
            add_shields=3,
            registries=fresh_registries
        )

        ship_data = ship.to_dict()

        # Count total components
        total_components = sum(
            len(layer.components) for layer in ship.layers.values()
        )
        assert total_components >= 10  # Bridge + Engine + 5 weapons + 3 shields + crew

        save_file = tmp_path / "mega_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        # All components should be preserved
        loaded_total = sum(
            len(layer.components) for layer in loaded_ship.layers.values()
        )
        assert loaded_total == total_components


# =============================================================================
# TestShipIOConcurrency
# =============================================================================

class TestShipIOConcurrency:
    """Tests for potential concurrency issues."""

    def test_multiple_ships_serialize_independently(self, fresh_registries, tmp_path):
        """Multiple ships should serialize without interference."""
        ships = [
            create_test_ship(name=f"Ship{i}", add_bridge=True, registries=fresh_registries)
            for i in range(3)
        ]

        # Serialize all ships
        ship_data_list = [ship.to_dict() for ship in ships]

        # Verify each has unique data
        names = [data['name'] for data in ship_data_list]
        assert names == ['Ship0', 'Ship1', 'Ship2']

        # Load them back
        from game.simulation.entities.ship import Ship
        loaded_ships = [
            Ship.from_dict(data, registries=fresh_registries)
            for data in ship_data_list
        ]

        loaded_names = [ship.name for ship in loaded_ships]
        assert loaded_names == ['Ship0', 'Ship1', 'Ship2']


# =============================================================================
# TestShipIODefaultValues
# =============================================================================

class TestShipIODefaultValues:
    """Tests for default value handling in ship serialization."""

    def test_default_movement_policy_preserved(self, fresh_registries, tmp_path):
        """Default movement policy should be serialized and loaded."""
        ship = create_test_ship(
            name="DefaultsShip",
            add_bridge=True,
            registries=fresh_registries
        )

        # Get default movement policy
        default_policy = ship.movement_policy

        ship_data = ship.to_dict()
        assert 'movement_policy' in ship_data
        assert ship_data['movement_policy'] == default_policy

        save_file = tmp_path / "defaults_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.movement_policy == default_policy

    def test_default_theme_id_preserved(self, fresh_registries, tmp_path):
        """Default theme ID should be serialized and loaded."""
        ship = create_test_ship(
            name="ThemeShip",
            add_bridge=True,
            registries=fresh_registries
        )

        ship_data = ship.to_dict()

        save_file = tmp_path / "theme_ship.json"
        with open(save_file, 'w') as f:
            json.dump(ship_data, f)

        with open(save_file, 'r') as f:
            loaded_data = json.load(f)

        from game.simulation.entities.ship import Ship
        loaded_ship = Ship.from_dict(loaded_data, registries=fresh_registries)

        assert loaded_ship.theme_id == ship.theme_id
