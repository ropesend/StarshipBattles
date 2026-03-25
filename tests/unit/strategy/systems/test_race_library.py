"""
Unit tests for RaceLibrary service.
"""
import pytest
import tempfile
import os
import shutil

from game.strategy.data.race_config import RaceConfig
from game.core.string_utils import slugify
from game.strategy.systems.race_library import RaceLibrary


class TestSlugify:
    """Tests for the slugify helper function (now in game.core.string_utils)."""

    def test_slugify_simple_name(self):
        """Test slugifying a simple name."""
        assert slugify("Test Race") == "test_race"

    def test_slugify_mixed_case(self):
        """Test slugifying mixed case."""
        assert slugify("TeStRaCe") == "testrace"

    def test_slugify_special_characters(self):
        """Test slugifying with special characters."""
        assert slugify("Test@Race!#123") == "testrace123"

    def test_slugify_hyphens(self):
        """Test slugifying with hyphens."""
        assert slugify("Test-Race-Name") == "test_race_name"

    def test_slugify_multiple_spaces(self):
        """Test slugifying with multiple spaces."""
        assert slugify("Test   Race") == "test_race"

    def test_slugify_empty_string(self):
        """Test slugifying empty string."""
        assert slugify("") == ""

    def test_slugify_only_special_chars(self):
        """Test slugifying string with only special characters."""
        assert slugify("@#$%") == ""

    def test_slugify_long_name(self):
        """Test slugifying a very long name (no length limit in core slugify)."""
        long_name = "A" * 100
        result = slugify(long_name)
        assert result == "a" * 100  # Core slugify doesn't truncate


class TestRaceLibraryBasic:
    """Basic RaceLibrary functionality tests."""

    @pytest.fixture
    def temp_races_folder(self):
        """Create a temporary folder for races."""
        folder = tempfile.mkdtemp()
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_init_default_folder(self):
        """Test RaceLibrary initializes with default folder."""
        lib = RaceLibrary()
        assert lib.races_folder is not None
        assert "races" in lib.races_folder

    def test_init_custom_folder(self, temp_races_folder):
        """Test RaceLibrary initializes with custom folder."""
        lib = RaceLibrary(temp_races_folder)
        assert lib.races_folder == temp_races_folder

    def test_get_all_races_empty_folder(self, temp_races_folder):
        """Test getting races from empty folder."""
        lib = RaceLibrary(temp_races_folder)
        races = lib.get_all_races()
        assert races == []

    def test_get_all_races_nonexistent_folder(self):
        """Test getting races from nonexistent folder."""
        lib = RaceLibrary("/nonexistent/path/races")
        races = lib.get_all_races()
        assert races == []

    def test_get_race_count_empty(self, temp_races_folder):
        """Test race count for empty folder."""
        lib = RaceLibrary(temp_races_folder)
        assert lib.get_race_count() == 0

    def test_race_exists_false(self, temp_races_folder):
        """Test race_exists returns False for nonexistent race."""
        lib = RaceLibrary(temp_races_folder)
        assert lib.race_exists("nonexistent_race") is False


class TestRaceLibrarySaveLoad:
    """RaceLibrary save/load tests."""

    @pytest.fixture
    def temp_races_folder(self):
        """Create a temporary folder for races."""
        folder = tempfile.mkdtemp()
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_save_race_creates_folder(self):
        """Test that save_race creates the races folder if needed."""
        folder = tempfile.mkdtemp()
        races_folder = os.path.join(folder, "new_races")

        try:
            lib = RaceLibrary(races_folder)
            config = RaceConfig(
                name="Test Race",
                flag_id="flag_001",
                portrait_id="portrait.jpg",
                theme_id="Federation",
            )

            success, message = lib.save_race(config)

            assert success is True
            assert os.path.exists(races_folder)

        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_save_race_generates_id(self, temp_races_folder):
        """Test that save_race generates an ID if not provided."""
        lib = RaceLibrary(temp_races_folder)
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )

        assert config.race_id == ""

        success, message = lib.save_race(config)

        assert success is True
        assert config.race_id != ""
        assert "test_race" in config.race_id

    def test_save_race_preserves_id(self, temp_races_folder):
        """Test that save_race preserves existing ID."""
        lib = RaceLibrary(temp_races_folder)
        config = RaceConfig(
            race_id="my_custom_id",
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )

        success, message = lib.save_race(config)

        assert success is True
        assert config.race_id == "my_custom_id"
        assert os.path.exists(os.path.join(temp_races_folder, "my_custom_id.json"))

    def test_save_and_load_race(self, temp_races_folder):
        """Test saving and loading a race."""
        lib = RaceLibrary(temp_races_folder)
        config = RaceConfig(
            race_id="save_load_test",
            name="Save Load Race",
            flag_id="flag_sl",
            portrait_id="sl_portrait.jpg",
            theme_id="Klingons",
            gravity_ideal=1.5,
            bio_description="Test description",
        )

        # Save
        success, message = lib.save_race(config)
        assert success is True

        # Load
        loaded = lib.get_race("save_load_test")

        assert loaded is not None
        assert loaded.race_id == "save_load_test"
        assert loaded.name == "Save Load Race"
        assert loaded.flag_id == "flag_sl"
        assert loaded.portrait_id == "sl_portrait.jpg"
        assert loaded.theme_id == "Klingons"
        assert loaded.gravity_ideal == 1.5
        assert loaded.bio_description == "Test description"

    def test_get_race_nonexistent(self, temp_races_folder):
        """Test getting a race that doesn't exist."""
        lib = RaceLibrary(temp_races_folder)
        result = lib.get_race("nonexistent_race")
        assert result is None


