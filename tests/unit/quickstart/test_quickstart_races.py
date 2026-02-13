"""
Tests for quickstart race fixtures.

These tests validate that the race fixtures used by quickstart buttons
are valid and can be loaded correctly. They also detect when code changes
break the fixture format.
"""
import pytest
from pathlib import Path

from game.strategy.data.race_config import RaceConfig
from game.core.json_utils import load_json
from tests.unit.quickstart.conftest import (
    get_quickstart_races_dir,
    load_all_quickstart_races,
)


# Load all quickstart race fixtures for parametrized tests
QUICKSTART_RACES = load_all_quickstart_races()


class TestQuickstartRaceFixturesExist:
    """Test that fixture files exist and are valid JSON."""

    def test_quickstart_races_directory_exists(self, quickstart_races_dir):
        """The quickstart races directory should exist."""
        assert quickstart_races_dir.exists(), "Quickstart races directory should exist"
        assert quickstart_races_dir.is_dir()

    def test_quickstart_races_not_empty(self):
        """Should have at least one quickstart race fixture."""
        assert len(QUICKSTART_RACES) > 0, "Should have at least one quickstart race fixture"

    def test_has_test_emp1(self, quickstart_races_dir):
        """Should have test_emp1.json fixture."""
        assert (quickstart_races_dir / "test_emp1.json").exists()

    def test_has_test_emp2(self, quickstart_races_dir):
        """Should have test_emp2.json fixture."""
        assert (quickstart_races_dir / "test_emp2.json").exists()


@pytest.mark.parametrize("race_name,race_data", QUICKSTART_RACES, ids=lambda x: x if isinstance(x, str) else x[0] if isinstance(x, tuple) else "unknown")
class TestQuickstartRacesValid:
    """Data-driven tests for quickstart race fixture validity."""

    def test_race_loads_as_valid_config(self, race_name, race_data):
        """Each quickstart race should load as a valid RaceConfig."""
        config = RaceConfig.from_dict(race_data)
        assert config is not None
        assert config.name, f"{race_name} must have a name"

    def test_race_has_required_fields(self, race_name, race_data):
        """Each quickstart race should have all required fields."""
        required_fields = ["race_id", "name", "flag_id", "portrait_id", "theme_id"]
        for field in required_fields:
            assert field in race_data, f"{race_name} missing required field: {field}"
            assert race_data[field], f"{race_name} has empty {field}"

    def test_race_passes_validation(self, race_name, race_data):
        """Each quickstart race should pass RaceConfig validation."""
        config = RaceConfig.from_dict(race_data)
        result = config.validate()
        assert result.is_valid, f"{race_name} validation failed: {result.first_error}"

    def test_race_is_complete(self, race_name, race_data):
        """Each quickstart race should be complete."""
        config = RaceConfig.from_dict(race_data)
        assert config.is_complete(), f"{race_name} should be complete"

    def test_race_round_trip_serialization(self, race_name, race_data):
        """Data should survive round-trip serialization."""
        config = RaceConfig.from_dict(race_data)
        serialized = config.to_dict()
        config2 = RaceConfig.from_dict(serialized)

        assert config2.race_id == config.race_id
        assert config2.name == config.name
        assert config2.flag_id == config.flag_id
        assert config2.portrait_id == config.portrait_id
        assert config2.theme_id == config.theme_id

    def test_race_has_valid_theme(self, race_name, race_data):
        """Each quickstart race should use a valid ship theme."""
        valid_themes = ["Federation", "Atlantians", "Romulans", "Klingons"]
        assert race_data["theme_id"] in valid_themes, \
            f"{race_name} has invalid theme: {race_data['theme_id']}"


class TestQuickstartRaceSpecificContent:
    """Tests for specific expected content in quickstart races."""

    def test_emp1_uses_federation_theme(self, quickstart_races_dir):
        """TestEmp1 should use Federation theme."""
        data = load_json(str(quickstart_races_dir / "test_emp1.json"))
        assert data["theme_id"] == "Federation"

    def test_emp2_uses_atlantians_theme(self, quickstart_races_dir):
        """TestEmp2 should use Atlantians theme."""
        data = load_json(str(quickstart_races_dir / "test_emp2.json"))
        assert data["theme_id"] == "Atlantians"

    def test_emp1_and_emp2_have_different_flags(self, quickstart_races_dir):
        """TestEmp1 and TestEmp2 should have different flag IDs."""
        emp1 = load_json(str(quickstart_races_dir / "test_emp1.json"))
        emp2 = load_json(str(quickstart_races_dir / "test_emp2.json"))
        assert emp1["flag_id"] != emp2["flag_id"], "Empires should have different flags"

    def test_emp1_and_emp2_have_different_portraits(self, quickstart_races_dir):
        """TestEmp1 and TestEmp2 should have different portrait IDs."""
        emp1 = load_json(str(quickstart_races_dir / "test_emp1.json"))
        emp2 = load_json(str(quickstart_races_dir / "test_emp2.json"))
        assert emp1["portrait_id"] != emp2["portrait_id"], "Empires should have different portraits"
