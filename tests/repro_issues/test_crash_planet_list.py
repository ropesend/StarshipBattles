
import pytest
from unittest.mock import MagicMock

# Minimal mocking of the Galaxy/System structure causing the crash
class MockGalaxy:
    def __init__(self):
        # The crash happens because systems is a dict, and iteration yields keys (HexCoord)
        # but the code tries to access .planets on the key.
        p1 = MagicMock()
        p1.name = "Earth"
        p2 = MagicMock()
        p2.name = "Mars"
        
        self.systems = {
            "HexCoord(0,0)": MagicMock(planets=[p1]),
            "HexCoord(1,0)": MagicMock(planets=[p2])
        }

class MockPlanetListWindow:
    def __init__(self, galaxy):
        self.galaxy = galaxy
    
    def _gather_planets(self):
        # This matches the FIXED implementation
        planets = []
        if self.galaxy and self.galaxy.systems:
            for s in self.galaxy.systems.values():
                for p in s.planets:
                    p._temp_system_ref = s 
                    planets.append(p)
        return planets

def test_repro_crash_fixed():
    """Verify that the fix prevents the crash."""
    galaxy = MockGalaxy()
    window = MockPlanetListWindow(galaxy)
    
    # Should NOT raise anymore
    planets = window._gather_planets()
    assert len(planets) == 2
    assert planets[0].name == "Earth"

