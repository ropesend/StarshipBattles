"""Focused tests for ModifierControlRow UI lifecycle and event handling."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame_gui
import pytest

from game.ui.screens.builder import modifier_row
from game.ui.screens.builder.modifier_row import ModifierControlRow


class _FakeElement:
    def __init__(self) -> None:
        self.enabled = True
        self.killed = False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def kill(self) -> None:
        self.killed = True


class _FakeButton(_FakeElement):
    def __init__(
        self,
        relative_rect,
        text: str = "",
        manager=None,
        container=None,
        object_id: str | None = None,
        tool_tip_text: str | None = None,
    ) -> None:
        super().__init__()
        self.relative_rect = relative_rect
        self.text = text
        self.manager = manager
        self.container = container
        self.object_id = object_id
        self.tool_tip_text = tool_tip_text

    def set_text(self, text: str) -> None:
        self.text = text


class _FakeEntry(_FakeElement):
    def __init__(
        self,
        relative_rect,
        manager=None,
        container=None,
        object_id: str | None = None,
    ) -> None:
        super().__init__()
        self.relative_rect = relative_rect
        self.manager = manager
        self.container = container
        self.object_id = object_id
        self.text = ""

    def set_text(self, text: str) -> None:
        self.text = text

    def get_text(self) -> str:
        return self.text


class _FakeSlider(_FakeElement):
    def __init__(
        self,
        relative_rect,
        start_value: float,
        value_range: tuple[float, float],
        manager=None,
        container=None,
        object_id: str | None = None,
        click_increment: float = 0.01,
    ) -> None:
        super().__init__()
        self.relative_rect = relative_rect
        self.current_value = start_value
        self.value_range = value_range
        self.manager = manager
        self.container = container
        self.object_id = object_id
        self.click_increment = click_increment
        self.enable_arrow_buttons = True
        self.rebuilt = False

    def rebuild(self) -> None:
        self.rebuilt = True

    def set_current_value(self, value: float) -> None:
        self.current_value = value

    def get_current_value(self) -> float:
        return self.current_value


@pytest.fixture(autouse=True)
def fake_pygame_gui(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(modifier_row, "UIButton", _FakeButton)
    monkeypatch.setattr(modifier_row, "UITextEntryLine", _FakeEntry)
    monkeypatch.setattr(modifier_row, "UIHorizontalSlider", _FakeSlider)


def _mod_def(*, min_val: float = 0.0, max_val: float = 10.0):
    return SimpleNamespace(
        name="Range Mount",
        description="Adjusts range",
        min_val=min_val,
        max_val=max_val,
    )


def _make_row(
    config: dict,
    *,
    callback: MagicMock | None = None,
    logic: MagicMock | None = None,
    mod_def=None,
) -> ModifierControlRow:
    return ModifierControlRow(
        manager=MagicMock(),
        container=MagicMock(),
        width=420,
        mod_id="range.mount",
        mod_def=mod_def or _mod_def(),
        config=config,
        on_change_callback=callback or MagicMock(),
        modifier_logic=logic,
    )


@pytest.mark.parametrize(
    ("config", "expected_actions"),
    [
        ({"control_type": "linear"}, []),
        (
            {
                "control_type": "linear_stepped",
                "step_buttons": [
                    {"label": "+", "mode": "delta_add", "value": 1.0},
                    {"label": "-", "mode": "delta_sub", "value": 1.0},
                ],
            },
            ["delta_add", "delta_sub"],
        ),
        (
            {"control_type": "facing_selector", "presets": [0, 90, 180]},
            ["set_value", "set_value", "set_value"],
        ),
    ],
)
def test_modifier_control_row_builds_supported_control_types(
    config: dict,
    expected_actions: list[str],
) -> None:
    row = _make_row(config)

    height = row.build_ui(12)

    assert height == 32
    assert row.toggle_btn.text == "[ ] Range Mount"
    assert row.toggle_btn.object_id == "#mod_range_mount"
    assert row.entry is not None
    assert row.slider is not None
    assert row.slider.rebuilt is True
    assert [data["action"] for data in row.buttons.values()] == expected_actions


def test_modifier_control_row_update_with_component_sets_controls_and_locks_mandatory() -> None:
    logic = MagicMock()
    logic.get_local_min_max.return_value = (2.0, 8.0)
    logic.is_modifier_mandatory.return_value = True
    row = _make_row({"control_type": "linear"}, logic=logic)
    row.build_ui(0)
    component = MagicMock()
    component.get_modifier.return_value = SimpleNamespace(value=7.25)

    row.update(component, {})

    assert row.is_active is True
    assert row.current_value == 7.25
    assert row.toggle_btn.text == "[x] Range Mount"
    assert row.toggle_btn.enabled is False
    assert row.entry.enabled is True
    assert row.entry.text == "7.25"
    assert row.slider.enabled is True
    assert row.slider.value_range == (2.0, 8.0)
    assert row.slider.current_value == 7.25


def test_modifier_control_row_update_with_template_modifier_uses_default_bounds() -> None:
    row = _make_row({"control_type": "linear"})
    row.build_ui(0)

    row.update(None, {"range.mount": 3.5})

    assert row.is_active is True
    assert row.toggle_btn.text == "[x] Range Mount"
    assert row.toggle_btn.enabled is True
    assert row.entry.enabled is True
    assert row.entry.text == "3.50"
    assert row.slider.value_range == (0.0, 10.0)
    assert row.slider.current_value == 3.5


def test_modifier_control_row_update_inactive_disables_value_controls() -> None:
    row = _make_row({"control_type": "linear"})
    row.build_ui(0)

    row.update(None, {})

    assert row.is_active is False
    assert row.toggle_btn.text == "[ ] Range Mount"
    assert row.toggle_btn.enabled is True
    assert row.entry.enabled is False
    assert row.slider.enabled is False
    assert row.entry.text == "0.00"


def test_modifier_control_row_handle_event_ignores_event_without_ui_element() -> None:
    row = _make_row({"control_type": "linear"})

    assert row.handle_event(SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED)) is False


def test_modifier_control_row_handle_event_ignores_inactive_non_toggle_control() -> None:
    callback = MagicMock()
    row = _make_row({"control_type": "linear"}, callback=callback)
    row.build_ui(0)
    row.is_active = False
    event = SimpleNamespace(
        type=pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
        ui_element=row.slider,
    )

    assert row.handle_event(event) is False
    callback.assert_not_called()


def test_modifier_control_row_handle_event_toggles_active_state() -> None:
    callback = MagicMock()
    logic = MagicMock()
    logic.is_modifier_mandatory.return_value = False
    row = _make_row({"control_type": "linear"}, callback=callback, logic=logic)
    row.build_ui(0)
    row.is_active = False
    event = SimpleNamespace(
        type=pygame_gui.UI_BUTTON_PRESSED,
        ui_element=row.toggle_btn,
    )

    assert row.handle_event(event) is True
    callback.assert_called_once_with("toggle", "range.mount", True)


def test_modifier_control_row_handle_event_ignores_mandatory_toggle() -> None:
    callback = MagicMock()
    logic = MagicMock()
    logic.is_modifier_mandatory.return_value = True
    row = _make_row({"control_type": "linear"}, callback=callback, logic=logic)
    row.build_ui(0)
    row.is_active = True
    row.component_context = MagicMock()
    event = SimpleNamespace(
        type=pygame_gui.UI_BUTTON_PRESSED,
        ui_element=row.toggle_btn,
    )

    assert row.handle_event(event) is False
    callback.assert_not_called()


def test_modifier_control_row_handle_event_facing_preset_sets_value() -> None:
    callback = MagicMock()
    row = _make_row(
        {"control_type": "facing_selector", "presets": [0, 90]},
        callback=callback,
        mod_def=_mod_def(max_val=360.0),
    )
    row.build_ui(0)
    row.update(None, {"range.mount": 0.0})
    preset_button = next(
        button for button, data in row.buttons.items() if data["value"] == 90
    )
    event = SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=preset_button)

    assert row.handle_event(event) is True
    callback.assert_called_once_with("value_change", "range.mount", 90.0)


@pytest.mark.parametrize(
    ("mode", "step", "expected"),
    [
        ("delta_add", 2.0, 7.0),
        ("delta_sub", 3.0, 2.0),
        ("snap_floor", 5.0, 0.0),
        ("snap_ceil", 5.0, 10.0),
    ],
)
def test_modifier_control_row_handle_event_step_buttons_change_value(
    mode: str,
    step: float,
    expected: float,
) -> None:
    callback = MagicMock()
    logic = MagicMock()
    logic.get_local_min_max.return_value = (0.0, 10.0)
    logic.calculate_snap_value.side_effect = lambda current, *_args: (
        0.0 if current == 5.0 and mode == "snap_floor" else 10.0
    )
    row = _make_row(
        {
            "control_type": "linear_stepped",
            "step_buttons": [{"label": mode, "mode": mode, "value": step}],
        },
        callback=callback,
        logic=logic,
    )
    row.build_ui(0)
    row.is_active = True
    row.current_value = 5.0
    row.component_context = MagicMock()
    button = next(iter(row.buttons))
    event = SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=button)

    assert row.handle_event(event) is True
    callback.assert_called_once_with("value_change", "range.mount", expected)


def test_modifier_control_row_handle_event_slider_change_callbacks() -> None:
    callback = MagicMock()
    row = _make_row({"control_type": "linear"}, callback=callback)
    row.build_ui(0)
    row.is_active = True
    row.current_value = 2.0
    row.slider.current_value = 4.25
    event = SimpleNamespace(
        type=pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
        ui_element=row.slider,
    )

    assert row.handle_event(event) is True
    callback.assert_called_once_with("value_change", "range.mount", 4.25)


def test_modifier_control_row_handle_event_text_entry_clamps_value() -> None:
    callback = MagicMock()
    row = _make_row({"control_type": "linear"}, callback=callback)
    row.build_ui(0)
    row.is_active = True
    row.current_value = 2.0
    row.entry.text = "99"
    event = SimpleNamespace(
        type=pygame_gui.UI_TEXT_ENTRY_FINISHED,
        ui_element=row.entry,
    )

    assert row.handle_event(event) is True
    callback.assert_called_once_with("value_change", "range.mount", 10.0)


def test_modifier_control_row_handle_event_text_entry_ignores_invalid_float() -> None:
    callback = MagicMock()
    row = _make_row({"control_type": "linear"}, callback=callback)
    row.build_ui(0)
    row.is_active = True
    row.entry.text = "not-a-number"
    event = SimpleNamespace(
        type=pygame_gui.UI_TEXT_ENTRY_FINISHED,
        ui_element=row.entry,
    )

    assert row.handle_event(event) is False
    callback.assert_not_called()


def test_modifier_control_row_kill_destroys_elements_and_resets_references() -> None:
    row = _make_row(
        {
            "control_type": "linear_stepped",
            "step_buttons": [{"label": "+", "mode": "delta_add", "value": 1.0}],
        }
    )
    row.build_ui(0)
    elements = list(row.ui_elements)

    row.kill()

    assert all(element.killed for element in elements)
    assert row.ui_elements == []
    assert row.buttons == {}
    assert row.slider is None
    assert row.entry is None

