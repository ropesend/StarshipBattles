"""Characterization tests for ``PlanetSelectionWindow`` (PROJ-329A
Phase 2 Task 2.3).

Pins the minimum-rect enforcement (950x650), label/selection_list/
btn_select widget construction, planet_detail_panel = None
initialization, callback wiring, and "Any Planet" button conditional
behavior.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.planet_selection_window import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    PlanetSelectionWindow,
)
from tests.fixtures.planet_selection_window_ui_builder import (
    MockPlanetSelectionWindowUiBuilder,
    NullPlanetSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _planet(name: str = "Earth"):
    """A planet-shaped MagicMock with the attributes the window reads."""
    p = MagicMock(name=f"Planet({name})")
    p.name = name
    p.image_id = None
    p.image_rotation = 0
    return p


def _make_window(
    planets,
    *,
    rect=None,
    callback=None,
    ui_builder=None,
    window_title="Select Planet to Colonize",
    list_label="Habitable bodies:",
    show_any_button=True,
):
    """Construct a real ``PlanetSelectionWindow`` under ``bypass_init``."""
    if rect is None:
        rect = pygame.Rect(0, 0, 1000, 700)
    if ui_builder is None:
        ui_builder = MockPlanetSelectionWindowUiBuilder()
    if callback is None:
        callback = MagicMock()
    with bypass_init(PlanetSelectionWindow):
        return PlanetSelectionWindow(
            rect,
            MagicMock(name="ui_manager"),
            planets,
            callback,
            window_manager=None,
            window_title=window_title,
            list_label=list_label,
            show_any_button=show_any_button,
            ui_builder=ui_builder,
        )


class TestPlanetSelectionWindowInit:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_planets_reference(self):
        planets = [_planet("Earth"), _planet("Mars")]
        window = _make_window(planets)
        assert window.planets is planets

    def test_stores_callback(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback)
        assert window.callback is callback

    def test_window_init_bypassed_flag_set(self):
        window = _make_window([_planet()])
        assert window._window_init_bypassed is True

    def test_planet_detail_panel_starts_none(self):
        window = _make_window([_planet()])
        assert window.planet_detail_panel is None

    def test_selected_planet_starts_none(self):
        window = _make_window([_planet()])
        assert window.selected_planet is None

    def test_current_selection_name_starts_none(self):
        window = _make_window([_planet()])
        assert window.current_selection_name is None

    def test_stores_list_label(self):
        window = _make_window([_planet()], list_label="Targets:")
        assert window._list_label == "Targets:"

    def test_stores_show_any_button_true(self):
        window = _make_window([_planet()], show_any_button=True)
        assert window._show_any_button is True

    def test_stores_show_any_button_false(self):
        window = _make_window([_planet()], show_any_button=False)
        assert window._show_any_button is False


class TestMinimumRectEnforcement:
    """``__init__`` clamps the rect to at least 950x650 in Stage 1, before
    the shell is constructed."""

    def test_undersized_width_clamped_to_min(self):
        rect = pygame.Rect(0, 0, 100, 700)
        _make_window([_planet()], rect=rect)
        assert rect.width == MIN_WINDOW_WIDTH

    def test_undersized_height_clamped_to_min(self):
        rect = pygame.Rect(0, 0, 1000, 100)
        _make_window([_planet()], rect=rect)
        assert rect.height == MIN_WINDOW_HEIGHT

    def test_oversized_dimensions_preserved(self):
        rect = pygame.Rect(0, 0, 1500, 1200)
        _make_window([_planet()], rect=rect)
        assert rect.width == 1500
        assert rect.height == 1200


class TestUiBuilderConditionalAnyButton:
    """The Any-Planet button is conditionally constructed by the builder
    based on the Stage-1 ``_show_any_button`` flag."""

    def test_show_any_true_populates_btn_any(self):
        window = _make_window([_planet()], show_any_button=True)
        assert window.btn_any is not None

    def test_show_any_false_leaves_btn_any_none(self):
        window = _make_window([_planet()], show_any_button=False)
        assert window.btn_any is None

    def test_null_builder_leaves_widget_slots_unset(self):
        window = _make_window(
            [_planet()],
            ui_builder=NullPlanetSelectionWindowUiBuilder(),
        )
        # Stage-1 always initializes btn_any to None for safety.
        assert window.btn_any is None
        # Other widget slots are not set at all when null builder runs.
        assert not hasattr(window, "label")
        assert not hasattr(window, "selection_list")
        assert not hasattr(window, "btn_select")


class TestUpdateButtonDispatch:
    """``update()`` polls Confirm + Any-Planet buttons; valid presses
    invoke the callback (with the planet, or None for Any-Planet) and
    kill the window."""

    def test_confirm_with_valid_selection_invokes_callback_with_planet(self):
        earth, mars = _planet("Earth"), _planet("Mars")
        callback = MagicMock()
        window = _make_window([earth, mars], callback=callback)
        window.btn_select.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = "Mars"
        # Pre-seed the selection-tracking attrs so update() skips the
        # PlanetReportPanel-creation branch (which needs self.rect, not
        # set under bypass per PROJ-325 PoC finding 1).
        window.current_selection_name = "Mars"
        window.selected_planet = mars

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_called_once_with(mars)
        mock_kill.assert_called_once()

    def test_confirm_without_selection_does_not_invoke_callback(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback)
        window.btn_select.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = None
        # Pre-seed to skip the panel-creation branch (PROJ-325 finding 1).
        window.current_selection_name = None
        window.selected_planet = None

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_not_called()
        mock_kill.assert_not_called()

    def test_any_planet_invokes_callback_with_none(self):
        callback = MagicMock()
        window = _make_window([_planet()], callback=callback, show_any_button=True)
        window.btn_any.check_pressed.return_value = True
        # Skip the panel-creation branch (needs self.rect; bypass shell
        # does not assign it per PROJ-325 PoC finding 1).
        window.current_selection_name = None
        window.selected_planet = None

        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_called_once_with(None)
        mock_kill.assert_called_once()
