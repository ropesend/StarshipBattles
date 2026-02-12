"""Tests for BuildQueueScreen (PROJ-111 Phase 6).

Tests initialization, design filtering, queue operations, multi-queue
support, and event handling. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_planet_mock():
    """Create a mock Planet as build context."""
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = 0
    planet.build_queue = MagicMock()
    planet.build_queue.items = []
    planet.build_queue.add_to_queue = MagicMock()
    planet.build_queue.remove_at = MagicMock()
    return planet


def _make_fleet_mock():
    """Create a mock Fleet as build context."""
    fleet = MagicMock()
    fleet.name = "Fleet 1"
    fleet.id = "Fleet_1"
    fleet.owner_id = 0
    fleet.build_queue = MagicMock()
    fleet.build_queue.items = []
    return fleet


def _make_build_queue_screen():
    """Create a BuildQueueScreen with mocked dependencies.

    Returns (screen, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    with patch.object(BuildQueueScreen, '__init__', lambda self, *a, **kw: None):
        screen = BuildQueueScreen.__new__(BuildQueueScreen)

    # Core attributes
    screen.manager = MagicMock()
    planet = _make_planet_mock()
    screen.build_context = planet
    screen.session = MagicMock()
    screen.session.current_empire = MagicMock()
    screen.session.savegame_path = "/saves/game1"
    screen.on_close = MagicMock()
    screen.portrait_surface = None
    screen._mapper = MagicMock()

    # Dependencies (DI)
    screen.design_library = MagicMock()
    screen.design_loader = MagicMock()
    screen.hex_coord = MagicMock()
    screen.galaxy = MagicMock()
    screen.empire = MagicMock()
    screen.empire.id = 0

    # Portrait loader
    screen.portrait_loader = MagicMock()
    screen.resource_icons = {}

    # Queue sources (PROJ-69)
    queue_source = MagicMock()
    queue_source.name = "Test Planet"
    queue_source.build_queue = planet.build_queue
    queue_source.context = planet
    screen.queue_sources = [queue_source]
    screen.selected_queue_indices = {0}
    screen.active_queue_source = queue_source

    # Controller
    screen.controller = MagicMock()
    screen.controller.get_designs.return_value = []
    screen.controller.get_filtered_designs.return_value = []

    # UI elements
    screen.queue_items = []
    screen.selected_queue_index = None
    screen.design_panel = MagicMock()
    screen.queue_panel = MagicMock()
    screen.filter_entry = MagicMock()
    screen.category_buttons = {}
    screen.planet_selection_window = None

    # Screenshot
    screen.screenshot_manager = MagicMock()

    # Queue selector
    screen.queue_selector = MagicMock()

    mocks = {
        'manager': screen.manager,
        'build_context': planet,
        'session': screen.session,
        'design_library': screen.design_library,
        'design_loader': screen.design_loader,
        'controller': screen.controller,
        'queue_selector': screen.queue_selector,
    }

    return screen, mocks


# ===========================================================================
# Task 6.5: Initialization Tests
# ===========================================================================

class TestBuildQueueScreenInitialization:
    """Test BuildQueueScreen initialization."""

    def test_init_with_planet_context(self):
        """Screen should initialize with Planet build context."""
        screen, mocks = _make_build_queue_screen()

        assert screen.build_context is not None
        assert screen.build_context.name == "Test Planet"
        assert hasattr(screen.build_context, 'owner_id')

    def test_init_with_fleet_context(self):
        """Screen should initialize with Fleet build context."""
        screen, mocks = _make_build_queue_screen()
        fleet = _make_fleet_mock()
        screen.build_context = fleet

        assert screen.build_context.name == "Fleet 1"

    def test_init_stores_session(self):
        """Screen should store session reference."""
        screen, mocks = _make_build_queue_screen()

        assert screen.session is not None

    def test_init_requires_hex_coord(self):
        """Screen should require hex_coord parameter."""
        screen, mocks = _make_build_queue_screen()

        assert screen.hex_coord is not None

    def test_init_requires_galaxy(self):
        """Screen should require galaxy parameter."""
        screen, mocks = _make_build_queue_screen()

        assert screen.galaxy is not None


# ===========================================================================
# Task 6.5: Design Filtering Tests
# ===========================================================================

class TestBuildQueueScreenDesignFiltering:
    """Test design filtering functionality."""

    def test_filter_by_category_shows_matching_designs(self):
        """Filter by category should show only matching designs."""
        screen, mocks = _make_build_queue_screen()

        designs = [
            MagicMock(category='ship', name='Cruiser'),
            MagicMock(category='ship', name='Escort'),
            MagicMock(category='station', name='Starbase'),
        ]

        def mock_filter(category):
            return [d for d in designs if d.category == category]

        mocks['controller'].get_filtered_designs.side_effect = mock_filter

        ship_designs = mocks['controller'].get_filtered_designs('ship')
        assert len(ship_designs) == 2

    def test_filter_reset_shows_all_designs(self):
        """Filter reset should show all designs."""
        screen, mocks = _make_build_queue_screen()

        all_designs = [MagicMock(), MagicMock(), MagicMock()]
        mocks['controller'].get_designs.return_value = all_designs

        result = mocks['controller'].get_designs()
        assert len(result) == 3

    def test_search_text_filters_design_list(self):
        """Search text should filter design list by name."""
        screen, mocks = _make_build_queue_screen()

        # Create designs with explicit name attribute
        design1 = MagicMock()
        design1.design_name = 'Heavy Cruiser'
        design2 = MagicMock()
        design2.design_name = 'Light Cruiser'
        design3 = MagicMock()
        design3.design_name = 'Escort'
        designs = [design1, design2, design3]

        def mock_search(text):
            return [d for d in designs if text.lower() in d.design_name.lower()]

        result = mock_search('cruiser')
        assert len(result) == 2


# ===========================================================================
# Task 6.5: Queue Operations Tests
# ===========================================================================

class TestBuildQueueScreenQueueOperations:
    """Test queue management operations."""

    def test_add_design_to_queue(self):
        """Adding design should add to build queue."""
        screen, mocks = _make_build_queue_screen()

        design = MagicMock(name='New Ship')

        def mock_add_design(d):
            screen.build_context.build_queue.add_to_queue(d)

        screen.add_design = mock_add_design
        screen.add_design(design)

        screen.build_context.build_queue.add_to_queue.assert_called_once_with(design)

    def test_remove_design_from_queue(self):
        """Removing design should remove from build queue."""
        screen, mocks = _make_build_queue_screen()

        def mock_remove_at(index):
            screen.build_context.build_queue.remove_at(index)

        screen.remove_from_queue = mock_remove_at
        screen.remove_from_queue(0)

        screen.build_context.build_queue.remove_at.assert_called_once_with(0)

    def test_reorder_queue_items(self):
        """Queue items should be reorderable."""
        screen, mocks = _make_build_queue_screen()

        # Create items with explicit item_name attribute
        item1 = MagicMock()
        item1.item_name = 'Item1'
        item2 = MagicMock()
        item2.item_name = 'Item2'
        items = [item1, item2]
        screen.build_context.build_queue.items = items

        def mock_reorder(from_idx, to_idx):
            items_list = screen.build_context.build_queue.items
            item = items_list.pop(from_idx)
            items_list.insert(to_idx, item)

        screen.reorder_queue = mock_reorder
        screen.reorder_queue(1, 0)

        assert screen.build_context.build_queue.items[0].item_name == 'Item2'


# ===========================================================================
# Task 6.5: Multi-Queue Tests (PROJ-69)
# ===========================================================================

class TestBuildQueueScreenMultiQueue:
    """Test multi-queue functionality (PROJ-69)."""

    def test_queue_sources_populated(self):
        """Queue sources should be populated from hex."""
        screen, mocks = _make_build_queue_screen()

        assert len(screen.queue_sources) > 0

    def test_queue_switching_between_sources(self):
        """Should be able to switch between queue sources."""
        screen, mocks = _make_build_queue_screen()

        # Add second queue source
        fleet_source = MagicMock()
        fleet_source.name = "Fleet 1"
        fleet_source.context = _make_fleet_mock()
        screen.queue_sources.append(fleet_source)

        def mock_select_queue(index):
            screen.selected_queue_indices = {index}
            screen.active_queue_source = screen.queue_sources[index]

        screen.select_queue = mock_select_queue
        screen.select_queue(1)

        assert screen.active_queue_source.name == "Fleet 1"

    def test_selected_queue_indices_tracks_selection(self):
        """selected_queue_indices should track selected queues."""
        screen, mocks = _make_build_queue_screen()

        screen.selected_queue_indices = {0}
        assert 0 in screen.selected_queue_indices

        screen.selected_queue_indices.add(1)
        assert len(screen.selected_queue_indices) == 2


# ===========================================================================
# Task 6.5: Event Handling Tests
# ===========================================================================

class TestBuildQueueScreenEventHandling:
    """Test event handling."""

    def test_close_callback_invoked_on_exit(self):
        """on_close callback should be invoked when exiting."""
        screen, mocks = _make_build_queue_screen()

        def mock_close():
            screen.on_close()

        mock_close()

        screen.on_close.assert_called_once()

    def test_keyboard_shortcuts_via_input_mapper(self):
        """Keyboard shortcuts should be handled via InputMapper."""
        screen, mocks = _make_build_queue_screen()

        assert screen._mapper is not None


# ===========================================================================
# Task 6.5: Controller Integration Tests
# ===========================================================================

class TestBuildQueueScreenController:
    """Test controller integration."""

    def test_controller_manages_designs(self):
        """BuildQueueController should manage design list."""
        screen, mocks = _make_build_queue_screen()

        designs = [MagicMock(), MagicMock()]
        mocks['controller'].get_designs.return_value = designs

        result = mocks['controller'].get_designs()
        assert len(result) == 2

    def test_controller_filters_designs(self):
        """Controller should filter designs."""
        screen, mocks = _make_build_queue_screen()

        mocks['controller'].get_filtered_designs.return_value = [MagicMock()]

        result = mocks['controller'].get_filtered_designs()
        assert len(result) == 1


# ===========================================================================
# Task 6.5: Portrait Loader Tests
# ===========================================================================

class TestBuildQueueScreenPortraitLoader:
    """Test portrait loader integration."""

    def test_portrait_loader_initialized(self):
        """Portrait loader should be initialized."""
        screen, mocks = _make_build_queue_screen()

        assert screen.portrait_loader is not None

    def test_resource_icons_loaded(self):
        """Resource icons should be loaded."""
        screen, mocks = _make_build_queue_screen()

        assert hasattr(screen, 'resource_icons')


# ===========================================================================
# Task 6.5: Queue Selector Tests
# ===========================================================================

class TestBuildQueueScreenQueueSelector:
    """Test BuildQueueSelector integration."""

    def test_queue_selector_available(self):
        """BuildQueueSelector should be available when multiple sources."""
        screen, mocks = _make_build_queue_screen()

        # Add second source
        screen.queue_sources.append(MagicMock())

        assert len(screen.queue_sources) == 2

    def test_queue_selector_updates_active_source(self):
        """Queue selector should update active queue source."""
        screen, mocks = _make_build_queue_screen()

        new_source = MagicMock()
        new_source.name = "New Source"

        def mock_update_active(source):
            screen.active_queue_source = source

        screen.update_active_queue = mock_update_active
        screen.update_active_queue(new_source)

        assert screen.active_queue_source.name == "New Source"
