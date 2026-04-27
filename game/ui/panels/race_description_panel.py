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
import logging
import pygame
import pygame_gui
from typing import Optional, TYPE_CHECKING

from game.ui.utils import create_section_header

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.services.race_description_llm_controller import (
        RaceDescriptionLLMController,
    )

logger = logging.getLogger(__name__)


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

        Layout — mirrors `_create_content()`'s y-coordinate math so the
        per-field buttons sit in their own header row (NOT both at y=5
        — that overlap was the v1 bug):

            y=5        : "Biological Description:" header + bio buttons (right) + bio_char_label (far right)
            y=33       : bio_text_box (height = text_area_height)
            y=33+TAH   : lbl_bio_status (slim status label in the 15px gap)
            y=33+TAH+15: "Sociological Description:" header + socio buttons + socio_char_label
            ...etc

        where TAH = text_area_height = (panel_height - 100) // 2.
        """
        self._controller = controller

        panel_width = self.panel.get_relative_rect().width - 20
        panel_height = self.panel.get_relative_rect().height - 20
        text_area_height = (panel_height - 100) // 2

        # Header rows: same y math as _create_content().
        bio_row_y = 5
        socio_row_y = 5 + 28 + text_area_height + 15

        # Status labels live in the gap below each text box (the 15px gap
        # between bio_text_box and the socio header — this is the
        # "below the text box, not inside it" placement from design.md).
        bio_status_y = 33 + text_area_height + 1  # 1px below bio_text_box
        socio_status_y = socio_row_y + 28 + text_area_height + 1

        # Buttons: 3 per row, 80px each with 4px gaps. Anchored to the
        # LEFT of the char_label (which lives at panel_width-110, w=110).
        btn_w = 80
        btn_h = 25
        gap = 4
        char_label_w = 110
        buttons_total_w = 3 * btn_w + 2 * gap
        buttons_x = panel_width - char_label_w - 10 - buttons_total_w

        def _btn_x(idx: int) -> int:
            return buttons_x + idx * (btn_w + gap)

        # ---------- Bio row ----------
        self.btn_generate_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(0), bio_row_y, btn_w, btn_h),
            text="Generate", manager=self.ui_manager, container=self.panel,
            object_id="#btn_generate_bio",
        )
        self.btn_cancel_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(1), bio_row_y, btn_w, btn_h),
            text="Cancel", manager=self.ui_manager, container=self.panel,
            object_id="#btn_cancel_bio",
        )
        self.btn_re_roll_bio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(2), bio_row_y, btn_w, btn_h),
            text="Re-roll", manager=self.ui_manager, container=self.panel,
            object_id="#btn_re_roll_bio",
        )

        # ---------- Socio row ----------
        self.btn_generate_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(0), socio_row_y, btn_w, btn_h),
            text="Generate", manager=self.ui_manager, container=self.panel,
            object_id="#btn_generate_socio",
        )
        self.btn_cancel_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(1), socio_row_y, btn_w, btn_h),
            text="Cancel", manager=self.ui_manager, container=self.panel,
            object_id="#btn_cancel_socio",
        )
        self.btn_re_roll_socio = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(_btn_x(2), socio_row_y, btn_w, btn_h),
            text="Re-roll", manager=self.ui_manager, container=self.panel,
            object_id="#btn_re_roll_socio",
        )

        # ---------- Status labels (below each text box) ----------
        self.lbl_bio_status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, bio_status_y, panel_width - 20, 13),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#lbl_bio_status",
        )
        self.lbl_socio_status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, socio_status_y, panel_width - 20, 13),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#lbl_socio_status",
        )

    def set_state(self, controller: 'RaceDescriptionLLMController') -> None:
        """Reconcile widget visibility / labels / text-box lock with controller state.

        Called from the screen's `on_change` callback whenever the
        controller's state transitions. On DONE this ALSO pushes the
        freshly-generated text from `race_config.bio_description` /
        `socio_description` into the corresponding text box — without
        this, the LLM result lands in the data model but never reaches
        the UI.
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
            race_field_attr="bio_description",
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
            race_field_attr="socio_description",
            FieldStatus=FieldStatus,
        )

    def _apply_field_state(
        self, *, status, elapsed, error, label_prefix,
        text_box, btn_generate, btn_cancel, btn_re_roll, lbl_status,
        race_field_attr, FieldStatus,
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
            # Push the freshly-generated text into the UI. Controller
            # has written to race_config; we reconcile the text box
            # from there. Guarded by an equality check to avoid a
            # repaint storm when set_state() is called repeatedly.
            new_text = getattr(self.race_config, race_field_attr) or ""
            current_text = text_box.get_text()
            if current_text != new_text:
                text_box.set_text(new_text)
                # pygame_gui UITextEntryBox sometimes doesn't re-render
                # after set_text if the widget was just enable()'d in the
                # same frame — force a layout rebuild to be safe.
                if hasattr(text_box, "rebuild"):
                    try:
                        text_box.rebuild()
                    except Exception as e:  # Intentional broad catch: rebuild is defensive
                        logger.warning(
                            "RaceDescriptionPanel: text_box.rebuild() failed: %s", e
                        )
                self.update_char_counts()
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