class TestRaceLibraryList:
    """RaceLibrary listing tests."""

    @pytest.fixture
    def populated_library(self):
        """Create a library with multiple races."""
        folder = tempfile.mkdtemp()
        lib = RaceLibrary(folder)

        # Add several races
        races = [
            RaceConfig(race_id="race_a", name="Alpha Race", flag_id="f1",
                      portrait_id="p1.jpg", theme_id="Federation"),
            RaceConfig(race_id="race_b", name="Beta Race", flag_id="f2",
                      portrait_id="p2.jpg", theme_id="Klingons"),
            RaceConfig(race_id="race_c", name="Charlie Race", flag_id="f3",
                      portrait_id="p3.jpg", theme_id="Romulans"),
        ]

        for race in races:
            lib.save_race(race)

        yield lib, folder

        shutil.rmtree(folder, ignore_errors=True)

    def test_get_all_races_returns_all(self, populated_library):
        """Test that get_all_races returns all saved races."""
        lib, folder = populated_library

        races = lib.get_all_races()

        assert len(races) == 3
        race_ids = [r.race_id for r in races]
        assert "race_a" in race_ids
        assert "race_b" in race_ids
        assert "race_c" in race_ids

    def test_get_all_races_sorted_by_name(self, populated_library):
        """Test that get_all_races returns races sorted by name."""
        lib, folder = populated_library

        races = lib.get_all_races()

        names = [r.name for r in races]
        assert names == ["Alpha Race", "Beta Race", "Charlie Race"]

    def test_get_race_count(self, populated_library):
        """Test race count with multiple races."""
        lib, folder = populated_library

        assert lib.get_race_count() == 3

    def test_race_exists(self, populated_library):
        """Test race_exists returns correct status."""
        lib, folder = populated_library

        assert lib.race_exists("race_a") is True
        assert lib.race_exists("race_b") is True
        assert lib.race_exists("nonexistent") is False


class TestRaceLibraryDelete:
    """RaceLibrary delete tests."""

    @pytest.fixture
    def temp_races_folder(self):
        """Create a temporary folder for races."""
        folder = tempfile.mkdtemp()
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_delete_race(self, temp_races_folder):
        """Test deleting a race."""
        lib = RaceLibrary(temp_races_folder)
        config = RaceConfig(
            race_id="to_delete",
            name="Delete Me",
            flag_id="f1",
            portrait_id="p1.jpg",
            theme_id="Federation",
        )

        # Save
        lib.save_race(config)
        assert lib.race_exists("to_delete") is True

        # Delete
        result = lib.delete_race("to_delete")

        assert result is True
        assert lib.race_exists("to_delete") is False

    def test_delete_nonexistent_race(self, temp_races_folder):
        """Test deleting a race that doesn't exist."""
        lib = RaceLibrary(temp_races_folder)

        result = lib.delete_race("nonexistent")

        assert result is False


class TestRaceLibraryIDGeneration:
    """RaceLibrary ID generation tests."""

    @pytest.fixture
    def temp_races_folder(self):
        """Create a temporary folder for races."""
        folder = tempfile.mkdtemp()
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_generate_race_id_from_name(self, temp_races_folder):
        """Test ID generation from name."""
        lib = RaceLibrary(temp_races_folder)

        id1 = lib._generate_race_id("Test Race")

        assert "test_race" in id1
        assert len(id1) > len("test_race")  # Has UUID suffix

    def test_generate_race_id_unique(self, temp_races_folder):
        """Test that generated IDs are unique."""
        lib = RaceLibrary(temp_races_folder)

        ids = [lib._generate_race_id("Same Name") for _ in range(10)]

        # All IDs should be unique
        assert len(set(ids)) == 10

    def test_generate_race_id_empty_name(self, temp_races_folder):
        """Test ID generation with empty name."""
        lib = RaceLibrary(temp_races_folder)

        race_id = lib._generate_race_id("")

        assert race_id.startswith("race_")
