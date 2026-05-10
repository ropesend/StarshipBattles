"""Focused tests for the weapons report panel coordinator."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pygame
import pygame_gui
import pytest

from game.ui.screens.builder.weapons_panel import WeaponsReportPanel


class _WeaponAbility:
    def __init__(self, weapon_range: int) -> None:
        self.range = weapon_range


class _Weapon:
    def __init__(self, name: str, sprite_index: int, weapon_range: int) -> None:
        self.name = name
        self.sprite_index = sprite_index
        self._ability = _WeaponAbility(weapon_range)

    def get_ability(self, ability_name: str) -> _WeaponAbility | None:
        if ability_name == "WeaponAbility":
            return self._ability
        return None


class _Screen:
    def __init__(self) -> None:
        self.old_clip = pygame.Rect(0, 0, 800, 600)
        self.current_clip = self.old_clip
        self.set_clips: list[pygame.Rect] = []

    def get_clip(self) -> pygame.Rect:
        return self.old_clip

    def set_clip(self, rect: pygame.Rect) -> None:
        self.current_clip = rect
        self.set_clips.append(rect)


def _make_panel(
    *,
    rect: pygame.Rect | None = None,
    weapon_count: int = 0,
    scroll_start: float = 0.0,
) -> WeaponsReportPanel:
    panel = WeaponsReportPanel.__new__(WeaponsReportPanel)
    panel.rect = rect or pygame.Rect(0, 0, 500, 140)
    panel.builder = SimpleNamespace(ship=MagicMock(name="ship"))
    panel.manager = MagicMock()
    panel.scroll_bar_width = 18
    panel.scroll_offset = 0
    panel._tooltip_data = None

    panel.btn_proj = object()
    panel.btn_beam = object()
    panel.btn_seek = object()
    panel.btn_all = object()

    panel.scroll_bar = MagicMock()
    panel.scroll_bar.start_percentage = scroll_start

    panel._viewmodel = MagicMock()
    panel._viewmodel.weapon_groups = [
        {"weapon": _Weapon(f"Weapon {i}", i, 100), "count": 1}
        for i in range(weapon_count)
    ]
    panel._viewmodel.max_range = 100
    panel._viewmodel.target_name = None
    panel._viewmodel.target_defense_mod = 0.0
    panel._viewmodel.verbose_tooltip = False
    panel._viewmodel.get_points_of_interest.return_value = []

    panel._renderer = MagicMock()
    panel._input_handler = MagicMock()
    panel._input_handler.detect_tooltip_hover.return_value = None
    return panel


@pytest.mark.parametrize(
    ("button_name", "expected_method", "expected_arg"),
    [
        ("btn_proj", "toggle_filter", "projectile"),
        ("btn_beam", "toggle_filter", "beam"),
        ("btn_seek", "toggle_filter", "seeker"),
        ("btn_all", "enable_all_filters", None),
    ],
)
def test_weapons_report_panel_routes_filter_button_events(
    button_name: str,
    expected_method: str,
    expected_arg: str | None,
) -> None:
    panel = _make_panel()
    event = SimpleNamespace(
        type=pygame_gui.UI_BUTTON_PRESSED,
        ui_element=getattr(panel, button_name),
    )

    panel.handle_event(event)

    method = getattr(panel._viewmodel, expected_method)
    if expected_arg is None:
        method.assert_called_once_with()
    else:
        method.assert_called_once_with(expected_arg)


def test_weapons_report_panel_update_scrollbar_shows_for_overflow() -> None:
    panel = _make_panel(rect=pygame.Rect(0, 0, 500, 120), weapon_count=4)

    panel._update_scrollbar()

    panel.scroll_bar.show.assert_called_once_with()
    panel.scroll_bar.hide.assert_not_called()
    panel.scroll_bar.set_visible_percentage.assert_called_once_with(
        pytest.approx(70 / 180)
    )


def test_weapons_report_panel_update_scrollbar_hides_and_resets_when_content_fits() -> None:
    panel = _make_panel(rect=pygame.Rect(0, 0, 500, 120), weapon_count=1)

    panel._update_scrollbar()

    panel.scroll_bar.hide.assert_called_once_with()
    panel.scroll_bar.show.assert_not_called()
    panel.scroll_bar.set_visible_percentage.assert_called_once_with(1.0)
    panel.scroll_bar.set_scroll_from_start_percentage.assert_called_once_with(0.0)


def test_weapons_report_panel_mousewheel_inside_scrolls_overflow_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _make_panel(rect=pygame.Rect(0, 0, 500, 150), weapon_count=10)
    panel.scroll_bar.start_percentage = 0.5
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (20, 20))
    event = SimpleNamespace(type=pygame.MOUSEWHEEL, y=-1)

    panel.handle_event(event)

    panel.scroll_bar.set_scroll_from_start_percentage.assert_called_once_with(
        pytest.approx(0.8)
    )


def test_weapons_report_panel_mousewheel_ignores_pointer_outside_panel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _make_panel(rect=pygame.Rect(0, 0, 500, 150), weapon_count=10)
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (600, 20))
    event = SimpleNamespace(type=pygame.MOUSEWHEEL, y=-1)

    panel.handle_event(event)

    panel.scroll_bar.set_scroll_from_start_percentage.assert_not_called()


def test_weapons_report_panel_draw_clips_viewport_and_skips_offscreen_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _make_panel(weapon_count=5, scroll_start=0.5)
    screen = _Screen()
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (20, 70))

    panel.draw(screen)

    assert screen.set_clips[0] == pygame.Rect(0, 40, 482, 90)
    assert screen.set_clips[-1] == screen.old_clip

    drawn_weapons = [
        call.args[1].name
        for call in panel._renderer.draw_weapon_row.call_args_list
    ]
    assert drawn_weapons == ["Weapon 2", "Weapon 3", "Weapon 4"]
    assert panel._renderer.draw_unified_weapon_bar.call_count == 3
    assert panel._input_handler.detect_tooltip_hover.call_count == 3
    panel._viewmodel.set_hovered_weapon.assert_any_call(None)
    panel._viewmodel.set_hovered_weapon.assert_any_call(
        panel._viewmodel.weapon_groups[3]["weapon"]
    )


def test_weapons_report_panel_draw_no_weapons_target_info_dispatch() -> None:
    panel = _make_panel(weapon_count=0)
    screen = _Screen()
    panel._viewmodel.target_name = "Target Dummy"
    panel._viewmodel.target_defense_mod = 1.25

    panel.draw(screen)

    assert panel._renderer.method_calls == [
        call.draw_target_info(screen, panel.rect, "Target Dummy", 1.25),
        call.draw_no_weapons_message(screen, panel.rect),
    ]
    assert screen.set_clips == []


def test_weapons_report_panel_draw_tooltip_dispatch_after_clip_restore(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _make_panel(weapon_count=1)
    screen = _Screen()
    tooltip_data = {
        "pos": (20, 70),
        "range": 50,
        "accuracy": "80%",
        "damage": 12,
    }
    panel._viewmodel.verbose_tooltip = True
    panel._input_handler.detect_tooltip_hover.return_value = tooltip_data
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (20, 70))

    def assert_tooltip_after_clip_restore(*args) -> None:
        assert screen.current_clip == screen.old_clip

    panel._renderer.draw_tooltip.side_effect = assert_tooltip_after_clip_restore

    panel.draw(screen)

    panel._renderer.draw_tooltip.assert_called_once_with(screen, tooltip_data, True)
