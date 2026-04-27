"""PROJ-309 Sub-phase 3.1 — RaceSetupInputHandler.

Routes pygame_gui events to controller / panel callbacks. Owns the
giant switch from the original `RaceSetupScreen.process_event`.

Per design §5: tab buttons, save-update dialog buttons, LLM dialog
buttons, LLM error popup OK, description-tab LLM buttons, main nav
buttons, gallery clicks, dropdowns, sliders, text-entry events.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen


class RaceSetupInputHandler:
    """Pygame-event → handler dispatch for `RaceSetupScreen`.

    Returns a bool indicating whether the event was handled, matching
    the `process_event` contract on `pygame_gui.elements.UIWindow`."""

    def __init__(self, *, screen: "RaceSetupScreen") -> None:
        self._screen = screen

    def handle(self, event: pygame.event.Event, *, super_handled: bool) -> bool:
        """Dispatch `event` to the right callback."""
        screen = self._screen
        controller = screen._controller
        renderer = screen._renderer
        description_controller = controller.description_controller

        handled = super_handled

        # PROJ-299: 30s/90s "still working" dialog buttons.
        if event.type == pygame_gui.UI_BUTTON_PRESSED and renderer.llm_dialog_window is not None:
            if event.ui_element == renderer.llm_dialog_btn_keep:
                renderer.close_llm_dialog()
                return True
            if event.ui_element == renderer.llm_dialog_btn_stop:
                if description_controller is not None:
                    description_controller.cancel_all()
                renderer.close_llm_dialog()
                return True

        # PROJ-299: error-popup OK button.
        if event.type == pygame_gui.UI_BUTTON_PRESSED and renderer.llm_error_popup is not None:
            if event.ui_element == renderer.llm_error_popup_btn_ok:
                renderer.close_llm_error_popup()
                return True

        # PROJ-299: description-tab LLM buttons. Routed early so they take
        # precedence over the catch-all gallery/randomize handlers below.
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and description_controller is not None
            and screen._description_panel is not None
        ):
            d = screen._description_panel
            if event.ui_element == d.btn_generate_bio:
                description_controller.generate_bio()
                return True
            if event.ui_element == d.btn_cancel_bio:
                description_controller.cancel_bio()
                return True
            if event.ui_element == d.btn_re_roll_bio:
                description_controller.re_roll_bio()
                return True
            if event.ui_element == d.btn_generate_socio:
                description_controller.generate_socio()
                return True
            if event.ui_element == d.btn_cancel_socio:
                description_controller.cancel_socio()
                return True
            if event.ui_element == d.btn_re_roll_socio:
                description_controller.re_roll_socio()
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Tab buttons first.
            for btn in screen.tab_buttons:
                if event.ui_element == btn:
                    screen._show_step(btn.tab_index)
                    handled = True
                    break

            # FEAT-05: Save/Update dialog buttons.
            if not handled and renderer.save_update_dialog is not None:
                if event.ui_element == renderer.btn_overwrite:
                    controller.on_overwrite_save()
                    handled = True
                elif event.ui_element == renderer.btn_save_new:
                    controller.on_save_as_new()
                    handled = True
                elif event.ui_element == renderer.btn_save_cancel:
                    controller.on_save_dialog_cancel()
                    handled = True

            if not handled:
                if event.ui_element == screen.btn_cancel:
                    controller.on_cancel()
                    handled = True
                elif event.ui_element == screen.btn_save:
                    controller.on_save()
                    handled = True
                elif screen.btn_load and event.ui_element == screen.btn_load:
                    controller.on_load_race()
                    handled = True
                elif event.ui_element == screen.btn_randomize:
                    controller.on_randomize()
                    handled = True
                elif (
                    getattr(screen, "btn_randomize_all", None) is not None
                    and event.ui_element == screen.btn_randomize_all
                ):
                    controller.randomize_all()
                    handled = True
                else:
                    if screen._flag_gallery and screen._flag_gallery.handle_button_click(event.ui_element):
                        handled = True
                    if not handled:
                        if screen._portrait_gallery and screen._portrait_gallery.handle_button_click(event.ui_element):
                            handled = True
                    if not handled:
                        if screen._theme_gallery and screen._theme_gallery.handle_button_click(event.ui_element):
                            handled = True

        # PROJ-66 Phase 6: dropdown changes (identity panel).
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if screen._identity_panel:
                screen._identity_panel.handle_event(event)
                screen._identity_panel.update_config()
            if screen._environment_panel:
                screen._environment_panel.handle_dropdown_change(event)
            handled = True

        # Slider changes.
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # PROJ-283 Phase 5 / PROJ-285 crash fix:
            # update_labels refreshes per-row value/tolerance/cost labels and
            # re-renders the points-remaining header (via
            # PreferenceRow.refresh_from_sliders -> _on_row_change);
            # update_config writes slider values back into
            # race_config.preferences + base_reproduction_rate / base_happiness.
            if screen._environment_panel:
                screen._environment_panel.update_labels()
                screen._environment_panel.update_config()
            if screen._aptitudes_panel:
                screen._aptitudes_panel.update_config()
                screen._aptitudes_panel.update_labels()
                screen._aptitudes_panel.update_budget_display()
            handled = True

        # Text-entry changes.
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if screen._identity_panel:
                screen._identity_panel.handle_event(event)
                screen._identity_panel.update_config()

            if screen._description_panel:
                desc_text_boxes = (
                    screen._description_panel.bio_text_box,
                    screen._description_panel.socio_text_box,
                )
                if event.ui_element in desc_text_boxes:
                    controller.update_description_char_counts()
                    controller.update_descriptions_from_text()
            handled = True

        return handled
