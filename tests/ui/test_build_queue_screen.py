"""
Tests for BuildQueueScreen UI component.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire


class MockSession:
    def __init__(self):
        self.savegame_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))

    def handle_command(self, cmd):
        """Mock command handler."""
        from game.strategy.engine.validation_result import ValidationResult
        return ValidationResult(True, "Command processed")


@pytest.fixture
def mock_design_library():
    """Mock DesignLibrary for testing."""
    with patch('game.ui.screens.build_queue_screen.DesignLibrary') as mock:
        # Create mock designs
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

        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def build_queue_screen(mock_design_library):
    """Create BuildQueueScreen for testing."""
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

    # Import and create screen
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(manager, planet, session, on_close)

    yield bq_screen

    pygame.quit()


def test_build_queue_screen_initializes(build_queue_screen):
    """Test that BuildQueueScreen creates without crashing."""
    assert build_queue_screen is not None
    assert build_queue_screen.planet is not None
    assert build_queue_screen.session is not None
    assert build_queue_screen.on_close is not None


def test_load_designs_by_category(build_queue_screen):
    """Test that designs are filtered by vehicle type."""
    # Test complex category
    complexes = build_queue_screen._load_designs_by_category("complex")
    assert len(complexes) > 0
    assert all(d.vehicle_type == "Planetary Complex" for d in complexes)

    # Test ship category
    ships = build_queue_screen._load_designs_by_category("ship")
    assert len(ships) > 0
    assert all(d.vehicle_type == "Ship" for d in ships)

    # Test satellite category
    satellites = build_queue_screen._load_designs_by_category("satellite")
    assert len(satellites) > 0
    assert all(d.vehicle_type == "Satellite" for d in satellites)

    # Test fighter category
    fighters = build_queue_screen._load_designs_by_category("fighter")
    assert len(fighters) > 0
    assert all(d.vehicle_type == "Fighter" for d in fighters)


def test_switch_category_filter(build_queue_screen):
    """Test that category buttons filter correctly."""
    # Start with complex category
    assert build_queue_screen.selected_category == "complex"

    # Switch to ship
    build_queue_screen._set_category("ship")
    assert build_queue_screen.selected_category == "ship"

    # Switch to satellite
    build_queue_screen._set_category("satellite")
    assert build_queue_screen.selected_category == "satellite"

    # Switch to fighter
    build_queue_screen._set_category("fighter")
    assert build_queue_screen.selected_category == "fighter"


def test_add_to_queue(build_queue_screen):
    """Test that selected design is added to planet construction queue."""
    initial_queue_length = len(build_queue_screen.planet.construction_queue)

    # Mock design selection
    build_queue_screen.selected_design = "mining_complex_mk1"
    build_queue_screen.selected_category = "complex"

    # Add to queue
    build_queue_screen._add_to_queue("mining_complex_mk1", 5)

    # Verify queue updated
    assert len(build_queue_screen.planet.construction_queue) == initial_queue_length + 1

    # Verify item structure
    item = build_queue_screen.planet.construction_queue[-1]
    assert isinstance(item, dict)
    assert item["design_id"] == "mining_complex_mk1"
    assert item["type"] == "complex"
    assert item["turns_remaining"] == 5


def test_queue_display_updates(build_queue_screen):
    """Test that UI refreshes when queue changes."""
    # Add item to queue
    build_queue_screen.planet.construction_queue.append({
        "design_id": "frigate_mk1",
        "type": "ship",
        "turns_remaining": 10
    })

    # Refresh display
    build_queue_screen._refresh_queue_display()

    # Verify queue panel has items (implementation-dependent check)
    # This will be refined when BuildQueueScreen is implemented
    assert hasattr(build_queue_screen, 'queue_items')


def test_close_callback_fires(build_queue_screen):
    """Test that on_close callback is invoked."""
    # Close the screen
    build_queue_screen._close()

    # Verify callback was called
    build_queue_screen.on_close.assert_called_once()


def test_planet_report_panel_exists(build_queue_screen):
    """Test that planet report panel is created."""
    assert hasattr(build_queue_screen, 'planet_report_panel')
    assert build_queue_screen.planet_report_panel is not None


def test_items_list_panel_exists(build_queue_screen):
    """Test that items list panel is created."""
    assert hasattr(build_queue_screen, 'items_list_panel')
    assert build_queue_screen.items_list_panel is not None


def test_filter_panel_exists(build_queue_screen):
    """Test that filter panel with category buttons exists."""
    assert hasattr(build_queue_screen, 'filter_panel')
    assert build_queue_screen.filter_panel is not None

    # Verify category buttons exist
    assert hasattr(build_queue_screen, 'btn_category_complex')
    assert hasattr(build_queue_screen, 'btn_category_ship')
    assert hasattr(build_queue_screen, 'btn_category_satellite')
    assert hasattr(build_queue_screen, 'btn_category_fighter')


def test_bottom_bar_exists(build_queue_screen):
    """Test that bottom bar with close button exists."""
    assert hasattr(build_queue_screen, 'btn_close')
    assert build_queue_screen.btn_close is not None


def test_no_savegame_path_handled_gracefully(mock_design_library):
    """Test that BuildQueueScreen handles None savegame_path without crashing."""
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
        atmosphere={},
        planet_type=PlanetType.TERRESTRIAL
    )
    planet.owner_id = 1

    # Create session with None savegame_path
    session = MockSession()
    session.savegame_path = None

    # Should not crash
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    screen_obj = BuildQueueScreen(manager, planet, session, lambda: None)

    # Should create with no designs available
    assert screen_obj is not None
    assert screen_obj.design_library is not None

    pygame.quit()
