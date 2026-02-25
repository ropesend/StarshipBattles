"""Component dropdown selector for Combat Lab UI.

Provides a dropdown menu for selecting ship components.
"""

import pygame

from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme


class ComponentDropdown:
    """Dropdown menu for selecting components from a ship's component list."""

    def __init__(self, x, y, width, height, component_ids, load_callback):
        """
        Initialize component dropdown.

        Args:
            x, y: Top-left position
            width, height: Dropdown dimensions (height is for closed state)
            component_ids: List of component IDs to choose from
            load_callback: Function(component_id) -> Dict, called when selection changes
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.component_ids = component_ids if component_ids else ["No components"]
        self.selected_index = 0
        self.is_expanded = False
        self.load_callback = load_callback

        # Fonts & Colors
        self.font = get_font(16)
        self.bg_color = theme.TAG_NORMAL_BG  # (50, 50, 60)
        self.selected_bg_color = (70, 70, 85)  # Unique
        self.hover_bg_color = (60, 60, 75)  # Unique
        self.text_color = theme.TEXT_WHITE
        self.border_color = theme.BORDER_ACTIVE

        self.hovered_index = -1

    def handle_click(self, event):
        """Handle mouse clicks on dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Click on closed dropdown header
            if not self.is_expanded:
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = True
                    return True

            # Click on expanded dropdown
            else:
                # Click on header closes it
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y <= mouse_y <= self.y + self.height):
                    self.is_expanded = False
                    return True

                # Click on option
                dropdown_height = self.height * len(self.component_ids)
                if (self.x <= mouse_x <= self.x + self.width and
                    self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):

                    option_index = (mouse_y - self.y - self.height) // self.height
                    if 0 <= option_index < len(self.component_ids):
                        self.selected_index = option_index
                        self.is_expanded = False
                        return True

                # Click outside closes dropdown
                else:
                    self.is_expanded = False
                    return True

        return False

    def handle_hover(self):
        """Track hovered option for visual feedback."""
        if not self.is_expanded:
            self.hovered_index = -1
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dropdown_height = self.height * len(self.component_ids)

        if (self.x <= mouse_x <= self.x + self.width and
            self.y + self.height <= mouse_y <= self.y + self.height + dropdown_height):
            self.hovered_index = (mouse_y - self.y - self.height) // self.height
        else:
            self.hovered_index = -1

    def get_selected_component_id(self):
        """Get currently selected component ID."""
        if 0 <= self.selected_index < len(self.component_ids):
            comp_id = self.component_ids[self.selected_index]
            return comp_id if comp_id != "No components" else None
        return None

    def draw(self, surface):
        """Draw the dropdown menu."""
        # Draw closed header
        header_rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, header_rect)
        pygame.draw.rect(surface, self.border_color, header_rect, 2)

        # Display selected component ID
        selected_text = self.component_ids[self.selected_index] if self.component_ids else "No components"
        text_surface = self.font.render(selected_text, True, self.text_color)
        text_x = self.x + 10
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

        # Draw dropdown arrow
        arrow_x = self.x + self.width - 25
        arrow_y = self.y + self.height // 2
        arrow_points = [
            (arrow_x, arrow_y - 5),
            (arrow_x + 10, arrow_y - 5),
            (arrow_x + 5, arrow_y + 5)
        ] if not self.is_expanded else [
            (arrow_x, arrow_y + 5),
            (arrow_x + 10, arrow_y + 5),
            (arrow_x + 5, arrow_y - 5)
        ]
        pygame.draw.polygon(surface, self.text_color, arrow_points)

        # Draw expanded options
        if self.is_expanded:
            for i, comp_id in enumerate(self.component_ids):
                option_y = self.y + self.height + (i * self.height)
                option_rect = (self.x, option_y, self.width, self.height)

                # Background color
                if i == self.hovered_index:
                    bg_color = self.hover_bg_color
                elif i == self.selected_index:
                    bg_color = self.selected_bg_color
                else:
                    bg_color = self.bg_color

                pygame.draw.rect(surface, bg_color, option_rect)
                pygame.draw.rect(surface, self.border_color, option_rect, 1)

                # Option text
                option_surface = self.font.render(comp_id, True, self.text_color)
                option_x = self.x + 10
                option_text_y = option_y + (self.height - option_surface.get_height()) // 2
                surface.blit(option_surface, (option_x, option_text_y))
