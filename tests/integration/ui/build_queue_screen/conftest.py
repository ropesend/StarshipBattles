"""
Shared fixtures for BuildQueueScreen tests.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.core.validation import ValidationResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}  # HexCoord -> List[Planet]
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        """Return planets at a given global hex coordinate."""
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()
        # PROJ-211: Add registries for DI
        self.registries = registries

    def handle_command(self, cmd):
        """Mock command handler."""
        return ValidationResult()


@pytest.fixture
def mock_design_library():
    """Mock DesignLibrary for testing.

    PROJ-40: Updated to create mock directly instead of patching.
    Now injected via DI in build_queue_screen fixture.
    """
    mock_instance = MagicMock()

    complex_design = MagicMock()
    complex_design.design_id = "mining_complex_mk1"
    complex_design.name = "Mining Complex"
    complex_design.vehicle_type = "Planetary Complex"

    ship_design = MagicMock()
    ship_design.design_id = "frigate_mk1"
    ship_design.name = "Frigate"
    ship_design.vehicle_type = "Ship"

    satellite_design = MagicMock()
    satellite_design.design_id = "defense_sat_mk1"
    satellite_design.name = "Defense Satellite"
    satellite_design.vehicle_type = "Satellite"

    fighter_design = MagicMock()
    fighter_design.design_id = "interceptor_mk1"
    fighter_design.name = "Interceptor"
    fighter_design.vehicle_type = "Fighter"

    mock_instance.scan_designs.return_value = [
        complex_design, ship_design, satellite_design, fighter_design
    ]
    mock_instance.designs_folder = "test_designs"
    mock_instance.load_design_data.return_value = None

    return mock_instance


@pytest.fixture
def mock_design_loader():
    """Mock SimulationDesignLoader for testing.

    PROJ-40: New fixture for DI injection.
    """
    return MagicMock()


@pytest.fixture
def build_queue_screen(mock_design_library, mock_design_loader, mock_registries):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection for dependencies.
    PROJ-109: Updated to provide required hex_coord, galaxy, empire parameters.
    PROJ-211: Updated to pass registries for DI.
    """
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    hex_coord = HexCoord(5, 5)
    # Create test planet
    planet = Planet(
        name="Test Colony",
        location=hex_coord,
        orbit_distance=3,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Create mock galaxy with planet
    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # Create mock session with registries
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    # Mock callback
    on_close = MagicMock()

    # Import and create screen with injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(
        manager,
        planet,
        session,
        on_close,
        design_library=mock_design_library,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire
    )

    yield bq_screen

    pygame.quit()
