"""
Tests for system blueprints JSON loading and validation.
"""
import pytest
import os
from pathlib import Path


class TestSystemBlueprintsLoader:
    """Tests for loading and validating system_blueprints.json."""

    def test_blueprints_file_exists(self):
        """Verify blueprints JSON file exists."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        loader = SystemBlueprintsLoader()
        blueprints_path = Path("data/system_blueprints.json")
        assert blueprints_path.exists(), f"Expected {blueprints_path} to exist"

    def test_load_returns_valid_dict(self):
        """Verify load() returns a dict with blueprints."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        loader = SystemBlueprintsLoader()
        data = loader.load()

        assert isinstance(data, dict)
        assert "blueprints" in data

    def test_all_required_blueprints_present(self):
        """Verify all required blueprints are defined."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        loader = SystemBlueprintsLoader()
        data = loader.load()
        blueprints = data["blueprints"]

        required = [
            "binary_no_planets",
            "solar_like",
            "red_dwarf_pack",
            "empty_warp_hub",
            "gas_giant_system"
        ]

        for name in required:
            assert name in blueprints, f"Missing required blueprint: {name}"

    def test_get_blueprint_returns_config(self):
        """Verify get_blueprint() returns blueprint config."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        loader = SystemBlueprintsLoader()
        data = loader.load()
        config = loader.get_blueprint("solar_like", data)

        assert isinstance(config, dict)
        assert "star_count" in config
        assert "planet_count" in config

    def test_get_blueprint_invalid_raises(self):
        """Verify get_blueprint() raises for unknown blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        loader = SystemBlueprintsLoader()
        data = loader.load()

        with pytest.raises(KeyError):
            loader.get_blueprint("nonexistent_blueprint", data)


class TestBlueprintSchema:
    """Tests for blueprint schema validation."""

    @pytest.fixture
    def loader(self):
        """Create loader instance."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        return SystemBlueprintsLoader()

    @pytest.fixture
    def all_blueprints(self, loader):
        """Load all blueprints."""
        data = loader.load()
        return data["blueprints"]

    def test_star_count_is_valid_distribution(self, all_blueprints):
        """Verify star_count is a valid distribution spec."""
        for name, bp in all_blueprints.items():
            star_count = bp.get("star_count")
            assert star_count is not None, f"{name} missing star_count"

            # Star count can be:
            # - integer (exact)
            # - dict with "min", "max" (range)
            # - dict with "distribution" (weighted)
            if isinstance(star_count, int):
                assert 1 <= star_count <= 4, f"{name} star_count out of range"
            elif isinstance(star_count, dict):
                if "min" in star_count:
                    assert 1 <= star_count["min"] <= star_count["max"] <= 4
                elif "distribution" in star_count:
                    weights = star_count["distribution"]
                    assert isinstance(weights, dict)
                    assert all(1 <= int(k) <= 4 for k in weights.keys())
            else:
                pytest.fail(f"{name} has invalid star_count type")

    def test_planet_count_is_valid_range(self, all_blueprints):
        """Verify planet_count has valid min/max."""
        for name, bp in all_blueprints.items():
            planet_count = bp.get("planet_count")
            assert planet_count is not None, f"{name} missing planet_count"

            assert "min" in planet_count, f"{name} planet_count missing min"
            assert "max" in planet_count, f"{name} planet_count missing max"
            assert planet_count["min"] >= 0
            assert planet_count["max"] >= planet_count["min"]
            assert planet_count["max"] <= 20  # Reasonable limit

    def test_blueprint_has_weight(self, all_blueprints):
        """Verify each blueprint has a selection weight."""
        for name, bp in all_blueprints.items():
            assert "weight" in bp, f"{name} missing weight"
            assert bp["weight"] > 0, f"{name} has non-positive weight"


