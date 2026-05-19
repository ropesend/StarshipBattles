"""Planet-list event router + selection coordinator.

PROJ-457 Phase 2: extracted from ``planet_list_window.py``. Owns:

* ``process_event`` — main event dispatch.
* Filter button helpers (``_set_all_filters``, ``_set_all_effects``,
  ``_toggle_filter``).
* Planet-selection cluster (``_on_planet_selected``,
  ``_resolve_demographic_view``, ``_detail_panel_geometry``,
  ``_navigate_to_selected``).

The window retains thin delegating shims for ``process_event`` and
``set_dimensions`` (pygame_gui overrides) and the public lifecycle
methods that ``StrategyGameStateManager`` and ``PlanetListRegistrar``
call into.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

import pygame
from pygame_gui import UI_BUTTON_PRESSED, UI_TEXT_ENTRY_FINISHED
from pygame_gui.elements import UIButton

from game.strategy.services.planet_economy_projector import compute_planet_production
from game.ui.filters.filter_state import FilterState
from game.ui.panels.planet_report_panel import PlanetReportPanel

if TYPE_CHECKING:
    from game.ui.screens.planet_list_window import PlanetListWindow


logger = logging.getLogger(__name__)


class PlanetListEventRouter:
    """Owns event dispatch + selection coordination for `PlanetListWindow`."""

    def __init__(self, window: "PlanetListWindow") -> None:
        self._w = window

    # -----------------------------------------------------------------------
    # Event dispatch
    # -----------------------------------------------------------------------

    def process_event(self, event) -> bool:
        w = self._w
        # Defer base-class processing back to the window's super().
        handled = w._super_process_event(event)

        # Handle all button presses in event-driven path (not polled per-frame)
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == w.btn_build_queue:
                if w.selected_planet:
                    logger.info(
                        f"Build Queue button clicked for planet: "
                        f"{w.selected_planet.name}"
                    )
                return True
            if event.ui_element == w.btn_navigate:
                self._navigate_to_selected()
                return True
            if event.ui_element == w.btn_apply:
                w.refresh_list()
                return True
            if event.ui_element == w.btn_all_types:
                self._set_all_filters(w.filter_types, 'types', True)
                return True
            if event.ui_element == w.btn_none_types:
                self._set_all_filters(w.filter_types, 'types', False)
                return True
            if event.ui_element == w.btn_all_owners:
                self._set_all_filters(w.filter_owner, 'owners', True)
                return True
            if event.ui_element == w.btn_none_owners:
                self._set_all_filters(w.filter_owner, 'owners', False)
                return True
            # FEAT-25: Effects All/None batch buttons → FilterState.YES / IGNORE
            if w.btn_all_effects is not None and event.ui_element == w.btn_all_effects:
                self._set_all_effects(FilterState.YES)
                return True
            if w.btn_none_effects is not None and event.ui_element == w.btn_none_effects:
                self._set_all_effects(FilterState.IGNORE)
                return True
            if event.ui_element == w.btn_save_preset:
                w._save_preset()
                return True
            # Check type toggle buttons
            for key, btn in w.ui_filters.get('types', {}).items():
                if event.ui_element == btn:
                    self._toggle_filter(w.filter_types, key, btn)
                    return True
            # Check owner toggle buttons
            for key, btn in w.ui_filters.get('owners', {}).items():
                if event.ui_element == btn:
                    self._toggle_filter(w.filter_owner, key, btn)
                    return True
            # FEAT-25: Effects tri-state radios
            for key, widget in w.ui_filters.get('effects', {}).items():
                new_state = widget.check_pressed(event.ui_element)
                if new_state is not None:
                    widget.set_state(new_state)
                    w.filter_effects[key] = new_state
                    w.refresh_list()
                    return True
            # Check column toggle buttons
            for col_id, btn in w.ui_filters.get('columns', {}).items():
                if event.ui_element == btn:
                    w._toggle_column(btn)
                    return True

        # Handle planet row clicks
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click
            mouse_pos = event.pos
            clicked_index = w.virtual_table.handle_click(mouse_pos)

            if clicked_index >= 0:
                planet = w.data_source.get_planet_at_index(clicked_index)
                if planet and planet != w.selected_planet:
                    logger.debug(f"Selecting planet: {planet.name}")
                    self._on_planet_selected(planet)
                return True  # Consume the event

        if event.type == UI_TEXT_ENTRY_FINISHED:
            # Check if it matches any of our range text boxes
            for key in ['gravity', 'temp', 'mass']:
                f = w.ui_filters[key]
                val = 0.0
                target_slider = None

                if event.ui_element == f['min_txt']:
                    target_slider = f['min']
                elif event.ui_element == f['max_txt']:
                    target_slider = f['max']

                if target_slider:
                    try:
                        val = float(event.text)
                        # Clamp to limits
                        limits = f['limits']
                        val = max(limits[0], min(limits[1], val))
                        target_slider.set_current_value(val)
                        w.refresh_list()
                    except ValueError:
                        pass  # Ignore invalid

        # Wheel handling — use VirtualTable's scrollbar
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if w.virtual_table._list_view_panel.get_abs_rect().collidepoint(m_pos):
                total_h = len(w.filtered_planets) * w.row_height
                if total_h > 0:
                    scroll_bar = w.virtual_table.scroll_bar
                    row_percent = w.row_height / total_h
                    current_pct = scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - scroll_bar.visible_percentage, new_pct))
                    scroll_bar.set_scroll_from_start_percentage(new_pct)
                    w.virtual_table.update_visible_rows()
                return True  # Consume event

        return handled

    # -----------------------------------------------------------------------
    # Filter button handlers
    # -----------------------------------------------------------------------

    def _set_all_filters(self, filter_dict, ui_key, enabled) -> None:
        """Set all filters in a category to enabled/disabled."""
        w = self._w
        for key, btn in w.ui_filters.get(ui_key, {}).items():
            filter_dict[key] = enabled
            label = getattr(btn, '_display_label', key)
            if enabled:
                btn.select()
                btn.set_text(f"[{label}]")
            else:
                btn.unselect()
                btn.set_text(f"{label}")
        w.refresh_list()

    def _set_all_effects(self, state: FilterState) -> None:
        """Set every Effects filter row to the same FilterState (FEAT-25)."""
        w = self._w
        for key, widget in w.ui_filters.get('effects', {}).items():
            w.filter_effects[key] = state
            widget.set_state(state)
        w.refresh_list()

    def _toggle_filter(self, filter_dict, key, btn) -> None:
        """Toggle a single filter in a category."""
        w = self._w
        state = not filter_dict[key]
        filter_dict[key] = state
        btn.select() if state else btn.unselect()
        label = getattr(btn, '_display_label', key)
        btn.set_text(f"[{label}]" if state else f"{label}")
        w.refresh_list()

    # -----------------------------------------------------------------------
    # Planet selection
    # -----------------------------------------------------------------------

    def _navigate_to_selected(self) -> None:
        """Navigate camera to the selected planet's system.

        PROJ-348 T5.3: route navigation through `controller.navigate_to`
        rather than calling `self.on_navigate_callback` directly. The
        controller owns the navigate-dispatch boundary; the window stays
        focused on widget concerns.
        """
        w = self._w
        if not w.selected_planet:
            return
        loc = getattr(
            w.selected_planet, '_cached_system_global_location', None
        )
        if loc and w.controller is not None:
            w.controller.navigate_to(loc)

    def _on_planet_selected(self, planet) -> None:
        """Handle planet selection - create/update detail panel."""
        w = self._w
        # Kill old panel if exists
        if w.planet_detail_panel:
            w.planet_detail_panel.kill()
            w.planet_detail_panel = None

        # Kill old button if exists
        if w.btn_build_queue:
            w.btn_build_queue.kill()
            w.btn_build_queue = None

        if planet is None:
            w.selected_planet = None
            return

        # Get portrait surface (use asset_resolver if available)
        portrait_surface = None
        if w.asset_resolver:
            portrait_surface = w.asset_resolver(planet)

        # Calculate panel position and dynamic height (right side of window)
        panel_x, panel_y, panel_height = self._detail_panel_geometry()

        # PROJ-292 H1: resolve the per-species demographic view for
        # colonized planets (delegates to controller, which gates on
        # owner_id + facade presence). Uncolonized planets and legacy
        # callers without a facade fall through to the pre-PROJ-289
        # rendering with view=None.
        view = self._resolve_demographic_view(planet)

        # Create planet report panel
        w.planet_detail_panel = PlanetReportPanel(
            manager=w.ui_manager,
            rect=pygame.Rect(panel_x, panel_y, w.detail_panel_width, panel_height),
            planet=planet,
            container=w,  # Window is the container
            portrait_surface=portrait_surface,
            show_complexes=False,  # Match strategy UI - no separate complexes column
            production_rates=compute_planet_production(planet, w._registries),
            empire=w.empire,  # PROJ-290
            race_registry=w._race_registry,  # PROJ-290
            view=view,  # PROJ-292 H1
        )

        # Add Build Queue button if player owns planet
        if planet.owner_id == w.empire.id:
            required_height = w.planet_detail_panel.get_height_required()
            btn_y = panel_y + min(panel_height, required_height) + 10
            w.btn_build_queue = UIButton(
                relative_rect=pygame.Rect(panel_x, btn_y, 200, 30),
                text="Open Build Yard",
                manager=w.ui_manager,
                container=w,
                object_id="#build_queue_btn_planet_list",
            )

        # Update selection tracking
        w.selected_planet = planet

    def _resolve_demographic_view(self, planet) -> Optional[Any]:
        """PROJ-292 H1: resolve per-species view for colonized planets.

        PROJ-348 T5.4: the legacy ``__new__``-bypass fallback was deleted.
        Bypass-init tests must wire a real ``PlanetListController`` (see
        ``tests/unit/ui/screens/test_planet_list_window.py:_make_planet_list_window``).
        """
        return self._w.controller.resolve_demographic_view(planet)

    def _detail_panel_geometry(self) -> tuple:
        """Calculate detail panel position and size relative to window."""
        w = self._w
        window_width = w.rect.width
        window_height = w.rect.height
        panel_x = window_width - w.detail_panel_width - 10
        panel_y = 60  # Below window title bar
        # Dynamic height: fill available space minus margins
        panel_height = max(450, window_height - panel_y - 80)
        return panel_x, panel_y, panel_height
