import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.ui.screens.build_queue_screen import BuildQueueScreen

class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.save_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()
        # PROJ-211: Add registries for DI
        self.registries = registries
        # PROJ-208: Track commands for test verification
        self.commands_handled = []

    def handle_command(self, cmd):
        """Mock command handler that executes queue commands.

        PROJ-208: Enables queue mutation tests to work with command pattern.
        """
        from game.core.validation import ValidationResult
        self.commands_handled.append(cmd)

        # Execute AddToConstructionQueueCommand to maintain queue behavior
        from game.strategy.engine.commands import (
            AddToConstructionQueueCommand,
            RemoveFromConstructionQueueCommand,
        )
        if isinstance(cmd, AddToConstructionQueueCommand):
            queue = self._resolve_queue(cmd.entity_id, cmd.entity_type, getattr(cmd, 'queue_id', None))
            if queue is not None:
                queue_item = {
                    "design_id": cmd.design_id,
                    "type": cmd.category,
                    "turns_remaining": 1.0,
                    "total_cost": {},
                    "resources_consumed": {},
                }
                if cmd.target_planet_id is not None:
                    queue_item["target_planet_id"] = cmd.target_planet_id
                if cmd.index is not None:
                    queue.insert(cmd.index, queue_item)
                else:
                    queue.append(queue_item)

        # PROJ-208: Execute RemoveFromConstructionQueueCommand for drag operations
        elif isinstance(cmd, RemoveFromConstructionQueueCommand):
            queue = self._resolve_queue(cmd.entity_id, cmd.entity_type, None)
            if queue is not None and 0 <= cmd.item_index < len(queue):
                queue.pop(cmd.item_index)

        return ValidationResult()

    def _resolve_entity(self, entity_id, entity_type):
        """Resolve entity by ID and type."""
        if entity_type == "planet":
            for planets in self.galaxy._global_hex_planets.values():
                for planet in planets:
                    if getattr(planet, 'id', None) == entity_id:
                        return planet
        elif entity_type == "fleet":
            return self.galaxy.fleets_by_id.get(entity_id)
        return None

    def _resolve_queue(self, entity_id, entity_type, queue_id):
        """Resolve the construction queue, handling multi-queue entities."""
        entity = self._resolve_entity(entity_id, entity_type)
        if entity is None:
            return None

        if queue_id is None:
            return getattr(entity, 'construction_queue', None)

        # Check if queue_id matches a facility's instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return getattr(facility, 'construction_queue', None)

        # Fallback to entity's main queue
        return getattr(entity, 'construction_queue', None)

