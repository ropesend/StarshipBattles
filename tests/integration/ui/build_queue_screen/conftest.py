"""
Shared fixtures for BuildQueueScreen tests.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.core.validation import validation_result


class MockSession:
    def __init__(self):
        self.savegame_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))

    def handle_command(self, cmd):
        """Mock command handler."""
        return validation_result(True, "Command processed")


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
def build_queue_screen(mock_design_library, mock_design_loader):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection for dependencies.
    """
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    # Create test planet
    planet = Planet(
        name="Test Colony",
        location=HexCoord(5, 5),
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
        planet_type=PlanetType.TERRESTRIAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Create mock session
    session = MockSession()

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
        design_loader=mock_design_loader
    )

    yield bq_screen

    pygame.quit()
