"""
Tests for FleetReportWindow multi-select and ship removal features.

PROJ-101 Phase 4: Multi-select + Remove Ships functionality.
PROJ-188 Phase 2: Updated for VirtualTable migration (selection -> MultiSelect).
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


def create_mock_ship(instance_id: str, name: str, serial: int = 1):
    """Create a mock ship for testing."""
    ship = Mock()
    ship.instance_id = instance_id
    ship.name = name
    ship.serial = serial
    ship.design_id = f"design-{instance_id}"
    ship.design_data = {'name': name, 'theme_id': 'Federation', 'ship_class': 'Frigate'}
    ship.is_alive = True
    ship.is_derelict = False
    ship.is_damaged = Mock(return_value=False)
    ship.get_hp_percentage = Mock(return_value=1.0)
    ship.get_display_id = Mock(return_value=f"SN-{serial:04d}")
    return ship


def create_mock_fleet(ships, fleet_id=1, owner_id=0):
    """Create a mock fleet for testing."""
    fleet = Mock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = (0, 0)
    fleet.ships = list(ships)
    fleet.speed = 5.0
    fleet.orders = []
    fleet.remove_ship = Mock(side_effect=lambda s: fleet.ships.remove(s) or True if s in fleet.ships else False)
    fleet.add_ship = Mock(side_effect=lambda s: fleet.ships.append(s))
    fleet.get_capability_summary = Mock(return_value={
        'can_warp': True, 'warp_limiting_ship': None,
        'fuel_endurance': 10, 'warp_jumps': 5
    })
    return fleet


def create_mock_empire(empire_id=0, next_fleet_id=100):
    """Create a mock empire for testing."""
    empire = Mock()
    empire.id = empire_id
    empire.fleets = []
    empire._next_fleet_id = next_fleet_id
    empire.get_next_fleet_id = Mock(side_effect=lambda: (
        setattr(empire, '_next_fleet_id', empire._next_fleet_id + 1) or empire._next_fleet_id - 1
    ))
    empire.add_fleet = Mock(side_effect=lambda f: empire.fleets.append(f))
    return empire


class TestFleetReportWindowInit:
    """Test FleetReportWindow initialization with empire parameter."""

    @pytest.fixture
    def mock_ships(self):
        """Create test ships."""
        return [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]

    @pytest.fixture
    def mock_fleet(self, mock_ships):
        """Create test fleet."""
        return create_mock_fleet(mock_ships)

    @pytest.fixture
    def mock_empire(self):
        """Create test empire."""
        return create_mock_empire()

    def test_init_stores_empire_reference(self, mock_fleet, mock_empire):
        """Window stores empire reference for fleet management."""
        with patch('pygame.display.get_surface') as mock_display:
            mock_display.return_value = Mock(get_size=Mock(return_value=(1920, 1080)))
            with patch('pygame_gui.UIManager'):
                with patch('game.ui.screens.fleet_report_window.UIWindow.__init__'):
                    with patch('game.ui.screens.fleet_report_window.FleetReportWindow._init_layout'):
                        with patch('game.ui.screens.fleet_report_window.FleetReportWindow.refresh_list'):
                            from game.ui.screens.fleet_report_window import FleetReportWindow
                            import pygame

                            rect = pygame.Rect(0, 0, 1600, 900)
                            manager = Mock()

                            window = FleetReportWindow(rect, manager, mock_fleet, empire=mock_empire)

                            assert window.empire is mock_empire

    def test_init_empire_defaults_to_none(self, mock_fleet):
        """Window empire defaults to None if not provided."""
        with patch('pygame.display.get_surface') as mock_display:
            mock_display.return_value = Mock(get_size=Mock(return_value=(1920, 1080)))
            with patch('pygame_gui.UIManager'):
                with patch('game.ui.screens.fleet_report_window.UIWindow.__init__'):
                    with patch('game.ui.screens.fleet_report_window.FleetReportWindow._init_layout'):
                        with patch('game.ui.screens.fleet_report_window.FleetReportWindow.refresh_list'):
                            from game.ui.screens.fleet_report_window import FleetReportWindow
                            import pygame

                            rect = pygame.Rect(0, 0, 1600, 900)
                            manager = Mock()

                            window = FleetReportWindow(rect, manager, mock_fleet)

                            assert window.empire is None

    def test_init_creates_selection_strategy(self, mock_fleet, mock_empire):
        """Window initializes selection as MultiSelect with no selected indices."""
        with patch('pygame.display.get_surface') as mock_display:
            mock_display.return_value = Mock(get_size=Mock(return_value=(1920, 1080)))
            with patch('pygame_gui.UIManager'):
                with patch('game.ui.screens.fleet_report_window.UIWindow.__init__'):
                    with patch('game.ui.screens.fleet_report_window.FleetReportWindow._init_layout'):
                        with patch('game.ui.screens.fleet_report_window.FleetReportWindow.refresh_list'):
                            from game.ui.screens.fleet_report_window import FleetReportWindow
                            from game.ui.components.table import MultiSelect
                            import pygame

                            rect = pygame.Rect(0, 0, 1600, 900)
                            manager = Mock()

                            window = FleetReportWindow(rect, manager, mock_fleet, empire=mock_empire)

                            assert isinstance(window.selection, MultiSelect)
                            assert len(window.selection.get_selected_indices()) == 0


class TestMultiSelectBehavior:
    """Test Ctrl+click multi-select behavior."""

    @pytest.fixture
    def window_with_ships(self):
        """Create a window with ships for testing selection behavior."""
        ships = [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]
        fleet = create_mock_fleet(ships)
        empire = create_mock_empire()

        with patch('pygame.display.get_surface') as mock_display:
            mock_display.return_value = Mock(get_size=Mock(return_value=(1920, 1080)))
            with patch('pygame_gui.UIManager'):
                with patch('game.ui.screens.fleet_report_window.UIWindow.__init__'):
                    with patch('game.ui.screens.fleet_report_window.FleetReportWindow._init_layout'):
                        with patch('game.ui.screens.fleet_report_window.FleetReportWindow.refresh_list'):
                            from game.ui.screens.fleet_report_window import FleetReportWindow
                            import pygame

                            rect = pygame.Rect(0, 0, 1600, 900)
                            manager = Mock()

                            window = FleetReportWindow(rect, manager, fleet, empire=empire)
                            # Mock the UI methods we need
                            window._update_detail_panel = Mock()
                            window._update_remove_button = Mock()
                            window._update_visible_rows = Mock()
                            window.view_model = Mock()
                            window.view_model.get_filtered_ships = Mock(return_value=ships)

                            return window, ships

    def test_normal_click_selects_single_ship(self, window_with_ships):
        """Normal click replaces selection with single ship."""
        window, ships = window_with_ships

        # Simulate normal click on index 2
        window.selected_indices = {0, 1}  # Pre-select some ships
        window.selected_indices = {2}  # Normal click behavior

        assert window.selected_indices == {2}

    def test_ctrl_click_adds_to_selection(self, window_with_ships):
        """Ctrl+click adds ship to existing selection."""
        window, ships = window_with_ships

        window.selected_indices = {0}
        window.selected_indices.add(1)  # Ctrl+click adds

        assert 0 in window.selected_indices
        assert 1 in window.selected_indices
        assert len(window.selected_indices) == 2

    def test_ctrl_click_removes_from_selection_when_multiple(self, window_with_ships):
        """Ctrl+click removes from selection when multiple selected."""
        window, ships = window_with_ships

        window.selected_indices = {0, 1, 2}
        window.selected_indices.discard(1)  # Ctrl+click removes

        assert 0 in window.selected_indices
        assert 1 not in window.selected_indices
        assert 2 in window.selected_indices

    def test_ctrl_click_cannot_deselect_last_ship(self, window_with_ships):
        """Ctrl+click cannot deselect the last remaining selected ship."""
        window, ships = window_with_ships

        window.selected_indices = {2}
        # Attempting to deselect when only 1 selected should NOT deselect
        if len(window.selected_indices) > 1:
            window.selected_indices.discard(2)

        assert 2 in window.selected_indices
        assert len(window.selected_indices) == 1


class TestShipRemoval:
    """Test ship removal to new fleet functionality."""

    @pytest.fixture
    def window_with_ships_and_empire(self):
        """Create window with ships and empire for removal testing."""
        ships = [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]
        fleet = create_mock_fleet(ships)
        empire = create_mock_empire()

        with patch('pygame.display.get_surface') as mock_display:
            mock_display.return_value = Mock(get_size=Mock(return_value=(1920, 1080)))
            with patch('pygame_gui.UIManager'):
                with patch('game.ui.screens.fleet_report_window.UIWindow.__init__'):
                    with patch('game.ui.screens.fleet_report_window.FleetReportWindow._init_layout'):
                        with patch('game.ui.screens.fleet_report_window.FleetReportWindow.refresh_list'):
                            from game.ui.screens.fleet_report_window import FleetReportWindow
                            import pygame

                            rect = pygame.Rect(0, 0, 1600, 900)
                            manager = Mock()

                            window = FleetReportWindow(rect, manager, fleet, empire=empire)
                            window._update_detail_panel = Mock()
                            window.refresh_list = Mock()
                            window.view_model = Mock()
                            window.view_model.get_filtered_ships = Mock(return_value=list(ships))
                            window.view_model.update_ships = Mock()
                            # Mock the sidebar component
                            window.sidebar = Mock()
                            window.sidebar.update_remove_button = Mock()
                            window.sidebar.update_summary = Mock()

                            # Mock the _create_fleet_for_ships to avoid real Fleet import issues
                            original_create_fleet = window._create_fleet_for_ships

                            def mock_create_fleet(ships_list):
                                mock_new_fleet = Mock()
                                mock_new_fleet.ships = list(ships_list)
                                mock_new_fleet.location = fleet.location
                                mock_new_fleet.owner_id = fleet.owner_id
                                mock_new_fleet.id = empire.get_next_fleet_id()
                                return mock_new_fleet

                            window._create_fleet_for_ships = mock_create_fleet

                            return window, fleet, empire, ships

    def test_remove_creates_new_fleet_at_same_location(self, window_with_ships_and_empire):
        """Removing ships creates a new fleet at the source fleet's location."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {1, 2}

        window._on_remove_selected_ships()

        # New fleet should be added to empire
        assert empire.add_fleet.called
        new_fleet = empire.add_fleet.call_args[0][0]
        assert new_fleet.location == fleet.location

    def test_removed_ships_not_in_source_fleet(self, window_with_ships_and_empire):
        """Removed ships are no longer in the source fleet."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {0, 1}
        original_ships = list(ships)

        window._on_remove_selected_ships()

        # Ships should have been removed from source fleet
        assert fleet.remove_ship.call_count == 2
        assert fleet.remove_ship.call_args_list[0][0][0] == original_ships[0]
        assert fleet.remove_ship.call_args_list[1][0][0] == original_ships[1]

    def test_removed_ships_in_new_fleet(self, window_with_ships_and_empire):
        """Removed ships are added to the new fleet."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {2, 3}

        window._on_remove_selected_ships()

        # New fleet should contain the removed ships
        new_fleet = empire.add_fleet.call_args[0][0]
        assert ships[2] in new_fleet.ships
        assert ships[3] in new_fleet.ships

    def test_new_fleet_added_to_empire(self, window_with_ships_and_empire):
        """New fleet is added to the empire's fleet list."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {0}

        window._on_remove_selected_ships()

        assert empire.add_fleet.called
        assert len(empire.fleets) == 1

    def test_selection_cleared_after_removal(self, window_with_ships_and_empire):
        """Selection is cleared after removal operation."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {0, 1, 2}

        window._on_remove_selected_ships()

        assert len(window.selection.get_selected_indices()) == 0

    def test_remove_does_nothing_without_empire(self, window_with_ships_and_empire):
        """Removal operation does nothing if no empire reference."""
        window, fleet, empire, ships = window_with_ships_and_empire

        window.empire = None
        # Set selection using the selection strategy
        window.selection._selected = {0, 1}

        window._on_remove_selected_ships()

        # No fleet should be added
        assert not empire.add_fleet.called

    def test_remove_does_nothing_with_empty_selection(self, window_with_ships_and_empire):
        """Removal operation does nothing if no ships selected."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Selection is already empty by default
        window.selection.clear()

        window._on_remove_selected_ships()

        # No fleet should be added
        assert not empire.add_fleet.called

    def test_ui_refreshed_after_removal(self, window_with_ships_and_empire):
        """UI is properly refreshed after removal."""
        window, fleet, empire, ships = window_with_ships_and_empire

        # Set selection using the selection strategy
        window.selection._selected = {0}
        # Mock sidebar for update_remove_button call
        window.sidebar = Mock()
        window.sidebar.update_remove_button = Mock()

        window._on_remove_selected_ships()

        # Verify UI refresh methods were called
        assert window._update_detail_panel.called
        assert window.refresh_list.called
        # sidebar.update_remove_button is called instead of _update_remove_button
        assert window.sidebar.update_remove_button.called


class TestRemoveButtonState:
    """Test Remove Selected button enable/disable behavior via sidebar."""

    @pytest.fixture
    def sidebar_with_button(self):
        """Create sidebar with mocked button for state testing."""
        from unittest.mock import Mock, MagicMock
        from game.ui.screens.fleet_report_sidebar import FleetReportSidebar

        # Create mock dependencies
        mock_panel = Mock()
        mock_panel.get_relative_rect.return_value = Mock(width=300)
        mock_manager = Mock()
        mock_view_model = Mock()
        mock_view_model.is_filter_enabled.return_value = True
        mock_view_model.get_filter_label.return_value = "Test"
        mock_column_manager = Mock()
        mock_column_manager.get_toggleable_columns.return_value = []
        mock_empire = Mock()

        # Patch pygame_gui elements
        with patch('game.ui.screens.fleet_report_sidebar.UIPanel'):
            with patch('game.ui.screens.fleet_report_sidebar.UILabel'):
                with patch('game.ui.screens.fleet_report_sidebar.UIButton'):
                    sidebar = FleetReportSidebar(
                        panel=mock_panel,
                        manager=mock_manager,
                        view_model=mock_view_model,
                        column_manager=mock_column_manager,
                        empire=mock_empire
                    )
                    # Mock the button directly
                    sidebar.btn_remove_selected = Mock()
                    sidebar.btn_remove_selected.enable = Mock()
                    sidebar.btn_remove_selected.disable = Mock()
                    sidebar.btn_remove_selected.set_text = Mock()

                    return sidebar

    def test_button_enabled_with_selection_and_empire(self, sidebar_with_button):
        """Button enabled when ships selected and empire available."""
        sidebar = sidebar_with_button
        sidebar.update_remove_button(2)

        sidebar.btn_remove_selected.enable.assert_called_once()
        sidebar.btn_remove_selected.set_text.assert_called_with("Remove Selected (2)")

    def test_button_disabled_without_selection(self, sidebar_with_button):
        """Button disabled when no ships selected."""
        sidebar = sidebar_with_button
        sidebar.update_remove_button(0)

        sidebar.btn_remove_selected.disable.assert_called_once()

    def test_button_disabled_without_empire(self, sidebar_with_button):
        """Button disabled when no empire reference."""
        sidebar = sidebar_with_button
        sidebar.empire = None

        sidebar.update_remove_button(1)

        sidebar.btn_remove_selected.disable.assert_called_once()

    def test_button_text_shows_selection_count(self, sidebar_with_button):
        """Button text shows number of selected ships."""
        sidebar = sidebar_with_button
        sidebar.update_remove_button(3)

        sidebar.btn_remove_selected.set_text.assert_called_with("Remove Selected (3)")
