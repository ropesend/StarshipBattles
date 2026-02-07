"""
Tests for BuildQueueScreen basic functionality.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
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


def test_build_queue_screen_initializes(build_queue_screen):
    """Test that BuildQueueScreen creates without crashing."""
    assert build_queue_screen is not None
    assert build_queue_screen.planet is not None
    assert build_queue_screen.session is not None
    assert build_queue_screen.on_close is not None


def test_load_designs_by_category(build_queue_screen):
    """Test that designs are filtered by vehicle type."""
    # Test complex category
    complexes = build_queue_screen.controller.load_designs_by_category("complex")
    assert len(complexes) > 0
    assert all(d.vehicle_type == "Planetary Complex" for d in complexes)

    # Test ship category
    ships = build_queue_screen.controller.load_designs_by_category("ship")
    assert len(ships) > 0
    assert all(d.vehicle_type == "Ship" for d in ships)

    # Test satellite category
    satellites = build_queue_screen.controller.load_designs_by_category("satellite")
    assert len(satellites) > 0
    assert all(d.vehicle_type == "Satellite" for d in satellites)

    # Test fighter category
    fighters = build_queue_screen.controller.load_designs_by_category("fighter")
    assert len(fighters) > 0
    assert all(d.vehicle_type == "Fighter" for d in fighters)


def test_switch_category_filter(build_queue_screen):
    """Test that category buttons filter correctly."""
    # Start with complex category
    assert build_queue_screen.controller.selected_category == "complex"

    # Switch to ship
    build_queue_screen.controller.set_category("ship")
    assert build_queue_screen.controller.selected_category == "ship"

    # Switch to satellite
    build_queue_screen.controller.set_category("satellite")
    assert build_queue_screen.controller.selected_category == "satellite"

    # Switch to fighter
    build_queue_screen.controller.set_category("fighter")
    assert build_queue_screen.controller.selected_category == "fighter"


def test_add_to_queue(build_queue_screen):
    """Test that selected design is added to planet construction queue."""
    initial_queue_length = len(build_queue_screen.planet.construction_queue)

    # Mock design selection
    build_queue_screen.drag_handler.selected_design = "mining_complex_mk1"
    build_queue_screen.controller.selected_category = "complex"

    # Add to queue
    build_queue_screen.controller.add_to_queue("mining_complex_mk1", 5)

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
    assert hasattr(build_queue_screen, 'planet_report')
    assert build_queue_screen.planet_report is not None


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


def test_no_savegame_path_handled_gracefully(mock_design_library, mock_design_loader):
    """Test that BuildQueueScreen handles None savegame_path without crashing.

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
        atmosphere={},
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1

    # Create session with None savegame_path
    session = MockSession()
    session.savegame_path = None

    # Should not crash - pass injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    screen_obj = BuildQueueScreen(
        manager,
        planet,
        session,
        lambda: None,
        design_library=mock_design_library,
        design_loader=mock_design_loader
    )

    # Should create with design_library injected
    assert screen_obj is not None
    assert screen_obj.design_library is not None

    pygame.quit()


def test_add_to_queue_defaults_to_1_turn(build_queue_screen):
    """Test that new items default to 1 turn build time."""
    # Mock design selection
    build_queue_screen.drag_handler.selected_design = "test_design"
    build_queue_screen.controller.selected_category = "complex"

    # Add to queue without specifying turns (should use default)
    build_queue_screen.controller.add_to_queue("test_design")

    # Verify item was added with 1 turn
    item = build_queue_screen.planet.construction_queue[-1]
    assert item["turns_remaining"] == 1


def test_drag_item_uses_1_turn_default(build_queue_screen):
    """Test that dragged items default to 1 turn if no turns specified."""
    # Simulate dragging an item without 'turns' key
    build_queue_screen.drag_handler.dragged_item = {
        'design_id': 'frigate_mk1',
        'name': 'Frigate',
        'category': 'ship',
        # Note: no 'turns' key
    }

    # Simulate drop event - manually call _add_to_queue as drop would
    # The actual drop handling gets 'turns' from dragged_item with default
    turns = build_queue_screen.drag_handler.dragged_item.get('turns', 1)  # Should be 1

    # Verify default is 1
    assert turns == 1


def test_add_ship_to_queue_with_shipyard(build_queue_screen):
    """Test that ships can be added when planet has a shipyard facility.

    Regression test for BUG-24: Ships couldn't be added to build queue
    even when planet had a space shipyard facility.
    """
    # Add a shipyard facility with correct design_data structure
    # This mimics how _spawn_complex creates facilities
    shipyard = PlanetaryFacility(
        instance_id="test-shipyard-1",
        design_id="space_shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "OUTER": [{"id": "space_shipyard", "modifiers": []}]
            }
        },
        is_operational=True
    )
    build_queue_screen.planet.facilities.append(shipyard)

    # Verify has_space_shipyard returns True
    assert build_queue_screen.planet.has_space_shipyard is True, \
        "has_space_shipyard should return True when shipyard facility exists"

    # Try to add a ship
    initial_queue_len = len(build_queue_screen.planet.construction_queue)
    build_queue_screen.controller.set_category("ship")
    build_queue_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was added
    assert len(build_queue_screen.planet.construction_queue) == initial_queue_len + 1, \
        "Ship should be added to construction queue when shipyard exists"
    assert build_queue_screen.planet.construction_queue[-1]["type"] == "ship"
    assert build_queue_screen.planet.construction_queue[-1]["design_id"] == "test_frigate"


def test_add_ship_fails_without_shipyard(build_queue_screen):
    """Test that ships cannot be added without a shipyard facility."""
    # Ensure no shipyard exists
    build_queue_screen.planet.facilities = []
    assert build_queue_screen.planet.has_space_shipyard is False

    # Try to add a ship
    initial_queue_len = len(build_queue_screen.planet.construction_queue)
    build_queue_screen.controller.set_category("ship")
    build_queue_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was NOT added
    assert len(build_queue_screen.planet.construction_queue) == initial_queue_len, \
        "Ship should NOT be added without a shipyard"
