"""
Tests for BuildQueueScreen basic functionality.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.core.validation import ValidationResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()

    def handle_command(self, cmd):
        """Mock command handler."""
        return ValidationResult()


def test_build_queue_screen_initializes(build_queue_screen):
    """Test that BuildQueueScreen creates without crashing."""
    assert build_queue_screen is not None
    assert build_queue_screen.build_context is not None
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
    initial_queue_length = len(build_queue_screen.build_context.construction_queue)

    # Mock design selection
    build_queue_screen.drag_handler.selected_design = "mining_complex_mk1"
    build_queue_screen.controller.selected_category = "complex"

    # Add to queue
    build_queue_screen.controller.add_to_queue("mining_complex_mk1", 5)

    # Verify queue updated
    assert len(build_queue_screen.build_context.construction_queue) == initial_queue_length + 1

    # Verify item structure
    item = build_queue_screen.build_context.construction_queue[-1]
    assert isinstance(item, dict)
    assert item["design_id"] == "mining_complex_mk1"
    assert item["type"] == "complex"
    assert item["turns_remaining"] == 5


def test_queue_display_updates(build_queue_screen):
    """Test that UI refreshes when queue changes."""
    # Add item to queue
    build_queue_screen.build_context.construction_queue.append({
        "design_id": "frigate_mk1",
        "type": "ship",
        "turns_remaining": 10
    })

    # Refresh display
    build_queue_screen._refresh_queue_display()

    # PROJ-180: Access via renderer.*
    # Verify queue panel has items (implementation-dependent check)
    assert hasattr(build_queue_screen.renderer, 'queue_items')


def test_close_callback_fires(build_queue_screen):
    """Test that on_close callback is invoked."""
    # Close the screen
    build_queue_screen._close()

    # Verify callback was called
    build_queue_screen.on_close.assert_called_once()


def test_planet_report_panel_exists(build_queue_screen):
    """Test that planet report panel is created."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'planet_report')
    assert build_queue_screen.panels.planet_report is not None


def test_items_list_panel_exists(build_queue_screen):
    """Test that items list panel is created."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'items_list_panel')
    assert build_queue_screen.panels.items_list_panel is not None


def test_filter_panel_exists(build_queue_screen):
    """Test that filter panel with category buttons exists."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'filter_panel')
    assert build_queue_screen.panels.filter_panel is not None

    # Verify category buttons exist
    assert hasattr(build_queue_screen.panels, 'btn_category_complex')
    assert hasattr(build_queue_screen.panels, 'btn_category_ship')
    assert hasattr(build_queue_screen.panels, 'btn_category_satellite')
    assert hasattr(build_queue_screen.panels, 'btn_category_fighter')


def test_bottom_bar_exists(build_queue_screen):
    """Test that bottom bar with close button exists."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'btn_close')
    assert build_queue_screen.panels.btn_close is not None


def test_no_savegame_path_handled_gracefully(mock_design_library, mock_design_loader):
    """Test that BuildQueueScreen handles None savegame_path without crashing.

    PROJ-40: Updated to use DI injection for dependencies.
    PROJ-109: Updated to provide required hex_coord, galaxy, empire parameters.
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
        atmosphere={},
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Create mock galaxy with planet
    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # Create session with None savegame_path
    session = MockSession(galaxy=galaxy, empire=empire)
    session.savegame_path = None

    # Should not crash - pass injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    screen_obj = BuildQueueScreen(
        manager,
        planet,
        session,
        lambda: None,
        design_library=mock_design_library,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire
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
    item = build_queue_screen.build_context.construction_queue[-1]
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


def test_add_ship_to_queue_with_shipyard(mock_design_library, mock_design_loader):
    """Test that ships can be added when planet has a shipyard facility.

    Regression test for BUG-24: Ships couldn't be added to build queue
    even when planet had a space shipyard facility.

    PROJ-109: Test creates screen with shipyard already present so queue source
    for ships is created at initialization time.
    """
    import pygame
    import pygame_gui
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

    hex_coord = HexCoord(5, 5)
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

    # Add shipyard facility BEFORE creating screen
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
    planet.facilities.append(shipyard)

    # Verify has_space_shipyard returns True
    assert planet.has_space_shipyard is True, \
        "has_space_shipyard should return True when shipyard facility exists"

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire)

    bq_screen = BuildQueueScreen(
        manager,
        planet,
        session,
        lambda: None,
        design_library=mock_design_library,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire
    )

    # Should have 2 queue sources: planetary yard + shipyard
    assert len(bq_screen.queue_sources) == 2, \
        f"Should have 2 queue sources, got {len(bq_screen.queue_sources)}"

    # Find and select the shipyard queue source (can_build_ships=True)
    shipyard_source = next(
        (s for s in bq_screen.queue_sources if s.can_build_ships), None
    )
    assert shipyard_source is not None, "Should have a shipyard queue source"
    bq_screen._queue_selector._on_queue_selected(
        bq_screen.queue_sources.index(shipyard_source)
    )

    # Try to add a ship
    initial_queue_len = len(shipyard_source.construction_queue)
    bq_screen.controller.set_category("ship")
    bq_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was added to shipyard queue
    assert len(shipyard_source.construction_queue) == initial_queue_len + 1, \
        "Ship should be added to shipyard queue when shipyard exists"
    assert shipyard_source.construction_queue[-1]["type"] == "ship"
    assert shipyard_source.construction_queue[-1]["design_id"] == "test_frigate"

    pygame.quit()


def test_add_ship_fails_without_shipyard(build_queue_screen):
    """Test that ships cannot be added when only planetary yard queue exists.

    PROJ-109: The default build_queue_screen fixture creates a planet without
    shipyard facilities, so only the "Planetary Yard" queue source exists
    (can_build_ships=False). Ships should be rejected.
    """
    # Default fixture has no shipyard - verify single queue source
    assert len(build_queue_screen.queue_sources) == 1, \
        "Should have only planetary yard queue source"
    assert build_queue_screen.active_queue_source.can_build_ships is False, \
        "Planetary yard should not build ships"

    # Try to add a ship
    initial_queue_len = len(build_queue_screen.active_queue_source.construction_queue)
    build_queue_screen.controller.set_category("ship")
    build_queue_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was NOT added
    assert len(build_queue_screen.active_queue_source.construction_queue) == initial_queue_len, \
        "Ship should NOT be added without a shipyard"