@pytest.fixture
def mock_design_library():
    """Mock DesignLibrary for testing.

    PROJ-40: Updated to create mock directly instead of patching.
    Now injected via DI.
    """
    mock_instance = MagicMock()

    # Design matching the default "complex" category
    design = MagicMock()
    design.design_id = "mining_complex_mk1"
    design.name = "Mining Complex"
    design.vehicle_type = "Planetary Complex"  # Category matching

    mock_instance.scan_designs.return_value = [design]
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
def build_queue_screen(mock_design_library, mock_design_loader, mock_registries, ui_manager):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection.
    PROJ-109: Updated to provide required hex_coord, galaxy, empire parameters.
    PROJ-211: Updated to pass registries for DI.
    """
    manager = ui_manager

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

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)
    on_close = MagicMock()

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

    # CRITICAL: Update manager to calculate rects
    manager.update(0.1)

    yield bq_screen

def test_drag_start(build_queue_screen):
    """Test that clicking a design button starts a drag."""
    # PROJ-180: Access via panels.*
    # Find a design button (now nested inside row panels)
    design_button = None
    for element in build_queue_screen.panels.items_scrollable.get_container().elements:
        # Check if this element is a row panel containing the button
        if isinstance(element, pygame_gui.elements.UIPanel) and hasattr(element, 'design_id'):
            # Search inside the panel for the button
            for child in element.get_container().elements:
                if isinstance(child, pygame_gui.elements.UIButton) and hasattr(child, 'design_id'):
                    design_button = child
                    break
        # Also check direct buttons (backwards compatibility)
        elif isinstance(element, pygame_gui.elements.UIButton) and hasattr(element, 'design_id'):
            design_button = element
        if design_button:
            break

    assert design_button is not None
    
    # Simulate mouse down on button using absolute coordinates
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
        'button': 1,
        'pos': design_button.get_abs_rect().center
    })
    build_queue_screen.handle_event(event)
    
    # Check if drag started
    assert build_queue_screen.drag_handler.dragged_item is not None
    assert build_queue_screen.drag_handler.dragged_item['design_id'] == design_button.design_id

def test_drag_drop_success(build_queue_screen):
    """Test that dropping a dragged design into the queue works."""
    # Setup drag state manually
    build_queue_screen.drag_handler.dragged_item = {
        'design_id': 'mining_complex_mk1',
        'name': 'Mining Complex',
        'category': 'complex'
    }
    
    initial_queue_len = len(build_queue_screen.build_context.construction_queue)
    
    # PROJ-180: Access via panels.*
    # Simulate mouse up over build queue panel
    drop_pos = build_queue_screen.panels.build_queue_panel.rect.center
    event = pygame.event.Event(pygame.MOUSEBUTTONUP, {
        'button': 1,
        'pos': drop_pos
    })
    build_queue_screen.handle_event(event)
    
    # Verify item added to queue
    assert len(build_queue_screen.build_context.construction_queue) == initial_queue_len + 1
    assert build_queue_screen.build_context.construction_queue[-1]['design_id'] == 'mining_complex_mk1'
    # Verify drag cleared
    assert build_queue_screen.drag_handler.dragged_item is None

def test_drag_cancel(build_queue_screen):
    """Test that dropping outside the queue cancels the drag (or removes if from queue)."""
    build_queue_screen.drag_handler.dragged_item = {
        'design_id': 'frigate_mk1',
        'name': 'Frigate',
        'category': 'ship'
    }
    
    initial_queue_len = len(build_queue_screen.build_context.construction_queue)
    
    # Simulate mouse up somewhere else (e.g. top left corner)
    drop_pos = (0, 0)
    event = pygame.event.Event(pygame.MOUSEBUTTONUP, {
        'button': 1,
        'pos': drop_pos
    })
    build_queue_screen.handle_event(event)
    
    # Verify nothing added
    assert len(build_queue_screen.build_context.construction_queue) == initial_queue_len
    # Verify drag cleared
    assert build_queue_screen.drag_handler.dragged_item is None

def test_reorder_queue(build_queue_screen):
    """Test reordering items within the queue."""
    # Setup initial queue: [A, B]
    build_queue_screen.build_context.construction_queue.clear()
    build_queue_screen.build_context.construction_queue.extend([
        {"design_id": "item_A", "type": "complex", "turns_remaining": 5},
        {"design_id": "item_B", "type": "complex", "turns_remaining": 5}
    ])
    build_queue_screen._refresh_queue_display()
    # CRITICAL: Update manager to calculate rects for new panels
    build_queue_screen.manager.update(0.1)
    
    # PROJ-221: Use VirtualTable row pool to find queue item row positions
    vt = build_queue_screen.panels.virtual_table
    row_pool = vt._row_pool
    # Row 1 (item B) - get its background panel position
    row_b_bg = row_pool[1]["bg"]

    # 1. Pick up B - start with mouse down
    event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
        'button': 1,
        'pos': row_b_bg.get_abs_rect().center
    })
    build_queue_screen.handle_event(event_down)

    # Simulate mouse motion to exceed drag threshold (10 pixels)
    motion_pos = (row_b_bg.get_abs_rect().centerx + 15,
                  row_b_bg.get_abs_rect().centery + 15)
    event_motion = pygame.event.Event(pygame.MOUSEMOTION, {
        'pos': motion_pos,
        'rel': (15, 15),
        'buttons': (1, 0, 0)  # Left button held down
    })
    build_queue_screen.handle_event(event_motion)

    assert build_queue_screen.drag_handler.dragged_item['design_id'] == "item_B"
    assert len(build_queue_screen.build_context.construction_queue) == 1 # A is left

    # PROJ-221: Drop at top of VirtualTable list view panel
    list_panel = vt._list_view_panel
    drop_pos = (list_panel.get_abs_rect().centerx,
                list_panel.get_abs_rect().top + 5)
    
    event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {
        'button': 1,
        'pos': drop_pos
    })
    build_queue_screen.handle_event(event_up)
    
    # 3. Verify: [B, A]
    assert len(build_queue_screen.build_context.construction_queue) == 2
    assert build_queue_screen.build_context.construction_queue[0]['design_id'] == "item_B"
    assert build_queue_screen.build_context.construction_queue[1]['design_id'] == "item_A"

def test_remove_from_queue(build_queue_screen):
    """Test removing an item by dragging it outside."""
    build_queue_screen.build_context.construction_queue.clear()
    build_queue_screen.build_context.construction_queue.extend([
        {"design_id": "to_remove", "type": "complex", "turns_remaining": 5}
    ])
    build_queue_screen._refresh_queue_display()
    build_queue_screen.manager.update(0.1)

    # PROJ-221: Use VirtualTable row pool to find queue item row positions
    vt = build_queue_screen.panels.virtual_table
    row_0_bg = vt._row_pool[0]["bg"]

    # 1. Pick up - start with mouse down
    event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
        'button': 1,
        'pos': row_0_bg.get_abs_rect().center
    })
    build_queue_screen.handle_event(event_down)

    # Simulate mouse motion to exceed drag threshold (10 pixels)
    motion_pos = (row_0_bg.get_abs_rect().centerx + 15,
                  row_0_bg.get_abs_rect().centery + 15)
    event_motion = pygame.event.Event(pygame.MOUSEMOTION, {
        'pos': motion_pos,
        'rel': (15, 15),
        'buttons': (1, 0, 0)  # Left button held down
    })
    build_queue_screen.handle_event(event_motion)

    # Verify drag started
    assert build_queue_screen.drag_handler.dragged_item is not None

    # 2. Drop outside (e.g. (0,0))
    event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {
        'button': 1,
        'pos': (0, 0)
    })
    build_queue_screen.handle_event(event_up)
    
    # 3. Verify queue is empty
    assert len(build_queue_screen.build_context.construction_queue) == 0
    assert build_queue_screen.drag_handler.dragged_item is None
