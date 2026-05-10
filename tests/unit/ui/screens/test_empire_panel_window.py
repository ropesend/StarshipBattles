"""Characterization tests for ``EmpirePanelWindow`` (PROJ-329B Phase 1).

This class had no tests before PROJ-329B; characterization written
against post-retrofit shape, which matches pre-retrofit production
behavior (Stage-1 state assignment unchanged, just hoisted above the
shell).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pygame_gui

from game.ui.screens.empire_panel_window import (
    TAB_MORE,
    TAB_NAMES,
    TAB_POPULATION,
    TAB_TREASURY,
    EmpirePanelUiBuilder,
    EmpirePanelWindow,
)
from tests.fixtures.empire_panel_window_ui_builder import (
    MockEmpirePanelWindowUiBuilder,
    NullEmpirePanelWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _empire(**overrides):
    e = MagicMock(name="Empire")
    e.race_config = overrides.get("race_config", MagicMock(name="RaceConfig"))
    e.portrait_id = overrides.get("portrait_id", "portrait_a")
    e.flag_id = overrides.get("flag_id", "flag_a")
    return e


def _make_window(
    empire=None,
    *,
    rect=None,
    on_close_callback=None,
    registries=None,
    race_registry=None,
    ui_builder=None,
):
    if empire is None:
        empire = _empire()
    if rect is None:
        rect = pygame.Rect(0, 0, 1100, 700)
    if ui_builder is None:
        ui_builder = MockEmpirePanelWindowUiBuilder()
    with bypass_init(EmpirePanelWindow):
        return EmpirePanelWindow(
            rect,
            MagicMock(name="ui_manager"),
            empire,
            window_manager=None,
            on_close_callback=on_close_callback,
            registries=registries,
            race_registry=race_registry,
            ui_builder=ui_builder,
        )


class TestEmpirePanelWindowStageOneState:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_empire_reference(self):
        empire = _empire()
        window = _make_window(empire)
        assert window.empire is empire

    def test_stores_close_callback(self):
        cb = MagicMock()
        window = _make_window(on_close_callback=cb)
        assert window.on_close_callback is cb

    def test_stores_registries(self):
        regs = MagicMock(name="GameRegistries")
        window = _make_window(registries=regs)
        assert window._registries is regs

    def test_stores_race_registry(self):
        rr = MagicMock(name="RaceRegistry")
        window = _make_window(race_registry=rr)
        assert window._race_registry is rr

    def test_close_callback_default_none(self):
        window = _make_window()
        assert window.on_close_callback is None

    def test_race_registry_default_none(self):
        window = _make_window()
        assert window._race_registry is None

    def test_asset_loader_assigned(self):
        from game.ui.screens.race_asset_loader import RaceAssetLoader
        window = _make_window()
        assert isinstance(window._asset_loader, RaceAssetLoader)

    def test_resource_icons_loaded(self):
        # PROJ-347 T4.4: under bypass_init the slot is the empty-dict
        # Stage-1 placeholder. The production builder branch (skipped
        # under bypass) calls load_resource_icons() AFTER the bypass
        # guard. Pin that the slot is a dict (production replaces the
        # placeholder with a populated dict).
        window = _make_window()
        assert isinstance(window._resource_icons, dict)

    def test_bypass_init_does_not_call_pygame_image_load(self):
        """PROJ-347 T4.4 Stage-1 purity: ``load_resource_icons()`` does
        ``pygame.image.load(...).convert_alpha()`` per resource icon —
        this is heavyweight Stage-2 work that must not run under
        bypass_init. Assert the slot is the empty-dict placeholder and
        that no ``pygame.image.load`` call happens during bypass-init
        construction.
        """
        from unittest.mock import patch

        with patch("pygame.image.load") as mock_load:
            window = _make_window()
            # Stage-1 placeholder is the empty dict; production load
            # ran neither in Stage 1 nor in the bypass branch of Stage 3.
            assert window._resource_icons == {}
            assert mock_load.call_count == 0, (
                f"pygame.image.load called {mock_load.call_count} times "
                f"under bypass_init — Stage-1 purity violated."
            )

    def test_treasury_panel_starts_none(self):
        window = _make_window()
        assert window._treasury_panel is None

    def test_current_tab_starts_at_treasury(self):
        window = _make_window()
        assert window.current_tab == TAB_TREASURY


class TestEmpirePanelWindowBuilderSeam:
    """``ui_builder`` seam wires correctly under bypass_init."""

    def test_window_init_bypassed_flag_set(self):
        window = _make_window()
        assert window._window_init_bypassed is True

    def test_ui_builder_kwarg_present(self):
        import inspect
        sig = inspect.signature(EmpirePanelWindow.__init__)
        assert 'ui_builder' in sig.parameters
        assert sig.parameters['ui_builder'].default is None

    def test_mock_builder_creates_three_tab_buttons(self):
        window = _make_window()
        assert len(window.tab_buttons) == len(TAB_NAMES)
        assert len(window.tab_buttons) == 3

    def test_mock_builder_creates_three_step_panels(self):
        window = _make_window()
        assert len(window.step_panels) == 3

    def test_mock_builder_selects_treasury_tab_by_default(self):
        window = _make_window()
        assert window.tab_buttons[TAB_TREASURY].is_selected is True
        assert window.tab_buttons[TAB_POPULATION].is_selected is False
        assert window.tab_buttons[TAB_MORE].is_selected is False

    def test_mock_builder_shows_only_treasury_panel(self):
        window = _make_window()
        assert window.step_panels[TAB_TREASURY].is_visible is True
        assert window.step_panels[TAB_POPULATION].is_visible is False
        assert window.step_panels[TAB_MORE].is_visible is False

    def test_null_builder_leaves_tab_state_default(self):
        window = _make_window(ui_builder=NullEmpirePanelWindowUiBuilder())
        # Stage-1 defaults: empty list + current_tab = TAB_TREASURY.
        assert window.tab_buttons == []
        assert window.step_panels == []
        assert window.current_tab == TAB_TREASURY

    def test_production_builder_implements_protocol(self):
        from tests.fixtures.ui_builder_protocol import UiBuilder
        assert isinstance(EmpirePanelUiBuilder(), UiBuilder)
        assert isinstance(MockEmpirePanelWindowUiBuilder(), UiBuilder)
        assert isinstance(NullEmpirePanelWindowUiBuilder(), UiBuilder)


class TestEmpirePanelWindowShowTab:
    """``_show_tab`` toggles visibility + selection state."""

    def test_show_tab_switches_to_population(self):
        window = _make_window()
        window._show_tab(TAB_POPULATION)
        assert window.current_tab == TAB_POPULATION
        assert window.step_panels[TAB_POPULATION].is_visible is True
        assert window.step_panels[TAB_TREASURY].is_visible is False

    def test_show_tab_clamps_above_max(self):
        window = _make_window()
        window._show_tab(99)
        # Clamped to last tab (index 2)
        assert window.current_tab == 2

    def test_show_tab_clamps_below_zero(self):
        window = _make_window()
        window._show_tab(-5)
        # Clamped to 0
        assert window.current_tab == 0

    def test_show_tab_updates_button_selection(self):
        window = _make_window()
        window._show_tab(TAB_MORE)
        assert window.tab_buttons[TAB_MORE].is_selected is True
        assert window.tab_buttons[TAB_TREASURY].is_selected is False


class TestEmpirePanelWindowEventsAndEmptyData:
    """Focused branch coverage for tab events and empty population data."""

    def test_process_event_switches_tab_for_button_press(self):
        window = _make_window()
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = window.tab_buttons[TAB_POPULATION]

        with patch(
            "pygame_gui.elements.UIWindow.process_event",
            return_value=False,
        ):
            handled = window.process_event(event)

        assert handled is True
        assert window.current_tab == TAB_POPULATION
        assert window.step_panels[TAB_POPULATION].is_visible is True

    def test_build_population_tab_with_no_race_config_shows_empty_message(self):
        empire = _empire(race_config=None)
        window = _make_window(empire, ui_builder=NullEmpirePanelWindowUiBuilder())
        panel = MagicMock(name="panel")
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 420, 320)

        with (
            patch(
                "game.ui.screens.empire_panel_window.UIScrollingContainer"
            ) as scroll_cls,
            patch("game.ui.screens.empire_panel_window.UILabel") as label_cls,
        ):
            window._build_population_tab(panel)

        scroll_cls.assert_called_once()
        label_cls.assert_called_once()
        assert (
            label_cls.call_args.kwargs["text"]
            == "No species data available"
        )
        scroll_cls.return_value.set_scrollable_area_dimensions.assert_not_called()

    def test_render_portrait_flag_row_skips_images_when_ids_missing(self):
        race_config = SimpleNamespace(portrait_id="", flag_id="")
        empire = _empire(race_config=race_config, portrait_id="", flag_id="")
        window = _make_window(empire, ui_builder=NullEmpirePanelWindowUiBuilder())
        window._asset_loader = MagicMock(name="asset_loader")

        with (
            patch("game.ui.screens.empire_panel_window.UIImage") as image_cls,
            patch("pygame.transform.smoothscale") as smoothscale,
        ):
            y_offset = window._render_portrait_flag_row(
                MagicMock(name="container"),
                race_config,
                25,
            )

        assert y_offset == 165
        window._asset_loader.load_portrait_full.assert_not_called()
        window._asset_loader.load_flag_full.assert_not_called()
        image_cls.assert_not_called()
        smoothscale.assert_not_called()

    def test_render_environment_section_uses_placeholders_for_missing_prefs(self):
        window = _make_window(ui_builder=NullEmpirePanelWindowUiBuilder())
        race_config = SimpleNamespace(preferences={})

        with (
            patch("game.ui.screens.empire_panel_window.create_section_header"),
            patch("game.ui.screens.empire_panel_window.UILabel") as label_cls,
        ):
            y_offset = window._render_environment_section(
                MagicMock(name="container"),
                race_config,
                10,
                500,
            )

        texts = [call.kwargs["text"] for call in label_cls.call_args_list]
        assert texts == [
            "Gravity: --",
            "Temperature: --",
            "Water: --",
            "Radiation Tolerance: --",
        ]
        assert y_offset == 10 + 24 + 5 + (4 * 24) + 15

    def test_render_descriptions_section_noops_for_empty_descriptions(self):
        window = _make_window(ui_builder=NullEmpirePanelWindowUiBuilder())
        race_config = SimpleNamespace(bio_description="", socio_description="")

        with (
            patch("game.ui.screens.empire_panel_window.create_section_header") as header,
            patch("game.ui.screens.empire_panel_window.UITextBox") as text_box,
        ):
            y_offset = window._render_descriptions_section(
                MagicMock(name="container"),
                race_config,
                40,
                500,
            )

        assert y_offset == 40
        header.assert_not_called()
        text_box.assert_not_called()
