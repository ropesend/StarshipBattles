import os
import tempfile
import pytest
import yaml
from game.strategy.data.naming import NameRegistry
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem
@pytest.fixture
def temp_yaml_file():
    """Create a temp yaml file for testing."""
    test_data = {
        "names": ["Alpha", "Beta", "Gamma", "Delta"]
    }
    fd, path = tempfile.mkstemp(suffix=".YAML")
    with os.fdopen(fd, 'w') as f:
        yaml.dump(test_data, f)
    yield path
    os.remove(path)


class TestNaming:
    def test_load_and_shuffle(self, temp_yaml_file):
        """Test that names are loaded and shuffled."""
        registry = NameRegistry(temp_yaml_file)
        assert len(registry.available_names) == 4
        # Cannot easily test shuffle without seed control, but length is key.

    def test_unique_names(self, temp_yaml_file):
        """Test that names are unique and exhausted correctly."""
        registry = NameRegistry(temp_yaml_file)
        names = set()
        for _ in range(4):
            names.add(registry.get_system_name())

        assert len(names) == 4
        assert "Alpha" in names

        # Test fallback
        fallback = registry.get_system_name()
        assert fallback.startswith("Unknown-")

    def test_roman_numerals(self):
        """Test Roman numeral conversion."""
        assert NameRegistry.to_roman(1) == "I"
        assert NameRegistry.to_roman(2) == "II"
        assert NameRegistry.to_roman(3) == "III"
        assert NameRegistry.to_roman(4) == "IV"
        assert NameRegistry.to_roman(5) == "V"
        assert NameRegistry.to_roman(9) == "IX"
        assert NameRegistry.to_roman(10) == "X"
