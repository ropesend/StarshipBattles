"""PROJ-309 Sub-phase 3.1 — RaceSetupRenderer.

Constructs ad-hoc pygame_gui modals at the screen level (FEAT-05
save-update dialog, PROJ-299 still-working dialog, PROJ-299 error
popup). Ship-preview-grid construction is delegated to
`ShipPreviewBuilder` (separate concern).

Per design §4 this module owns the modal-widget references so it can
kill them on close.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui

from game.ui.screens.race_setup.ship_preview import ShipPreviewBuilder

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen

logger = logging.getLogger(__name__)


class RaceSetupRenderer:
    """Modal construction + ship-preview grid.

    Holds references to widgets it constructs so it can kill them on
    close. Does NOT mutate `race_config`, panel state, or view-model
    state; those concerns live on Controller and ViewModel respectively.
    """

    def __init__(self, *, screen: "RaceSetupScreen") -> None:
        self._screen = screen

        # FEAT-05 save-update dialog widgets.
        self.save_update_dialog: Optional[pygame_gui.elements.UIWindow] = None
        self.btn_overwrite: Optional[pygame_gui.elements.UIButton] = None
        self.btn_save_new: Optional[pygame_gui.elements.UIButton] = None
        self.btn_save_cancel: Optional[pygame_gui.elements.UIButton] = None

        # PROJ-299 still-working dialog widgets.
        self.llm_dialog_window: Optional[pygame_gui.elements.UIWindow] = None
        self.llm_dialog_btn_keep: Optional[pygame_gui.elements.UIButton] = None
        self.llm_dialog_btn_stop: Optional[pygame_gui.elements.UIButton] = None
        self.llm_dialog_field: str = ""

        # PROJ-299 error popup widgets.
        self.llm_error_popup: Optional[pygame_gui.elements.UIWindow] = None
        self.llm_error_popup_btn_ok: Optional[pygame_gui.elements.UIButton] = None

        # Ship-preview construction is delegated to a dedicated builder.
        self._ship_preview = ShipPreviewBuilder(screen=screen)

    # ------------------------------------------------------------------
    # FEAT-05 save-update dialog
    # ------------------------------------------------------------------

    def show_save_update_dialog(self) -> None:
        """FEAT-05: Show dialog asking to overwrite or save as new species."""
        if self.save_update_dialog is not None:
            return  # Already showing

        screen = self._screen

        dialog_width = 400
        dialog_height = 180
        container = screen.get_container()
        cx = (container.get_size()[0] - dialog_width) // 2
        cy = (container.get_size()[1] - dialog_height) // 2

        self.save_update_dialog = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(cx, cy, dialog_width, dialog_height),
            manager=screen.ui_manager,
            window_display_title="Save Species",
            object_id="#save_update_dialog",
            resizable=False,
        )

        dialog_container = self.save_update_dialog.get_container()
        dw = dialog_container.get_size()[0]

        # Message label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, dw - 20, 50),
            text="This species was loaded from the library.",
            manager=screen.ui_manager,
            container=dialog_container,
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 40, dw - 20, 50),
            text="How would you like to save it?",
            manager=screen.ui_manager,
            container=dialog_container,
        )

        # Buttons
        btn_width = 110
        btn_height = 36
        btn_y = 95
        spacing = 15
        total_btn_width = btn_width * 3 + spacing * 2
        start_x = (dw - total_btn_width) // 2

        self.btn_overwrite = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, btn_y, btn_width, btn_height),
            text="Overwrite",
            manager=screen.ui_manager,
            container=dialog_container,
            object_id="#btn_overwrite",
        )

        self.btn_save_new = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + btn_width + spacing, btn_y, btn_width, btn_height),
            text="Save as New",
            manager=screen.ui_manager,
            container=dialog_container,
            object_id="#btn_save_new",
        )

        self.btn_save_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + 2 * (btn_width + spacing), btn_y, btn_width, btn_height),
            text="Cancel",
            manager=screen.ui_manager,
            container=dialog_container,
            object_id="#btn_save_cancel",
        )

    def close_save_update_dialog(self) -> None:
        """Kill + clear the FEAT-05 save-update dialog widgets."""
        if self.save_update_dialog is not None:
            self.save_update_dialog.kill()
        self.save_update_dialog = None
        self.btn_overwrite = None
        self.btn_save_new = None
        self.btn_save_cancel = None

    # ------------------------------------------------------------------
    # PROJ-299 still-working dialog
    # ------------------------------------------------------------------

    def show_llm_dialog(self, field: str, *, threshold: int) -> None:
        """Construct the still-working modal. Pattern mirrors `show_save_update_dialog`."""
        screen = self._screen
        self.llm_dialog_field = field
        # Centre within the screen's own container — same pattern used by
        # `show_save_update_dialog`. NOT `self.window_display_size`,
        # which doesn't exist on UIWindow.
        screen_w, screen_h = screen.get_container().get_size()
        dialog_w, dialog_h = 480, 180
        x = (screen_w - dialog_w) // 2
        y = (screen_h - dialog_h) // 2

        self.llm_dialog_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(x, y, dialog_w, dialog_h),
            manager=screen.ui_manager,
            window_display_title="Still working…",
            object_id="#llm_dialog",
        )
        container = self.llm_dialog_window.get_container()
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(15, 15, dialog_w - 60, 60),
            text=f"Generating {field} after {threshold} seconds. Keep waiting or stop?",
            manager=screen.ui_manager,
            container=container,
        )
        self.llm_dialog_btn_keep = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(15, 90, 200, 36),
            text="Keep Waiting",
            manager=screen.ui_manager,
            container=container,
        )
        self.llm_dialog_btn_stop = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(225, 90, 200, 36),
            text="Stop",
            manager=screen.ui_manager,
            container=container,
        )

    def close_llm_dialog(self) -> None:
        if self.llm_dialog_window is not None:
            self.llm_dialog_window.kill()
        self.llm_dialog_window = None
        self.llm_dialog_btn_keep = None
        self.llm_dialog_btn_stop = None
        self.llm_dialog_field = ""

    # ------------------------------------------------------------------
    # PROJ-299 per-error-type popup
    # ------------------------------------------------------------------

    def show_llm_error_popup(self, message: str) -> None:
        screen = self._screen
        # Same centring pattern as show_save_update_dialog — `get_container()`
        # returns the screen's UIPanel/Container; `.get_size()` is its (w, h).
        screen_w, screen_h = screen.get_container().get_size()
        dialog_w, dialog_h = 480, 160
        x = (screen_w - dialog_w) // 2
        y = (screen_h - dialog_h) // 2
        self.llm_error_popup = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(x, y, dialog_w, dialog_h),
            manager=screen.ui_manager,
            window_display_title="Generation failed",
            object_id="#llm_error_popup",
        )
        container = self.llm_error_popup.get_container()
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(15, 15, dialog_w - 60, 60),
            text=message,
            manager=screen.ui_manager,
            container=container,
        )
        self.llm_error_popup_btn_ok = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, 90, 120, 36),
            text="OK",
            manager=screen.ui_manager,
            container=container,
        )

    def close_llm_error_popup(self) -> None:
        if self.llm_error_popup is not None:
            self.llm_error_popup.kill()
        self.llm_error_popup = None
        self.llm_error_popup_btn_ok = None

    # ------------------------------------------------------------------
    # Ships-tab preview grid (delegated to ShipPreviewBuilder)
    # ------------------------------------------------------------------

    def refresh_ship_preview(self, theme_id: str) -> None:
        """Refresh the ship-preview grid for `theme_id`."""
        self._ship_preview.refresh(theme_id)
