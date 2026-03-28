
import pytest
from unittest.mock import MagicMock
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.ui.screens.planet_list_filters import gather_planets, filter_planets

class TestPlanetListFilters:
    """Tests for planet list filtering and categorization."""
    
    def test_gather_planets_categorization(self):
        """Verify gather_planets correctly categorizes new planet types."""
        galaxy = MagicMock()
        empire = MagicMock()
        
        # Create mock planets with new types
        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.CONTINENTAL
        p1.name = "Terra"
        p1.mass = 5.97e24
        p1.surface_gravity = 9.81
        p1.surface_temperature = 288
        
        p2 = MagicMock(spec=Planet)
        p2.planet_type = PlanetType.ICE_GIANT
        p2.name = "Neptune"
        p2.mass = 1.02e26
        p2.surface_gravity = 11.15
        p2.surface_temperature = 72
        
        # Mock system structure
        system = MagicMock()
        system.planets = [p1, p2]
        galaxy.systems = {'Sys1': system}
        
        planets = gather_planets(galaxy, empire)
        
        assert len(planets) == 2
        # Verify cached categories match "Title Case" of Enum
        assert p1._cached_type_category == "Continental"
        assert p2._cached_type_category == "Ice Giant"

    def test_filter_planets_by_type(self):
        """Verify filter_planets respects new type filters."""
        # Create planets with cached values (simulating gather_planets result)
        p1 = MagicMock()
        p1._cached_type_category = "Continental"
        p1._cached_name_lower = "terra"
        p1._cached_gravity_g = 1.0
        p1.surface_temperature = 288
        p1._cached_mass_earth = 1.0
        p1.owner_id = 1
        
        p2 = MagicMock()
        p2._cached_type_category = "Ice Giant"
        p2._cached_name_lower = "neptune"
        p2._cached_gravity_g = 1.1
        p2.surface_temperature = 72
        p2._cached_mass_earth = 17.0
        p2.owner_id = 1
        
        all_planets = [p1, p2]
        
        # Test 1: Both enabled
        filter_types = {'Continental': True, 'Ice Giant': True}
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 2
        
        # Test 2: Disable Ice Giant
        filter_types['Ice Giant'] = False
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 1
        assert res[0] == p1
        
        # Test 3: Disable All
        filter_types['Continental'] = False
        res = filter_planets(all_planets, "", filter_types, 0, 100, 0, 1000, 0, 1000, {'Player': True}, MagicMock(id=1))
        assert len(res) == 0


class TestGatherPlanetsCachesSystemLocation:
    """gather_planets should cache system global_location for navigation."""

    def test_caches_system_global_location(self):
        """Each planet should get _cached_system_global_location from its system."""
        galaxy = MagicMock()
        empire = MagicMock()

        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.CONTINENTAL
        p1.name = "Terra"
        p1.mass = 5.97e24
        p1.surface_gravity = 9.81

        system = MagicMock()
        system.name = "Solar"
        system.global_location = HexCoord(10, 20)
        system.planets = [p1]
        galaxy.systems = {'Solar': system}

        planets = gather_planets(galaxy, empire)
        assert len(planets) == 1
        assert p1._cached_system_global_location == HexCoord(10, 20)

    def test_different_systems_cache_different_locations(self):
        """Planets from different systems should get their own system location."""
        galaxy = MagicMock()
        empire = MagicMock()

        p1 = MagicMock(spec=Planet)
        p1.planet_type = PlanetType.ARID
        p1.name = "Dry"
        p1.mass = 3e24
        p1.surface_gravity = 5.0

        p2 = MagicMock(spec=Planet)
        p2.planet_type = PlanetType.PELAGIC
        p2.name = "Wet"
        p2.mass = 6e24
        p2.surface_gravity = 10.0

        sys1 = MagicMock()
        sys1.name = "Alpha"
        sys1.global_location = HexCoord(5, 5)
        sys1.planets = [p1]

        sys2 = MagicMock()
        sys2.name = "Beta"
        sys2.global_location = HexCoord(50, 50)
        sys2.planets = [p2]

        galaxy.systems = {'Alpha': sys1, 'Beta': sys2}

        planets = gather_planets(galaxy, empire)
        assert p1._cached_system_global_location == HexCoord(5, 5)
        assert p2._cached_system_global_location == HexCoord(50, 50)
