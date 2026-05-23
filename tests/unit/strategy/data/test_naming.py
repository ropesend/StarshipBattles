"""
Unit tests for game/strategy/data/naming.py (NameRegistry).

Tests cover:
- Initialization and file loading
- Name retrieval and exhaustion
- Roman numeral conversion
- Error handling
"""
import os
import random
import tempfile
import pytest
import yaml

from game.strategy.data.naming import NameRegistry


class TestNameRegistryInit:
    """Tests for NameRegistry initialization."""

    def test_init_without_file(self):
        """Registry initializes empty without a file."""
        registry = NameRegistry()
        assert registry.available_names == []
        assert registry.used_names == set()

    def test_init_with_valid_file(self, tmp_path):
        """Registry loads names from valid YAML file."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["Alpha", "Beta", "Gamma"]}))

        registry = NameRegistry(str(yaml_file))
        assert len(registry.available_names) == 3
        assert set(registry.available_names) == {"Alpha", "Beta", "Gamma"}

    def test_init_with_nonexistent_file(self):
        """Registry handles missing file gracefully."""
        registry = NameRegistry("/nonexistent/path/names.yaml")
        assert registry.available_names == []


class TestNameRegistryLoadData:
    """Tests for load_data method."""

    def test_load_valid_yaml(self, tmp_path):
        """Loads names from valid YAML file."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["One", "Two", "Three"]}))

        registry = NameRegistry()
        registry.load_data(str(yaml_file))

        assert len(registry.available_names) == 3
        assert set(registry.available_names) == {"One", "Two", "Three"}

    def test_load_missing_names_key(self, tmp_path):
        """Handles YAML without 'names' key."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text(yaml.dump({"other_key": ["a", "b"]}))

        registry = NameRegistry()
        registry.load_data(str(yaml_file))

        # Should remain empty (warning logged)
        assert registry.available_names == []

    def test_load_names_not_list(self, tmp_path):
        """Handles YAML where 'names' is not a list."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text(yaml.dump({"names": "not a list"}))

        registry = NameRegistry()
        registry.load_data(str(yaml_file))

        # Should remain empty (warning logged)
        assert registry.available_names == []

    def test_load_invalid_yaml(self, tmp_path):
        """Handles malformed YAML file."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("invalid: yaml: content: [")

        registry = NameRegistry()
        registry.load_data(str(yaml_file))

        # Should remain empty (error logged)
        assert registry.available_names == []

    def test_load_nonexistent_file(self):
        """Handles missing file path."""
        registry = NameRegistry()
        registry.load_data("/nonexistent/file.yaml")

        # Should remain empty (error logged)
        assert registry.available_names == []


class TestSeededShuffle:
    """PROJ-473 Task 0.2: the load-time name shuffle must draw from an
    injected seeded RNG so system-name order is reproducible for a fixed seed
    (it was bare module-level ``random.shuffle`` before — hazard H1/S8)."""

    def test_injected_rng_makes_shuffle_deterministic(self, tmp_path):
        """Two registries built with the SAME injected ``random.Random(seed)``
        produce the same ``available_names`` order."""
        yaml_file = tmp_path / "names.yaml"
        names = [f"Star{i}" for i in range(50)]
        yaml_file.write_text(yaml.dump({"names": names}))

        r1 = NameRegistry(str(yaml_file), rng=random.Random(123))
        r2 = NameRegistry(str(yaml_file), rng=random.Random(123))

        assert r1.available_names == r2.available_names
        # And it actually shuffled (not just identity order).
        assert r1.available_names != names

    def test_different_seeds_differ(self, tmp_path):
        """Different injected seeds yield different orders."""
        yaml_file = tmp_path / "names.yaml"
        names = [f"Star{i}" for i in range(50)]
        yaml_file.write_text(yaml.dump({"names": names}))

        r1 = NameRegistry(str(yaml_file), rng=random.Random(1))
        r2 = NameRegistry(str(yaml_file), rng=random.Random(2))

        assert r1.available_names != r2.available_names


class TestGetSystemName:
    """Tests for get_system_name method."""

    def test_returns_name_from_list(self, tmp_path):
        """Returns a name from available names."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["Sirius", "Vega", "Polaris"]}))

        registry = NameRegistry(str(yaml_file))
        name = registry.get_system_name()

        assert name in ["Sirius", "Vega", "Polaris"]
        assert name in registry.used_names
        assert len(registry.available_names) == 2

    def test_tracks_used_names(self, tmp_path):
        """Used names are tracked."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["A", "B"]}))

        registry = NameRegistry(str(yaml_file))
        name1 = registry.get_system_name()
        name2 = registry.get_system_name()

        assert name1 != name2
        assert name1 in registry.used_names
        assert name2 in registry.used_names

    def test_exhausted_returns_fallback(self, tmp_path):
        """Returns fallback when names exhausted."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["Only"]}))

        registry = NameRegistry(str(yaml_file))
        name1 = registry.get_system_name()
        name2 = registry.get_system_name()

        assert name1 == "Only"
        assert name2 == "Unknown-2"

    def test_empty_registry_returns_fallback(self):
        """Returns fallback when registry is empty."""
        registry = NameRegistry()

        name1 = registry.get_system_name()
        name2 = registry.get_system_name()

        # Note: fallback numbering is based on used_names count
        # Since fallback names aren't tracked, all return Unknown-1
        assert name1 == "Unknown-1"
        assert name2 == "Unknown-1"

    def test_fallback_numbering_based_on_used_count(self):
        """Fallback numbers based on used_names count."""
        registry = NameRegistry()

        # All return Unknown-1 since used_names stays empty
        names = [registry.get_system_name() for _ in range(3)]
        assert all(n == "Unknown-1" for n in names)

    def test_skips_manually_added_used_names(self, tmp_path):
        """Skips names that were pre-added to used_names."""
        yaml_file = tmp_path / "names.yaml"
        yaml_file.write_text(yaml.dump({"names": ["A", "B", "C"]}))

        registry = NameRegistry(str(yaml_file))
        # Manually mark some names as used
        registry.used_names.add("A")
        registry.used_names.add("B")

        # Should skip A and B when encountered
        names = [registry.get_system_name() for _ in range(2)]

        # C should be available, then fallback
        assert "C" in names or "Unknown-" in names[1]


