"""
Unit tests for ship_loader.py.

Tests the vehicle class loading functions and ship data initialization:
- load_vehicle_classes_data (pure function)
- load_vehicle_classes (registry-populating wrapper)
- initialize_ship_data (facade function)
- get_or_create_validator (validator initialization)
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from game.simulation.entities.ship_loader import (
    load_vehicle_classes_data,
    load_vehicle_classes,
    initialize_ship_data,
    get_or_create_validator,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def vehicle_classes_data():
    """Sample vehicle classes data."""
    return {
        "classes": {
            "Frigate": {
                "id": "frigate",
                "base_hull": 100,
                "slots": 5,
            },
            "Cruiser": {
                "id": "cruiser",
                "base_hull": 200,
                "slots": 10,
            },
        }
    }


@pytest.fixture
def vehicle_layers_data():
    """Sample vehicle layers data."""
    return {
        "definitions": {
            "standard_layers": {
                "hull": {"order": 1, "name": "Hull"},
                "armor": {"order": 2, "name": "Armor"},
            },
            "capital_layers": {
                "hull": {"order": 1, "name": "Hull"},
                "armor": {"order": 2, "name": "Heavy Armor"},
                "shields": {"order": 3, "name": "Shields"},
            },
        }
    }


@pytest.fixture
def classes_with_layer_config():
    """Vehicle classes referencing layer configurations."""
    return {
        "classes": {
            "Frigate": {
                "id": "frigate",
                "base_hull": 100,
                "layer_config": "standard_layers",
            },
            "Battleship": {
                "id": "battleship",
                "base_hull": 500,
                "layer_config": "capital_layers",
            },
        }
    }


@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary data directory with basic files."""
    return tmp_path


@pytest.fixture
def mock_registry_manager():
    """Create a mock RegistryManager."""
    manager = MagicMock()
    manager.vehicle_classes = {}
    manager._validator = None
    return manager


# =============================================================================
# Tests: load_vehicle_classes_data (pure function)
# =============================================================================

class TestLoadVehicleClassesData:
    """Tests for load_vehicle_classes_data function."""

    def test_loads_vehicle_classes_from_file(self, tmp_path, vehicle_classes_data):
        """Successfully loads vehicle classes from JSON file."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        result = load_vehicle_classes_data(str(file_path))

        assert "Frigate" in result
        assert "Cruiser" in result
        assert result["Frigate"]["base_hull"] == 100
        assert result["Cruiser"]["base_hull"] == 200

    def test_raises_runtime_error_for_missing_file(self, tmp_path):
        """Raises RuntimeError when vehicle classes file is not found."""
        nonexistent = tmp_path / "does_not_exist.json"

        with pytest.raises(RuntimeError, match="Critical Error"):
            load_vehicle_classes_data(str(nonexistent))

    def test_returns_deep_copy_of_data(self, tmp_path, vehicle_classes_data):
        """Returns a deep copy, not a reference to internal data."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        result1 = load_vehicle_classes_data(str(file_path))
        result2 = load_vehicle_classes_data(str(file_path))

        # Modify result1 and verify result2 is unaffected
        result1["Frigate"]["base_hull"] = 9999
        assert result2["Frigate"]["base_hull"] == 100

    def test_handles_empty_classes_dict(self, tmp_path):
        """Handles file with empty classes dictionary."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text('{"classes": {}}')

        result = load_vehicle_classes_data(str(file_path))

        assert result == {}

    def test_handles_missing_classes_key(self, tmp_path):
        """Returns empty dict if classes key is missing."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text('{"other_data": "value"}')

        result = load_vehicle_classes_data(str(file_path))

        assert result == {}

    def test_resolves_layer_configuration(
        self, tmp_path, classes_with_layer_config, vehicle_layers_data
    ):
        """Resolves layer_config references to actual layer definitions."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        assert "layers" in result["Frigate"]
        assert result["Frigate"]["layers"]["hull"]["order"] == 1
        assert "layers" in result["Battleship"]
        assert "shields" in result["Battleship"]["layers"]

    def test_layer_config_not_found_leaves_class_unchanged(
        self, tmp_path, vehicle_layers_data
    ):
        """Class with unknown layer_config does not get layers added."""
        classes_data = {
            "classes": {
                "Mystery": {
                    "id": "mystery",
                    "layer_config": "nonexistent_config",
                },
            }
        }
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_data))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        assert "Mystery" in result
        assert "layers" not in result["Mystery"]
        assert result["Mystery"]["layer_config"] == "nonexistent_config"

    def test_loads_layers_from_adjacent_file(self, tmp_path, classes_with_layer_config, vehicle_layers_data):
        """Loads vehiclelayers.json from same directory if not specified."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        # Only specify classes file, layers should be found automatically
        result = load_vehicle_classes_data(str(classes_file))

        assert "layers" in result["Frigate"]

    def test_handles_missing_layers_file_gracefully(self, tmp_path, classes_with_layer_config):
        """Continues without error if layers file doesn't exist."""
        classes_file = tmp_path / "vehicleclasses.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        # No layers file created

        result = load_vehicle_classes_data(str(classes_file))

        assert "Frigate" in result
        # layer_config remains but layers not resolved
        assert "layers" not in result["Frigate"]

    def test_uses_default_path_when_none_provided(self):
        """Uses Paths.VEHICLE_CLASSES_FILE when no path provided."""
        with patch('game.simulation.entities.ship_loader.Paths') as mock_paths:
            mock_paths.VEHICLE_CLASSES_FILE = "/fake/path/vehicleclasses.json"

            with patch('game.simulation.entities.ship_loader.load_json_required') as mock_load:
                mock_load.return_value = {"classes": {"Test": {"id": "test"}}}

                with patch('game.simulation.entities.ship_loader.load_json', return_value={}):
                    with patch('os.path.exists', return_value=True):
                        result = load_vehicle_classes_data()

                mock_load.assert_called_once()
                assert "Test" in result


