"""Integration tests for the click gate in StrategyEventRouter.

PROJ-216 Phase 4: These tests verify that the click gate correctly blocks
or allows map clicks based on the presence of UI elements.

The critical fix was replacing get_hovering_any_element() which blocked ALL
clicks when hidden UI elements (visible=0 buttons) were registered with
pygame_gui, with an explicit check for blocking UI elements (modals, windows).
"""

import pytest
from unittest.mock import MagicMock, PropertyMock


# --- Test Helpers ---

def _create_mock_window(alive: bool = True, rect_contains: bool = False):
    """Create a mock window for testing.

    Args:
        alive: Whether window.alive() returns True.
        rect_contains: Whether rect.collidepoint() returns True.

    Returns:
        MagicMock configured as a window.
    """
    window = MagicMock()
    window.alive.return_value = alive
    window.rect.collidepoint.return_value = rect_contains
    return window


def _create_strategy_event_router():
    """Create a StrategyEventRouter with mocked StrategyUI dependencies.

    Returns:
        Tuple of (router, ui_mock, window_manager_mock).
    """
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    # Create mock UI
    ui = MagicMock()
    ui.width = 1920
    ui.sidebar_width = 300  # Sidebar occupies x > 1620

    # Create mock window manager with all windows set to None (not open)
    wm = MagicMock()
    wm.fleet_orders_window = None
    wm.planet_list_window = None
    wm.star_list_window = None
    wm.fleet_report_window = None
    wm.transfer_dialog = None
    wm.build_queue_list_window = None
    wm.empire_build_queue_window = None
    wm.event_log_window = None
    wm.empire_panel_window = None
    wm._pending_confirmation_dialog = None
    wm.move_choice_window = None
    wm.cargo_quick_dialog = None
    wm.planet_selection_window = None
    wm.system_selection_window = None
    wm.fleet_selection_window = None
    # PROJ-309 sub-phase 3.10: was previously omitted from this scan.
    wm.planet_abilities_window = None

    # PROJ-313: StrategyModalWindow live-list. Migrated windows participate
    # via iter_live_modals() instead of slot fields. Tests can append to
    # wm._modals_for_test to register a window with the new mechanism.
    wm._modals_for_test = []
    wm.iter_live_modals = lambda: iter(list(wm._modals_for_test))

    ui.window_manager = wm

    # No menu panel by default
    ui.menu_panel = None
    # issue #20: fleet right-click context menu starts closed; this slot
    # must default to None so the click gate's defensive ``getattr`` doesn't
    # treat a MagicMock auto-attribute as an open menu.
    ui.fleet_context_menu = None

    # Top bar and resource bar (should block clicks in their areas)
    top_bar = MagicMock()
    top_bar.rect.collidepoint.return_value = False
    ui.top_bar = top_bar

    resource_bar = MagicMock()
    resource_bar.rect.collidepoint.return_value = False
    ui.resource_bar = resource_bar

    # Create router
    router = StrategyEventRouter(ui)

    return router, ui, wm


# ===========================================================================
# Task 4.1: Click Gate Integration Tests
# ===========================================================================

