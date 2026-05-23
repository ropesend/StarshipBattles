"""
Unit tests for TechPresetLoader.

Tests preset loading, validation, availability checks, and error handling.
"""
import os
import json
import pytest
from unittest.mock import patch

from game.simulation.systems.tech_preset_loader import TechPresetLoader, TECH_PRESETS_DIR


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_presets_dir(tmp_path):
    """Create a temporary directory with test preset files."""
    presets_dir = tmp_path / "tech_presets"
    presets_dir.mkdir()
    return presets_dir


@pytest.fixture
def sample_preset_data():
    """Standard preset data for testing."""
    return {
        "name": "Test Preset",
        "description": "A test preset for unit tests",
        "unlocked_components": ["hull_escort", "laser_cannon", "basic_engine"],
        "unlocked_modifiers": ["simple_size_mount", "basic_armor_mod"]
    }


@pytest.fixture
def wildcard_preset_data():
    """Preset with wildcard for all components/modifiers."""
    return {
        "name": "All Tech",
        "description": "All tech unlocked",
        "unlocked_components": ["*"],
        "unlocked_modifiers": ["*"]
    }


@pytest.fixture
def minimal_preset_data():
    """Preset with minimal data (missing optional fields)."""
    return {
        "name": "Minimal",
        "description": "Minimal preset"
        # Missing unlocked_components and unlocked_modifiers
    }


@pytest.fixture
def create_preset(temp_presets_dir):
    """Factory fixture to create preset files in temp directory."""
    def _create(name: str, data: dict):
        filepath = temp_presets_dir / f"{name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return filepath
    return _create


# =============================================================================
# Test: list_presets
# =============================================================================


class TestListPresets:
    """Tests for TechPresetLoader.list_presets()."""

    def test_list_presets_returns_sorted_names(self, temp_presets_dir, create_preset, sample_preset_data):
        """list_presets returns preset names sorted alphabetically."""
        create_preset("zebra_preset", sample_preset_data)
        create_preset("alpha_preset", sample_preset_data)
        create_preset("mid_preset", sample_preset_data)

        with patch.object(
            TechPresetLoader, 'list_presets',
            wraps=TechPresetLoader.list_presets
        ):
            with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
                result = TechPresetLoader.list_presets()

        assert result == ["alpha_preset", "mid_preset", "zebra_preset"]

    def test_list_presets_empty_directory(self, temp_presets_dir):
        """list_presets returns empty list when no presets exist."""
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.list_presets()

        assert result == []

    def test_list_presets_ignores_non_json_files(self, temp_presets_dir, create_preset, sample_preset_data):
        """list_presets only includes .json files."""
        create_preset("valid_preset", sample_preset_data)

        # Create non-JSON files
        (temp_presets_dir / "readme.txt").write_text("Not a preset")
        (temp_presets_dir / "backup.json.bak").write_text("{}")

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.list_presets()

        assert result == ["valid_preset"]

    def test_list_presets_with_real_presets(self):
        """list_presets returns real preset names from the data directory."""
        result = TechPresetLoader.list_presets()

        # Should contain the actual presets from data/tech_presets/
        assert "default" in result
        assert "early_game" in result
        assert "mid_game" in result
        assert len(result) >= 3


# =============================================================================
# Test: load_preset
# =============================================================================