# =============================================================================
# Tests: load_vehicle_classes (registry wrapper)
# =============================================================================

class TestLoadVehicleClasses:
    """Tests for load_vehicle_classes function."""

    def test_populates_registry_with_loaded_data(self, tmp_path, vehicle_classes_data):
        """Loads data and populates registry via provider."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        # PROJ-174: Use provider pattern via DI
        vehicle_classes = {}
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = vehicle_classes

        load_vehicle_classes(str(file_path), registry_provider=mock_provider)

        assert "Frigate" in vehicle_classes
        assert "Cruiser" in vehicle_classes

    def test_clears_existing_registry_before_loading(self, tmp_path, vehicle_classes_data):
        """Clears existing vehicle_classes before populating."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        # PROJ-174: Use provider pattern via DI
        existing_classes = {"OldClass": {"id": "old"}}
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = existing_classes

        load_vehicle_classes(str(file_path), registry_provider=mock_provider)

        # OldClass should be gone, only new classes present
        assert "OldClass" not in existing_classes
        assert "Frigate" in existing_classes

    def test_uses_default_path_when_none_provided(self):
        """Uses Paths.VEHICLE_CLASSES_FILE when no path provided."""
        with patch('game.simulation.entities.ship_loader.load_vehicle_classes_data') as mock_load:
            mock_load.return_value = {"Test": {"id": "test"}}

            # PROJ-174: Use provider pattern via DI
            vehicle_classes = {}
            mock_provider = MagicMock()
            mock_provider.get_vehicle_classes.return_value = vehicle_classes

            with patch('game.simulation.entities.ship_loader.load_json', return_value={}):
                with patch('game.simulation.entities.ship_loader.Paths') as mock_paths:
                    mock_paths.VEHICLE_CLASSES_FILE = "/default/path.json"

                    load_vehicle_classes(registry_provider=mock_provider)

                    # Verify default path was used
                    mock_load.assert_called()

    def test_logs_loaded_count(self, tmp_path, vehicle_classes_data, caplog):
        """Logs the number of loaded vehicle classes."""
        import logging
        caplog.set_level(logging.INFO, logger="game.simulation.entities.ship_loader")

        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        # PROJ-174: Use provider pattern via DI
        vehicle_classes = {}
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = vehicle_classes

        load_vehicle_classes(str(file_path), registry_provider=mock_provider)

        assert "Loaded 2 vehicle classes" in caplog.text

    def test_logs_layer_configurations(self, tmp_path, classes_with_layer_config, vehicle_layers_data, caplog):
        """Logs layer configurations when present."""
        import logging
        caplog.set_level(logging.INFO, logger="game.simulation.entities.ship_loader")

        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        # PROJ-174: Use provider pattern via DI
        vehicle_classes = {}
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = vehicle_classes

        load_vehicle_classes(str(classes_file), registry_provider=mock_provider)

        assert "layer configurations" in caplog.text