class TestClickGateIntegration:
    """Integration tests for click gate behavior.

    PROJ-216: Verifies the fix that replaced get_hovering_any_element()
    with explicit window/modal checks.
    """

    def test_map_click_not_blocked_by_hidden_buttons(self):
        """Click on map area with no windows open returns False (click passes through).

        This is the core test for PROJ-216 fix: hidden buttons (visible=0)
        should NOT block map clicks.
        """
        router, ui, wm = _create_strategy_event_router()

        # Click in map area (not in sidebar, not on any window)
        mx, my = 800, 500  # Well within map area

        result = router.handle_click(mx, my, 1)

        assert result is False, "Map click should NOT be blocked when no windows are open"

    def test_map_click_not_blocked_when_all_windows_none(self):
        """Map click passes through when all window references are None."""
        router, ui, wm = _create_strategy_event_router()

        # Verify all windows are None
        assert wm.fleet_orders_window is None
        assert wm.planet_list_window is None
        assert wm.fleet_report_window is None

        mx, my = 500, 400

        result = router.handle_click(mx, my, 1)

        assert result is False

    def test_sidebar_click_always_blocked(self):
        """Click in sidebar area always returns True (blocked)."""
        router, ui, wm = _create_strategy_event_router()

        # Sidebar is at x > (1920 - 300) = 1620
        mx, my = 1700, 500

        result = router.handle_click(mx, my, 1)

        assert result is True, "Sidebar clicks should be blocked"

    def test_sidebar_click_at_boundary(self):
        """Click exactly at sidebar boundary is blocked."""
        router, ui, wm = _create_strategy_event_router()

        # Sidebar starts at x > 1620, so x = 1621 is in sidebar
        mx, my = 1621, 500

        result = router.handle_click(mx, my, 1)

        assert result is True

    def test_map_click_just_before_sidebar_passes(self):
        """Click just before sidebar boundary passes through."""
        router, ui, wm = _create_strategy_event_router()

        # x = 1620 is NOT in sidebar (sidebar is x > 1620)
        mx, my = 1620, 500

        result = router.handle_click(mx, my, 1)

        assert result is False

    def test_map_click_blocked_by_any_live_modal_under_full_modality(self):
        """Click blocked whenever any StrategyModalWindow is live (issue #12).

        Renamed/inverted from ``test_map_click_blocked_by_fleet_orders_window``
        as part of issue #12. Under full modality, the router no longer
        consults the modal's rect — any live modal in ``iter_live_modals()``
        is sufficient to block the click. The dropped
        ``window.rect.collidepoint.assert_called_with(...)`` assertion was
        pinning the obsolete rect-coincident contract.
        """
        router, ui, wm = _create_strategy_event_router()

        # A live modal is registered; whether the click happens to be
        # inside its rect is intentionally irrelevant under full modality.
        window = _create_mock_window(alive=True, rect_contains=True)
        wm._modals_for_test.append(window)

        mx, my = 600, 400

        result = router.handle_click(mx, my, 1)

        assert result is True, (
            "Issue #12: any live StrategyModalWindow must block clicks"
        )

    def test_map_click_blocked_by_planet_list_window(self):
        """Click blocked when planet_list_window is open at that position."""
        router, ui, wm = _create_strategy_event_router()

        window = _create_mock_window(alive=True, rect_contains=True)
        wm._modals_for_test.append(window)  # PROJ-313 migrated

        mx, my = 600, 400

        result = router.handle_click(mx, my, 1)

        assert result is True, "Click should be blocked by planet_list_window"

    def test_map_click_blocked_by_confirmation_dialog(self):
        """Click blocked when confirmation dialog is open at that position."""
        router, ui, wm = _create_strategy_event_router()

        dialog = _create_mock_window(alive=True, rect_contains=True)
        wm._pending_confirmation_dialog = dialog

        mx, my = 960, 540  # Center of screen, typical dialog position

        result = router.handle_click(mx, my, 1)

        assert result is True, "Click should be blocked by confirmation dialog"

    def test_map_click_not_blocked_by_dead_window(self):
        """Click passes through when window exists but is not alive."""
        router, ui, wm = _create_strategy_event_router()

        # Window reference exists but alive() returns False
        window = _create_mock_window(alive=False, rect_contains=True)
        wm.fleet_orders_window = window

        mx, my = 600, 400

        result = router.handle_click(mx, my, 1)

        assert result is False, "Dead window should not block clicks"

    def test_map_click_not_blocked_when_click_outside_window(self):
        """Click passes through when window is open but click is outside it."""
        router, ui, wm = _create_strategy_event_router()

        # Window is alive but click point is NOT inside its rect
        window = _create_mock_window(alive=True, rect_contains=False)
        wm.fleet_orders_window = window

        mx, my = 100, 100  # Click outside window area

        result = router.handle_click(mx, my, 1)

        assert result is False, "Click outside window should pass through"

    def test_top_bar_click_blocked(self):
        """Click in top bar area is blocked."""
        router, ui, wm = _create_strategy_event_router()

        # Configure top_bar to contain the click
        ui.top_bar.rect.collidepoint.return_value = True

        mx, my = 800, 25  # Typical top bar area

        result = router.handle_click(mx, my, 1)

        assert result is True, "Top bar clicks should be blocked"

    def test_resource_bar_click_blocked(self):
        """Click in resource bar area is blocked."""
        router, ui, wm = _create_strategy_event_router()

        # Configure resource_bar to contain the click
        ui.resource_bar.rect.collidepoint.return_value = True

        mx, my = 800, 60  # Typical resource bar area

        result = router.handle_click(mx, my, 1)

        assert result is True, "Resource bar clicks should be blocked"

    def test_menu_panel_click_blocked(self):
        """Click on menu panel is blocked."""
        router, ui, wm = _create_strategy_event_router()

        # Create menu panel
        menu_panel = MagicMock()
        menu_panel.get_abs_rect.return_value.collidepoint.return_value = True
        ui.menu_panel = menu_panel

        mx, my = 100, 100  # Inside menu panel

        result = router.handle_click(mx, my, 1)

        assert result is True, "Menu panel clicks should be blocked"

    def test_click_outside_menu_panel_passes(self):
        """Click outside menu panel passes through."""
        router, ui, wm = _create_strategy_event_router()

        # Menu panel exists but click is outside
        menu_panel = MagicMock()
        menu_panel.get_abs_rect.return_value.collidepoint.return_value = False
        ui.menu_panel = menu_panel

        mx, my = 800, 500  # Outside menu panel

        result = router.handle_click(mx, my, 1)

        assert result is False

    def test_multiple_windows_block_under_full_modality_regardless_of_rect_coincidence(self):
        """Multiple live modals block clicks regardless of rect (issue #12).

        Renamed/inverted from ``test_multiple_windows_check_all`` as part
        of issue #12. The previous test pinned the rect-pass-through
        contract: "click passes through if not inside ANY window's rect".
        Under full modality, the live-list membership alone is sufficient
        to block; rect coincidence is no longer consulted.
        """
        router, ui, wm = _create_strategy_event_router()

        # Multiple live modals, none containing the click point under their
        # rect — under full modality this no longer matters.
        wm.fleet_orders_window = _create_mock_window(alive=True, rect_contains=False)
        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=False))
        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=False))

        mx, my = 500, 400

        result = router.handle_click(mx, my, 1)

        assert result is True, (
            "Issue #12: any live StrategyModalWindow must block clicks "
            "outside its rect (full modality)."
        )

    def test_first_matching_window_blocks(self):
        """First window that contains the click point blocks it."""
        router, ui, wm = _create_strategy_event_router()

        # First window doesn't contain click
        wm.fleet_orders_window = _create_mock_window(alive=True, rect_contains=False)
        # Second window contains click
        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))  # PROJ-313 migrated

        mx, my = 500, 400

        result = router.handle_click(mx, my, 1)

        assert result is True


