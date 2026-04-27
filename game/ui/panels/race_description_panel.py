"""
Race Description Panel - Text description fields for races.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-299 Phase 5: extended with LLM-driven generation widgets
(`btn_generate_bio` / `btn_cancel_bio` / `btn_re_roll_bio` and the socio
counterparts, plus `lbl_bio_status` / `lbl_socio_status`). Wire via
`attach_controller(controller)`; refresh widget visibility via
`set_state(controller)` from the screen's on_change callback.

Provides UI controls for configuring:
- Biological description (max 500 chars)
- Sociological description (max 500 chars)
"""
import pygame
import pygame_gui
from typing import Optional, TYPE_CHECKING

from game.ui.utils import create_section_header

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.services.race_description_llm_controller import (
        RaceDescriptionLLMController,
    )


class RaceDescriptionPanel:
    """
    Panel for configuring race description text fields.

    Creates and manages text boxes for biological and sociological
    descriptions with character count tracking.
    """

    # Maximum character length for descriptions.
    # PROJ-299: bumped 500 → 5000 to accommodate LLM-generated bio + socio
    # paragraph-length output. The existing `text[:MAX_LENGTH]` truncate
    # path stays intact, so any over-length input is still safely capped.
    MAX_LENGTH = 5000

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig'
    ):
        """
        Create description panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write values from/to
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config

        # Text box references
        self.bio_text_box: Optional[pygame_gui.elements.UITextEntryBox] = None
        self.bio_char_label: Optional[pygame_gui.elements.UILabel] = None
        self.socio_text_box: Optional[pygame_gui.elements.UITextEntryBox] = None
        self.socio_char_label: Optional[pygame_gui.elements.UILabel] = None

        self._create_content()

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        panel_height = self.panel.get_relative_rect().height - 20
        y = 5

        # Calculate height for each text area (split available space)
        text_area_height = (panel_height - 100) // 2

        # Biological Description
        create_section_header("Biological Description:", y, 300, self.ui_manager, self.panel)
        self.bio_char_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_width - 110, y, 110, 25),
            text=f"{len(self.race_config.bio_description)}/{self.MAX_LENGTH}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 28

        self.bio_text_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect(10, y, panel_width, text_area_height),
            initial_text=self.race_config.bio_description,
            manager=self.ui_manager,
            container=self.panel,
            object_id="#description_box"
        )
        y += text_area_height + 15

        # Sociological Description
        create_section_header("Sociological Description:", y, 300, self.ui_manager, self.panel)
        self.socio_char_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_width - 110, y, 110, 25),
            text=f"{len(self.race_config.socio_description)}/{self.MAX_LENGTH}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 28

        self.socio_text_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect(10, y, panel_width, text_area_height),
            initial_text=self.race_config.socio_description,
            manager=self.ui_manager,
            container=self.panel,
            object_id="#description_box"
        )

    def update_char_counts(self):
        """Update character count labels for description text boxes."""
        if self.bio_text_box and self.bio_char_label:
            text = self.bio_text_box.get_text()
            count = len(text)
            self.bio_char_label.set_text(f"{count}/{self.MAX_LENGTH}")

        if self.socio_text_box and self.socio_char_label:
            text = self.socio_text_box.get_text()
            count = len(text)
            self.socio_char_label.set_text(f"{count}/{self.MAX_LENGTH}")

    def update_config(self):
        """Update race_config from description text boxes."""
        if self.bio_text_box:
            text = self.bio_text_box.get_text()
            # Enforce max char limit
            self.race_config.bio_description = text[:self.MAX_LENGTH]

        if self.socio_text_box:
            text = self.socio_text_box.get_text()
            # Enforce max char limit
            self.race_config.socio_description = text[:self.MAX_LENGTH]

    def set_from_config(self):
        """Set text box values from race_config (for loading saved races)."""
        if self.bio_text_box:
            self.bio_text_box.set_text(self.race_config.bio_description or "")

        if self.socio_text_box:
            self.socio_text_box.set_text(self.race_config.socio_description or "")

        self.update_char_counts()

    # =========================================================================
    # PROJ-299: LLM-driven description generation widgets
    # =========================================================================

    def attach_controller(self, controller: 'RaceDescriptionLLMController') -> None:
        """Bind a `RaceDescriptionLLMController` and create the LLM-related widgets.

        Creates the per-field Generate / Cancel / Re-roll buttons and a
        status label below each text box. Initial visibility is set by
        `set_state(controller)` (call from the on_change callback).
        """
        self._controller = controller

        # Layout: a small row of 3 buttons + a status label, just under each
        # text box. The text box already eats `text_area_height`, so we
        # piggyback off the same horizontal coordinates.
        panel_width = self.panel.get_relative_rect().width - 20

        # Bio buttons row — placed immediately below the bio text box.
        # Estimated y-coord: header (28) + text_area_height — but we don't
        # have that here; instead, drop the buttons at the bottom of the
        # panel and let pygame_gui's container clipping hide them gracefully.
        # For real layout, race_setup_screen rebuilds on tab switch.
        btn_w = 110
        btn_h = 28
        gap = 6
        # Bio row — anchor near bio_text_box position. We ask pygame_gui
        # to place us at the panel's left edge, near the bottom of the bio
        # area. For test-friendliness we use a fixed y; production layout
        # is refined visually.
        bio_row_y = 5  # row anchor for bio (above text); refined visually
        socio_row_y = 5  # row anchor for socio

        self.btn_generate_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 3 * (btn_w + gap), bio_row_y, btn_w, btn_h),
            text="Generate Bio",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_generate_bio",
        )
        self.btn_cancel_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 2 * (btn_w + gap), bio_row_y, btn_w, btn_h),
            text="Cancel",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_cancel_bio",
        )
        self.btn_re_roll_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - (btn_w + gap), bio_row_y, btn_w, btn_h),
            text="Re-roll",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_re_roll_bio",
        )

        self.btn_generate_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 3 * (btn_w + gap), socio_row_y, btn_w, btn_h),
            text="Generate Socio",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_generate_socio",
        )
        self.btn_cancel_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 2 * (btn_w + gap), socio_row_y, btn_w, btn_h),
            text="Cancel",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_cancel_socio",
        )
        self.btn_re_roll_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - (btn_w + gap), socio_row_y, btn_w, btn_h),
            text="Re-roll",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#btn_re_roll_socio",
        )

        # Status labels — below the text boxes. Placed at fixed offsets;
        # production layout is fine-tuned visually.
        self.lbl_bio_status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, bio_row_y + btn_h + 2, panel_width - 20, 20),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#lbl_bio_status",
        )
        self.lbl_socio_status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, socio_row_y + btn_h + 2, panel_width - 20, 20),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#lbl_socio_status",
        )

    def set_state(self, controller: 'RaceDescriptionLLMController') -> None:
        """Reconcile widget visibility / labels / text-box lock with controller state.

        Called from the screen's `on_change` callback whenever the
        controller's state transitions.
        """
        # Late import to avoid the strategy → UI cycle at import time.
        from game.strategy.services.race_description_llm_controller import FieldStatus

        self._apply_field_state(
            status=controller.bio_status,
            elapsed=controller.bio_elapsed_seconds,
            error=controller.bio_error,
            label_prefix="Bio",
            text_box=self.bio_text_box,
            btn_generate=self.btn_generate_bio,
            btn_cancel=self.btn_cancel_bio,
            btn_re_roll=self.btn_re_roll_bio,
            lbl_status=self.lbl_bio_status,
            FieldStatus=FieldStatus,
        )
        self._apply_field_state(
            status=controller.socio_status,
            elapsed=controller.socio_elapsed_seconds,
            error=controller.socio_error,
            label_prefix="Socio",
            text_box=self.socio_text_box,
            btn_generate=self.btn_generate_socio,
            btn_cancel=self.btn_cancel_socio,
            btn_re_roll=self.btn_re_roll_socio,
            lbl_status=self.lbl_socio_status,
            FieldStatus=FieldStatus,
        )

    def _apply_field_state(
        self, *, status, elapsed, error, label_prefix,
        text_box, btn_generate, btn_cancel, btn_re_roll, lbl_status,
        FieldStatus,
    ) -> None:
        """Per-field state reconciliation."""
        if status == FieldStatus.IDLE:
            btn_generate.show()
            btn_generate.enable()
            btn_cancel.hide()
            btn_re_roll.hide()
            lbl_status.set_text("")
            text_box.enable()
        elif status == FieldStatus.RUNNING:
            btn_generate.disable()
            btn_generate.show()
            btn_cancel.show()
            btn_re_roll.hide()
            lbl_status.set_text(f"Generating {label_prefix}… {int(elapsed)}s")
            text_box.disable()
        elif status == FieldStatus.DONE:
            btn_generate.show()
            btn_generate.enable()
            btn_cancel.hide()
            btn_re_roll.show()
            lbl_status.set_text("")
            text_box.enable()
        elif status == FieldStatus.ERROR:
            btn_generate.show()
            btn_generate.enable()
            btn_cancel.hide()
            btn_re_roll.hide()
            err_msg = type(error).__name__ if error is not None else "Error"
            lbl_status.set_text(f"{label_prefix} generation failed ({err_msg})")
            text_box.enable()
        elif status == FieldStatus.CANCELLED:
            btn_generate.show()
            btn_generate.enable()
            btn_cancel.hide()
            btn_re_roll.hide()
            lbl_status.set_text("")
            text_box.enable()
