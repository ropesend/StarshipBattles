"""FEAT-20: Tests for the `Run 10 Turns` button in the strategy top bar.

The button is unconditionally instantiated by `create_strategy_panels` (the
revised FEAT-20 scope removed the `--dev` gate so the button always appears
next to End Turn).
"""
from __future__ import annotations

import os
from dataclasses import fields
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame
import pytest


# Force headless before pygame import.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class TestRun10TurnsButtonField:
    """`btn_run_10_turns` must exist as a declared field on StrategyWidgets."""

    def test_btn_run_10_turns_field_declared(self):
        """The widgets dataclass must declare `btn_run_10_turns: Any = None`."""
        from game.ui.screens.strategy_panel_manager import StrategyWidgets
        field_names = {f.name for f in fields(StrategyWidgets)}
        assert "btn_run_10_turns" in field_names

    def test_btn_run_10_turns_default_is_none(self):
        """Default value is None on the bare dataclass; populated by
        `create_strategy_panels`."""
        from game.ui.screens.strategy_panel_manager import StrategyWidgets
        widgets = StrategyWidgets()
        assert widgets.btn_run_10_turns is None


def _create_panels():
    """Create panels via `create_strategy_panels` with a real UIManager."""
    import pygame
    import pygame_gui
    from game.ui.screens.strategy_panel_manager import create_strategy_panels

    pygame.init()
    pygame.font.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1440, 900), pygame.NOFRAME)

    manager = pygame_gui.UIManager((1440, 900))
    selection_cb = MagicMock()
    widgets = create_strategy_panels(
        manager, 1440, 900, sidebar_width=400,
        on_ui_selection_callback=selection_cb,
    )
    return widgets


class TestRun10TurnsButtonVisibility:
    """The button is always created by `create_strategy_panels`."""

    def test_button_always_present(self):
        widgets = _create_panels()
        assert widgets.btn_run_10_turns is not None


class _Widget:
    def __init__(self, width: int = 100, height: int = 100) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.dimensions: list[tuple[float, float]] = []
        self.positions: list[tuple[float, float]] = []
        self.tooltips: list[str] = []

    def set_dimensions(self, dimensions: tuple[float, float]) -> None:
        self.dimensions.append(dimensions)
        self.rect.size = (int(dimensions[0]), int(dimensions[1]))

    def set_relative_position(self, position: tuple[float, float]) -> None:
        self.positions.append(position)
        self.rect.topleft = (int(position[0]), int(position[1]))

    def set_tooltip(self, text: str) -> None:
        self.tooltips.append(text)


def _fake_resizable_ui() -> SimpleNamespace:
    return SimpleNamespace(
        system_panel=_Widget(),
        system_tree=_Widget(),
        sector_panel=_Widget(),
        sector_tree=_Widget(),
        detail_panel=_Widget(),
        detail_text=_Widget(),
        graph_image=_Widget(),
        graph_rect=pygame.Rect(10, 170, 150, 100),
        spectrum_graph=None,
        atmosphere_graph=None,
        btn_raw_data=_Widget(20, 20),
    )


class TestResizeStrategyPanels:
    def test_panel_resize_rebuilds_graphs_and_moves_raw_data_button(self, monkeypatch):
        from game.ui.screens import strategy_panel_manager as panel_manager

        ui = _fake_resizable_ui()
        monkeypatch.setattr(
            panel_manager,
            "SpectrumGraph",
            lambda width, height: ("spectrum", width, height),
        )
        monkeypatch.setattr(
            panel_manager,
            "AtmosphereGraph",
            lambda width, height: ("atmosphere", width, height),
        )

        panel_manager.resize_strategy_panels(
            ui, MagicMock(), width=1200, height=900, sidebar_width=300
        )

        assert ui.system_panel.dimensions[-1] == pytest.approx((280, (900 - 20) / 3 - 5))
        assert ui.system_panel.positions[-1] == (-290, 10)
        assert ui.detail_text.dimensions[-1][0] == 120
        assert ui.graph_image.dimensions[-1] == (150, ui.graph_rect.height)
        assert ui.spectrum_graph == ("spectrum", int(ui.graph_rect.height), int(ui.graph_rect.width))
        assert ui.atmosphere_graph == ("atmosphere", int(ui.graph_rect.height), int(ui.graph_rect.width))
        assert ui.btn_raw_data.positions[-1] == (ui.graph_rect.right - 22, ui.graph_rect.top + 2)

    def test_resize_strategy_panels_clamps_graph_height_to_minimum(self, monkeypatch):
        from game.ui.screens import strategy_panel_manager as panel_manager

        ui = _fake_resizable_ui()
        monkeypatch.setattr(panel_manager, "SpectrumGraph", lambda width, height: None)
        monkeypatch.setattr(panel_manager, "AtmosphereGraph", lambda width, height: None)

        panel_manager.resize_strategy_panels(
            ui, MagicMock(), width=1200, height=320, sidebar_width=300
        )

        assert ui.graph_rect.height == 50
        assert ui.graph_image.dimensions[-1] == (150, 50)


def _fake_tooltip_ui() -> SimpleNamespace:
    button_names = [
        "btn_next_turn",
        "btn_planets",
        "btn_empire",
        "btn_research",
        "btn_design",
        "btn_build_queues",
        "btn_prev_colony",
        "btn_next_colony",
        "btn_prev_fleet",
        "btn_next_fleet",
        "btn_colonize",
        "btn_orders",
        "btn_fleet_report",
        "btn_build_fleet",
    ]
    return SimpleNamespace(**{name: _Widget(20, 20) for name in button_names})


class TestApplyHotkeyTooltips:
    def test_apply_hotkey_tooltips_returns_without_mapper(self):
        from game.ui.screens.strategy_panel_manager import apply_hotkey_tooltips

        ui = _fake_tooltip_ui()

        apply_hotkey_tooltips(ui, None)

        assert all(not button.tooltips for button in vars(ui).values())

    def test_apply_hotkey_tooltips_sets_only_bound_actions(self):
        from game.core.input_actions import InputAction
        from game.ui.screens.strategy_panel_manager import apply_hotkey_tooltips

        ui = _fake_tooltip_ui()
        hints = {
            InputAction.STRATEGY_NEXT_TURN: "Enter",
            InputAction.STRATEGY_PREV_FLEET: "Shift+F",
            InputAction.FLEET_COLONIZE: "C",
        }
        mapper = MagicMock()
        mapper.get_display_text.side_effect = lambda action: hints.get(action, "")

        apply_hotkey_tooltips(ui, mapper)

        assert ui.btn_next_turn.tooltips == ["Enter"]
        assert ui.btn_prev_fleet.tooltips == ["Shift+F"]
        assert ui.btn_colonize.tooltips == ["C"]
        assert ui.btn_planets.tooltips == []
