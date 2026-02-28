"""
Tests for RaceRandomizer - random race generation for species setup.
"""
import pytest
from unittest.mock import patch

from game.strategy.data.race_config import (
    GOVERNMENT_TYPES,
    GOVERNMENT_ORGANIZATIONS,
    LEADER_TITLES,
    PHYSICAL_TYPES,
    SOCIETY_TYPES,
)


class TestRaceRandomizerIdentity:
    """Tests for identity field randomization."""

    def test_randomize_identity_sets_race_name(self):
        """Randomized identity has a non-empty race name."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["race_name"]
        assert len(result["race_name"]) > 0

    def test_randomize_identity_sets_plural(self):
        """Randomized identity has a non-empty plural form."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["race_name_plural"]
        assert len(result["race_name_plural"]) > 0

    def test_randomize_identity_sets_leader_name(self):
        """Randomized identity has a non-empty leader name."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["leader_name"]
        assert len(result["leader_name"]) > 0

    def test_randomize_identity_selects_valid_physical_type(self):
        """Physical type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["physical_type"] in PHYSICAL_TYPES

    def test_randomize_identity_selects_valid_government_type(self):
        """Government type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["government_type"] in GOVERNMENT_TYPES

    def test_randomize_identity_selects_valid_government_org(self):
        """Government organization is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["government_organization"] in GOVERNMENT_ORGANIZATIONS

    def test_randomize_identity_selects_valid_leader_title(self):
        """Leader title is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["leader_title"] in LEADER_TITLES

    def test_randomize_identity_selects_valid_society_type(self):
        """Society type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["society_type"] in SOCIETY_TYPES

    def test_randomize_identity_generates_faction_name(self):
        """Faction name is generated from race name and government type."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["faction_name"]
        assert result["race_name"] in result["faction_name"]
        assert result["government_type"] in result["faction_name"]


class TestRaceRandomizerPortraitAware:
    """Tests for portrait-aware name generation."""

    def test_randomize_identity_with_portrait_uses_portrait_names(self):
        """When a portrait ID is given, names come from the portrait data."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        # Use a known portrait ID from the data file
        portrait_id = "Gemini_Generated_Image_59rl4259rl4259rl.jpg"
        result = RaceRandomizer.randomize_identity(portrait_id=portrait_id)

        # Should be one of the portrait-specific names
        expected_names = ["Syntheran", "Korvex", "Mechara", "Cypherite"]
        assert result["race_name"] in expected_names

    def test_randomize_identity_with_unknown_portrait_uses_fallback(self):
        """Unknown portrait ID falls back to generic names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity(portrait_id="nonexistent.jpg")
        assert result["race_name"]
        assert len(result["race_name"]) > 0

    def test_randomize_identity_without_portrait_uses_fallback(self):
        """No portrait ID uses fallback names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity(portrait_id=None)
        assert result["race_name"]


class TestRaceRandomizerVisuals:
    """Tests for visual randomization (flag + portrait selection)."""

    def test_randomize_flag_returns_valid_id(self):
        """Randomized flag ID is from the available flags list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        available_flags = ["flag_abc", "flag_def", "flag_ghi"]
        result = RaceRandomizer.randomize_flag(available_flags)
        assert result in available_flags

    def test_randomize_flag_empty_list_returns_empty(self):
        """Empty flag list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_flag([])
        assert result == ""

    def test_randomize_portrait_returns_valid_id(self):
        """Randomized portrait ID is from the available portraits list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        available = ["portrait_a.jpg", "portrait_b.jpg"]
        result = RaceRandomizer.randomize_portrait(available)
        assert result in available

    def test_randomize_portrait_empty_list_returns_empty(self):
        """Empty portrait list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_portrait([])
        assert result == ""


class TestRaceRandomizerShips:
    """Tests for ship theme randomization."""

    def test_randomize_theme_returns_valid_id(self):
        """Randomized theme is from the available themes list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        themes = ["Federation", "Klingons", "Romulans"]
        result = RaceRandomizer.randomize_theme(themes)
        assert result in themes

    def test_randomize_theme_empty_list_returns_empty(self):
        """Empty theme list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_theme([])
        assert result == ""


class TestRaceNamesDataFile:
    """Tests for race_names.json data integrity."""

    def test_race_names_file_loads(self):
        """Race names JSON file loads successfully."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert data is not None
        assert "portraits" in data

    def test_race_names_has_fallback_names(self):
        """Data file contains fallback names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert "fallback_names" in data
        assert len(data["fallback_names"]) > 0

    def test_race_names_has_fallback_leaders(self):
        """Data file contains fallback leader names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert "fallback_leaders" in data
        assert len(data["fallback_leaders"]) > 0

    def test_portrait_entries_have_required_fields(self):
        """Each portrait entry has names and leaders."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        for portrait_id, entry in data["portraits"].items():
            assert "names" in entry, f"Missing 'names' for {portrait_id}"
            assert "leaders" in entry, f"Missing 'leaders' for {portrait_id}"
            assert len(entry["names"]) > 0, f"Empty 'names' for {portrait_id}"
            assert len(entry["leaders"]) > 0, f"Empty 'leaders' for {portrait_id}"

    def test_name_entries_have_name_and_plural(self):
        """Each name entry has both 'name' and 'plural' fields."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        for portrait_id, entry in data["portraits"].items():
            for name_entry in entry["names"]:
                assert "name" in name_entry, f"Missing 'name' in {portrait_id}"
                assert "plural" in name_entry, f"Missing 'plural' in {portrait_id}"