class TestToRoman:
    """Tests for to_roman static method."""

    # PROJ-480 Task 3.40: parametrize the 16 to_roman tests.
    # Ids name the original test for failure-id continuity.
    @pytest.mark.parametrize(
        "num, roman",
        [
            (1, "I"),
            (2, "II"),
            (3, "III"),
            (4, "IV"),
            (5, "V"),
            (9, "IX"),
            (10, "X"),
            (40, "XL"),
            (50, "L"),
            (90, "XC"),
            (100, "C"),
            (400, "CD"),
            (500, "D"),
            (900, "CM"),
            (1000, "M"),
            (1994, "MCMXCIV"),
            (3999, "MMMCMXCIX"),
        ],
        ids=[
            "one", "two", "three", "four_subtractive", "five",
            "nine_subtractive", "ten", "forty_subtractive", "fifty",
            "ninety_subtractive", "hundred", "four_hundred_subtractive",
            "five_hundred", "nine_hundred_subtractive", "thousand",
            "complex_1994", "complex_3999_max_standard",
        ],
    )
    def test_to_roman(self, num, roman):
        assert NameRegistry.to_roman(num) == roman

    def test_sequential_1_to_10(self):
        """Test sequential numerals 1-10."""
        expected = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        for n, roman in enumerate(expected, start=1):
            assert NameRegistry.to_roman(n) == roman

    # Edge cases
    def test_zero_returns_string(self):
        """0 returns '0' (out of range)."""
        assert NameRegistry.to_roman(0) == "0"

    def test_negative_returns_string(self):
        """Negative numbers return string representation."""
        assert NameRegistry.to_roman(-5) == "-5"

    def test_above_3999_returns_string(self):
        """4000+ returns string representation."""
        assert NameRegistry.to_roman(4000) == "4000"
        assert NameRegistry.to_roman(5000) == "5000"