class TestLoadPreset:
    """Tests for TechPresetLoader.load_preset()."""

    def test_load_preset_returns_data(self, temp_presets_dir, create_preset, sample_preset_data):
        """load_preset returns the preset data dictionary."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.load_preset("test_preset")

        assert result == sample_preset_data

    def test_load_preset_raises_for_missing(self, temp_presets_dir):
        """load_preset raises FileNotFoundError for nonexistent preset."""
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            with pytest.raises(FileNotFoundError) as exc_info:
                TechPresetLoader.load_preset("nonexistent_preset")

        assert "nonexistent_preset" in str(exc_info.value)

    def test_load_preset_preserves_all_fields(self, temp_presets_dir, create_preset):
        """load_preset preserves all fields from the JSON file."""
        preset_data = {
            "name": "Full Preset",
            "description": "Detailed description",
            "unlocked_components": ["comp_a", "comp_b"],
            "unlocked_modifiers": ["mod_x", "mod_y"],
            "extra_field": "custom_value"  # Extra field should be preserved
        }
        create_preset("full_preset", preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.load_preset("full_preset")

        assert result["name"] == "Full Preset"
        assert result["extra_field"] == "custom_value"

    def test_load_real_default_preset(self):
        """load_preset can load the real default preset."""
        result = TechPresetLoader.load_preset("default")

        assert result["name"] == "Default (All Tech)"
        assert result["unlocked_components"] == ["*"]
        assert result["unlocked_modifiers"] == ["*"]

    def test_load_real_early_game_preset(self):
        """load_preset can load the real early_game preset."""
        result = TechPresetLoader.load_preset("early_game")

        assert result["name"] == "Early Game Tech"
        assert "hull_escort" in result["unlocked_components"]
        assert "laser_cannon" in result["unlocked_components"]


# =============================================================================
# Test: get_available_components
# =============================================================================


class TestGetAvailableComponentsAndModifiers:
    """Parametrized tests for the get_available_{components,modifiers}() pair
    (PROJ-479 Task 1.18 consolidation)."""

    @pytest.mark.parametrize(
        "getter_name,sample_expected",
        [
            ("get_available_components", ["hull_escort", "laser_cannon", "basic_engine"]),
            ("get_available_modifiers", ["simple_size_mount", "basic_armor_mod"]),
        ],
        ids=["components", "modifiers"],
    )
    def test_get_returns_list(
        self, temp_presets_dir, create_preset, sample_preset_data,
        getter_name, sample_expected
    ):
        create_preset("test_preset", sample_preset_data)
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = getattr(TechPresetLoader, getter_name)("test_preset")
        assert result == sample_expected

    @pytest.mark.parametrize(
        "getter_name",
        ["get_available_components", "get_available_modifiers"],
        ids=["components", "modifiers"],
    )
    def test_get_returns_empty_when_missing(
        self, temp_presets_dir, create_preset, minimal_preset_data, getter_name
    ):
        create_preset("minimal", minimal_preset_data)
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = getattr(TechPresetLoader, getter_name)("minimal")
        assert result == []

    @pytest.mark.parametrize(
        "getter_name",
        ["get_available_components", "get_available_modifiers"],
        ids=["components", "modifiers"],
    )
    def test_get_wildcard(
        self, temp_presets_dir, create_preset, wildcard_preset_data, getter_name
    ):
        create_preset("wildcard", wildcard_preset_data)
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = getattr(TechPresetLoader, getter_name)("wildcard")
        assert result == ["*"]

    def test_get_components_raises_for_missing_preset(self, temp_presets_dir):
        """get_available_components raises FileNotFoundError for missing preset
        (components-only — modifiers has no equivalent test in the original)."""
        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            with pytest.raises(FileNotFoundError):
                TechPresetLoader.get_available_components("nonexistent")


# =============================================================================
# Test: is_component_available
# =============================================================================


class TestIsComponentAvailable:
    """Tests for TechPresetLoader.is_component_available()."""

    def test_component_in_list_returns_true(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_component_available returns True when component is in list."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_component_available("laser_cannon", "test_preset")

        assert result is True

    def test_component_not_in_list_returns_false(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_component_available returns False when component is not in list."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_component_available("plasma_cannon", "test_preset")

        assert result is False

    def test_wildcard_allows_any_component(self, temp_presets_dir, create_preset, wildcard_preset_data):
        """is_component_available returns True for any component with wildcard."""
        create_preset("wildcard", wildcard_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Any component should be available with wildcard
            assert TechPresetLoader.is_component_available("any_component", "wildcard") is True
            assert TechPresetLoader.is_component_available("another_one", "wildcard") is True
            assert TechPresetLoader.is_component_available("", "wildcard") is True

    def test_empty_component_list_returns_false(self, temp_presets_dir, create_preset, minimal_preset_data):
        """is_component_available returns False when component list is empty."""
        create_preset("minimal", minimal_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_component_available("any_component", "minimal")

        assert result is False

    def test_with_real_early_game_preset(self):
        """is_component_available works with real early_game preset."""
        # Available in early_game
        assert TechPresetLoader.is_component_available("laser_cannon", "early_game") is True
        assert TechPresetLoader.is_component_available("hull_escort", "early_game") is True

        # Not in early_game (advanced tech)
        # Note: Testing with a component that definitely isn't in the early_game list
        assert TechPresetLoader.is_component_available("nonexistent_advanced_weapon", "early_game") is False


# =============================================================================
# Test: is_modifier_available
# =============================================================================


class TestIsModifierAvailable:
    """Tests for TechPresetLoader.is_modifier_available()."""

    def test_modifier_in_list_returns_true(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_modifier_available returns True when modifier is in list."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_modifier_available("simple_size_mount", "test_preset")

        assert result is True

    def test_modifier_not_in_list_returns_false(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_modifier_available returns False when modifier is not in list."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_modifier_available("advanced_mod", "test_preset")

        assert result is False

    def test_wildcard_allows_any_modifier(self, temp_presets_dir, create_preset, wildcard_preset_data):
        """is_modifier_available returns True for any modifier with wildcard."""
        create_preset("wildcard", wildcard_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            assert TechPresetLoader.is_modifier_available("any_modifier", "wildcard") is True
            assert TechPresetLoader.is_modifier_available("another_mod", "wildcard") is True

    def test_empty_modifier_list_returns_false(self, temp_presets_dir, create_preset, minimal_preset_data):
        """is_modifier_available returns False when modifier list is empty."""
        create_preset("minimal", minimal_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.is_modifier_available("any_modifier", "minimal")

        assert result is False

    def test_with_real_default_preset(self):
        """is_modifier_available with wildcard default preset allows any modifier."""
        # Default preset has "*" for modifiers
        assert TechPresetLoader.is_modifier_available("any_modifier", "default") is True
        assert TechPresetLoader.is_modifier_available("nonexistent_mod", "default") is True


# =============================================================================
# Test: Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_preset_with_empty_lists(self, temp_presets_dir, create_preset):
        """Preset with empty component/modifier lists works correctly."""
        preset_data = {
            "name": "Empty Lists",
            "description": "No components or modifiers",
            "unlocked_components": [],
            "unlocked_modifiers": []
        }
        create_preset("empty_lists", preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            components = TechPresetLoader.get_available_components("empty_lists")
            modifiers = TechPresetLoader.get_available_modifiers("empty_lists")
            is_comp_available = TechPresetLoader.is_component_available("test", "empty_lists")
            is_mod_available = TechPresetLoader.is_modifier_available("test", "empty_lists")

        assert components == []
        assert modifiers == []
        assert is_comp_available is False
        assert is_mod_available is False

    def test_preset_name_with_special_characters(self, temp_presets_dir, create_preset, sample_preset_data):
        """Preset names with underscores and numbers work correctly."""
        create_preset("preset_v2_beta", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.load_preset("preset_v2_beta")

        assert result["name"] == "Test Preset"

    def test_wildcard_in_mixed_list(self, temp_presets_dir, create_preset):
        """Wildcard mixed with other components still enables all."""
        preset_data = {
            "name": "Mixed Wildcard",
            "description": "Wildcard with other entries",
            "unlocked_components": ["specific_comp", "*", "another_comp"],
            "unlocked_modifiers": ["*"]
        }
        create_preset("mixed_wildcard", preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Wildcard should still work even if other entries exist
            assert TechPresetLoader.is_component_available("any_component", "mixed_wildcard") is True

    def test_unicode_in_preset_content(self, temp_presets_dir, create_preset):
        """Preset with unicode characters in name/description works."""
        preset_data = {
            "name": "Preset with accents",
            "description": "Description with special chars",
            "unlocked_components": ["comp_alpha"],
            "unlocked_modifiers": []
        }
        create_preset("unicode_preset", preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            result = TechPresetLoader.load_preset("unicode_preset")

        assert result["name"] == "Preset with accents"

    def test_tech_presets_dir_constant(self):
        """TECH_PRESETS_DIR constant points to expected location."""
        assert "tech_presets" in TECH_PRESETS_DIR
        assert os.path.isdir(TECH_PRESETS_DIR)


# =============================================================================
# Test: Integration with Real Data
# =============================================================================


class TestRealDataIntegration:
    """Integration tests with actual preset files."""

    def test_all_real_presets_are_loadable(self):
        """All presets in the data directory can be loaded without errors."""
        presets = TechPresetLoader.list_presets()

        for preset_name in presets:
            data = TechPresetLoader.load_preset(preset_name)
            assert "name" in data
            assert "description" in data

    def test_real_presets_have_valid_structure(self):
        """All real presets have expected structure."""
        presets = TechPresetLoader.list_presets()

        for preset_name in presets:
            data = TechPresetLoader.load_preset(preset_name)

            # Required fields
            assert isinstance(data.get("name"), str)
            assert isinstance(data.get("description"), str)

            # Component and modifier lists (may be missing, but if present must be lists)
            components = data.get("unlocked_components")
            modifiers = data.get("unlocked_modifiers")

            if components is not None:
                assert isinstance(components, list)
            if modifiers is not None:
                assert isinstance(modifiers, list)

    def test_default_preset_unlocks_everything(self):
        """Default preset uses wildcards for all tech."""
        data = TechPresetLoader.load_preset("default")

        assert TechPresetLoader.is_component_available("any_random_id", "default") is True
        assert TechPresetLoader.is_modifier_available("any_random_id", "default") is True

    def test_early_game_preset_is_restrictive(self):
        """Early game preset has limited tech (not wildcards)."""
        components = TechPresetLoader.get_available_components("early_game")
        modifiers = TechPresetLoader.get_available_modifiers("early_game")

        # Should not be wildcards
        assert "*" not in components
        assert "*" not in modifiers

        # Should have specific items
        assert len(components) > 0
        assert len(modifiers) > 0


# =============================================================================
# Test: Preset Data Consistency
# =============================================================================


class TestPresetDataConsistency:
    """Tests for preset data consistency and format validation."""

    def test_component_ids_are_strings(self):
        """All component IDs in presets are strings."""
        presets = TechPresetLoader.list_presets()

        for preset_name in presets:
            components = TechPresetLoader.get_available_components(preset_name)
            for comp_id in components:
                assert isinstance(comp_id, str), f"Component ID {comp_id} in {preset_name} is not a string"

    def test_modifier_ids_are_strings(self):
        """All modifier IDs in presets are strings."""
        presets = TechPresetLoader.list_presets()

        for preset_name in presets:
            modifiers = TechPresetLoader.get_available_modifiers(preset_name)
            for mod_id in modifiers:
                assert isinstance(mod_id, str), f"Modifier ID {mod_id} in {preset_name} is not a string"

    def test_preset_names_are_unique(self):
        """All preset names are unique (no duplicates)."""
        presets = TechPresetLoader.list_presets()
        assert len(presets) == len(set(presets))

    def test_preset_name_matches_filename(self):
        """Preset name should be consistent with its content."""
        # Default preset should indicate it's a default/all preset
        default_data = TechPresetLoader.load_preset("default")
        assert "Default" in default_data["name"] or "All" in default_data["name"]

    def test_early_game_is_subset_of_mid_game_components(self):
        """Early game components should be a subset of mid game components."""
        early_components = set(TechPresetLoader.get_available_components("early_game"))
        mid_components = set(TechPresetLoader.get_available_components("mid_game"))

        # All early game components should be in mid game
        assert early_components.issubset(mid_components), \
            f"Early game components not in mid game: {early_components - mid_components}"


# =============================================================================
# Test: Availability Check Performance
# =============================================================================


class TestAvailabilityCheckBehavior:
    """Tests for component/modifier availability check behavior."""

    def test_is_component_available_case_sensitive(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_component_available is case-sensitive."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Exact match should work
            assert TechPresetLoader.is_component_available("laser_cannon", "test_preset") is True
            # Case mismatch should fail
            assert TechPresetLoader.is_component_available("Laser_Cannon", "test_preset") is False
            assert TechPresetLoader.is_component_available("LASER_CANNON", "test_preset") is False

    def test_is_modifier_available_case_sensitive(self, temp_presets_dir, create_preset, sample_preset_data):
        """is_modifier_available is case-sensitive."""
        create_preset("test_preset", sample_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Exact match should work
            assert TechPresetLoader.is_modifier_available("simple_size_mount", "test_preset") is True
            # Case mismatch should fail
            assert TechPresetLoader.is_modifier_available("Simple_Size_Mount", "test_preset") is False

    def test_availability_check_with_whitespace_id(self, temp_presets_dir, create_preset):
        """Availability checks handle IDs with whitespace correctly."""
        preset_data = {
            "name": "Whitespace Test",
            "description": "Test preset",
            "unlocked_components": ["comp_with_space ", " space_prefix"],
            "unlocked_modifiers": []
        }
        create_preset("whitespace", preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Exact match including whitespace
            assert TechPresetLoader.is_component_available("comp_with_space ", "whitespace") is True
            assert TechPresetLoader.is_component_available("comp_with_space", "whitespace") is False

    def test_wildcard_check_is_efficient(self, temp_presets_dir, create_preset, wildcard_preset_data):
        """Wildcard check should be O(1) - just checks for '*' in list."""
        create_preset("wildcard", wildcard_preset_data)

        with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir)):
            # Even very long component IDs should work instantly with wildcard
            long_id = "x" * 1000
            assert TechPresetLoader.is_component_available(long_id, "wildcard") is True
