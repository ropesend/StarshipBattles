"""
Unit tests for Galaxy class.

Tests core galaxy functionality including system lookups and name mapping.
"""

import pytest
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.hex_math import HexCoord


class TestGalaxyNameMap:
    """Tests for Galaxy name_map and get_system_by_name()."""

    def test_get_system_by_name_returns_correct_system(self):
        """get_system_by_name() should return the system with matching name."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        result = galaxy.get_system_by_name("Alpha")

        assert result is system

    def test_get_system_by_name_returns_none_for_unknown_name(self):
        """get_system_by_name() should return None for unknown names."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        result = galaxy.get_system_by_name("Unknown")

        assert result is None

    def test_get_system_by_name_empty_galaxy(self):
        """get_system_by_name() should return None for empty galaxy."""
        galaxy = Galaxy(radius=1000)

        result = galaxy.get_system_by_name("Alpha")

        assert result is None

    def test_name_map_populated_on_add_system(self):
        """add_system() should populate name_map."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Beta", global_location=HexCoord(10, 20))

        galaxy.add_system(system)

        assert "Beta" in galaxy.name_map
        assert galaxy.name_map["Beta"] is system

    def test_name_map_with_multiple_systems(self):
        """name_map should contain all added systems."""
        galaxy = Galaxy(radius=1000)
        s1 = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        s2 = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        s3 = StarSystem(name="Gamma", global_location=HexCoord(0, 100))

        galaxy.add_system(s1)
        galaxy.add_system(s2)
        galaxy.add_system(s3)

        assert galaxy.get_system_by_name("Alpha") is s1
        assert galaxy.get_system_by_name("Beta") is s2
        assert galaxy.get_system_by_name("Gamma") is s3

    def test_get_system_by_name_is_case_sensitive(self):
        """get_system_by_name() should be case-sensitive."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        # Exact match works
        assert galaxy.get_system_by_name("Alpha") is system
        # Different case returns None
        assert galaxy.get_system_by_name("alpha") is None
        assert galaxy.get_system_by_name("ALPHA") is None

    def test_name_map_preserved_after_from_dict(self):
        """name_map should be rebuilt correctly after deserialization."""
        galaxy = Galaxy(radius=1000)
        s1 = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        s2 = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(s1)
        galaxy.add_system(s2)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Name map should work on restored galaxy
        assert restored.get_system_by_name("Alpha") is not None
        assert restored.get_system_by_name("Alpha").name == "Alpha"
        assert restored.get_system_by_name("Beta") is not None
        assert restored.get_system_by_name("Beta").name == "Beta"
        assert restored.get_system_by_name("Unknown") is None


class TestGalaxySystemLookup:
    """Tests for system coordinate lookups."""

    def test_systems_dict_keyed_by_coord(self):
        """systems dict should be keyed by HexCoord."""
        galaxy = Galaxy(radius=1000)
        coord = HexCoord(5, 10)
        system = StarSystem(name="Test", global_location=coord)
        galaxy.add_system(system)

        assert coord in galaxy.systems
        assert galaxy.systems[coord] is system

    def test_add_system_updates_both_maps(self):
        """add_system() should update both systems and name_map."""
        galaxy = Galaxy(radius=1000)
        coord = HexCoord(42, -10)
        system = StarSystem(name="Dual", global_location=coord)

        galaxy.add_system(system)

        # Both lookups should work
        assert galaxy.systems[coord] is system
        assert galaxy.name_map["Dual"] is system
        assert galaxy.get_system_by_name("Dual") is system
