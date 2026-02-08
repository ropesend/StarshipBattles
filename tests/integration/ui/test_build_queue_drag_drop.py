import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.ui.screens.build_queue_screen import BuildQueueScreen

class MockSession:
    def __init__(self):
        self.save_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))

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
def build_queue_screen(mock_design_library, mock_design_loader):
    """Create BuildQueueScreen for testing.

    PROJ-40: Updated to use DI injection.
    """
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))

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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    session = MockSession()
    on_close = MagicMock()

    bq_screen = BuildQueueScreen(
        manager,
        planet,
        session,
        on_close,
        design_library=mock_design_library,
        design_loader=mock_design_loader
    )

    # CRITICAL: Update manager to calculate rects
    manager.update(0.1)

    yield bq_screen
    pygame.quit()

def test_drag_start(build_queue_screen):
    """Test that clicking a design button starts a drag."""
    # Find a design button (now nested inside row panels)
    design_button = None
    for element in build_queue_screen.items_scrollable.get_container().elements:
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
    
    # Simulate mouse up over build queue panel
    drop_pos = build_queue_screen.build_queue_panel.rect.center
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
    
    # Drag item B (index 1) to top (estimate y offset)
    # Find panel for item B
    panel_B = build_queue_screen.queue_items[1]
    
    # 1. Pick up B - start with mouse down
    event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
        'button': 1,
        'pos': panel_B.get_abs_rect().center
    })
    build_queue_screen.handle_event(event_down)

    # Simulate mouse motion to exceed drag threshold (10 pixels)
    motion_pos = (panel_B.get_abs_rect().centerx + 15,
                  panel_B.get_abs_rect().centery + 15)
    event_motion = pygame.event.Event(pygame.MOUSEMOTION, {
        'pos': motion_pos,
        'rel': (15, 15),
        'buttons': (1, 0, 0)  # Left button held down
    })
    build_queue_screen.handle_event(event_motion)

    assert build_queue_screen.drag_handler.dragged_item['design_id'] == "item_B"
    assert len(build_queue_screen.build_context.construction_queue) == 1 # A is left
    
    # 2. Drop at top of queue panel
    # The queue panel starts at some Y. rel_y // 65 = 0 means index 0.
    # Let's drop at the absolute top of the queue scrollable
    drop_pos = (build_queue_screen.queue_scrollable.get_abs_rect().centerx, 
                build_queue_screen.queue_scrollable.get_abs_rect().top + 5)
    
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
    
    panel = build_queue_screen.queue_items[0]
    
    # 1. Pick up - start with mouse down
    event_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
        'button': 1,
        'pos': panel.get_abs_rect().center
    })
    build_queue_screen.handle_event(event_down)

    # Simulate mouse motion to exceed drag threshold (10 pixels)
    motion_pos = (panel.get_abs_rect().centerx + 15,
                  panel.get_abs_rect().centery + 15)
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
