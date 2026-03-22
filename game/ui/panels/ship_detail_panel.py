"""
Ship Detail Panel - Displays detailed ship information with damage tracking.

PROJ-03 Phase 4: Wraps DesignReportPanel for ShipInstance display with
component damage visualization.

Cross-layer imports (acceptable for UI display):
- ShipInstance: TYPE_CHECKING - used for type hints only
- LayerType: Runtime - iterates ship layers for component display
"""
from __future__ import annotations

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIScrollingContainer, UIImage
from typing import Dict, Optional, Tuple, List, TYPE_CHECKING

from game.core.constants import LayerType, ResourceType  # Canonical location for LayerType
from game.ui.assets import ShipThemeManager
from game.ui.colors import HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, HP_DESTROYED, BAR_BG, BAR_BORDER

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


def get_damage_color(hp_percentage: float) -> Tuple[int, int, int]:
    """
    Get color representing damage level.

    Args:
        hp_percentage: HP as fraction 0.0-1.0

    Returns:
        RGB tuple for damage visualization:
        - Green for >75%
        - Yellow for 50-75%
        - Red for 1-50%
        - Gray for 0% (destroyed)
    """
    if hp_percentage <= 0:
        return HP_DESTROYED
    elif hp_percentage < 0.5:
        return HP_CRITICAL
    elif hp_percentage < 0.75:
        return HP_DAMAGED
    else:
        return HP_HEALTHY