class TestClickGateWithAllWindowTypes:
    """Tests that all window types in window_manager are properly checked."""

    def test_transfer_dialog_blocks(self):
        """Transfer dialog blocks clicks in its area.

        PROJ-313: transfer_dialog migrated; now registered via iter_live_modals.
        """
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))

        result = router.handle_click(600, 400, 1)

        assert result is True

    def test_build_queue_list_window_blocks(self):
        """Build queue list window blocks clicks in its area."""
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))  # PROJ-313 migrated

        result = router.handle_click(600, 400, 1)

        assert result is True

    def test_empire_build_queue_window_blocks(self):
        """Empire build queue window blocks clicks in its area.

        PROJ-313: migrated to StrategyModalWindow; registered via iter_live_modals.
        """
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))

        result = router.handle_click(600, 400, 1)

        assert result is True

    def test_event_log_window_blocks(self):
        """Event log window blocks clicks in its area.

        PROJ-313: migrated to StrategyModalWindow; registered via iter_live_modals.
        """
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))

        result = router.handle_click(600, 400, 1)

        assert result is True

    def test_empire_panel_window_blocks(self):
        """Empire panel window blocks clicks in its area.

        PROJ-313: migrated to StrategyModalWindow; registered via iter_live_modals.
        """
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))

        result = router.handle_click(600, 400, 1)

        assert result is True

    def test_fleet_report_window_blocks(self):
        """Fleet report window blocks clicks in its area."""
        router, ui, wm = _create_strategy_event_router()

        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))  # PROJ-313 migrated

        result = router.handle_click(600, 400, 1)

        assert result is True


class TestIsBlockingUIElementAt:
    """Direct tests for _is_blocking_ui_element_at helper method."""

    def test_returns_false_when_nothing_blocking(self):
        """Returns False when no blocking elements at position."""
        router, ui, wm = _create_strategy_event_router()

        result = router._is_blocking_ui_element_at(500, 400)

        assert result is False

    def test_returns_true_for_alive_window_at_position(self):
        """Returns True when alive window contains position."""
        router, ui, wm = _create_strategy_event_router()

        # PROJ-313: register via iter_live_modals (fleet_orders_window migrated)
        wm._modals_for_test.append(_create_mock_window(alive=True, rect_contains=True))

        result = router._is_blocking_ui_element_at(500, 400)

        assert result is True

    def test_handles_missing_pending_confirmation_dialog(self):
        """Gracefully handles when _pending_confirmation_dialog attribute doesn't exist."""
        router, ui, wm = _create_strategy_event_router()

        # Remove the attribute entirely
        del wm._pending_confirmation_dialog

        # Should not raise - uses getattr with default None
        result = router._is_blocking_ui_element_at(500, 400)

        assert result is False

    def test_handles_missing_top_bar(self):
        """Gracefully handles when top_bar attribute doesn't exist."""
        router, ui, wm = _create_strategy_event_router()

        # Remove top_bar
        del ui.top_bar

        # Should not raise - uses hasattr check
        result = router._is_blocking_ui_element_at(500, 400)

        assert result is False

    def test_handles_missing_resource_bar(self):
        """Gracefully handles when resource_bar attribute doesn't exist."""
        router, ui, wm = _create_strategy_event_router()

        # Remove resource_bar
        del ui.resource_bar

        # Should not raise - uses hasattr check
        result = router._is_blocking_ui_element_at(500, 400)

        assert result is False
