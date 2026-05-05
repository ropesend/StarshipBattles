from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.race_setup import panel_factory


class PanelStub:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        self._rect = pygame.Rect(0, 0, width, height)

    def get_relative_rect(self) -> pygame.Rect:
        return self._rect


def _screen_stub() -> SimpleNamespace:
    controller = SimpleNamespace(
        on_load_race=MagicMock(name="on_load_race"),
        randomize_all=MagicMock(name="randomize_all"),
        on_theme_selected=MagicMock(name="on_theme_selected"),
        attach_description_controller=MagicMock(
            name="attach_description_controller"
        ),
        on_description_controller_change=MagicMock(
            name="on_description_controller_change"
        ),
    )
    return SimpleNamespace(
        ui_manager=MagicMock(name="ui_manager"),
        race_config=MagicMock(name="race_config"),
        _asset_loader=MagicMock(name="asset_loader"),
        _controller=controller,
        _summary_panel=None,
        _identity_panel=None,
        _flag_gallery=None,
        _portrait_gallery=None,
        _theme_gallery=None,
        _environment_panel=None,
        _aptitudes_panel=None,
        _description_panel=None,
        btn_load=None,
        btn_randomize_all=None,
        ship_preview_scroll=None,
    )


def test_create_summary_panel_wires_callbacks_and_buttons() -> None:
    screen = _screen_stub()
    panel = PanelStub()
    panel_instance = MagicMock(name="summary_panel")
    panel_instance.btn_load = MagicMock(name="btn_load")
    panel_instance.btn_randomize_all = MagicMock(name="btn_randomize_all")

    with patch.object(
        panel_factory, "RaceSummaryPanel", return_value=panel_instance
    ) as panel_cls:
        panel_factory.create_summary_panel(screen, panel)

    panel_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        asset_loader=screen._asset_loader,
        on_load_race_callback=screen._controller.on_load_race,
        on_randomize_all_callback=screen._controller.randomize_all,
    )
    assert screen._summary_panel is panel_instance
    assert screen.btn_load is panel_instance.btn_load
    assert screen.btn_randomize_all is panel_instance.btn_randomize_all


def test_create_identity_panel_wires_race_config() -> None:
    screen = _screen_stub()
    panel = PanelStub()

    with patch.object(panel_factory, "RaceIdentityPanel") as panel_cls:
        panel_factory.create_identity_panel(screen, panel)

    panel_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )
    assert screen._identity_panel is panel_cls.return_value


def test_create_visuals_panel_builds_flag_and_portrait_galleries() -> None:
    screen = _screen_stub()
    panel = PanelStub(width=820, height=500)

    with (
        patch.object(panel_factory, "RaceFlagGallery") as flag_cls,
        patch.object(panel_factory, "RacePortraitGallery") as portrait_cls,
    ):
        panel_factory.create_visuals_panel(screen, panel)

    flag_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=10,
        y=10,
        width=390,
        height=470,
        asset_loader=screen._asset_loader,
    )
    portrait_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=405,
        y=10,
        width=390,
        height=470,
        asset_loader=screen._asset_loader,
    )
    assert screen._flag_gallery is flag_cls.return_value
    assert screen._portrait_gallery is portrait_cls.return_value


def test_create_ships_panel_wires_theme_gallery_and_preview_scroll() -> None:
    screen = _screen_stub()
    panel = PanelStub(width=820, height=500)

    with (
        patch.object(panel_factory, "RaceThemeGallery") as gallery_cls,
        patch(
            "game.ui.screens.race_setup.panel_factory.pygame_gui.elements.UILabel"
        ) as label_cls,
        patch(
            "game.ui.screens.race_setup.panel_factory.pygame_gui.elements."
            "UIScrollingContainer"
        ) as scroll_cls,
    ):
        panel_factory.create_ships_panel(screen, panel)

    label_cls.assert_called_once()
    gallery_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
        x=10,
        y=55,
        width=200,
        height=435,
        on_select_callback=screen._controller.on_theme_selected,
    )
    scroll_cls.assert_called_once()
    assert screen._theme_gallery is gallery_cls.return_value
    assert screen.ship_preview_scroll is scroll_cls.return_value


def test_create_environment_panel_wires_panel() -> None:
    screen = _screen_stub()
    panel = PanelStub()

    with patch.object(panel_factory, "RaceEnvironmentPanel") as panel_cls:
        panel_factory.create_environment_panel(screen, panel)

    panel_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )
    assert screen._environment_panel is panel_cls.return_value


def test_create_aptitudes_panel_wires_panel() -> None:
    screen = _screen_stub()
    panel = PanelStub()

    with patch.object(panel_factory, "RaceAptitudesPanel") as panel_cls:
        panel_factory.create_aptitudes_panel(screen, panel)

    panel_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )
    assert screen._aptitudes_panel is panel_cls.return_value


def test_create_descriptions_panel_without_provider_skips_llm_wiring() -> None:
    screen = _screen_stub()
    panel = PanelStub()

    with (
        patch.object(panel_factory, "RaceDescriptionPanel") as panel_cls,
        patch("game.services.llm.get_default_llm_provider", return_value=None),
    ):
        panel_factory.create_descriptions_panel(screen, panel)

    panel_cls.assert_called_once_with(
        panel=panel,
        manager=screen.ui_manager,
        race_config=screen.race_config,
    )
    screen._controller.attach_description_controller.assert_not_called()
    assert screen._description_panel is panel_cls.return_value


def test_create_descriptions_panel_attaches_llm_controller() -> None:
    screen = _screen_stub()
    panel = PanelStub()
    provider = MagicMock(name="provider")

    with (
        patch.object(panel_factory, "RaceDescriptionPanel") as panel_cls,
        patch("game.services.llm.get_default_llm_provider", return_value=provider),
        patch(
            "game.strategy.data.race_caption_loader.RaceCaptionLoader"
        ) as caption_loader_cls,
        patch(
            "game.strategy.services.race_description_llm_controller."
            "RaceDescriptionLLMController"
        ) as controller_cls,
    ):
        panel_factory.create_descriptions_panel(screen, panel)

    controller_cls.assert_called_once_with(
        race_config=screen.race_config,
        provider=provider,
        caption_loader=caption_loader_cls.return_value,
        on_change=screen._controller.on_description_controller_change,
    )
    description_controller = controller_cls.return_value
    screen._controller.attach_description_controller.assert_called_once_with(
        description_controller
    )
    panel_cls.return_value.attach_controller.assert_called_once_with(
        description_controller
    )
    panel_cls.return_value.set_state.assert_called_once_with(description_controller)
