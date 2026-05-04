"""Characterization tests for ModifierEditorPanel (PROJ-340).

Pins observed behavior of ``ModifierEditorPanel`` at
``game/ui/panels/builder_widgets.py``:

* Layout when no editing component is selected.
* The toggle-add-modifier branch in ``_on_row_change``.
* The clear-settings button branch in ``handle_event``.

``pygame_gui`` widget classes are patched so construction is inert
(PROJ-340 D-005).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame_gui
import pytest

from game.ui.panels import builder_widgets as bw_module
from game.ui.panels.builder_widgets import ModifierEditorPanel


@pytest.fixture
def patched_pygame_gui_elements():
    """Replace UIButton/UILabel/UIScrollingContainer with MagicMocks during a test."""
    with patch.multiple(
        bw_module,
        UIButton=MagicMock(),
        UILabel=MagicMock(),
        UIScrollingContainer=MagicMock(),
    ):
        yield


@pytest.fixture
def panel(patched_pygame_gui_elements):
    """Build a ModifierEditorPanel with mocked dependencies."""
    manager = MagicMock()
    container = MagicMock()
    registries = MagicMock()
    registries.modifiers = {}  # No allowed modifiers by default.
    on_change = MagicMock()

    p = ModifierEditorPanel(
        manager=manager,
        container=container,
        width=300,
        on_change_callback=on_change,
        registries=registries,
    )
    p.on_change_callback = on_change  # Expose for assertions.
    return p


# ----------------------------------------------------------------------------
# layout(): no-component branch shows hint
# ----------------------------------------------------------------------------


class TestLayoutNoComponent:
    def test_layout_renders_select_component_hint_when_editing_component_is_none(
        self, panel,
    ):
        assert panel.editing_component is None

        # Capture which UILabel constructions occur.
        with patch.object(bw_module, "UILabel", MagicMock()) as ui_label:
            panel.layout(start_y=0)

        # Two labels are constructed in the no-component branch:
        # - "── Component Modifiers ──"
        # - "Select a component to edit modifiers"
        texts = [call.kwargs.get("text") for call in ui_label.call_args_list]
        assert "── Component Modifiers ──" in texts
        assert "Select a component to edit modifiers" in texts


# ----------------------------------------------------------------------------
# _on_row_change toggle=True branch
# ----------------------------------------------------------------------------


class TestOnRowChangeToggle:
    def test_on_row_change_toggle_true_adds_modifier_and_recalculates(
        self, panel,
    ):
        # editing_component must be truthy for the toggle path to fire.
        comp = MagicMock()
        added_mod = MagicMock()
        comp.get_modifier.return_value = added_mod

        panel.editing_component = comp
        # Replace the resolved logic with a mock so initial value is
        # deterministic.
        panel._logic = MagicMock()
        panel._logic.get_initial_value.return_value = 7.5

        panel._on_row_change("toggle", "turret_mount", True)

        comp.add_modifier.assert_called_once_with("turret_mount")
        # After add, get_modifier was queried and the returned modifier had
        # its value set to the logic-provided initial value.
        comp.get_modifier.assert_called_with("turret_mount")
        assert added_mod.value == 7.5
        comp.recalculate_stats.assert_called_once()
        panel.on_change_callback.assert_called_once()


# ----------------------------------------------------------------------------
# handle_event: clear-settings button
# ----------------------------------------------------------------------------


class TestHandleEventClearSettings:
    def test_handle_event_clear_settings_button_returns_clear_settings_action(
        self, panel,
    ):
        # The button is set during layout(); for this test we install a
        # sentinel directly.
        sentinel_btn = MagicMock()
        panel.clear_settings_btn = sentinel_btn

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = sentinel_btn

        result = panel.handle_event(event)

        assert result == ("clear_settings", None)
