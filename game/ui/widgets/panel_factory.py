"""Factory utilities for creating common UI panel patterns.

PROJ-204 Phase 5: Consolidates duplicated panel+title creation pattern.
"""
import pygame
from pygame_gui.elements import UIPanel, UILabel


class PanelFactory:
    """Factory class for creating common UI panel configurations.

    Consolidates the repeated pattern of creating a panel with a title label
    that appears across multiple builder UI components.
    """

    @staticmethod
    def create_titled_panel(rect, manager, title, object_id):
        """Create a panel with an optional title label.

        Args:
            rect: pygame.Rect defining panel position and size.
            manager: pygame_gui.UIManager for element creation.
            title: Title text for the panel header. If None, no label is created.
            object_id: Object ID string for the panel (e.g., '#right_panel').

        Returns:
            Tuple of (panel, label) where label is None if title was None.
        """
        panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id=object_id
        )

        label = None
        if title:
            label = UILabel(
                relative_rect=pygame.Rect(10, 5, 200, 30),
                text=title,
                manager=manager,
                container=panel
            )

        return panel, label
