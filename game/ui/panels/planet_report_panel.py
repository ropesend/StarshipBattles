"""
Planet Report Panel - Reusable widget for displaying planet information.

This widget encapsulates the planet detail display from the strategy screen,
showing planet portrait, comprehensive stats, and atmosphere composition graph.
"""

import os
from typing import Dict, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox, UIPanel, UIScrollingContainer, UILabel
from game.ui.screens.strategy_detail_fmt import format_planet_info
from game.ui.fonts import get_font

if TYPE_CHECKING:
    from game.core.protocols import IPlanet, IFacility
from game.ui.panels.strategy_widgets import AtmosphereGraph
from game.ui.panels.build_queue_portraits import RESOURCE_PORTRAIT_FILES, RESOURCE_FALLBACK_COLORS
from game.core.constants import PLANET_RESOURCES
from collections import Counter


# Height reserved for resource grid at bottom of panel
RESOURCE_PANEL_HEIGHT = 100


class PlanetReportPanel:
    """
    Reusable panel that displays comprehensive planet information.

    Components:
    - Portrait (150x150 at 10, 10)
    - Info text (UITextBox with HTML in middle)
    - Atmosphere graph (150px wide at 10, 170)
    - Complexes list (scrollable, right side)
    """

    def __init__(
        self,
        manager,
        rect,
        planet,
        container=None,
        portrait_surface=None,
        show_complexes=True,
        production_rates: Optional[Dict[str, float]] = None
    ):
        """
        Initialize planet report panel.

        Args:
            manager: pygame_gui UIManager
            rect: pygame.Rect for panel dimensions
            planet: Planet object to display
            container: Optional parent container
            portrait_surface (pygame.Surface, optional): Pre-loaded portrait image.
                If provided, will be used instead of generating placeholder.
            show_complexes (bool, optional): Whether to show the complexes list.
                Defaults to True. Set to False for contexts like Strategy UI.
            production_rates (Dict[str, float], optional): Per-resource production rates.
                Used for the resource grid. Defaults to empty dict.
        """
        self.manager = manager
        self.rect = rect
        self.planet = planet
        self.container = container
        self._init_portrait_surface = portrait_surface
        self.production_rates = production_rates or {}
        self._resource_icons: Dict[str, pygame.Surface] = {}
        self._resource_grid_items: List = []

        # Load resource icons
        self._load_resource_icons()

        # Create panel container
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # Portrait (10, 10, 150, 150)
        self.portrait_image = UIImage(
            relative_rect=pygame.Rect(10, 10, 150, 150),
            image_surface=pygame.Surface((150, 150)),
            manager=manager,
            container=self.panel
        )

        # Reserve space for complexes list on the right (200px wide)
        complexes_width = 200
        complexes_gap = 10

        # Info text (170, 10, text_w, text_h) - width depends on whether complexes are shown
        # Height reduced to make room for resource panel at bottom
        if show_complexes:
            text_w = rect.width - 180 - complexes_width - complexes_gap  # Leave room for complexes list
        else:
            text_w = rect.width - 180  # Only leave room for portrait and graph
        text_h = rect.height - 20 - RESOURCE_PANEL_HEIGHT
        self.detail_text = UITextBox(
            html_text=format_planet_info(planet),
            relative_rect=pygame.Rect(170, 10, text_w, text_h),
            manager=manager,
            container=self.panel
        )

        # Complexes list (scrollable, right side) - only if show_complexes is True
        # Height reduced to make room for resource panel at bottom
        if show_complexes:
            complexes_x = rect.width - complexes_width - 10  # 10px margin from right edge
            complexes_h = rect.height - 20 - RESOURCE_PANEL_HEIGHT
            self.complexes_container = UIScrollingContainer(
                relative_rect=pygame.Rect(complexes_x, 10, complexes_width, complexes_h),
                manager=manager,
                container=self.panel
            )

            # Complexes header
            UILabel(
                relative_rect=pygame.Rect(5, 5, complexes_width - 10, 25),
                text="Built Complexes",
                manager=manager,
                container=self.complexes_container
            )

            # Track complex list items for updates
            self.complex_items = []
        else:
            # No complexes list - set to None
            self.complexes_container = None
            self.complex_items = []

        # Atmosphere graph (10, 170, 150, graph_h)
        # Height reduced to make room for resource panel at bottom
        graph_y = 170
        graph_h = rect.height - 180 - RESOURCE_PANEL_HEIGHT
        if graph_h < 50:
            graph_h = 50

        self.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
        self.graph_image = UIImage(
            relative_rect=self.graph_rect,
            image_surface=pygame.Surface((150, graph_h)),
            manager=manager,
            container=self.panel
        )

        # Create atmosphere graph renderer with SWAPPED dimensions for rotation
        # Strategy screen uses AtmosphereGraph(height, width) then rotates -90 degrees
        self.graph = AtmosphereGraph(int(graph_h), 150)

        # Resource grid panel at bottom (PROJ-82)
        resource_y = rect.height - RESOURCE_PANEL_HEIGHT - 10
        self.resource_panel = UIPanel(
            relative_rect=pygame.Rect(10, resource_y, rect.width - 20, RESOURCE_PANEL_HEIGHT),
            manager=manager,
            container=self.panel
        )

        # Initial render
        self._update_portrait(portrait_surface)
        self._update_graph()
        self._update_complexes_list()
        self._build_resource_grid()

    def update_planet(
        self,
        planet,
        portrait_surface=None,
        production_rates: Optional[Dict[str, float]] = None
    ):
        """
        Update display for a new planet.

        Args:
            planet: Planet object to display
            portrait_surface: Optional pygame Surface for planet portrait
            production_rates: Optional per-resource production rates for the grid
        """
        self.planet = planet
        self.production_rates = production_rates or {}

        # Update info text
        self.detail_text.html_text = format_planet_info(planet)
        self.detail_text.rebuild()

        # Update portrait, graph, complexes list, and resource grid
        self._update_portrait(portrait_surface)
        self._update_graph()
        self._update_complexes_list()
        self._update_resource_grid()

    def _update_portrait(self, portrait_surface=None):
        """Update planet portrait image."""
        if portrait_surface:
            # Use provided portrait surface (from strategy scene asset system)
            scaled = pygame.transform.smoothscale(portrait_surface, (150, 150))
            self.portrait_image.set_image(scaled)
        else:
            # Create placeholder portrait (gradient based on planet type)
            portrait_surf = pygame.Surface((150, 150))

            # Color based on planet type (planet_type always present via IPlanet)
            type_colors = {
                'TERRESTRIAL': (100, 150, 200),
                'GAS_GIANT': (200, 150, 100),
                'ICE_GIANT': (150, 200, 255),
                'ROCKY': (150, 100, 80),
                'OCEANIC': (50, 100, 200)
            }
            base_color = type_colors.get(
                self.planet.planet_type.name,
                (100, 100, 100)
            )

            # Simple gradient fill
            for y in range(150):
                fade = 1.0 - (y / 150.0) * 0.3
                color = tuple(int(c * fade) for c in base_color)
                pygame.draw.line(portrait_surf, color, (0, y), (150, y))

            # Add planet name text
            font = get_font(16, bold=True)
            text = font.render(self.planet.name[:20], True, (255, 255, 255))
            text_rect = text.get_rect(center=(75, 75))

            # Add shadow for readability
            shadow = font.render(self.planet.name[:20], True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(76, 76))
            portrait_surf.blit(shadow, shadow_rect)
            portrait_surf.blit(text, text_rect)

            # Add border
            pygame.draw.rect(portrait_surf, (200, 200, 200), (0, 0, 150, 150), 2)

            # Update UIImage
            self.portrait_image.set_image(portrait_surf)

    def _update_graph(self):
        """Update atmosphere graph visualization."""
        # Render atmosphere graph vertically then rotate -90 degrees (matches strategy screen)
        graph_surface = self.graph.render(self.planet, vertical=True)
        graph_surface = pygame.transform.rotate(graph_surface, -90)

        # Update UIImage
        self.graph_image.set_image(graph_surface)

    def _update_complexes_list(self):
        """Update the list of built complexes on the planet."""
        # Check if complexes list is enabled
        if not self.complexes_container:
            return  # Complexes list disabled, nothing to update

        # Clear existing items - copy list to avoid mutation during iteration (BUG-26)
        items_to_kill = list(self.complex_items)
        for item in items_to_kill:
            item.kill()
        self.complex_items = []

        # Check if planet has facilities (facilities always present via IPlanet)
        if not self.planet.facilities:
            # Show "None" message
            no_complexes_label = UILabel(
                relative_rect=pygame.Rect(5, 35, 190, 25),
                text="None",
                manager=self.manager,
                container=self.complexes_container
            )
            self.complex_items.append(no_complexes_label)
            return

        # Count complexes by design_id
        complex_counts = Counter(facility.design_id for facility in self.planet.facilities)

        # Create list items
        y_offset = 35  # Start below header
        for design_id, count in sorted(complex_counts.items()):
            # Get name from first facility with this design_id
            facility_name = next(
                (f.name for f in self.planet.facilities if f.design_id == design_id),
                design_id  # Fallback to design_id if name not found
            )

            # Format display text
            if count > 1:
                display_text = f"{facility_name} x{count}"
            else:
                display_text = facility_name

            # Create label
            complex_label = UILabel(
                relative_rect=pygame.Rect(5, y_offset, 190, 25),
                text=display_text,
                manager=self.manager,
                container=self.complexes_container
            )
            self.complex_items.append(complex_label)

            y_offset += 30  # Gap between items

    def _format_compact_number(self, value: float) -> str:
        """Format a number with K/M suffixes for compact display."""
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.0f}k"
        else:
            return str(int(value))

    def _build_resource_grid(self) -> None:
        """
        Build the resource grid panel with icons, quantity, quality, and production rows.
        """
        # Clear any existing grid items
        for item in self._resource_grid_items:
            item.kill()
        self._resource_grid_items = []

        grid_width = self.resource_panel.relative_rect.width
        label_col_width = 40  # Width for row labels (Qty, Qual, Prod)
        col_w = (grid_width - label_col_width - 20) // 5  # 5 resources, 20px padding

        # Row labels column (left side)
        row_labels = ["Qty", "Qual", "Prod"]
        row_y_offsets = [28, 48, 68]

        for label_text, y_offset in zip(row_labels, row_y_offsets):
            label = UILabel(
                relative_rect=pygame.Rect(5, y_offset, label_col_width, 20),
                text=label_text,
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(label)

        # Resource columns
        planet_resources = self.planet.resources or {}

        for i, resource_name in enumerate(PLANET_RESOURCES):
            col_x = label_col_width + 10 + i * col_w

            # Icon header (centered within column)
            icon_surf = self._resource_icons.get(resource_name)
            if icon_surf:
                icon_x = col_x + (col_w - 24) // 2
                icon_image = UIImage(
                    relative_rect=pygame.Rect(icon_x, 2, 24, 24),
                    image_surface=icon_surf,
                    manager=self.manager,
                    container=self.resource_panel
                )
                self._resource_grid_items.append(icon_image)

            # Get resource data
            r_data = planet_resources.get(resource_name, {})
            quantity = r_data.get('quantity', 0) if isinstance(r_data, dict) else 0
            quality = r_data.get('quality', 0) if isinstance(r_data, dict) else 0
            production = self.production_rates.get(resource_name, 0.0)

            # Quantity label
            qty_label = UILabel(
                relative_rect=pygame.Rect(col_x, 28, col_w, 20),
                text=self._format_compact_number(quantity),
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(qty_label)

            # Quality label
            qual_label = UILabel(
                relative_rect=pygame.Rect(col_x, 48, col_w, 20),
                text=f"{quality:.0f}" if quality else "0",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(qual_label)

            # Production label
            prod_label = UILabel(
                relative_rect=pygame.Rect(col_x, 68, col_w, 20),
                text=self._format_compact_number(production) if production else "0",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(prod_label)

    def _update_resource_grid(self) -> None:
        """Refresh resource grid values when planet changes."""
        self._build_resource_grid()

    def _load_resource_icons(self, icon_size: int = 24) -> None:
        """
        Load resource portrait icons for the resource grid.

        Args:
            icon_size: Size of the square icons in pixels (default 24).
        """
        base_path = os.path.join("assets", "Images", "Resource Portraits")

        for resource in PLANET_RESOURCES:
            filename = RESOURCE_PORTRAIT_FILES.get(resource)
            if filename:
                path = os.path.join(base_path, filename)
                try:
                    img = pygame.image.load(path)
                    self._resource_icons[resource] = pygame.transform.smoothscale(
                        img, (icon_size, icon_size)
                    )
                except (FileNotFoundError, pygame.error):
                    # Create fallback colored square
                    surf = pygame.Surface((icon_size, icon_size))
                    color = RESOURCE_FALLBACK_COLORS.get(resource, (128, 128, 128))
                    surf.fill(color)
                    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 1)
                    self._resource_icons[resource] = surf
            else:
                # No filename mapped, create gray placeholder
                surf = pygame.Surface((icon_size, icon_size))
                surf.fill((128, 128, 128))
                pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 1)
                self._resource_icons[resource] = surf

    def get_height_required(self):
        """
        Get minimum height required for this panel.

        Returns:
            int: Minimum height in pixels (350 + RESOURCE_PANEL_HEIGHT)
        """
        return 350 + RESOURCE_PANEL_HEIGHT

    def kill(self):
        """Clean up all UI elements."""
        # Clean up resource grid items
        for item in self._resource_grid_items:
            item.kill()
        self._resource_grid_items = []

        # Clean up resource panel
        if hasattr(self, 'resource_panel') and self.resource_panel:
            self.resource_panel.kill()

        # Clean up main panel (contains all other elements)
        if hasattr(self, 'panel'):
            self.panel.kill()


def compute_planet_production(planet: 'IPlanet') -> Dict[str, float]:
    """Compute per-resource production rates for a colony planet.

    Scans the planet's facilities for ResourceHarvester abilities and calculates
    production = base_harvest_rate * planet_resource_quality.

    This is a shared utility used by the strategy detail panel, build queue,
    and planets list to display consistent production data.

    Args:
        planet: Planet object with facilities and resources.

    Returns:
        Dict mapping resource name to production rate per turn.
    """
    if planet.owner_id is None:
        return {}

    from game.core.registry import get_default_registry_provider, GameRegistries
    provider = get_default_registry_provider()
    registries = GameRegistries(
        components=provider.get_components(),
        modifiers=provider.get_modifiers(),
        vehicle_classes=provider.get_vehicle_classes(),
        resources=provider.get_resources(),
    )

    rates: Dict[str, float] = {}
    facility: 'IFacility'
    for facility in planet.facilities:
        if not facility.is_operational:
            continue
        design_data = facility.design_data
        for layer_data in design_data.get('layers', {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                harvester = _get_harvester_info(comp, registries)
                if harvester:
                    res_type = harvester.get('resource_type', '')
                    base_rate = harvester.get('base_harvest_rate', 0.0)
                    if res_type and base_rate > 0:
                        quality = planet.resources.get(res_type, {}).get('quality', 0.0)
                        rates[res_type] = rates.get(res_type, 0.0) + base_rate * quality
    return rates


def _get_harvester_info(comp, registries) -> Optional[dict]:
    """Extract ResourceHarvester info from a component entry.

    Checks inline abilities first, then falls back to registry lookup.
    """
    if isinstance(comp, dict):
        harvester = comp.get('abilities', {}).get('ResourceHarvester')
        if isinstance(harvester, dict):
            return harvester
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            comp_def = registries.components.get(comp_id)
            if comp_def is not None:
                abilities = getattr(comp_def, 'abilities', {}) or {}
                harvester = abilities.get('ResourceHarvester')
                if isinstance(harvester, dict):
                    return harvester
    return None
