"""TestLabRenderer — orchestrator.

PROJ-309 sub-phase 3.3 split `renderer.py` into a `renderer/` subpackage.
This module hosts the public class. It owns shared font + layout state and
delegates each visual region to a panel class.

Public-API stability:

* `TestLabRenderer` is re-exported from `renderer/__init__.py` so existing
  callers (`from game.ui.screens.test_lab.renderer import TestLabRenderer`)
  continue to work.
* `TestLabRenderer._format_check_pair` and `TestLabRenderer._is_condition_verified`
  remain accessible as class attributes — the existing pure-function tests
  in `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` use
  the class-attribute access pattern. The aliases below preserve that.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pygame

from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme

from ._condition_logic import is_condition_verified, format_check_pair
from ._draw_helpers import draw_output_log
from .header_panel import HeaderPanel
from .category_panel import CategoryPanel
from .tag_filter_panel import TagFilterPanel
from .test_list_panel import TestListPanel
from .metadata_panel import MetadataPanel
from .validation_panel import ValidationPanel


class TestLabRenderer:
    """
    Renders the Combat Lab UI.

    All draw methods read from ViewModel/controller state and render to the screen.
    Button rects computed during rendering are stored back to the ViewModel for
    input handler use.

    This renderer does NOT mutate business state - only rect positions in ViewModel.
    """

    # Color scheme - from theme module
    BG_COLOR = theme.BG_PRIMARY
    PANEL_BG = theme.BG_PANEL
    BORDER_COLOR = theme.BORDER
    TEXT_COLOR = theme.TEXT
    HEADER_COLOR = theme.TEXT_HEADER
    SELECTED_COLOR = theme.SELECTED_BG
    HOVER_COLOR = theme.TEXT_DIM
    CATEGORY_BG = theme.BG_CATEGORY

    # Test-compat aliases — existing tests import
    # `TestLabRenderer._format_check_pair` and `TestLabRenderer._is_condition_verified`
    # as class attributes. Keep them callable from the class so the legacy
    # test pattern (instantiate via `__new__`, call as bound/unbound method)
    # continues to work without modification.
    _format_check_pair = staticmethod(format_check_pair)

    def _is_condition_verified(self, condition_text, validation_results) -> bool:
        return is_condition_verified(condition_text, validation_results)

    def __init__(self):
        """Initialize the renderer with fonts."""
        self.title_font = get_font(48)
        self.header_font = get_font(24)
        self.body_font = get_font(18)
        self.small_font = get_font(14)

        # Layout dimensions
        self.category_width = 220
        self.test_list_width = 420
        self.metadata_width = 540
        self.header_height = 80

        # Construct panel components
        self._header_panel = HeaderPanel(
            title_font=self.title_font,
            body_font=self.body_font,
            small_font=self.small_font,
            header_color=self.HEADER_COLOR,
            text_color=self.TEXT_COLOR,
            category_bg=self.CATEGORY_BG,
            border_color=self.BORDER_COLOR,
        )
        self._category_panel = CategoryPanel(
            header_font=self.header_font,
            body_font=self.body_font,
            small_font=self.small_font,
            header_color=self.HEADER_COLOR,
            text_color=self.TEXT_COLOR,
            selected_color=self.SELECTED_COLOR,
            category_bg=self.CATEGORY_BG,
            panel_bg=self.PANEL_BG,
            border_color=self.BORDER_COLOR,
            category_width=self.category_width,
            header_height=self.header_height,
        )
        self._tag_filter_panel = TagFilterPanel(
            small_font=self.small_font,
            header_color=self.HEADER_COLOR,
            text_color=self.TEXT_COLOR,
            category_bg=self.CATEGORY_BG,
            border_color=self.BORDER_COLOR,
        )
        self._test_list_panel = TestListPanel(
            header_font=self.header_font,
            body_font=self.body_font,
            small_font=self.small_font,
            header_color=self.HEADER_COLOR,
            text_color=self.TEXT_COLOR,
            selected_color=self.SELECTED_COLOR,
            panel_bg=self.PANEL_BG,
            border_color=self.BORDER_COLOR,
            category_width=self.category_width,
            test_list_width=self.test_list_width,
            header_height=self.header_height,
        )
        self._validation_panel = ValidationPanel(
            body_font=self.body_font,
            small_font=self.small_font,
        )
        self._metadata_panel = MetadataPanel(
            header_font=self.header_font,
            body_font=self.body_font,
            small_font=self.small_font,
            header_color=self.HEADER_COLOR,
            text_color=self.TEXT_COLOR,
            panel_bg=self.PANEL_BG,
            border_color=self.BORDER_COLOR,
            category_width=self.category_width,
            test_list_width=self.test_list_width,
            metadata_width=self.metadata_width,
            header_height=self.header_height,
            validation_panel=self._validation_panel,
        )

    def draw(
        self,
        surface: pygame.Surface,
        viewmodel,
        controller,
        registry,
        categories: List[str],
        filtered_scenarios: Dict[str, Any],
        executor,
        ui_manager,
    ) -> None:
        """
        Main draw method - renders the entire Combat Lab UI.

        Args:
            surface: Pygame surface to draw on
            viewmodel: TestLabViewModel with UI state
            controller: TestLabUIController with business state
            registry: TestRegistry for test data
            categories: List of category names
            filtered_scenarios: Dict of test_id -> scenario_info
            executor: TestLabExecutor for batch state
            ui_manager: pygame_gui UIManager
        """
        surface.fill(self.BG_COLOR)

        # Header
        self._header_panel.draw(surface, controller, registry, viewmodel)

        # Three-column layout — category panel returns its terminal-y so
        # we can position the tag-filter section beneath it without coupling
        # the two panels (the original code had _draw_category_sidebar call
        # _draw_tag_filters directly).
        category_end_y = self._category_panel.draw(
            surface, controller, registry, categories, viewmodel,
        )
        self._tag_filter_panel.draw(
            surface, 20, category_end_y + 15, controller, registry, viewmodel,
        )
        self._test_list_panel.draw(
            surface, controller, filtered_scenarios, viewmodel, executor,
        )
        self._metadata_panel.draw(
            surface, controller, registry, viewmodel,
        )

        # Panels (from ViewModel)
        if viewmodel.tabbed_ship_panel:
            viewmodel.tabbed_ship_panel.draw(surface)
        for panel in viewmodel.ship_panels:
            panel.draw(surface)
        for panel in viewmodel.component_panels:
            panel.draw(surface)
        if viewmodel.results_panel:
            viewmodel.results_panel.draw(surface)
        if viewmodel.test_details_panel:
            viewmodel.test_details_panel.draw(surface)

        # Output log
        draw_output_log(surface, self.small_font, controller.output_log)

        # Update and draw pygame_gui UIManager
        ui_manager.update(1.0 / 60.0)
        ui_manager.draw_ui(surface)

        # Dialogs (drawn on top)
        if viewmodel.json_popup and viewmodel.json_popup.is_open:
            viewmodel.json_popup.draw(surface)
        if viewmodel.confirmation_dialog and viewmodel.confirmation_dialog.is_open:
            viewmodel.confirmation_dialog.draw(surface)