class ShipDetailPanel:
    """
    Panel displaying detailed ship information with damage tracking.

    Designed to work with ShipInstance from the strategy layer,
    showing current HP/resources vs max, and component damage.
    """

    def __init__(self, manager, rect: pygame.Rect, container=None,
                 on_remove_ship=None):
        """
        Initialize ship detail panel.

        Args:
            manager: pygame_gui UIManager
            rect: Panel dimensions and position
            container: Optional parent container
            on_remove_ship: Optional callback(ShipInstance) when remove button clicked
        """
        self.manager = manager
        self.rect = rect
        self.container = container
        self.current_ship: Optional[ShipInstance] = None
        self.on_remove_ship = on_remove_ship

        # Layer collapse state
        self.expanded_layers: Dict[str, bool] = {
            'HULL': True,
            'CORE': True,
            'INNER': False,
            'OUTER': False,
            'ARMOR': True,
        }

        # UI elements
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # Scrolling container for content
        content_rect = pygame.Rect(0, 0, rect.width - 10, rect.height - 10)
        self.scroll_container = UIScrollingContainer(
            relative_rect=content_rect,
            manager=manager,
            container=self.panel
        )

        # Dynamic UI elements
        self.ui_elements: List = []
        self.layer_buttons: Dict[str, UIButton] = {}
        self.btn_remove: Optional[UIButton] = None

        # Show placeholder initially
        self._show_placeholder()

    def _show_placeholder(self):
        """Show placeholder when no ship selected."""
        self._clear_elements()

        placeholder = UILabel(
            relative_rect=pygame.Rect(10, 10, self.rect.width - 40, 30),
            text="Select a ship to view details",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(placeholder)

    def _clear_elements(self):
        """Clear all dynamic UI elements."""
        for element in self.ui_elements:
            element.kill()
        self.ui_elements.clear()
        self.layer_buttons.clear()

    def _get_scaled_image(self, raw_surf: Optional[pygame.Surface], target_size: int) -> pygame.Surface:
        """
        Scale an image to fit within a square target size while preserving aspect ratio.

        Args:
            raw_surf: Source surface, or None for placeholder
            target_size: Target width/height in pixels

        Returns:
            Scaled surface centered on a target_size x target_size background
        """
        result = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        result.fill(BAR_BG)  # Dark background

        if raw_surf:
            w, h = raw_surf.get_size()
            scale = min(target_size / w, target_size / h) * 0.9  # 90% to leave margin
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = pygame.transform.smoothscale(raw_surf, (new_w, new_h))

            # Center on result
            x_off = (target_size - new_w) // 2
            y_off = (target_size - new_h) // 2
            result.blit(scaled, (x_off, y_off))
        else:
            # Draw placeholder icon
            pygame.draw.rect(result, BAR_BORDER, (10, 10, target_size - 20, target_size - 20), 2)
            # Simple ship silhouette
            center = target_size // 2
            pygame.draw.polygon(result, BAR_BORDER, [
                (center, 20),
                (center + 30, target_size - 30),
                (center - 30, target_size - 30)
            ])

        return result

    def update_ship(self, ship_instance: Optional[ShipInstance]):
        """
        Update display for a ship instance.

        Args:
            ship_instance: ShipInstance to display, or None to show placeholder
        """
        self.current_ship = ship_instance

        if ship_instance is None:
            self._show_placeholder()
            return

        self._clear_elements()
        self._build_ship_display(ship_instance)

    def _build_ship_display(self, ship: ShipInstance):
        """Build the full ship display."""
        y = 10
        width = self.rect.width - 40

        # --- Ship Images (Portrait + Top-Down) ---
        image_size = 120
        image_spacing = 10
        total_images_width = image_size * 2 + image_spacing
        images_x = (self.rect.width - total_images_width) // 2 - 10  # Center the images

        # Get theme and ship class
        theme_id = ship.design_data.get('theme_id', 'Federation')
        ship_class = ship.design_data.get('ship_class', 'Unknown')
        theme_mgr = ShipThemeManager.instance()

        # Portrait image (left)
        portrait_surf = self._get_scaled_image(
            theme_mgr.get_portrait_image(theme_id, ship_class),
            image_size
        )
        portrait_img = UIImage(
            relative_rect=pygame.Rect(images_x, y, image_size, image_size),
            image_surface=portrait_surf,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(portrait_img)

        # Top-down image (right)
        topdown_surf = self._get_scaled_image(
            theme_mgr.load_image(theme_id, ship_class),
            image_size
        )
        topdown_img = UIImage(
            relative_rect=pygame.Rect(images_x + image_size + image_spacing, y, image_size, image_size),
            image_surface=topdown_surf,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(topdown_img)

        y += image_size + 10

        # --- Header ---
        display_id = ship.get_display_id() or ship.instance_id[:8]
        header = UILabel(
            relative_rect=pygame.Rect(10, y, width, 30),
            text=display_id,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(header)
        y += 35

        # Ship name (if different from design)
        design_name = ship.design_data.get('name', ship.design_id)
        if ship.name != design_name:
            name_label = UILabel(
                relative_rect=pygame.Rect(10, y, width, 25),
                text=f'"{ship.name}"',
                manager=self.manager,
                container=self.scroll_container
            )
            self.ui_elements.append(name_label)
            y += 28

        # --- Status Section ---
        y = self._add_section_header("STATUS", 10, y, width)

        status_text = ship.get_status_text()
        hp_display = ship.get_hp_display()
        hp_pct = ship.get_hp_percentage()
        hp_color = get_damage_color(hp_pct)

        status_label = UILabel(
            relative_rect=pygame.Rect(10, y, width, 25),
            text=f"Status: {status_text}",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(status_label)
        y += 25

        hp_label = UILabel(
            relative_rect=pygame.Rect(10, y, width, 25),
            text=f"HP: {hp_display} ({hp_pct * 100:.0f}%)",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(hp_label)
        y += 30

        # --- Resources Section ---
        y = self._add_section_header("RESOURCES", 10, y, width)

        for resource in [ResourceType.FUEL, ResourceType.ENERGY, ResourceType.AMMO]:
            display = ship.get_resource_display(resource)
            if display != "N/A":
                pct = ship.get_resource_percentage(resource)
                label = UILabel(
                    relative_rect=pygame.Rect(10, y, width, 22),
                    text=f"{resource.capitalize()}: {display} ({pct * 100:.0f}%)",
                    manager=self.manager,
                    container=self.scroll_container
                )
                self.ui_elements.append(label)
                y += 24
        y += 5

        # --- Component Damage Section ---
        damage_count = ship.get_damaged_component_count()
        if damage_count > 0:
            y = self._add_section_header(f"COMPONENT DAMAGE ({damage_count})", 10, y, width)
            y = self._build_damage_section(ship, 10, y, width)

        # --- Combat Stats Section ---
        y = self._add_section_header("COMBAT RECORD", 10, y, width)

        stats_text = [
            f"Battles Survived: {ship.battles_survived}",
            f"Kills: {ship.kills}",
            f"Experience: {ship.experience}",
        ]
        for text in stats_text:
            label = UILabel(
                relative_rect=pygame.Rect(10, y, width, 22),
                text=text,
                manager=self.manager,
                container=self.scroll_container
            )
            self.ui_elements.append(label)
            y += 24

        # --- Remove from Fleet button ---
        if self.on_remove_ship:
            y += 10
            self.btn_remove = UIButton(
                relative_rect=pygame.Rect(10, y, width, 30),
                text="Remove from Fleet",
                manager=self.manager,
                container=self.scroll_container,
                object_id="#btn_remove_ship"
            )
            self.ui_elements.append(self.btn_remove)
            y += 40

        # Update scrollable area
        self.scroll_container.set_scrollable_area_dimensions((width, y + 20))

    def _add_section_header(self, title: str, x: int, y: int, width: int) -> int:
        """Add a section header and return new y position."""
        header = UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text=f"── {title} ──",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(header)
        return y + 28

    def _build_damage_section(self, ship: ShipInstance, x: int, y: int, width: int) -> int:
        """
        Build the component damage display section with collapsible layers.

        Groups damaged components by layer and allows expand/collapse.
        """
        damaged_by_layer = ship.get_damaged_components_by_layer()

        if not damaged_by_layer:
            no_damage = UILabel(
                relative_rect=pygame.Rect(x, y, width, 22),
                text="No component damage",
                manager=self.manager,
                container=self.scroll_container
            )
            self.ui_elements.append(no_damage)
            return y + 25

        # Layer display order
        layer_order = ['HULL', 'CORE', 'INNER', 'OUTER', 'ARMOR', 'UNKNOWN']

        for layer_name in layer_order:
            if layer_name not in damaged_by_layer:
                continue

            components = damaged_by_layer[layer_name]
            is_expanded = self.expanded_layers.get(layer_name, True)

            # Layer header button (clickable to toggle)
            expand_char = "▼" if is_expanded else "▶"
            layer_damage_count = len(components)

            layer_btn = UIButton(
                relative_rect=pygame.Rect(x, y, width - 10, 24),
                text=f"{expand_char} {layer_name} ({layer_damage_count} damaged)",
                manager=self.manager,
                container=self.scroll_container,
                object_id=f"#layer_{layer_name}"
            )
            self.ui_elements.append(layer_btn)
            self.layer_buttons[layer_name] = layer_btn
            y += 26

            # If expanded, show individual components
            if is_expanded:
                for comp_id, current_hp in components:
                    # Parse component name from ID (e.g., "reactor_standard_0" -> "Reactor Standard")
                    # Remove trailing _N index if present
                    parts = comp_id.rsplit('_', 1)
                    if len(parts) > 1 and parts[1].isdigit():
                        base_id = parts[0]
                    else:
                        base_id = comp_id
                    comp_name = base_id.replace('_', ' ').title()

                    # Determine color based on HP (would need max HP for percentage)
                    # For now, just display HP value with indicator
                    label = UILabel(
                        relative_rect=pygame.Rect(x + 15, y, width - 30, 22),
                        text=f"• {comp_name}: {current_hp} HP",
                        manager=self.manager,
                        container=self.scroll_container
                    )
                    self.ui_elements.append(label)
                    y += 24

                y += 4  # Small gap after expanded layer

        return y + 5

    def toggle_layer(self, layer_name: str):
        """Toggle a layer's expanded/collapsed state."""
        if layer_name in self.expanded_layers:
            self.expanded_layers[layer_name] = not self.expanded_layers[layer_name]
            # Rebuild display if we have a ship
            if self.current_ship:
                self.update_ship(self.current_ship)

    def process_event(self, event) -> bool:
        """
        Process UI events.

        Args:
            event: pygame event

        Returns:
            True if event was handled
        """
        # Handle layer toggle buttons and remove button
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Remove from fleet button
            if self.btn_remove and event.ui_element == self.btn_remove:
                if self.on_remove_ship and self.current_ship:
                    self.on_remove_ship(self.current_ship)
                return True
            # Layer toggle buttons
            for layer_name, button in self.layer_buttons.items():
                if event.ui_element == button:
                    self.toggle_layer(layer_name)
                    return True
        return False

    def kill(self):
        """Clean up all UI elements."""
        self._clear_elements()
        if self.panel:
            self.panel.kill()