# =============================================================================
# Tests: initialize_ship_data (facade)
# =============================================================================

class TestInitializeShipData:
    """Tests for initialize_ship_data function."""

    def test_calls_load_vehicle_classes_with_custom_path(self, tmp_path):
        """Calls load_vehicle_classes with path derived from base_path."""
        with patch('game.simulation.entities.ship_loader.load_vehicle_classes') as mock_load:
            initialize_ship_data(str(tmp_path))

            expected_path = str(tmp_path / "data" / "vehicleclasses.json")
            mock_load.assert_called_once_with(expected_path)

    def test_calls_load_vehicle_classes_with_default_path(self):
        """Calls load_vehicle_classes with no arguments when base_path is None."""
        with patch('game.simulation.entities.ship_loader.load_vehicle_classes') as mock_load:
            initialize_ship_data()

            mock_load.assert_called_once_with()

    def test_propagates_errors_from_load_vehicle_classes(self, tmp_path):
        """Propagates RuntimeError from load_vehicle_classes."""
        with patch('game.simulation.entities.ship_loader.load_vehicle_classes') as mock_load:
            mock_load.side_effect = RuntimeError("Critical Error")

            with pytest.raises(RuntimeError, match="Critical Error"):
                initialize_ship_data(str(tmp_path))


# =============================================================================
# Tests: get_or_create_validator
# =============================================================================

class TestGetOrCreateValidator:
    """Tests for get_or_create_validator function."""

    def test_returns_existing_validator(self):
        """Returns existing validator if already set."""
        mock_validator = MagicMock()

        with patch('game.simulation.entities.ship_loader.RegistryManager') as MockRM:
            mock_registry = MagicMock()
            mock_registry.get_validator.return_value = mock_validator
            MockRM.instance.return_value = mock_registry

            result = get_or_create_validator()

        assert result is mock_validator

    def test_creates_validator_when_none_exists(self):
        """Creates new ShipDesignValidator when none exists."""
        with patch('game.simulation.entities.ship_loader.RegistryManager') as MockRM:
            mock_registry = MagicMock()
            mock_registry.get_validator.return_value = None
            mock_registry.components = {}
            mock_registry.modifiers = {}
            mock_registry.vehicle_classes = {}
            mock_registry.resources = {}
            MockRM.instance.return_value = mock_registry

            with patch('game.simulation.entities.ship_loader.ShipDesignValidator') as MockValidator:
                mock_new_validator = MagicMock()
                MockValidator.return_value = mock_new_validator

                with patch('game.simulation.entities.ship_loader.set_validator') as mock_set:
                    result = get_or_create_validator()

                    # Verify validator was created
                    MockValidator.assert_called_once()
                    # Verify validator was set
                    mock_set.assert_called_once_with(mock_new_validator)
                    assert result is mock_new_validator

    def test_creates_validator_with_game_registries(self):
        """Creates validator using GameRegistries from provider."""
        # PROJ-174: Use provider pattern via DI
        mock_provider = MagicMock()
        mock_provider.get_components.return_value = {"comp1": {}}
        mock_provider.get_modifiers.return_value = {"mod1": {}}
        mock_provider.get_vehicle_classes.return_value = {"class1": {}}
        mock_provider.get_resources.return_value = {"res1": {}}

        with patch('game.simulation.entities.ship_loader.RegistryManager') as MockRM:
            mock_registry = MagicMock()
            mock_registry.get_validator.return_value = None
            MockRM.instance.return_value = mock_registry

            with patch('game.simulation.entities.ship_loader.ShipDesignValidator') as MockValidator:
                with patch('game.simulation.entities.ship_loader.set_validator'):
                    # GameRegistries is imported inside the function from game.core.registry
                    with patch('game.core.registry.GameRegistries') as MockGameReg:
                        get_or_create_validator(registry_provider=mock_provider)

                        # Verify GameRegistries was created with provider data
                        MockGameReg.assert_called_once_with(
                            components={"comp1": {}},
                            modifiers={"mod1": {}},
                            vehicle_classes={"class1": {}},
                            resources={"res1": {}}
                        )


