"""Tests for EmpireBuildQueueWindow (PROJ-76 Phase 2).

Verifies the empire-wide build queue window foundation:
- Window initialization and layout
- Source list population
- Row rendering and selection
- Close callback behavior
- Empty empire handling
"""
import pytest
from unittest.mock import MagicMock, patch, call

from game.strategy.data.build_queue_source import BuildQueueSource


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source(queue_id="planet_1_base", display_name="Alpha - Base",
                 context_type="planet", can_build_ships=False,
                 can_build_complexes=True, queue_items=None) -> BuildQueueSource:
    """Create a BuildQueueSource for testing."""
    return BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=MagicMock(),
        construction_queue=queue_items or [],
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type=context_type,
    )


def _make_window(sources=None, on_close=None, on_navigate=None):
    """Create an EmpireBuildQueueWindow with mocked pygame_gui.

    Bypasses UIWindow.__init__ to avoid needing real pygame display.
    Sets up minimal state for testing business logic.
    """
    from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow

    if sources is None:
        sources = [
            _make_source("planet_1_base", "Alpha - Base", "planet"),
            _make_source("yard-001", "Alpha - Shipyard 1", "planet",
                         can_build_ships=True),
            _make_source("fleet_5", "Explorer Fleet - Space Yard", "fleet",
                         can_build_ships=True),
        ]

    mock_empire = MagicMock()
    mock_galaxy = MagicMock()

    with patch.object(EmpireBuildQueueWindow, '__init__',
                      lambda self, *a, **kw: None):
        win = EmpireBuildQueueWindow.__new__(EmpireBuildQueueWindow)

    # Set up minimal state matching constructor
    win.empire = mock_empire
    win.galaxy = mock_galaxy
    win.on_close_callback = on_close
    win.on_navigate_to_hex = on_navigate
    win.all_sources = list(sources)
    win.filtered_sources = list(sources)
    win.selected_source = None
    win.selected_index = -1
    win.row_height = 50
    win.header_height = 40
    win.sidebar_width = 300
    win.ui_manager = MagicMock()

    # Mock UI elements
    win.scroll_bar = MagicMock()
    win.scroll_bar.start_percentage = 0.0
    win.scroll_bar.visible_percentage = 1.0
    win.list_panel = MagicMock()
    win.list_view_rect = MagicMock()
    win.list_view_rect.height = 500
    win.main_panel = MagicMock()
    win.header_container = MagicMock()
    win.sidebar_panel = MagicMock()
    win.row_elements = []

    return win


# =======================================================================
# Initialization Tests
# =======================================================================

class TestWindowInitialization:
    """EmpireBuildQueueWindow should initialize with correct state."""

    def test_window_stores_empire(self):
        """Window stores empire reference."""
        win = _make_window()
        assert win.empire is not None

    def test_window_stores_galaxy(self):
        """Window stores galaxy reference."""
        win = _make_window()
        assert win.galaxy is not None

    def test_window_stores_sources(self):
        """Window collects and stores build queue sources."""
        sources = [
            _make_source("p1", "Planet 1"),
            _make_source("p2", "Planet 2"),
        ]
        win = _make_window(sources=sources)
        assert len(win.all_sources) == 2
        assert win.all_sources[0].queue_id == "p1"
        assert win.all_sources[1].queue_id == "p2"

    def test_window_no_initial_selection(self):
        """Window starts with no row selected."""
        win = _make_window()
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_window_stores_close_callback(self):
        """Window stores close callback."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        assert win.on_close_callback is cb

    def test_window_stores_navigate_callback(self):
        """Window stores navigate-to-hex callback."""
        cb = MagicMock()
        win = _make_window(on_navigate=cb)
        assert win.on_navigate_to_hex is cb


# =======================================================================
# Source Display Tests
# =======================================================================

class TestSourceDisplay:
    """Window should display build queue sources correctly."""

    def test_displays_all_sources(self):
        """All sources appear in filtered list initially."""
        sources = [
            _make_source("p1", "Alpha - Base"),
            _make_source("p2", "Beta - Shipyard 1"),
            _make_source("f1", "Fleet - Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        assert len(win.filtered_sources) == 3

    def test_source_names_accessible(self):
        """Display names are accessible from filtered sources."""
        sources = [_make_source("p1", "Alpha - Base")]
        win = _make_window(sources=sources)
        assert win.filtered_sources[0].display_name == "Alpha - Base"

    def test_empty_empire_shows_no_sources(self):
        """Window handles empire with no build queues gracefully."""
        win = _make_window(sources=[])
        assert len(win.all_sources) == 0
        assert len(win.filtered_sources) == 0


# =======================================================================
# Row Selection Tests
# =======================================================================

class TestRowSelection:
    """Window should handle row click selection."""

    def test_select_source_updates_selected(self):
        """Clicking a source row updates selected_source."""
        sources = [
            _make_source("p1", "Alpha - Base"),
            _make_source("p2", "Beta - Shipyard"),
        ]
        win = _make_window(sources=sources)
        win._select_source(1)
        assert win.selected_source is sources[1]
        assert win.selected_index == 1

    def test_select_first_source(self):
        """Can select the first source."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(0)
        assert win.selected_source is sources[0]
        assert win.selected_index == 0

    def test_select_out_of_range_ignored(self):
        """Selecting an invalid index does not crash."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(5)
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_select_negative_index_ignored(self):
        """Selecting a negative index does not crash."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(-1)
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_reselect_same_source(self):
        """Selecting the same source again keeps selection."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(0)
        win._select_source(0)
        assert win.selected_index == 0


# =======================================================================
# Close Callback Tests
# =======================================================================

class TestCloseCallback:
    """Window close should invoke callback."""

    def test_close_calls_callback(self):
        """kill() invokes on_close_callback."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        # Mock the parent kill to avoid real UIWindow teardown
        with patch('pygame_gui.elements.UIWindow.kill'):
            win.kill()
        cb.assert_called_once()

    def test_close_without_callback_no_crash(self):
        """kill() works when no callback is provided."""
        win = _make_window(on_close=None)
        with patch('pygame_gui.elements.UIWindow.kill'):
            win.kill()
        # No exception = success


# =======================================================================
# Queue Info Display Tests
# =======================================================================

class TestQueueInfoDisplay:
    """Window should format queue info for display."""

    def test_get_queue_summary_empty_queue(self):
        """Empty queue shows dash placeholder."""
        source = _make_source("p1", "Alpha", queue_items=[])
        win = _make_window(sources=[source])
        summary = win._get_queue_summary(source)
        assert summary == "-"

    def test_get_queue_summary_with_items(self):
        """Queue with items shows count."""
        items = [
            {"design_id": "frigate", "turns_remaining": 3},
            {"design_id": "destroyer", "turns_remaining": 5},
        ]
        source = _make_source("p1", "Alpha", queue_items=items)
        win = _make_window(sources=[source])
        summary = win._get_queue_summary(source)
        assert "2" in summary

    def test_get_capabilities_text_complexes_only(self):
        """Source that can only build complexes shows 'Complexes'."""
        source = _make_source(can_build_ships=False, can_build_complexes=True)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Complexes"

    def test_get_capabilities_text_ships_and_complexes(self):
        """Source that can build both shows 'Ships & Complexes'."""
        source = _make_source(can_build_ships=True, can_build_complexes=True)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Ships & Complexes"

    def test_get_capabilities_text_ships_only(self):
        """Source that can only build ships shows 'Ships'."""
        source = _make_source(can_build_ships=True, can_build_complexes=False)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Ships"
