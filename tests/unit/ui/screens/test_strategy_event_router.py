"""Tests for StrategyEventRouter click gate functionality (PROJ-216 Phase 2).

Tests the _is_blocking_ui_element_at() method which replaces the overly broad
get_hovering_any_element() check that was blocking ALL map clicks.

The fix ensures:
- Hidden buttons (visible=0) do NOT block map clicks
- Active modal windows DO block map clicks when under cursor
- Top bar and resource bar DO block map clicks
- Sidebar area is handled separately (not tested here)
"""

import pytest
from unittest.mock import MagicMock, PropertyMock
import pygame


class MockRect:
    """Simple rect mock that supports collidepoint()."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def collidepoint(self, pos):
        x, y = pos
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)


@pytest.fixture
def mock_ui():
    """Create a mock StrategyUI with typical window setup."""
    ui = MagicMock()
    ui.width = 2560
    ui.height = 1600
    ui.sidebar_width = 300

    # Window manager with no windows open
    ui.window_manager = MagicMock()
    ui.window_manager.fleet_orders_window = None
    ui.window_manager.planet_list_window = None
    ui.window_manager.star_list_window = None
    ui.window_manager.fleet_report_window = None
    ui.window_manager.transfer_dialog = None
    ui.window_manager.build_queue_list_window = None
    ui.window_manager.empire_build_queue_window = None
    ui.window_manager.event_log_window = None
    ui.window_manager.empire_panel_window = None
    ui.window_manager._pending_confirmation_dialog = None
    ui.window_manager.move_choice_window = None
    ui.window_manager.cargo_quick_dialog = None
    ui.window_manager.planet_selection_window = None
    ui.window_manager.system_selection_window = None
    ui.window_manager.fleet_selection_window = None
    # PROJ-309 sub-phase 3.10: was previously omitted from this scan.
    ui.window_manager.planet_abilities_window = None

    # PROJ-313: StrategyModalWindow live-list. Migrated windows register
    # here via the base class's __init__. Tests can append to
    # _modals_for_test to simulate registration.
    ui.window_manager._modals_for_test = []
    ui.window_manager.iter_live_modals = lambda: iter(list(ui.window_manager._modals_for_test))

    # Menu panel not open
    ui.menu_panel = None
    ui.fleet_context_menu = None  # issue #20

    # Top bar and resource bar
    ui.top_bar = MagicMock()
    ui.top_bar.rect = MockRect(0, 0, 2260, 50)  # width - sidebar_width, height 50

    ui.resource_bar = MagicMock()
    ui.resource_bar.rect = MockRect(0, 50, 2260, 24)  # below top bar, height 24

    return ui


@pytest.fixture
def event_router(mock_ui):
    """Create a StrategyEventRouter with mock UI."""
    from game.ui.screens.strategy_event_router import StrategyEventRouter
    return StrategyEventRouter(mock_ui)


class TestClickGateMapArea:
    """Test clicks on the main map area (not sidebar/top bar)."""

    def test_map_click_passes_through_with_no_windows(self, event_router, mock_ui):
        """Click on map area with no windows open should NOT be blocked."""
        # Click in the middle of the map area (below top bar, left of sidebar)
        mx, my = 1000, 800

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False, "Map click should pass through when no windows are open"

    def test_map_click_not_blocked_by_hidden_buttons(self, event_router, mock_ui):
        """Click should NOT be blocked by hidden buttons (visible=0).

        This is the key fix for PROJ-216: hidden buttons were causing
        get_hovering_any_element() to return True and block all clicks.
        The new implementation doesn't check hidden elements at all.
        """
        # The new implementation doesn't even check hidden buttons,
        # so we just verify that a map click passes through
        mx, my = 1000, 800

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False, "Map click should NOT be blocked by hidden buttons"


class TestClickGateWindows:
    """Test clicks blocked by modal windows."""

    def test_click_blocked_by_fleet_orders_window(self, event_router, mock_ui):
        """Click on fleet_orders_window should be blocked.

        PROJ-313: fleet_orders_window migrated to StrategyModalWindow;
        registered via iter_live_modals.
        """
        # Create a mock window at (500, 300) with size 400x500
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(500, 300, 400, 500)
        mock_ui.window_manager._modals_for_test.append(window)

        # Click inside the window
        mx, my = 700, 500
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on fleet_orders_window should be blocked"

    def test_click_outside_fleet_orders_window_blocked_under_full_modality(self, event_router, mock_ui):
        """Click outside a live StrategyModalWindow should be blocked (issue #12).

        Renamed/inverted from `test_click_outside_fleet_orders_window_not_blocked`
        as part of issue #12. The old contract (rect-coincident block, gutter
        pass-through) is intentionally replaced with full modality: any live
        StrategyModalWindow blocks ALL background clicks regardless of position.
        """
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(500, 300, 400, 500)
        # PROJ-313 / issue #12: live modals are tracked through iter_live_modals.
        mock_ui.window_manager._modals_for_test.append(window)

        # Click outside the window's rect — under full modality this is blocked.
        mx, my = 200, 800
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, (
            "Issue #12: any live StrategyModalWindow must block clicks "
            "outside its rect (full modality)."
        )

    def test_click_blocked_by_planet_list_window(self, event_router, mock_ui):
        """Click on planet_list_window should be blocked."""
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(100, 100, 2000, 1400)
        mock_ui.window_manager._modals_for_test.append(window)  # PROJ-313 migrated

        mx, my = 1000, 800
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on planet_list_window should be blocked"

    def test_click_blocked_by_confirmation_dialog(self, event_router, mock_ui):
        """Click on confirmation dialog should be blocked."""
        dialog = MagicMock()
        dialog.alive.return_value = True
        dialog.rect = MockRect(1000, 700, 400, 200)
        mock_ui.window_manager._pending_confirmation_dialog = dialog

        mx, my = 1100, 800
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on confirmation dialog should be blocked"

    def test_dead_window_does_not_block(self, event_router, mock_ui):
        """A killed/dead window should not block clicks."""
        window = MagicMock()
        window.alive.return_value = False  # Window is dead
        window.rect = MockRect(500, 300, 400, 500)
        mock_ui.window_manager.fleet_orders_window = window

        mx, my = 700, 500  # Inside where the window was
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False, "Dead window should not block clicks"

    def test_click_blocked_by_fleet_report_window(self, event_router, mock_ui):
        """Click on fleet_report_window should be blocked."""
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(100, 100, 2000, 1400)
        mock_ui.window_manager._modals_for_test.append(window)  # PROJ-313 migrated

        mx, my = 1000, 800
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True

    def test_click_blocked_by_transfer_dialog(self, event_router, mock_ui):
        """Click on transfer_dialog should be blocked.

        PROJ-313: transfer_dialog migrated to StrategyModalWindow;
        registered via iter_live_modals.
        """
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(900, 500, 750, 600)
        mock_ui.window_manager._modals_for_test.append(window)

        mx, my = 1000, 700
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True

    def test_click_blocked_by_empire_build_queue_window(self, event_router, mock_ui):
        """Click on empire_build_queue_window should be blocked.

        PROJ-313: empire_build_queue_window migrated to StrategyModalWindow;
        registered via iter_live_modals.
        """
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(100, 100, 2000, 1400)
        mock_ui.window_manager._modals_for_test.append(window)

        mx, my = 1000, 800
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True

    def test_click_blocked_by_event_log_window(self, event_router, mock_ui):
        """Click on event_log_window should be blocked.

        PROJ-313: event_log_window migrated; uses iter_live_modals.
        """
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(400, 200, 1600, 1000)
        mock_ui.window_manager._modals_for_test.append(window)

        mx, my = 1000, 700
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True


class TestClickGateOrBridge:
    """PROJ-313 OR-bridge: iter_live_modals participates in click gating.

    During Phases 3-7 the router scans BOTH the legacy slot fields AND
    the new modal list. Either source must independently produce a
    blocking result.
    """

    def _make_live_window(self, rect):
        win = MagicMock()
        win.alive.return_value = True
        win.rect = rect
        return win

    def test_click_blocked_by_modal_list_alone(self, event_router, mock_ui):
        """Click on a window in iter_live_modals should be blocked."""
        win = self._make_live_window(MockRect(500, 300, 400, 500))
        mock_ui.window_manager.iter_live_modals = MagicMock(return_value=iter([win]))

        result = event_router._is_blocking_ui_element_at(700, 500)

        assert result is True

    def test_click_outside_modal_list_window_blocked_under_full_modality(self, event_router, mock_ui):
        """Click outside a modal-list window's rect should be blocked (issue #12).

        Renamed/inverted from `test_click_outside_modal_list_window_passes`.
        Under issue #12's full-modality contract, any live StrategyModalWindow
        blocks ALL background clicks regardless of click position. The
        rect-pass-through behavior the old test pinned is intentionally gone.
        """
        win = self._make_live_window(MockRect(500, 300, 400, 500))
        mock_ui.window_manager.iter_live_modals = MagicMock(return_value=iter([win]))

        result = event_router._is_blocking_ui_element_at(100, 800)

        assert result is True

    def test_has_modal_open_returns_true_with_only_modal_list(self, event_router, mock_ui):
        """has_modal_open returns True when modal list populated, no slots."""
        win = MagicMock()
        win.alive.return_value = True
        mock_ui.window_manager.iter_live_modals = MagicMock(return_value=iter([win]))
        mock_ui.menu_panel = None
        mock_ui.scene = MagicMock()
        mock_ui.scene.build_queue_screen = None

        assert event_router.has_modal_open() is True

    def test_has_modal_open_returns_true_with_only_modal_list_item(self, event_router, mock_ui):
        """has_modal_open returns True when modal list populated.

        PROJ-313 Phase 6: every strategy modal is now a StrategyModalWindow
        subclass and registered via iter_live_modals(). The legacy slot-scan
        path is empty (only menu_panel and build_queue_screen remain as
        pre-modal-tracking checks).
        """
        win = MagicMock()
        win.alive.return_value = True
        mock_ui.window_manager.iter_live_modals = lambda: iter([win])
        mock_ui.menu_panel = None
        mock_ui.scene = MagicMock()
        mock_ui.scene.build_queue_screen = None

        assert event_router.has_modal_open() is True

    def test_has_modal_open_returns_false_when_both_empty(self, event_router, mock_ui):
        """has_modal_open returns False when slots and modal list both empty."""
        mock_ui.window_manager.iter_live_modals = MagicMock(return_value=iter([]))
        mock_ui.menu_panel = None
        mock_ui.scene = MagicMock()
        mock_ui.scene.build_queue_screen = None

        assert event_router.has_modal_open() is False

    def test_modal_list_dead_ref_does_not_block(self, event_router, mock_ui):
        """iter_live_modals is responsible for filtering dead refs; if it
        does yield a dead window the click test still respects rect, but
        normally dead refs are reaped before yield."""
        # iter_live_modals normally reaps dead refs, but verify the
        # router doesn't add an extra .alive() check (it trusts the
        # iterator's contract).
        mock_ui.window_manager.iter_live_modals = MagicMock(return_value=iter([]))

        result = event_router._is_blocking_ui_element_at(700, 500)

        assert result is False


class TestClickGateMenuPanel:
    """Test clicks blocked by menu panel."""

    def test_click_blocked_by_menu_panel(self, event_router, mock_ui):
        """Click on menu panel should be blocked."""
        menu = MagicMock()
        menu.get_abs_rect.return_value = MockRect(2100, 50, 160, 300)
        mock_ui.menu_panel = menu

        mx, my = 2150, 200
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on menu panel should be blocked"

    def test_click_outside_menu_panel_not_blocked(self, event_router, mock_ui):
        """Click outside menu panel should pass through."""
        menu = MagicMock()
        menu.get_abs_rect.return_value = MockRect(2100, 50, 160, 300)
        mock_ui.menu_panel = menu

        mx, my = 1000, 800  # Not on menu panel
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False


class TestClickGateFleetContextMenu:
    """Test clicks blocked by the fleet right-click context menu (issue #20).

    The rejected fix shipped the menu without teaching the click gate
    about it, so left-clicks on a menu row fell through to
    ``_handle_picking`` and the queued ``UI_BUTTON_PRESSED`` dispatch
    never landed. Treat the fleet context menu identically to the
    top-bar ``menu_panel``: clicks inside its rect are blocking, clicks
    outside it pass through.
    """

    def test_click_blocked_by_fleet_context_menu(self, event_router, mock_ui):
        """Click inside the fleet context menu rect must be blocked."""
        menu = MagicMock()
        menu.get_abs_rect.return_value = MockRect(800, 400, 260, 200)
        mock_ui.fleet_context_menu = menu

        mx, my = 900, 500  # inside the menu rect
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, (
            "Issue #20: clicks inside the fleet context menu rect must be "
            "treated as blocking so they don't leak to _handle_picking, "
            "which would mutate UI state mid-MOUSEBUTTONDOWN/UP cycle and "
            "prevent the queued UI_BUTTON_PRESSED from dispatching."
        )

    def test_click_outside_fleet_context_menu_not_blocked(self, event_router, mock_ui):
        """Click outside the fleet context menu rect must pass through."""
        menu = MagicMock()
        menu.get_abs_rect.return_value = MockRect(800, 400, 260, 200)
        mock_ui.fleet_context_menu = menu

        mx, my = 200, 800  # well outside the menu rect
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False, (
            "Click outside the fleet context menu rect should pass through "
            "to the hex picker (matches the click-outside-dismiss contract)."
        )

    def test_no_fleet_context_menu_does_not_block(self, event_router, mock_ui):
        """When no fleet context menu is open, the branch must be inert."""
        mock_ui.fleet_context_menu = None

        mx, my = 900, 500
        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False


class TestClickGateTopBar:
    """Test clicks blocked by top bar and resource bar."""

    def test_click_blocked_by_top_bar(self, event_router, mock_ui):
        """Click on top bar should be blocked."""
        mx, my = 1000, 25  # Within top bar (0-50)

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on top bar should be blocked"

    def test_click_blocked_by_resource_bar(self, event_router, mock_ui):
        """Click on resource bar should be blocked."""
        mx, my = 1000, 60  # Within resource bar (50-74)

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, "Click on resource bar should be blocked"

    def test_click_below_bars_passes_through(self, event_router, mock_ui):
        """Click below top/resource bars should pass through."""
        mx, my = 1000, 100  # Below bars (y > 74)

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is False, "Click below bars should pass through"


class TestHandleClickIntegration:
    """Integration tests for handle_click() method."""

    def test_sidebar_click_blocked(self, event_router, mock_ui):
        """Click in sidebar area should be blocked."""
        # Sidebar is at x > width - sidebar_width = 2560 - 300 = 2260
        mx, my = 2400, 800

        result = event_router.handle_click(mx, my, 1)

        assert result is True, "Sidebar click should be blocked"

    def test_map_click_passes_when_no_blocking_elements(self, event_router, mock_ui):
        """Click on map should pass through with no blocking elements."""
        mx, my = 1000, 800  # Below bars, left of sidebar

        result = event_router.handle_click(mx, my, 1)

        assert result is False, "Map click should pass through"

    def test_map_click_blocked_when_window_open(self, event_router, mock_ui):
        """Click on map should be blocked when a window is there.

        PROJ-313: register via iter_live_modals (fleet_orders_window migrated).
        """
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(800, 600, 400, 400)
        mock_ui.window_manager._modals_for_test.append(window)

        mx, my = 1000, 800  # Inside window
        result = event_router.handle_click(mx, my, 1)

        assert result is True, "Click on window should be blocked"


class TestFullModalityBlocksAllBackgroundClicks:
    """Issue #12: any live StrategyModalWindow blocks ALL background clicks.

    The three named windows from the bug report (PlanetListWindow,
    StarListWindow, EmpirePanelWindow) are 90% of screen, so clicks in
    the gutter outside their rect previously leaked through. The new
    contract is full modality: any live modal blocks the entire
    background regardless of click position.
    """

    @pytest.mark.parametrize(
        "window_label, rect",
        [
            ("planet_list_window", MockRect(128, 80, 2304, 1440)),
            ("star_list_window", MockRect(128, 80, 2304, 1440)),
            ("empire_panel_window", MockRect(128, 80, 2304, 1440)),
        ],
    )
    def test_click_outside_modal_rect_blocked(
        self, event_router, mock_ui, window_label, rect
    ) -> None:
        """A live modal blocks clicks outside its rect (full modality)."""
        window = MagicMock(name=window_label)
        window.alive.return_value = True
        window.rect = rect
        mock_ui.window_manager._modals_for_test.append(window)

        # Click clearly outside the window's rect — in the gutter.
        mx, my = 50, 1550
        assert rect.collidepoint((mx, my)) is False, "Test setup: must be outside rect"

        result = event_router._is_blocking_ui_element_at(mx, my)

        assert result is True, (
            f"Issue #12: {window_label} must block clicks outside its rect"
        )

    def test_click_inside_modal_rect_still_blocked(self, event_router, mock_ui) -> None:
        """Sanity: full modality also blocks clicks inside the rect."""
        window = MagicMock()
        window.alive.return_value = True
        window.rect = MockRect(500, 300, 400, 500)
        mock_ui.window_manager._modals_for_test.append(window)

        # Click inside the window.
        result = event_router._is_blocking_ui_element_at(700, 500)

        assert result is True

    def test_no_live_modal_allows_background_click(self, event_router) -> None:
        """When no modal is live, background clicks pass through."""
        # _modals_for_test is empty by fixture default; nothing else open.
        result = event_router._is_blocking_ui_element_at(1000, 800)

        assert result is False


class TestHandleButtonPressedModalGuard:
    """Issue #12: _handle_button_pressed must early-return when a modal is live.

    Top-bar UI_BUTTON_PRESSED events previously dispatched directly to
    open_planet_list / open_star_list / open_empire_panel etc. with no
    consultation of has_modal_open(). The new guard makes top-bar
    buttons inert while any StrategyModalWindow is live.
    """

    @pytest.fixture
    def router_with_buttons(self, event_router, mock_ui):
        """Wire button attributes on the mock UI to distinct sentinels.

        The handler dispatches on `event.ui_element is ui.btn_X`, so each
        button slot must have a stable identity. MagicMock attribute access
        already returns the same child mock each call, so we just touch
        each one to materialize the sentinels.
        """
        for btn in (
            "btn_planets", "btn_stars", "btn_design", "btn_build_queues",
            "btn_all_queues", "btn_menu", "btn_events", "btn_empire",
            "btn_raw_data", "btn_colonize", "btn_orders", "btn_planet_orders",
            "btn_fleet_report",
        ):
            getattr(mock_ui, btn)
        return event_router

    @pytest.mark.parametrize("button_name", [
        "btn_planets",
        "btn_stars",
        "btn_empire",
        "btn_design",
        "btn_build_queues",
        "btn_all_queues",
        "btn_events",
        "btn_raw_data",
    ])
    def test_button_press_inert_while_modal_open(
        self, router_with_buttons, mock_ui, button_name
    ) -> None:
        """Top-bar button press is a no-op while any modal is live."""
        # A live modal exists.
        modal = MagicMock()
        modal.alive.return_value = True
        modal.rect = MockRect(0, 0, 100, 100)
        mock_ui.window_manager._modals_for_test.append(modal)

        # Reset all open_* call counts so we can detect dispatch.
        for opener in (
            "open_planet_list", "open_star_list", "open_build_queue_list",
            "open_empire_build_queue_window", "toggle_menu_panel",
            "open_event_log", "open_empire_panel", "show_raw_data_popup",
        ):
            getattr(mock_ui, opener).reset_mock()
        mock_ui.scene.on_design_click.reset_mock()

        event = MagicMock()
        event.ui_element = getattr(mock_ui, button_name)

        router_with_buttons._handle_button_pressed(event)

        # NO opener should have been invoked.
        assert mock_ui.open_planet_list.call_count == 0
        assert mock_ui.open_star_list.call_count == 0
        assert mock_ui.open_build_queue_list.call_count == 0
        assert mock_ui.open_empire_build_queue_window.call_count == 0
        assert mock_ui.toggle_menu_panel.call_count == 0
        assert mock_ui.open_event_log.call_count == 0
        assert mock_ui.open_empire_panel.call_count == 0
        assert mock_ui.show_raw_data_popup.call_count == 0
        assert mock_ui.scene.on_design_click.call_count == 0

    def test_button_press_still_dispatches_when_no_modal(
        self, router_with_buttons, mock_ui
    ) -> None:
        """Sanity: with no modal open, top-bar button press still dispatches."""
        # No modals open: the fixture leaves scene.build_queue_screen as a
        # MagicMock which has_modal_open would otherwise treat as live, so
        # set it to None here.
        mock_ui.scene.build_queue_screen = None
        mock_ui.open_planet_list.reset_mock()
        event = MagicMock()
        event.ui_element = mock_ui.btn_planets

        router_with_buttons._handle_button_pressed(event)

        assert mock_ui.open_planet_list.call_count == 1
