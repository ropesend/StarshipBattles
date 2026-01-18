"""
Tests for TechPresetLoader.

Following TDD approach: write tests first (RED), then implement (GREEN).
"""
import pytest
import os
from game.simulation.systems.tech_preset_loader import TechPresetLoader


class TestTechPresetLoaderListPresets:
    """Tests for listing available presets."""

    def test_list_presets_returns_list(self):
        """list_presets() returns a list of preset names."""
        presets = TechPresetLoader.list_presets()

        assert isinstance(presets, list)

    def test_list_presets_includes_default(self):
        """list_presets() includes 'default' preset."""
        presets = TechPresetLoader.list_presets()

        assert "default" in presets

    def test_list_presets_includes_early_game(self):
        """list_presets() includes 'early_game' preset."""
        presets = TechPresetLoader.list_presets()

        assert "early_game" in presets

    def test_list_presets_includes_mid_game(self):
        """list_presets() includes 'mid_game' preset."""
        presets = TechPresetLoader.list_presets()

        assert "mid_game" in presets

    def test_list_presets_excludes_extensions(self):
        """list_presets() returns names without .json extension."""
        presets = TechPresetLoader.list_presets()

        for preset in presets:
            assert not preset.endswith('.json')


class TestTechPresetLoaderLoadPreset:
    """Tests for loading preset data."""

    def test_load_preset_returns_dict(self):
        """load_preset() returns a dictionary."""
        data = TechPresetLoader.load_preset("default")

        assert isinstance(data, dict)

    def test_load_preset_has_name_field(self):
        """Loaded preset has 'name' field."""
        data = TechPresetLoader.load_preset("default")

        assert "name" in data
        assert isinstance(data["name"], str)

    def test_load_preset_has_description_field(self):
        """Loaded preset has 'description' field."""
        data = TechPresetLoader.load_preset("default")

        assert "description" in data
        assert isinstance(data["description"], str)

    def test_load_preset_has_unlocked_components(self):
        """Loaded preset has 'unlocked_components' field."""
        data = TechPresetLoader.load_preset("default")

        assert "unlocked_components" in data
        assert isinstance(data["unlocked_components"], list)

    def test_load_preset_has_unlocked_modifiers(self):
        """Loaded preset has 'unlocked_modifiers' field."""
        data = TechPresetLoader.load_preset("default")

        assert "unlocked_modifiers" in data
        assert isinstance(data["unlocked_modifiers"], list)

    def test_load_preset_default_has_wildcard(self):
        """Default preset uses '*' wildcard for all components."""
        data = TechPresetLoader.load_preset("default")

        assert "*" in data["unlocked_components"]
        assert "*" in data["unlocked_modifiers"]

    def test_load_preset_early_game_has_specific_components(self):
        """Early game preset lists specific components."""
        data = TechPresetLoader.load_preset("early_game")

        assert "laser_cannon" in data["unlocked_components"]
        assert "railgun" in data["unlocked_components"]
        assert "*" not in data["unlocked_components"]

    def test_load_preset_raises_on_missing_file(self):
        """load_preset() raises FileNotFoundError for missing preset."""
        with pytest.raises(FileNotFoundError):
            TechPresetLoader.load_preset("nonexistent_preset")


class TestTechPresetLoaderGetAvailableComponents:
    """Tests for getting available component IDs."""

    def test_get_available_components_default_returns_wildcard(self):
        """Default preset returns ['*'] for components."""
        components = TechPresetLoader.get_available_components("default")

        assert "*" in components

    def test_get_available_components_early_game_returns_list(self):
        """Early game preset returns list of specific component IDs."""
        components = TechPresetLoader.get_available_components("early_game")

        assert isinstance(components, list)
        assert len(components) > 0
        assert "laser_cannon" in components

    def test_get_available_components_mid_game_has_more_than_early(self):
        """Mid game preset has more components than early game."""
        early_components = TechPresetLoader.get_available_components("early_game")
        mid_components = TechPresetLoader.get_available_components("mid_game")

        # Mid game should include all early game components plus more
        assert len(mid_components) > len(early_components)

    def test_get_available_components_raises_on_missing_preset(self):
        """get_available_components() raises FileNotFoundError for missing preset."""
        with pytest.raises(FileNotFoundError):
            TechPresetLoader.get_available_components("nonexistent_preset")


class TestTechPresetLoaderGetAvailableModifiers:
    """Tests for getting available modifier IDs."""

    def test_get_available_modifiers_default_returns_wildcard(self):
        """Default preset returns ['*'] for modifiers."""
        modifiers = TechPresetLoader.get_available_modifiers("default")

        assert "*" in modifiers

    def test_get_available_modifiers_early_game_returns_list(self):
        """Early game preset returns list of specific modifier IDs."""
        modifiers = TechPresetLoader.get_available_modifiers("early_game")

        assert isinstance(modifiers, list)
        assert len(modifiers) > 0

    def test_get_available_modifiers_raises_on_missing_preset(self):
        """get_available_modifiers() raises FileNotFoundError for missing preset."""
        with pytest.raises(FileNotFoundError):
            TechPresetLoader.get_available_modifiers("nonexistent_preset")


class TestTechPresetLoaderFileLocations:
    """Tests for file path resolution."""

    def test_presets_directory_exists(self):
        """Tech presets directory exists in data/tech_presets/."""
        from game.simulation.systems.tech_preset_loader import TECH_PRESETS_DIR

        assert os.path.exists(TECH_PRESETS_DIR)
        assert os.path.isdir(TECH_PRESETS_DIR)

    def test_default_preset_file_exists(self):
        """default.json exists in tech presets directory."""
        from game.simulation.systems.tech_preset_loader import TECH_PRESETS_DIR

        default_path = os.path.join(TECH_PRESETS_DIR, "default.json")
        assert os.path.exists(default_path)

    def test_early_game_preset_file_exists(self):
        """early_game.json exists in tech presets directory."""
        from game.simulation.systems.tech_preset_loader import TECH_PRESETS_DIR

        early_path = os.path.join(TECH_PRESETS_DIR, "early_game.json")
        assert os.path.exists(early_path)


class TestTechPresetLoaderCaching:
    """Tests for preset data caching (optional optimization)."""

    def test_load_preset_is_idempotent(self):
        """Loading same preset twice returns identical data."""
        data1 = TechPresetLoader.load_preset("default")
        data2 = TechPresetLoader.load_preset("default")

        assert data1 == data2

    def test_multiple_preset_loads_work(self):
        """Can load multiple different presets."""
        default_data = TechPresetLoader.load_preset("default")
        early_data = TechPresetLoader.load_preset("early_game")

        assert default_data != early_data
        assert default_data["name"] != early_data["name"]
