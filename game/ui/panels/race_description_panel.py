"""
Race Description Panel - Text description fields for races.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

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


class RaceDescriptionPanel:
    """
    Panel for configuring race description text fields.

    Creates and manages text boxes for biological and sociological
    descriptions with character count tracking.
    """

    # Maximum character length for descriptions
    MAX_LENGTH = 500

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
            relative_rect=pygame.Rect(panel_width - 80, y, 80, 25),
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
            relative_rect=pygame.Rect(panel_width - 80, y, 80, 25),
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
