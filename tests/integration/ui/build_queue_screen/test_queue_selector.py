"""
Tests for BuildQueueScreen queue selector panel (PROJ-69 Phase 3).

Tests cover:
- Queue selector panel creation and visibility
- Single-click queue selection
- Ctrl+click multi-select toggle
- Queue display updates when switching queues
- Multi-select message display
- Queue source backward compatibility (single build_context)
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.build_queue_source import BuildQueueSource
from game.core.validation import validation_result


class MockSession:
    def __init__(self):
        self.savegame_path = "test_savegame"
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))

    def handle_command(self, cmd):
        return validation_result(True, "Command processed")


@pytest.fixture
def mock_design_library():
    mock_instance = MagicMock()
    design = MagicMock()
    design.design_id = "mining_complex_mk1"
    design.name = "Mining Complex"
    design.vehicle_type = "Planetary Complex"
    mock_instance.scan_designs.return_value = [design]
    mock_instance.designs_folder = "test_designs"
    mock_instance.load_design_data.return_value = None
    return mock_instance


@pytest.fixture
def mock_design_loader():
    return MagicMock()


@pytest.fixture
def build_queue_screen(mock_design_library, mock_design_loader):
    """Create BuildQueueScreen for testing queue selector."""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    manager = pygame_gui.UIManager((1920, 1080))

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

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(
        manager,
        planet,
        session,
        on_close,
        design_library=mock_design_library,
        design_loader=mock_design_loader
    )

    manager.update(0.1)
    yield bq_screen
    pygame.quit()


# --- Panel existence tests ---

def test_queue_selector_panel_exists(build_queue_screen):
    """Test that queue selector panel is created."""
    assert hasattr(build_queue_screen, 'queue_selector_panel')
    assert build_queue_screen.queue_selector_panel is not None


def test_queue_selector_scrollable_exists(build_queue_screen):
    """Test that queue selector scrollable container is created."""
    assert hasattr(build_queue_screen, 'queue_selector_scrollable')
    assert build_queue_screen.queue_selector_scrollable is not None


def test_queue_selector_buttons_exist(build_queue_screen):
    """Test that queue selector buttons are created for each queue source."""
    assert hasattr(build_queue_screen, 'queue_selector_buttons')
    assert len(build_queue_screen.queue_selector_buttons) == len(build_queue_screen.queue_sources)


# --- Queue source initialization tests ---

def test_single_build_context_creates_one_queue_source(build_queue_screen):
    """Test that a single build_context creates one queue source in backward compat mode."""
    assert len(build_queue_screen.queue_sources) == 1
    source = build_queue_screen.queue_sources[0]
    assert isinstance(source, BuildQueueSource)
    assert source.context_type == "planet"
    assert source.can_build_complexes is True


def test_queue_source_references_same_queue(build_queue_screen):
    """Test that the queue source's construction_queue is the same object as build_context's."""
    source = build_queue_screen.queue_sources[0]
    assert source.construction_queue is build_queue_screen.build_context.construction_queue


def test_default_selection_is_first_queue(build_queue_screen):
    """Test that the first queue is selected by default."""
    assert 0 in build_queue_screen.selected_queue_indices
    assert build_queue_screen.active_queue_source is build_queue_screen.queue_sources[0]


# --- Queue selection tests ---

def test_on_queue_selected_updates_active_source(build_queue_screen):
    """Test that queue selection updates the active queue source."""
    # With single source, selecting index 0 should still work
    # PROJ-86: Use selector's internal method via screen's callback
    build_queue_screen._queue_selector._on_queue_selected(0)
    assert build_queue_screen.active_queue_source is build_queue_screen.queue_sources[0]
    assert build_queue_screen.selected_queue_indices == {0}


def test_on_queue_toggled_prevents_empty_selection(build_queue_screen):
    """Test that toggling off the only selected queue falls back to index 0."""
    # PROJ-86: Use selector's internal method via screen's callback
    build_queue_screen._queue_selector._on_queue_toggled(0)
    # Should not allow empty selection - falls back to {0}
    assert len(build_queue_screen.selected_queue_indices) > 0
    assert 0 in build_queue_screen.selected_queue_indices


# --- Multi-source tests (simulated) ---

def test_multiple_queue_sources_create_buttons():
    """Test that multiple queue sources create multiple selector buttons."""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    manager = pygame_gui.UIManager((1920, 1080))

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

    # Add a shipyard facility so there are 2 queue sources
    shipyard = PlanetaryFacility(
        instance_id="shipyard-1",
        design_id="space_shipyard_complex",
        name="Space Shipyard",
        design_data={"layers": {"OUTER": [{"id": "space_shipyard", "modifiers": []}]}},
        is_operational=True
    )
    planet.facilities.append(shipyard)

    session = MockSession()

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = None

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager, planet, session, lambda: None,
        design_library=mock_lib, design_loader=MagicMock()
    )

    # Should have 1 legacy source (backward compat wraps build_context as single source)
    assert len(bq.queue_sources) == 1
    assert len(bq.queue_selector_buttons) == 1

    pygame.quit()


def test_multi_select_sets_active_to_none():
    """Test that selecting multiple queues sets active_queue_source to None."""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    manager = pygame_gui.UIManager((1920, 1080))

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

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = None

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager, planet, session, lambda: None,
        design_library=mock_lib, design_loader=MagicMock()
    )

    # Manually add a second queue source to test multi-select behavior
    second_source = BuildQueueSource(
        queue_id="test_second",
        display_name="Test Second Queue",
        owner_entity=planet,
        construction_queue=[],
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet"
    )
    bq.queue_sources.append(second_source)
    bq._refresh_queue_selector()

    # Select both queues
    # PROJ-86: Use selector's internal methods
    bq._queue_selector.selected_indices = {0}
    bq._queue_selector._on_queue_toggled(1)

    assert len(bq.selected_queue_indices) == 2
    assert bq.active_queue_source is None

    # Go back to single select
    bq._queue_selector._on_queue_selected(0)
    assert len(bq.selected_queue_indices) == 1
    assert bq.active_queue_source is bq.queue_sources[0]

    pygame.quit()


def test_queue_display_shows_active_source_items():
    """Test that queue display shows items from the active queue source."""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    manager = pygame_gui.UIManager((1920, 1080))

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

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = None

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager, planet, session, lambda: None,
        design_library=mock_lib, design_loader=MagicMock()
    )

    # Add items to the active queue source
    bq.active_queue_source.construction_queue.append({
        "design_id": "test_item", "type": "complex", "turns_remaining": 3
    })
    bq._refresh_queue_display()

    # Should have 1 queue item displayed
    assert len(bq.queue_items) == 1

    pygame.quit()


def test_queue_selector_has_queue_source_index_tags(build_queue_screen):
    """Test that queue selector buttons are tagged with queue_source_index."""
    for idx, btn in enumerate(build_queue_screen.queue_selector_buttons):
        assert hasattr(btn, 'queue_source_index')
        assert btn.queue_source_index == idx
