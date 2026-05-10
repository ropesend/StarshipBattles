"""Characterization tests for ``FleetSelectionWindow`` (PROJ-329A Phase 2
Task 2.2).

Pins the four-widget construction (label, selection_list, btn_confirm,
btn_cancel), the ``update()`` button-press dispatch, the
``_label_to_fleet`` lookup, and the callback invocation. Uses the
two-stage construction pattern: ``bypass_init`` + an explicit
``MockFleetSelectionWindowUiBuilder``.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame

from game.ui.screens.fleet_selection_window import (
    FleetSelectionWindow,
    _fleet_display_label,
)
from tests.fixtures.fleet_selection_window_ui_builder import (
    MockFleetSelectionWindowUiBuilder,
    NullFleetSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _fleet(fleet_id: int = 1, name: str = "Alpha", composition: str = "3 ships"):
    """Build a FleetInfo-like MagicMock with the attributes the window reads."""
    f = MagicMock(name=f"FleetInfo({fleet_id})")
    f.fleet_id = fleet_id
    f.name = name
    f.composition_summary = composition
    return f


def _make_window(fleets, *, callback=None, ui_builder=None, window_title="Select Fleet to Join"):
    """Construct a real ``FleetSelectionWindow`` under ``bypass_init``."""
    if ui_builder is None:
        ui_builder = MockFleetSelectionWindowUiBuilder()
    if callback is None:
        callback = MagicMock()
    with bypass_init(FleetSelectionWindow):
        return FleetSelectionWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(name="ui_manager"),
            fleets,
            callback,
            window_manager=None,
            window_title=window_title,
            ui_builder=ui_builder,
        )


class TestFleetSelectionWindowInit:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_fleets_reference(self):
        fleets = [_fleet(1), _fleet(2)]
        window = _make_window(fleets)
        assert window.fleets is fleets

    def test_stores_callback(self):
        callback = MagicMock()
        window = _make_window([_fleet(1)], callback=callback)
        assert window.callback is callback

    def test_builds_display_labels_one_per_fleet(self):
        fleets = [_fleet(1, "Alpha", "3 ships"), _fleet(2, "Bravo", "5 ships")]
        window = _make_window(fleets)
        assert window._display_labels == [
            "Alpha — 3 ships",
            "Bravo — 5 ships",
        ]

    def test_label_to_fleet_lookup_round_trips(self):
        fleets = [_fleet(1, "Alpha", "3 ships"), _fleet(2, "Bravo", "5 ships")]
        window = _make_window(fleets)
        assert window._label_to_fleet["Alpha — 3 ships"] is fleets[0]
        assert window._label_to_fleet["Bravo — 5 ships"] is fleets[1]

    def test_window_init_bypassed_flag_set(self):
        window = _make_window([_fleet(1)])
        assert window._window_init_bypassed is True

    def test_null_builder_leaves_widget_slots_unset(self):
        window = _make_window(
            [_fleet(1)],
            ui_builder=NullFleetSelectionWindowUiBuilder(),
        )
        assert not hasattr(window, "label")
        assert not hasattr(window, "selection_list")
        assert not hasattr(window, "btn_confirm")
        assert not hasattr(window, "btn_cancel")

    def test_mock_builder_populates_four_widget_slots(self):
        window = _make_window([_fleet(1)])
        assert window.label is not None
        assert window.selection_list is not None
        assert window.btn_confirm is not None
        assert window.btn_cancel is not None


class TestFleetDisplayLabel:
    def test_format_includes_name_and_composition(self):
        f = _fleet(7, "Gamma", "12 ships")
        assert _fleet_display_label(f) == "Gamma — 12 ships"


class TestUpdateButtonDispatch:
    """``update()`` polls the buttons; pressing Confirm with a selection
    invokes the callback and kills the window. Cancel kills without
    callback."""

    def test_confirm_with_valid_selection_invokes_callback_and_kills(self):
        fleets = [_fleet(1, "Alpha", "3 ships"), _fleet(2, "Bravo", "5 ships")]
        callback = MagicMock()
        window = _make_window(fleets, callback=callback)
        window.btn_confirm.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = "Bravo — 5 ships"

        # patch UIWindow.update so super().update() is a no-op under bypass.
        from unittest.mock import patch
        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_called_once_with(fleets[1])
        mock_kill.assert_called_once()

    def test_confirm_without_selection_does_not_invoke_callback(self):
        callback = MagicMock()
        window = _make_window([_fleet(1)], callback=callback)
        window.btn_confirm.check_pressed.return_value = True
        window.selection_list.get_single_selection.return_value = None

        from unittest.mock import patch
        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_not_called()
        mock_kill.assert_not_called()

    def test_cancel_kills_without_callback(self):
        callback = MagicMock()
        window = _make_window([_fleet(1)], callback=callback)
        window.btn_cancel.check_pressed.return_value = True

        from unittest.mock import patch
        with patch("pygame_gui.elements.UIWindow.update", return_value=None):
            with patch.object(window, "kill") as mock_kill:
                window.update(0.016)

        callback.assert_not_called()
        mock_kill.assert_called_once()