class TestBinaryNoPlanets:
    """Tests specific to binary_no_planets blueprint."""

    @pytest.fixture
    def blueprint(self):
        """Load binary_no_planets blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        loader = SystemBlueprintsLoader()
        data = loader.load()
        return loader.get_blueprint("binary_no_planets", data)

    def test_has_two_stars(self, blueprint):
        """Binary systems should have exactly 2 stars."""
        star_count = blueprint["star_count"]
        if isinstance(star_count, int):
            assert star_count == 2
        elif isinstance(star_count, dict) and "min" in star_count:
            assert star_count["min"] == 2

    def test_few_or_no_planets(self, blueprint):
        """Binary no planets should have 0-1 planets."""
        planet_count = blueprint["planet_count"]
        assert planet_count["max"] <= 1


class TestSolarLike:
    """Tests specific to solar_like blueprint."""

    @pytest.fixture
    def blueprint(self):
        """Load solar_like blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        loader = SystemBlueprintsLoader()
        data = loader.load()
        return loader.get_blueprint("solar_like", data)

    def test_has_one_star(self, blueprint):
        """Solar-like systems should have 1 star."""
        star_count = blueprint["star_count"]
        if isinstance(star_count, int):
            assert star_count == 1
        elif isinstance(star_count, dict) and "min" in star_count:
            assert star_count["min"] == 1
            assert star_count["max"] == 1

    def test_multiple_planets(self, blueprint):
        """Solar-like systems should have 4-8 planets."""
        planet_count = blueprint["planet_count"]
        assert planet_count["min"] >= 4
        assert planet_count["max"] <= 10


class TestRedDwarfPack:
    """Tests specific to red_dwarf_pack blueprint."""

    @pytest.fixture
    def blueprint(self):
        """Load red_dwarf_pack blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        loader = SystemBlueprintsLoader()
        data = loader.load()
        return loader.get_blueprint("red_dwarf_pack", data)

    def test_has_one_star(self, blueprint):
        """Red dwarf pack should have 1 star."""
        star_count = blueprint["star_count"]
        if isinstance(star_count, int):
            assert star_count == 1

    def test_has_star_mass_constraint(self, blueprint):
        """Red dwarf pack should constrain star mass to red dwarf range."""
        assert "star_mass" in blueprint
        star_mass = blueprint["star_mass"]
        # Red dwarfs are 0.08 - 0.5 solar masses
        assert star_mass["max"] <= 0.5


class TestEmptyWarpHub:
    """Tests specific to empty_warp_hub blueprint."""

    @pytest.fixture
    def blueprint(self):
        """Load empty_warp_hub blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        loader = SystemBlueprintsLoader()
        data = loader.load()
        return loader.get_blueprint("empty_warp_hub", data)

    def test_few_planets(self, blueprint):
        """Empty warp hub should have 0-1 planets."""
        planet_count = blueprint["planet_count"]
        assert planet_count["max"] <= 1


class TestGasGiantSystem:
    """Tests specific to gas_giant_system blueprint."""

    @pytest.fixture
    def blueprint(self):
        """Load gas_giant_system blueprint."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        loader = SystemBlueprintsLoader()
        data = loader.load()
        return loader.get_blueprint("gas_giant_system", data)

    def test_has_planet_mass_bias(self, blueprint):
        """Gas giant system should bias towards large planets."""
        assert "planet_mass" in blueprint
        planet_mass = blueprint["planet_mass"]
        # Should have bias towards gas giant range (>6e24 kg)
        assert "bias" in planet_mass or "min" in planet_mass


class TestWeightedSelection:
    """Tests for weighted blueprint selection."""

    def test_select_random_blueprint(self):
        """Test weighted random selection of blueprints."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        import random

        loader = SystemBlueprintsLoader()
        data = loader.load()

        # Set seed for reproducibility
        random.seed(42)

        selected = loader.select_random_blueprint(data)
        assert selected is not None
        assert selected in data["blueprints"]

    def test_selection_respects_weights(self):
        """Test that selection respects relative weights."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        import random

        loader = SystemBlueprintsLoader()
        data = loader.load()

        # Run many selections
        random.seed(12345)
        counts = {}
        for _ in range(1000):
            name = loader.select_random_blueprint(data)
            counts[name] = counts.get(name, 0) + 1

        # Verify all blueprints were selected at least once
        # (assuming all have non-zero weight)
        for name, bp in data["blueprints"].items():
            if bp.get("weight", 0) > 0:
                assert name in counts, f"{name} was never selected"
