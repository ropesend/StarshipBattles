import pytest
from unittest.mock import MagicMock
from game.ui.screens.build_queue_screen import BuildQueueScreen
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.empire import Empire
from tests.integration.ui.build_queue_screen.conftest import MockGalaxy, MockSession

def test_apply_tooltips_crash_none_buttons(ui_manager, mock_design_library, mock_design_loader, mock_registries):
    hex_coord = HexCoord(0, 0)
    planet = Planet(name="Test", location=hex_coord, orbit_distance=1, mass=1, radius=1, surface_area=1, density=1, surface_gravity=1, surface_pressure=1, surface_temperature=1, surface_water=1, tectonic_activity=1, magnetic_field=1, planet_type=PlanetType.CONTINENTAL)
    planet.owner_id = 1
    galaxy = MockGalaxy()
    empire = Empire(1, "Test", (255, 0, 0))
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    mock_mapper = MagicMock()
    mock_mapper.get_display_text.return_value = "HINT"

    screen = BuildQueueScreen(
        ui_manager,
        planet,
        session,
        lambda: None,
        design_library=mock_design_library,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire,
        input_mapper=mock_mapper
    )
