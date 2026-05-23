"""Ship panel components for Combat Lab UI.

Provides ship display panels: simple, tabbed, and component panels.
"""
from __future__ import annotations

from typing import Any

import pygame

from game.ui.fonts import get_font
from game.ui.screens.test_lab import theme
from game.ui.widgets.scrollable_json_panel import ScrollableJsonPanel
from .component_dropdown import ComponentDropdown
import json


class ShipPanel:
    """Panel showing ship JSON only (full height like Test Details)."""

    def __init__(self, x, y, width, height, ship_info):
        """
        Initialize ship panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            ship_info: Dict with 'role', 'ship_data'
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ship_info = ship_info

        # Ship JSON viewer (full height)
        self.ship_viewer = ScrollableJsonPanel(
            x=x,
            y=y,
            width=width,
            height=height,
            title=f"Ship: {ship_info['role']}"
        )
        self.ship_viewer.set_json_with_diff(json.dumps(ship_info['ship_data']), {})

    def handle_event(self, event) -> bool:
        """Handle input events (scrolling)."""
        return self.ship_viewer.handle_event(event)

    def update(self) -> None:
        """No-op; reserved for interface consistency."""
        pass

    def draw(self, surface) -> None:
        """Draw the ship panel."""
        self.ship_viewer.draw(surface)


class TabbedShipPanel:
    """Panel showing multiple ships with tabs (for tests with 3+ ships)."""

    def __init__(self, x, y, width, height, ships_info):
        """
        Initialize tabbed ship panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            ships_info: List of dicts with 'role', 'ship_data'
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ships_info = ships_info
        self.selected_tab = 0

        # Fonts
        self.tab_font = get_font(12)
        self.header_font = get_font(16)

        # Colors
        self.bg_color = theme.BG_CONTENT
        self.border_color = theme.BORDER
        self.header_color = theme.TEXT_HEADER
        self.tab_color = theme.TAB_NORMAL
        self.tab_selected_color = theme.TAB_SELECTED
        self.tab_hover_color = theme.TAB_HOVER
        self.text_color = theme.TEXT

        # Tab dimensions
        self.header_height = 30
        self.tab_height = 28
        self.tab_margin = 5

        # Create JSON viewers for each ship
        viewer_y = y + self.header_height + self.tab_height + 5
        viewer_height = height - self.header_height - self.tab_height - 10
        self.viewers = []
        for ship_info in ships_info:
            viewer = ScrollableJsonPanel(
                x=x,
                y=viewer_y,
                width=width,
                height=viewer_height,
                title=f"Ship: {ship_info['role']}"
            )
            viewer.set_json_with_diff(json.dumps(ship_info['ship_data']), {})
            self.viewers.append(viewer)

        # Calculate tab widths
        self._calculate_tab_rects()

    def _calculate_tab_rects(self) -> None:
        """Calculate tab button rectangles."""
        self.tab_rects = []
        num_tabs = len(self.ships_info)
        tab_width = min(120, (self.width - 20) // num_tabs - self.tab_margin)

        for i, ship_info in enumerate(self.ships_info):
            tab_x = self.x + 10 + i * (tab_width + self.tab_margin)
            tab_y = self.y + self.header_height
            self.tab_rects.append(pygame.Rect(tab_x, tab_y, tab_width, self.tab_height))

    def handle_event(self, event) -> bool:
        """Handle input events (tab clicks, scrolling)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self.tab_rects):
                if rect.collidepoint(mx, my):
                    self.selected_tab = i
                    return True

        # Forward scroll events to the selected viewer
        if self.selected_tab < len(self.viewers):
            return self.viewers[self.selected_tab].handle_event(event)
        return False

    def update(self) -> None:
        """No-op; reserved for interface consistency."""
        pass

    def draw(self, surface) -> None:
        """Draw the tabbed ship panel."""
        # Draw background
        pygame.draw.rect(surface, self.bg_color,
                        (self.x, self.y, self.width, self.height), border_radius=5)
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2, border_radius=5)

        # Draw header
        header_text = self.header_font.render("SHIPS", True, self.header_color)
        surface.blit(header_text, (self.x + 10, self.y + 5))

        # Draw tabs
        mouse_pos = pygame.mouse.get_pos()
        for i, (rect, ship_info) in enumerate(zip(self.tab_rects, self.ships_info)):
            # Determine tab color
            if i == self.selected_tab:
                color = self.tab_selected_color
            elif rect.collidepoint(mouse_pos):
                color = self.tab_hover_color
            else:
                color = self.tab_color

            # Draw tab background
            pygame.draw.rect(surface, color, rect, border_radius=3)
            if i == self.selected_tab:
                pygame.draw.rect(surface, self.header_color, rect, 1, border_radius=3)

            # Draw tab text (truncated if needed)
            role = ship_info.get('role', f'Ship {i+1}')
            tab_text = role if len(role) <= 12 else role[:11] + "..."
            text_surf = self.tab_font.render(tab_text, True, self.text_color)
            text_x = rect.x + (rect.width - text_surf.get_width()) // 2
            text_y = rect.y + (rect.height - text_surf.get_height()) // 2
            surface.blit(text_surf, (text_x, text_y))

        # Draw selected ship's JSON viewer
        if self.selected_tab < len(self.viewers):
            self.viewers[self.selected_tab].draw(surface)

    def get_selected_ship_info(self) -> dict | None:
        """Get the currently selected ship's info."""
        if self.selected_tab < len(self.ships_info):
            return self.ships_info[self.selected_tab]
        return None


class ComponentPanel:
    """Panel showing component dropdown + component JSON (full height)."""

    def __init__(self, x, y, width, height, component_ids, load_component_callback):
        """
        Initialize component panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
            component_ids: List of component IDs
            load_component_callback: Function(component_id) -> Dict
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.load_component_callback = load_component_callback

        # Component dropdown at top
        dropdown_height = 40
        self.component_dropdown = ComponentDropdown(
            x=x + 10,
            y=y + 10,
            width=width - 20,
            height=dropdown_height,
            component_ids=component_ids,
            load_callback=load_component_callback
        )

        # Component JSON viewer below dropdown
        component_viewer_y = y + dropdown_height + 20
        component_viewer_height = height - dropdown_height - 30
        selected_comp_id = self.component_dropdown.get_selected_component_id()
        component_data = load_component_callback(selected_comp_id) if selected_comp_id else {}

        self.component_viewer = ScrollableJsonPanel(
            x=x,
            y=component_viewer_y,
            width=width,
            height=component_viewer_height,
            title="Component JSON"
        )
        self.component_viewer.set_json_with_diff(json.dumps(component_data) if component_data else None, {})

    def handle_event(self, event) -> bool:
        """Handle input events (scrolling, dropdown clicks)."""
        # Try dropdown first
        if self.component_dropdown.handle_click(event):
            # Selection changed - update component viewer
            selected_comp_id = self.component_dropdown.get_selected_component_id()
            if selected_comp_id:
                component_data = self.load_component_callback(selected_comp_id)
                if component_data:
                    self.component_viewer.set_json_with_diff(json.dumps(component_data), {})
            return True

        # Try scrolling on component viewer
        if self.component_viewer.handle_event(event):
            return True

        return False

    def update(self) -> None:
        """Update hover states."""
        self.component_dropdown.handle_hover()

    def draw(self, surface) -> None:
        """Draw the component panel."""
        self.component_viewer.draw(surface)
        self.component_dropdown.draw(surface)  # Draw dropdown last so it's on top when expanded