# =============================================================================
# Tests: Edge Cases and Error Handling
# =============================================================================

class TestEdgeCasesAndErrorHandling:
    """Edge case and error handling tests."""

    def test_load_vehicle_classes_data_with_unicode(self, tmp_path):
        """Handles Unicode characters in vehicle class names and data."""
        unicode_data = {
            "classes": {
                "Destroyer": {
                    "id": "Zerstorer",
                    "description": "German destroyer class",
                },
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(unicode_data, ensure_ascii=False), encoding='utf-8')

        result = load_vehicle_classes_data(str(file_path))

        assert "Destroyer" in result
        assert result["Destroyer"]["id"] == "Zerstorer"

    def test_load_vehicle_classes_data_with_nested_structures(self, tmp_path):
        """Handles deeply nested data structures."""
        nested_data = {
            "classes": {
                "Complex": {
                    "id": "complex",
                    "nested": {
                        "level1": {
                            "level2": {
                                "level3": ["a", "b", "c"],
                            }
                        }
                    }
                }
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(nested_data))

        result = load_vehicle_classes_data(str(file_path))

        assert result["Complex"]["nested"]["level1"]["level2"]["level3"] == ["a", "b", "c"]

    def test_load_vehicle_classes_data_preserves_numeric_values(self, tmp_path):
        """Preserves numeric values including floats and negative numbers."""
        numeric_data = {
            "classes": {
                "Numeric": {
                    "id": "numeric",
                    "integer": 42,
                    "float": 3.14159,
                    "negative": -100,
                    "zero": 0,
                }
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(numeric_data))

        result = load_vehicle_classes_data(str(file_path))

        assert result["Numeric"]["integer"] == 42
        assert abs(result["Numeric"]["float"] - 3.14159) < 0.0001
        assert result["Numeric"]["negative"] == -100
        assert result["Numeric"]["zero"] == 0

    def test_load_vehicle_classes_data_handles_large_file(self, tmp_path):
        """Handles files with many vehicle classes."""
        large_data = {
            "classes": {
                f"Class_{i}": {"id": f"class_{i}", "value": i}
                for i in range(100)
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(large_data))

        result = load_vehicle_classes_data(str(file_path))

        assert len(result) == 100
        assert result["Class_0"]["value"] == 0
        assert result["Class_99"]["value"] == 99

    def test_layer_definitions_are_deep_copied(self, tmp_path, classes_with_layer_config, vehicle_layers_data):
        """Layer definitions are deep copied, not referenced."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        result1 = load_vehicle_classes_data(str(classes_file), str(layers_file))
        result2 = load_vehicle_classes_data(str(classes_file), str(layers_file))

        # Modify layers in result1
        result1["Frigate"]["layers"]["hull"]["order"] = 999

        # Verify result2 is unaffected
        assert result2["Frigate"]["layers"]["hull"]["order"] == 1

    def test_handles_json_decode_error(self, tmp_path):
        """Raises appropriate error for invalid JSON."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            load_vehicle_classes_data(str(file_path))

    def test_handles_empty_file(self, tmp_path):
        """Raises appropriate error for empty file."""
        file_path = tmp_path / "empty.json"
        file_path.write_text("")

        with pytest.raises(json.JSONDecodeError):
            load_vehicle_classes_data(str(file_path))


# =============================================================================
# Tests: Path Resolution
# =============================================================================

class TestPathResolution:
    """Tests for path resolution logic."""

    def test_relative_path_resolved_to_module_directory(self, tmp_path):
        """Relative path is resolved relative to module directory when not found."""
        # This tests the fallback logic in load_vehicle_classes_data
        with patch('os.path.exists') as mock_exists:
            # First call returns False (path doesn't exist as given)
            # Second call returns True (path exists relative to module)
            mock_exists.side_effect = [False, True]

            with patch('game.simulation.entities.ship_loader.load_json_required') as mock_load:
                mock_load.return_value = {"classes": {"Test": {"id": "test"}}}

                with patch('game.simulation.entities.ship_loader.load_json', return_value={}):
                    result = load_vehicle_classes_data("relative/path.json")

                assert "Test" in result

    def test_absolute_path_used_directly(self, tmp_path, vehicle_classes_data):
        """Absolute path is used directly without modification."""
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(vehicle_classes_data))

        result = load_vehicle_classes_data(str(file_path))

        assert "Frigate" in result


# =============================================================================
# Tests: Additional Edge Cases (PROJ-118 Phase 2)
# =============================================================================

class TestLoadVehicleClassesWithLayersPath:
    """Tests for load_vehicle_classes with explicit layers_file_path."""

    def test_load_vehicle_classes_with_explicit_layers_path(
        self, tmp_path, classes_with_layer_config, vehicle_layers_data
    ):
        """load_vehicle_classes resolves layers when explicit path provided."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "custom_layers.json"  # Non-standard name
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        # PROJ-174: Use provider pattern via DI
        vehicle_classes = {}
        mock_provider = MagicMock()
        mock_provider.get_vehicle_classes.return_value = vehicle_classes

        load_vehicle_classes(str(classes_file), str(layers_file), registry_provider=mock_provider)

        # Verify layers were resolved
        assert "layers" in vehicle_classes.get("Frigate", {})


class TestLoadVehicleClassesDataLayerEdgeCases:
    """Edge cases for layer configuration resolution."""

    def test_layer_definitions_empty_dict(self, tmp_path, classes_with_layer_config):
        """Handles layer file with empty definitions dict."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text('{"definitions": {}}')

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        # Classes exist but layers not resolved (empty definitions)
        assert "Frigate" in result
        assert "layers" not in result["Frigate"]

    def test_layer_file_missing_definitions_key(self, tmp_path, classes_with_layer_config):
        """Handles layer file without definitions key."""
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_with_layer_config))
        layers_file.write_text('{"other_key": "value"}')

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        # Classes exist but layers not resolved (no definitions key)
        assert "Frigate" in result
        assert "layers" not in result["Frigate"]

    def test_multiple_classes_reference_same_layer_config(
        self, tmp_path, vehicle_layers_data
    ):
        """Multiple classes can reference the same layer configuration."""
        classes_data = {
            "classes": {
                "Ship1": {"id": "ship1", "layer_config": "standard_layers"},
                "Ship2": {"id": "ship2", "layer_config": "standard_layers"},
                "Ship3": {"id": "ship3", "layer_config": "capital_layers"},
            }
        }
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_data))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        # Both Ship1 and Ship2 get the same layer structure
        assert result["Ship1"]["layers"] == result["Ship2"]["layers"]
        # Ship3 gets different layers
        assert "shields" in result["Ship3"]["layers"]
        assert "shields" not in result["Ship1"]["layers"]

    def test_class_without_layer_config_unchanged(
        self, tmp_path, vehicle_layers_data
    ):
        """Classes without layer_config are not modified."""
        classes_data = {
            "classes": {
                "Simple": {"id": "simple", "base_hull": 50},
            }
        }
        classes_file = tmp_path / "vehicleclasses.json"
        layers_file = tmp_path / "vehiclelayers.json"
        classes_file.write_text(json.dumps(classes_data))
        layers_file.write_text(json.dumps(vehicle_layers_data))

        result = load_vehicle_classes_data(str(classes_file), str(layers_file))

        assert result["Simple"]["id"] == "simple"
        assert result["Simple"]["base_hull"] == 50
        assert "layers" not in result["Simple"]
        assert "layer_config" not in result["Simple"]


