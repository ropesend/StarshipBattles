"""
Unit tests for RaceLibrary service.
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import MagicMock

from game.strategy.data.race_config import RaceConfig
from game.core.string_utils import slugify
from game.core.protocols import IRaceRegistry
from game.strategy.systems.race_library import RaceLibrary, CachedRaceRegistry


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
        """Test saving and loading a race.

        PROJ-283 Phase 4: legacy `gravity_ideal` field deleted; gravity
        preference is now expressed via `preferences["gravity"].setpoint`
        (m/s², so 1.5 g = 14.715 m/s²)."""
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.habitability_factors import get_factor

        lib = RaceLibrary(temp_races_folder)
        config = RaceConfig(
            race_id="save_load_test",
            name="Save Load Race",
            flag_id="flag_sl",
            portrait_id="sl_portrait.jpg",
            theme_id="Klingons",
            bio_description="Test description",
        )
        gravity = get_factor("gravity")
        config.preferences["gravity"] = EnvironmentalPreference(
            setpoint=1.5 * 9.81, tolerance=gravity.default_tolerance,
            min_value=gravity.min_value, max_value=gravity.max_value,
            step=gravity.step,
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
        assert loaded.preferences["gravity"].setpoint == pytest.approx(1.5 * 9.81)
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


class TestCachedRaceRegistry:
    """PROJ-287: Session-scoped in-memory cache over RaceLibrary.

    Verifies the IRaceRegistry contract: hits and misses are cached, and
    invalidate() clears entries so freshly-saved races are picked up.
    """

    def _make_race(self, race_id):
        return RaceConfig(
            race_id=race_id,
            name=race_id.title(),
            flag_id="flag",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )

    def test_first_call_delegates_to_backing_library(self):
        """First get_race call must hit the backing library."""
        backing = MagicMock(spec=RaceLibrary)
        race = self._make_race("foo")
        backing.get_race.return_value = race

        registry = CachedRaceRegistry(backing)
        result = registry.get_race("foo")

        assert result is race
        backing.get_race.assert_called_once_with("foo")

    def test_second_call_uses_cache(self):
        """Second get_race call for the same id must NOT hit the backing library."""
        backing = MagicMock(spec=RaceLibrary)
        race = self._make_race("foo")
        backing.get_race.return_value = race

        registry = CachedRaceRegistry(backing)
        registry.get_race("foo")
        registry.get_race("foo")

        assert backing.get_race.call_count == 1

    def test_missing_race_returns_none_and_caches_none(self):
        """Missing races return None AND the None is cached (no re-query)."""
        backing = MagicMock(spec=RaceLibrary)
        backing.get_race.return_value = None

        registry = CachedRaceRegistry(backing)
        first = registry.get_race("missing")
        second = registry.get_race("missing")

        assert first is None
        assert second is None
        assert backing.get_race.call_count == 1

    def test_invalidate_specific_id_clears_one_entry(self):
        """invalidate(race_id) clears that entry; next get_race re-queries."""
        backing = MagicMock(spec=RaceLibrary)
        race_a = self._make_race("a")
        race_b = self._make_race("b")
        backing.get_race.side_effect = lambda rid: {"a": race_a, "b": race_b}.get(rid)

        registry = CachedRaceRegistry(backing)
        registry.get_race("a")
        registry.get_race("b")
        backing.get_race.reset_mock()

        registry.invalidate("a")

        registry.get_race("a")  # Should re-query
        registry.get_race("b")  # Should still be cached

        backing.get_race.assert_called_once_with("a")

    def test_invalidate_no_args_clears_all_entries(self):
        """invalidate() with no args clears the entire cache."""
        backing = MagicMock(spec=RaceLibrary)
        race_a = self._make_race("a")
        race_b = self._make_race("b")
        backing.get_race.side_effect = lambda rid: {"a": race_a, "b": race_b}.get(rid)

        registry = CachedRaceRegistry(backing)
        registry.get_race("a")
        registry.get_race("b")
        backing.get_race.reset_mock()

        registry.invalidate()

        registry.get_race("a")
        registry.get_race("b")

        assert backing.get_race.call_count == 2

    def test_invalidate_unknown_id_is_noop(self):
        """invalidate(race_id) for an uncached id must not raise."""
        backing = MagicMock(spec=RaceLibrary)
        registry = CachedRaceRegistry(backing)

        registry.invalidate("never_cached")  # Must not raise

    def test_conforms_to_iraceregistry_protocol(self):
        """CachedRaceRegistry must satisfy the IRaceRegistry runtime_checkable Protocol."""
        backing = MagicMock(spec=RaceLibrary)
        registry = CachedRaceRegistry(backing)

        assert isinstance(registry, IRaceRegistry)


# ---------------------------------------------------------------------------
# PROJ-292 Phase 3 Task 3.4 (M2): pin the cache invalidation contract.
# PROJ-287 shipped without coverage for the invalidation path. Per
# decisions.md, PROJ-292 does NOT add an mtime-fallback (taking the
# documented "explicit invalidate only" default). These tests pin the
# manual-invalidate behaviour so future refactors can't silently break it.
# ---------------------------------------------------------------------------


def _minimal_race(race_id: str, name: str) -> RaceConfig:
    return RaceConfig(
        race_id=race_id,
        name=name,
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


class TestCachedRaceRegistryStaleness:
    """`CachedRaceRegistry.invalidate(race_id)` is the one and only
    supported path for refreshing cached entries. PROJ-287 documented
    this ("external file edits require restart"); these tests pin the
    behaviour so a future refactor can't silently break it."""

    def test_invalidate_causes_reread(self):
        """Cached then invalidated: next `get_race` must delegate to the
        backing library again and return the new value."""
        config_a = _minimal_race("foo", "Foo-A")
        config_b = _minimal_race("foo", "Foo-B")
        backing = MagicMock(spec=RaceLibrary)
        backing.get_race.side_effect = [config_a, config_b]

        registry = CachedRaceRegistry(backing)

        # First call populates cache from backing.
        assert registry.get_race("foo") is config_a
        # Second call hits the cache — side_effect NOT advanced.
        assert registry.get_race("foo") is config_a
        assert backing.get_race.call_count == 1

        # Invalidate + refetch triggers a second backing call.
        registry.invalidate("foo")
        assert registry.get_race("foo") is config_b
        assert backing.get_race.call_count == 2

    def test_invalidate_other_race_does_not_affect_cached(self):
        """Targeted `invalidate(X)` must only clear X. Other cached
        entries continue to serve from cache."""
        config_foo = _minimal_race("foo", "Foo")
        config_bar = _minimal_race("bar", "Bar")
        backing = MagicMock(spec=RaceLibrary)
        backing.get_race.side_effect = lambda race_id: {
            "foo": config_foo,
            "bar": config_bar,
        }.get(race_id)

        registry = CachedRaceRegistry(backing)
        # Prime both entries.
        registry.get_race("foo")
        registry.get_race("bar")
        assert backing.get_race.call_count == 2

        registry.invalidate("foo")
        # "bar" still cached — no backing call.
        registry.get_race("bar")
        assert backing.get_race.call_count == 2

        # "foo" re-reads on next access.
        registry.get_race("foo")
        assert backing.get_race.call_count == 3

    def test_invalidate_all_clears_every_entry(self):
        """`invalidate()` with no arg must clear the whole cache so
        every subsequent `get_race` re-reads from the backing library."""
        configs = {
            "a": _minimal_race("a", "A"),
            "b": _minimal_race("b", "B"),
            "c": _minimal_race("c", "C"),
        }
        backing = MagicMock(spec=RaceLibrary)
        backing.get_race.side_effect = lambda race_id: configs.get(race_id)

        registry = CachedRaceRegistry(backing)
        registry.get_race("a")
        registry.get_race("b")
        registry.get_race("c")
        assert backing.get_race.call_count == 3

        registry.invalidate()  # no arg → clear everything

        registry.get_race("a")
        registry.get_race("b")
        registry.get_race("c")
        assert backing.get_race.call_count == 6

    def test_none_result_is_cached_and_invalidated_the_same_way(self):
        """A `None` lookup result (unknown race_id) must cache + invalidate
        identically to a hit so save-drift species don't spam the
        backing library across repeated UI renders."""
        backing = MagicMock(spec=RaceLibrary)
        backing.get_race.side_effect = [None, _minimal_race("ghost", "Found")]

        registry = CachedRaceRegistry(backing)

        # First lookup: None is cached.
        assert registry.get_race("ghost") is None
        # Second lookup: cached None served without re-reading.
        assert registry.get_race("ghost") is None
        assert backing.get_race.call_count == 1

        # Invalidate: next lookup re-reads and now returns a real config.
        registry.invalidate("ghost")
        result = registry.get_race("ghost")
        assert result is not None
        assert result.race_id == "ghost"
        assert backing.get_race.call_count == 2
