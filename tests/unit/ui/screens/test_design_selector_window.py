"""Tests for DesignSelectorWindow (PROJ-111 Phase 6 Task 6.6).

Tests initialization, filtering, selection, and event handling for the
design selection UI. Uses bypass-init pattern to avoid UIWindow dependencies.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_design_metadata(design_id="ship_001", name="Test Ship", ship_class="Cruiser",
                          vehicle_type="Ship", mass=150.0, is_obsolete=False):
    """Create a mock DesignMetadata."""
    design = MagicMock()
    design.design_id = design_id
    design.name = name
    design.ship_class = ship_class
    design.vehicle_type = vehicle_type
    design.mass = mass
    design.is_obsolete = is_obsolete
    return design


def _make_design_catalog(designs=None):
    """Create a mock DesignLibrary."""
    library = MagicMock()
    library.designs_folder = "/saves/empire_1/designs"

    # Default designs if none provided
    if designs is None:
        designs = [
            _make_design_metadata("ship_001", "Alpha Cruiser", "Cruiser", "Ship", 150.0),
            _make_design_metadata("ship_002", "Beta Destroyer", "Destroyer", "Ship", 80.0),
            _make_design_metadata("ship_003", "Gamma Fighter", "Escort", "Fighter", 30.0),
            _make_design_metadata("ship_004", "Old Battleship", "Battleship", "Ship", 300.0, True),
        ]

    # search_designs returns filtered list
    def search_designs(name_query="", filters=None):
        result = list(designs)
        if filters is None:
            filters = {}

        # Filter by name
        if name_query:
            result = [d for d in result if name_query.lower() in d.name.lower()]

        # Filter by ship class
        ship_class = filters.get('ship_class')
        if ship_class:
            result = [d for d in result if d.ship_class == ship_class]

        # Filter by vehicle type
        vehicle_type = filters.get('vehicle_type')
        if vehicle_type:
            result = [d for d in result if d.vehicle_type == vehicle_type]

        # Filter obsolete
        show_obsolete = filters.get('show_obsolete', False)
        if not show_obsolete:
            result = [d for d in result if not d.is_obsolete]

        return result

    library.search_designs = MagicMock(side_effect=search_designs)
    library.mark_obsolete = MagicMock(return_value=(True, "Success"))

    return library


def _make_selector_window(design_catalog=None, mode="load", on_select_callback=None):
    """Create a DesignSelectorWindow with mocked dependencies.

    Returns (window, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.design_selector_window import DesignSelectorWindow

    # Bypass UIWindow.__init__
    with patch.object(DesignSelectorWindow, '__init__', lambda self, *a, **kw: None):
        window = DesignSelectorWindow.__new__(DesignSelectorWindow)

    # Design library
    if design_catalog is None:
        design_catalog = _make_design_catalog()
    window.design_catalog = design_catalog

    # Mode and callback
    window.mode = mode
    window.on_select_callback = on_select_callback

    # State
    window.all_designs = []
    window.filtered_designs = []
    window.selected_design_id = None

    # Filter state
    window.filter_name = ""
    window.filter_ship_class = None
    window.filter_vehicle_type = None
    window.show_obsolete = False

    # Layout constants
    window.sidebar_width = 250
    window.row_height = 60

    # UI Manager
    ui_manager = MagicMock()
    window.ui_manager = ui_manager

    # Mock UI elements
    window.name_search_entry = MagicMock()
    window.name_search_entry.get_text.return_value = ""

    window.class_dropdown = MagicMock()
    window.class_dropdown.selected_option = "All Classes"

    window.type_dropdown = MagicMock()
    window.type_dropdown.selected_option = "All Types"

    window.role_dropdown = MagicMock()
    window.role_dropdown.selected_option = "All Roles"

    window.obsolete_button = MagicMock()
    window.apply_filters_button = MagicMock()
    window.select_button = MagicMock()
    window.cancel_button = MagicMock()

    # Mock container methods
    window.get_container = MagicMock(return_value=MagicMock())
    window.get_container().get_rect.return_value = pygame.Rect(0, 0, 800, 600)

    # Mock list container
    window.list_container = MagicMock()
    window.list_container.get_container.return_value = MagicMock()
    window.list_container.get_container().get_rect.return_value = pygame.Rect(0, 0, 500, 500)

    # Mock sidebar and button panels
    window.sidebar_panel = MagicMock()
    window.main_panel = MagicMock()
    window.button_panel = MagicMock()

    # Design rows
    window.design_rows = []

    # Button-to-data mappings (replaces monkey-patching on UIButton objects)
    window._button_design_map = {}
    window._obsolete_buttons = set()
    window._obsolete_state_map = {}

    # Mock kill method
    window.kill = MagicMock()

    mocks = {
        'design_catalog': design_catalog,
        'ui_manager': ui_manager,
    }

    return window, mocks


# --- Filtering Tests ---

class TestDesignSelectorFiltering:
    """Tests for design filtering functionality."""

    def test_refresh_designs_calls_search(self):
        """Test _refresh_designs calls search_designs."""
        window, mocks = _make_selector_window()
        window._rebuild_design_list = MagicMock()

        window._refresh_designs()

        mocks['design_catalog'].search_designs.assert_called()

    def test_filter_by_ship_class(self):
        """Test filtering by ship class."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.class_dropdown.selected_option = "Cruiser"

        window._refresh_designs()

        # Check search was called with class filter
        call_args = library.search_designs.call_args
        assert call_args[1]['filters']['ship_class'] == "Cruiser"

    def test_filter_by_vehicle_type(self):
        """Test filtering by vehicle type."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.type_dropdown.selected_option = "Fighter"

        window._refresh_designs()

        # Check search was called with type filter
        call_args = library.search_designs.call_args
        assert call_args[1]['filters']['vehicle_type'] == "Fighter"

    def test_text_search_filters_by_name(self):
        """Test text search filters by design name."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.filter_name = "Alpha"

        window._refresh_designs()

        # Check search was called with name query
        call_args = library.search_designs.call_args
        assert call_args[1]['name_query'] == "Alpha"

    def test_obsolete_filter_toggle(self):
        """Test obsolete filter toggle."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.show_obsolete = True

        window._refresh_designs()

        # Check search was called with show_obsolete
        call_args = library.search_designs.call_args
        assert call_args[1]['filters']['show_obsolete'] is True

    def test_combined_filters(self):
        """Test combining multiple filters."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.filter_name = "Battle"
        window.class_dropdown.selected_option = "Battleship"
        window.show_obsolete = True

        window._refresh_designs()

        call_args = library.search_designs.call_args
        assert call_args[1]['name_query'] == "Battle"
        assert call_args[1]['filters']['ship_class'] == "Battleship"
        assert call_args[1]['filters']['show_obsolete'] is True

    def test_all_classes_means_no_filter(self):
        """Test All Classes dropdown option means no class filter."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.class_dropdown.selected_option = "All Classes"

        window._refresh_designs()

        call_args = library.search_designs.call_args
        assert call_args[1]['filters']['ship_class'] is None

    def test_dropdown_tuple_value_extraction(self):
        """Test handling pygame_gui dropdown tuple values."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        # pygame_gui sometimes returns (current, previous) tuple
        window.class_dropdown.selected_option = ("Destroyer", "Cruiser")

        window._refresh_designs()

        call_args = library.search_designs.call_args
        assert call_args[1]['filters']['ship_class'] == "Destroyer"

    def test_refresh_sorts_by_name(self):
        """Test refresh sorts designs by name."""
        designs = [
            _make_design_metadata("z", "Zephyr"),
            _make_design_metadata("a", "Alpha"),
            _make_design_metadata("m", "Manta"),
        ]
        library = _make_design_catalog(designs)
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()

        window._refresh_designs()

        # Filtered designs should be sorted by name
        names = [d.name for d in window.filtered_designs]
        assert names == sorted(names)


# --- Selection Tests ---

class TestDesignSelectorSelection:
    """Tests for design selection functionality."""

    def test_design_selected_stores_id(self):
        """Test selecting design stores design_id."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)

        # Mock the _on_select to avoid full chain
        window._on_select = MagicMock()

        window._on_design_selected("ship_001")

        assert window.selected_design_id == "ship_001"

    def test_design_selected_enables_select_button(self):
        """Test selecting design enables select button."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)
        window._on_select = MagicMock()

        window._on_design_selected("ship_001")

        window.select_button.enable.assert_called()

    def test_on_select_invokes_callback(self):
        """Test _on_select invokes callback with design_id."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)
        window.selected_design_id = "ship_002"

        window._on_select()

        callback.assert_called_once_with("ship_002")

    def test_on_select_kills_window(self):
        """Test _on_select closes window after callback."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)
        window.selected_design_id = "ship_002"

        window._on_select()

        window.kill.assert_called_once()

    def test_on_select_no_action_without_selection(self):
        """Test _on_select does nothing without selection."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)
        window.selected_design_id = None

        window._on_select()

        callback.assert_not_called()
        window.kill.assert_not_called()

    def test_design_selected_triggers_immediate_selection(self):
        """Test design row select button triggers immediate selection."""
        callback = MagicMock()
        window, _ = _make_selector_window(on_select_callback=callback)

        # _on_design_selected calls _on_select immediately
        window._on_design_selected("ship_003")

        callback.assert_called_once_with("ship_003")

    def test_empty_library_no_selection_available(self):
        """Test empty library has no designs to select."""
        library = _make_design_catalog(designs=[])
        window, _ = _make_selector_window(design_catalog=library)

        window._refresh_designs()

        assert len(window.filtered_designs) == 0


# --- Event Handling Tests ---

class TestDesignSelectorEvents:
    """Tests for event handling."""

    def test_apply_filters_button_refreshes(self):
        """Test apply filters button triggers refresh."""
        window, _ = _make_selector_window()
        window._refresh_designs = MagicMock()
        window.name_search_entry.get_text.return_value = "Test"

        window._on_apply_filters()

        assert window.filter_name == "Test"
        window._refresh_designs.assert_called_once()

    def test_toggle_obsolete_updates_state(self):
        """Test toggle obsolete updates show_obsolete state."""
        window, _ = _make_selector_window()
        window._refresh_designs = MagicMock()
        window.show_obsolete = False

        window._toggle_obsolete()

        assert window.show_obsolete is True

    def test_toggle_obsolete_updates_button_text(self):
        """Test toggle obsolete updates button text."""
        window, _ = _make_selector_window()
        window._refresh_designs = MagicMock()
        window.show_obsolete = False

        window._toggle_obsolete()

        window.obsolete_button.set_text.assert_called()
        call_text = window.obsolete_button.set_text.call_args[0][0]
        assert "Show Obsolete" in call_text

    def test_cancel_button_kills_window(self):
        """Test cancel button closes window."""
        import pygame_gui

        window, _ = _make_selector_window()

        # Create mock event
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = window.cancel_button

        # Patch super().process_event
        with patch.object(window.__class__.__bases__[0], 'process_event', return_value=False):
            window.process_event(event)

        window.kill.assert_called()

    def test_on_toggle_obsolete_calls_library(self):
        """Test obsolete toggle on design row calls library."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._refresh_designs = MagicMock()

        window._on_toggle_obsolete("ship_001", False)

        # Should call mark_obsolete with new state (True)
        library.mark_obsolete.assert_called_once_with("ship_001", True)

    def test_on_toggle_obsolete_refreshes_on_success(self):
        """Test obsolete toggle refreshes list on success."""
        library = _make_design_catalog()
        library.mark_obsolete.return_value = (True, "Success")
        window, _ = _make_selector_window(design_catalog=library)
        window._refresh_designs = MagicMock()

        window._on_toggle_obsolete("ship_001", False)

        window._refresh_designs.assert_called()


# --- UI Creation Tests ---

class TestDesignSelectorUICreation:
    """Tests for UI element creation."""

    def test_rebuild_design_list_clears_existing(self):
        """Test _rebuild_design_list clears existing rows."""
        window, _ = _make_selector_window()

        # Add some mock rows
        row1 = MagicMock()
        row2 = MagicMock()
        window.design_rows = [row1, row2]
        window.filtered_designs = []

        window._rebuild_design_list()

        row1.kill.assert_called()
        row2.kill.assert_called()

    def test_rebuild_design_list_creates_rows(self):
        """Test _rebuild_design_list creates row for each design."""
        designs = [
            _make_design_metadata("ship_001", "Alpha"),
            _make_design_metadata("ship_002", "Beta"),
        ]
        library = _make_design_catalog(designs)
        window, _ = _make_selector_window(design_catalog=library)
        window.filtered_designs = designs

        # Mock _create_design_row to track calls
        window._create_design_row = MagicMock(return_value=MagicMock())

        window._rebuild_design_list()

        assert window._create_design_row.call_count == 2

    def test_design_row_layout(self):
        """Test design row contains expected elements."""
        window, _ = _make_selector_window()
        design = _make_design_metadata("ship_001", "Test Ship", "Cruiser", "Ship", 150.0)

        # We can't fully test UI creation without pygame_gui, but we can verify
        # the method accepts correct parameters
        # Just verify it doesn't raise with mock setup
        with patch('game.ui.screens.design_selector_window.UIPanel') as mock_panel:
            mock_panel.return_value = MagicMock()
            with patch('game.ui.screens.design_selector_window.UILabel'):
                with patch('game.ui.screens.design_selector_window.UIButton'):
                    with patch('game.ui.screens.design_selector_window.UIImage'):
                        with patch.object(window, '_load_portrait_thumbnail', return_value=MagicMock()):
                            with patch.object(window, '_load_topdown_thumbnail', return_value=None):
                                row = window._create_design_row(design, 0, 400)
                                assert row is not None

    def test_design_row_with_spaces_in_design_id(self):
        """Test _create_design_row sanitizes design_id for object_id (spaces).

        Regression test: design IDs from filenames can contain spaces
        (e.g. 'BS Battleship GC'), which pygame_gui rejects in object_id.
        """
        window, _ = _make_selector_window()
        design = _make_design_metadata("BS Battleship GC", "BS Battleship GC")

        with patch('game.ui.screens.design_selector_window.UIPanel') as mock_panel:
            mock_panel.return_value = MagicMock()
            with patch('game.ui.screens.design_selector_window.UILabel'):
                with patch('game.ui.screens.design_selector_window.UIButton'):
                    with patch('game.ui.screens.design_selector_window.UIImage'):
                        with patch.object(window, '_load_portrait_thumbnail', return_value=MagicMock()):
                            with patch.object(window, '_load_topdown_thumbnail', return_value=None):
                                row = window._create_design_row(design, 0, 400)
                                assert row is not None

                                # Verify object_id passed to UIPanel has no spaces
                                panel_call = mock_panel.call_args
                                object_id = panel_call[1]['object_id']
                                assert ' ' not in object_id
                                assert '.' not in object_id

    def test_design_row_with_fullstops_in_design_id(self):
        """Test _create_design_row sanitizes design_id for object_id (fullstops).

        Regression test: design IDs could contain fullstops (e.g. 'v2.0_cruiser'),
        which pygame_gui rejects in object_id.
        """
        window, _ = _make_selector_window()
        design = _make_design_metadata("v2.0_cruiser", "V2.0 Cruiser")

        with patch('game.ui.screens.design_selector_window.UIPanel') as mock_panel:
            mock_panel.return_value = MagicMock()
            with patch('game.ui.screens.design_selector_window.UILabel'):
                with patch('game.ui.screens.design_selector_window.UIButton'):
                    with patch('game.ui.screens.design_selector_window.UIImage'):
                        with patch.object(window, '_load_portrait_thumbnail', return_value=MagicMock()):
                            with patch.object(window, '_load_topdown_thumbnail', return_value=None):
                                row = window._create_design_row(design, 0, 400)
                                assert row is not None

                                panel_call = mock_panel.call_args
                                object_id = panel_call[1]['object_id']
                                assert '.' not in object_id


# --- Mode-Specific Tests ---

class TestDesignSelectorModes:
    """Tests for load vs target mode differences."""

    def test_load_mode_behavior(self):
        """Test load mode basic behavior."""
        window, _ = _make_selector_window(mode="load")

        assert window.mode == "load"

    def test_target_mode_behavior(self):
        """Test target mode basic behavior."""
        window, _ = _make_selector_window(mode="target")

        assert window.mode == "target"


# --- Integration-Style Tests ---

class TestDesignSelectorIntegration:
    """Integration-style tests for complete workflows."""

    def test_search_and_select_workflow(self):
        """Test complete search and select workflow."""
        designs = [
            _make_design_metadata("ship_001", "Alpha Cruiser"),
            _make_design_metadata("ship_002", "Beta Destroyer"),
        ]
        library = _make_design_catalog(designs)
        callback = MagicMock()
        window, _ = _make_selector_window(design_catalog=library, on_select_callback=callback)
        window._rebuild_design_list = MagicMock()

        # Set search filter
        window.filter_name = "Alpha"
        window._refresh_designs()

        # Should only have Alpha in filtered results
        assert len(window.filtered_designs) == 1
        assert window.filtered_designs[0].name == "Alpha Cruiser"

        # Select it
        window._on_design_selected("ship_001")

        # Callback should be invoked
        callback.assert_called_once_with("ship_001")

    def test_filter_obsolete_workflow(self):
        """Test filtering obsolete designs workflow."""
        designs = [
            _make_design_metadata("ship_001", "Current Ship", is_obsolete=False),
            _make_design_metadata("ship_002", "Old Ship", is_obsolete=True),
        ]
        library = _make_design_catalog(designs)
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()

        # Default: hide obsolete
        window._refresh_designs()
        assert len(window.filtered_designs) == 1

        # Toggle to show obsolete
        window.show_obsolete = True
        window._refresh_designs()
        assert len(window.filtered_designs) == 2


# ---------------------------------------------------------------------------
# PROJ-347 T4.3c: Pattern §33 widget-ref placeholders
# ---------------------------------------------------------------------------

class TestDesignSelectorWindowWidgetPlaceholders:
    """PROJ-347 T4.3c — Pattern §33 widget-ref placeholders.

    ``process_event`` reads ``apply_filters_button``, ``obsolete_button``,
    ``select_button``, ``cancel_button``, ``name_search_entry``,
    ``class_dropdown``, ``type_dropdown``. Stage 1 must set these to
    ``None`` before the bypass guard so a Null-builder test can
    construct via ``bypass_init`` without subsequent AttributeError.
    """

    def _make_window(self, *, ui_builder):
        from game.ui.screens.design_selector_window import DesignSelectorWindow
        from tests.fixtures.ui_widget_factory import bypass_init

        rect = pygame.Rect(0, 0, 800, 600)
        with bypass_init(DesignSelectorWindow):
            return DesignSelectorWindow(
                rect,
                MagicMock(name="ui_manager"),
                _make_design_catalog(),
                mode="load",
                on_select_callback=MagicMock(name="on_select_callback"),
                ui_builder=ui_builder,
            )

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        from tests.fixtures.design_selector_window_ui_builder import (
            NullDesignSelectorWindowUiBuilder,
        )
        window = self._make_window(
            ui_builder=NullDesignSelectorWindowUiBuilder()
        )
        for slot in (
            "sidebar_panel", "name_search_entry", "class_dropdown",
            "type_dropdown", "obsolete_button", "apply_filters_button",
            "main_panel", "scroll_container", "select_button",
            "cancel_button",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )


# ---------------------------------------------------------------------------
# QA Observation 2 (2026-05-16): Load Design dropdown options + ordering.
# ---------------------------------------------------------------------------

def _vehicleclasses_data():
    """Load data/vehicleclasses.json — single source of truth for filter
    expectations in these tests."""
    import json
    import os
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    )
    path = os.path.join(repo_root, "data", "vehicleclasses.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["classes"]


class TestDesignSelectorDropdownOptions:
    """QA Obs 2 — verify the Ship Class and Vehicle Type dropdowns are
    derived from `data/vehicleclasses.json` rather than hardcoded stale
    lists.
    """

    def _capture_dropdown_calls(self):
        """Run _create_sidebar with UIDropDownMenu patched; return the
        list of constructor-kwargs in call order so we can interrogate
        per-dropdown options and y-positions.
        """
        from unittest.mock import patch
        window, _ = _make_selector_window()

        # _create_sidebar reads a UIPanel container - stub the constructors
        # so we can run the real builder without pygame_gui state.
        with patch("game.ui.screens.design_selector_window.UIPanel"), \
             patch("game.ui.screens.design_selector_window.UILabel") as mock_label, \
             patch("game.ui.screens.design_selector_window.UIButton"), \
             patch("game.ui.screens.design_selector_window.UITextEntryLine"), \
             patch(
                 "game.ui.screens.design_selector_window.UIDropDownMenu"
             ) as mock_dd:
            mock_dd.return_value = MagicMock()
            mock_label.return_value = MagicMock()
            window._create_sidebar()

            return mock_dd.call_args_list, mock_label.call_args_list

    def _get_dropdown_options(self, call_args_list, starting_option):
        """Find the dropdown construction call whose starting_option matches
        and return its options_list."""
        for ca in call_args_list:
            kwargs = ca.kwargs
            if kwargs.get("starting_option") == starting_option:
                return kwargs["options_list"]
        raise AssertionError(
            f"No UIDropDownMenu constructed with starting_option={starting_option!r}"
        )

    def _get_dropdown_y(self, call_args_list, starting_option):
        """Find the dropdown construction call and return its
        relative_rect.y position."""
        for ca in call_args_list:
            kwargs = ca.kwargs
            if kwargs.get("starting_option") == starting_option:
                return kwargs["relative_rect"].y
        raise AssertionError(
            f"No UIDropDownMenu constructed with starting_option={starting_option!r}"
        )

    # --- Vehicle Type dropdown ---

    def test_type_dropdown_includes_mine(self):
        """The Vehicle Type filter must include 'Mine' (QA Obs 2)."""
        dd_calls, _ = self._capture_dropdown_calls()
        opts = self._get_dropdown_options(dd_calls, "All Types")
        assert "Mine" in opts, (
            f"Vehicle Type dropdown is missing 'Mine'; got {opts!r}"
        )

    def test_type_dropdown_includes_all_vehicleclasses_types(self):
        """Every unique `type` in vehicleclasses.json must appear in the
        Vehicle Type dropdown (registry-driven contract)."""
        dd_calls, _ = self._capture_dropdown_calls()
        opts = self._get_dropdown_options(dd_calls, "All Types")

        data_types = {cls["type"] for cls in _vehicleclasses_data().values()}
        missing = data_types - set(opts)
        assert not missing, (
            f"Vehicle Type dropdown missing types from data: {missing}"
        )

    # --- Ship Class dropdown ---

    def test_class_dropdown_excludes_phantom_carrier(self):
        """'Carrier' is a role/configuration, not a vehicle class — must
        NOT appear in the Ship Class dropdown."""
        dd_calls, _ = self._capture_dropdown_calls()
        opts = self._get_dropdown_options(dd_calls, "All Classes")
        assert "Carrier" not in opts, (
            f"Phantom 'Carrier' class present in dropdown: {opts!r}"
        )

    def test_class_dropdown_uses_data_spelling(self):
        """Data uses 'Battle Cruiser' (with space); dropdown must match
        verbatim because filter_designs does exact-string equality."""
        dd_calls, _ = self._capture_dropdown_calls()
        opts = self._get_dropdown_options(dd_calls, "All Classes")
        assert "Battle Cruiser" in opts, (
            f"'Battle Cruiser' missing from dropdown: {opts!r}"
        )
        assert "Battlecruiser" not in opts, (
            f"Stale 'Battlecruiser' (no space) present: {opts!r}"
        )

    def test_class_dropdown_includes_all_vehicleclasses_classes(self):
        """Every class name in vehicleclasses.json must appear in the
        Ship Class dropdown (registry-driven contract)."""
        dd_calls, _ = self._capture_dropdown_calls()
        opts = self._get_dropdown_options(dd_calls, "All Classes")

        for class_name in _vehicleclasses_data().keys():
            assert class_name in opts, (
                f"Class '{class_name}' from data missing from dropdown: {opts!r}"
            )

    # --- Ordering ---

    def test_filter_order_vehicle_type_before_ship_class(self):
        """QA Obs 2: Vehicle Type filter must render ABOVE Ship Class."""
        dd_calls, _ = self._capture_dropdown_calls()
        type_y = self._get_dropdown_y(dd_calls, "All Types")
        class_y = self._get_dropdown_y(dd_calls, "All Classes")
        assert type_y < class_y, (
            f"Vehicle Type (y={type_y}) should render above Ship Class "
            f"(y={class_y})"
        )

    # --- Mine filter end-to-end ---

    def test_mine_filter_propagates_to_search_designs(self):
        """Selecting 'Mine' in the type dropdown must be forwarded to
        DesignLibrary.search_designs as a vehicle_type filter."""
        library = _make_design_catalog()
        window, _ = _make_selector_window(design_catalog=library)
        window._rebuild_design_list = MagicMock()
        window.type_dropdown.selected_option = "Mine"

        window._refresh_designs()

        call_args = library.search_designs.call_args
        assert call_args[1]["filters"]["vehicle_type"] == "Mine"