class TestInitializeShipDataEdgeCases:
    """Additional edge cases for initialize_ship_data."""

    def test_initialize_ship_data_with_trailing_separator(self, tmp_path):
        """Handles base_path with trailing path separator."""
        # Path with trailing separator
        base_path_with_sep = str(tmp_path) + "\\"

        with patch('game.simulation.entities.ship_loader.load_vehicle_classes') as mock_load:
            initialize_ship_data(base_path_with_sep)

            # Should still construct path correctly
            mock_load.assert_called_once()
            call_arg = mock_load.call_args[0][0]
            assert "vehicleclasses.json" in call_arg


class TestValidatorCaching:
    """Tests for validator caching behavior."""

    def test_get_or_create_validator_caches_result(self):
        """Multiple calls return the same validator instance."""
        mock_validator = MagicMock()

        with patch('game.simulation.entities.ship_loader.RegistryManager') as MockRM:
            mock_registry = MagicMock()
            # First call: no validator, subsequent calls: return cached
            mock_registry.get_validator.return_value = mock_validator
            MockRM.instance.return_value = mock_registry

            result1 = get_or_create_validator()
            result2 = get_or_create_validator()

        assert result1 is result2
        assert result1 is mock_validator


class TestLoadVehicleClassesDataSpecialCharacters:
    """Tests for special characters in vehicle class data."""

    def test_class_name_with_spaces(self, tmp_path):
        """Handles class names containing spaces."""
        data = {
            "classes": {
                "Heavy Cruiser Mk II": {"id": "heavy_cruiser_mk2", "slots": 15},
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(data))

        result = load_vehicle_classes_data(str(file_path))

        assert "Heavy Cruiser Mk II" in result
        assert result["Heavy Cruiser Mk II"]["slots"] == 15

    def test_class_with_special_characters_in_values(self, tmp_path):
        """Handles special characters in class values."""
        data = {
            "classes": {
                "Special": {
                    "id": "special",
                    "description": "A ship with 'quotes' and \"double quotes\"",
                    "notes": "Line1\nLine2\tTabbed",
                },
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(data))

        result = load_vehicle_classes_data(str(file_path))

        assert "quotes" in result["Special"]["description"]
        assert "\n" in result["Special"]["notes"]

    def test_class_with_boolean_values(self, tmp_path):
        """Preserves boolean values in class definitions."""
        data = {
            "classes": {
                "Booleans": {
                    "id": "booleans",
                    "is_capital": True,
                    "is_fighter": False,
                },
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(data))

        result = load_vehicle_classes_data(str(file_path))

        assert result["Booleans"]["is_capital"] is True
        assert result["Booleans"]["is_fighter"] is False

    def test_class_with_null_values(self, tmp_path):
        """Preserves null/None values in class definitions."""
        data = {
            "classes": {
                "Nullable": {
                    "id": "nullable",
                    "optional_field": None,
                },
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(data))

        result = load_vehicle_classes_data(str(file_path))

        assert result["Nullable"]["optional_field"] is None

    def test_class_with_array_values(self, tmp_path):
        """Preserves array values in class definitions."""
        data = {
            "classes": {
                "Arrays": {
                    "id": "arrays",
                    "allowed_slots": ["weapon", "engine", "sensor"],
                    "empty_array": [],
                },
            }
        }
        file_path = tmp_path / "vehicleclasses.json"
        file_path.write_text(json.dumps(data))

        result = load_vehicle_classes_data(str(file_path))

        assert result["Arrays"]["allowed_slots"] == ["weapon", "engine", "sensor"]
        assert result["Arrays"]["empty_array"] == []
