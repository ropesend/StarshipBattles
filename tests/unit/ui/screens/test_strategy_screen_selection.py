"""Tests for ``strategy_screen_selection`` (PROJ-330)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.ui.screens import strategy_screen_selection as selection


def _make_screen():
    screen = MagicMock()
    screen.selected_object = None
    screen.selected_fleet = None
    screen.last_selected_system = None
    screen.systems = []
    screen.human_player_ids = [0]
    screen.current_player_index = 0
    screen.session = MagicMock()
    screen.session.active_empire = MagicMock(id=0)
    # PROJ-475: BUG-125 gate reads screen.active_empire_id.
    screen.active_empire_id = 0
    screen.ui = MagicMock()
    screen.ui.window_manager = MagicMock()
    screen.ui.window_manager.transfer_dialog = None
    screen._colonization = MagicMock()
    screen._get_object_asset = MagicMock(return_value="IMG")
    return screen


class TestOnUiSelection:
    def test_assigns_selected_object(self):
        screen = _make_screen()
        obj = MagicMock()
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=False):
            selection.on_ui_selection(screen, obj)
        assert screen.selected_object is obj
        screen.ui.show_detailed_report.assert_called_once_with(obj, "IMG")

    def test_star_system_updates_last_selected(self):
        screen = _make_screen()
        sys_obj = MagicMock()
        with patch.object(selection, "is_star_system", return_value=True), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=False):
            selection.on_ui_selection(screen, sys_obj)
        assert screen.last_selected_system is sys_obj

    def test_planet_resolves_parent_system(self):
        screen = _make_screen()
        planet = MagicMock()
        sys_a = MagicMock()
        sys_a.planets = []
        sys_a.warp_points = []
        sys_b = MagicMock()
        sys_b.planets = [planet]
        sys_b.warp_points = []
        screen.systems = [sys_a, sys_b]
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=True), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=False):
            selection.on_ui_selection(screen, planet)
        assert screen.last_selected_system is sys_b

    def test_friendly_fleet_sets_selected_fleet(self):
        screen = _make_screen()
        fleet = MagicMock(owner_id=0)
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=True):
            selection.on_ui_selection(screen, fleet)
        assert screen.selected_fleet is fleet

    def test_enemy_fleet_does_not_set_selected_fleet(self):
        screen = _make_screen()
        screen.selected_fleet = "PRIOR"
        fleet = MagicMock(owner_id=99)
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=True):
            selection.on_ui_selection(screen, fleet)
        # Enemy fleet — selected_fleet untouched (is_fleet True path)
        assert screen.selected_fleet == "PRIOR"

    def test_non_fleet_clears_selected_fleet(self):
        screen = _make_screen()
        screen.selected_fleet = "PRIOR"
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=False):
            selection.on_ui_selection(screen, MagicMock())
        assert screen.selected_fleet is None

    def test_open_transfer_dialog_receives_external_selection(self):
        screen = _make_screen()
        screen.ui.window_manager.transfer_dialog = MagicMock()
        obj = MagicMock()
        with patch.object(selection, "is_star_system", return_value=False), \
             patch.object(selection, "is_planet", return_value=False), \
             patch.object(selection, "is_warp_point", return_value=False), \
             patch.object(selection, "is_fleet", return_value=False):
            selection.on_ui_selection(screen, obj)
        screen.ui.window_manager.transfer_dialog.handle_external_selection.assert_called_once_with(obj)


class TestOnColonizeClick:
    def test_no_fleet_is_noop(self):
        screen = _make_screen()
        screen.selected_fleet = None
        selection.on_colonize_click(screen)
        screen.ui.open_transfer_dialog.assert_not_called()

    def test_opens_transfer_dialog_at_fleet_location(self):
        screen = _make_screen()
        fleet = MagicMock()
        fleet.location = "LOC"
        screen.selected_fleet = fleet
        selection.on_colonize_click(screen)
        screen.ui.open_transfer_dialog.assert_called_once_with(fleet, "LOC")


class TestOnColonizePlanetSelected:
    def test_success_opens_transfer_dialog_at_planet_global_hex(self):
        screen = _make_screen()
        from game.core.hex_math import HexCoord

        fleet = MagicMock()
        screen.selected_fleet = fleet
        planet = MagicMock()
        planet.location = HexCoord(1, 1)
        sys_obj = MagicMock()
        sys_obj.planets = [planet]
        sys_obj.global_location = HexCoord(2, 2)
        screen.systems = [sys_obj]
        screen._colonization.issue_colonize_order.return_value = {"type": "success"}
        selection.on_colonize_planet_selected(screen, planet)
        screen.ui.open_transfer_dialog.assert_called_once()
        screen.on_ui_selection.assert_called_once_with(fleet)

    def test_failure_does_not_open_dialog(self):
        screen = _make_screen()
        screen.selected_fleet = MagicMock()
        screen._colonization.issue_colonize_order.return_value = {"type": "failure"}
        selection.on_colonize_planet_selected(screen, MagicMock())
        screen.ui.open_transfer_dialog.assert_not_called()


class TestRequestColonizeOrder:
    def test_opponent_fleet_is_blocked(self):
        screen = _make_screen()
        screen.active_empire_id = 0
        fleet = MagicMock(owner_id=99)
        selection.request_colonize_order(screen, fleet)
        screen._colonization.request_colonize_order.assert_not_called()

    def test_active_empire_none_allows(self):
        screen = _make_screen()
        screen.active_empire_id = None
        fleet = MagicMock(owner_id=42)
        screen._colonization.request_colonize_order.return_value = {"type": "success"}
        selection.request_colonize_order(screen, fleet)
        screen._colonization.request_colonize_order.assert_called_once()
        assert screen.selected_fleet is fleet
        screen.on_ui_selection.assert_called_once_with(fleet)

    def test_success_calls_on_ui_selection(self):
        screen = _make_screen()
        fleet = MagicMock(owner_id=0)
        screen._colonization.request_colonize_order.return_value = {"type": "success"}
        selection.request_colonize_order(screen, fleet)
        screen.on_ui_selection.assert_called_once_with(fleet)

    def test_failure_skips_on_ui_selection(self):
        screen = _make_screen()
        fleet = MagicMock(owner_id=0)
        screen._colonization.request_colonize_order.return_value = {"type": "failure"}
        selection.request_colonize_order(screen, fleet)
        screen.on_ui_selection.assert_not_called()
