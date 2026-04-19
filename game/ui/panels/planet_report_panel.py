"""
Planet Report Panel - Reusable widget for displaying planet information.

This widget encapsulates the planet detail display from the strategy screen,
showing planet portrait, comprehensive stats, and atmosphere composition graph.
"""

import os
from typing import Dict, List, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox, UIPanel, UIScrollingContainer, UILabel
from game.core.paths import Paths
from game.ui.screens.strategy_detail_fmt import format_planet_info
from game.ui.fonts import get_font
from game.ui.utils.formatters import format_compact_number

from game.ui.panels.strategy_widgets import AtmosphereGraph
from game.ui.panels.build_queue_portraits import RESOURCE_PORTRAIT_FILES, RESOURCE_FALLBACK_COLORS
# All resource types displayed in the planet report panel
ALL_RESOURCE_NAMES = ["metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo"]
from game.ui.colors import (
    PLANET_TERRESTRIAL, PLANET_GAS_GIANT, PLANET_ICE, PLANET_ROCKY, PLANET_OCEANIC,
    TEXT_DIM, WHITE, TEXT_LIGHT
)
from collections import Counter


# Height reserved for resource grid at bottom of panel
RESOURCE_PANEL_HEIGHT = 160


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
        production_rates: Optional[Dict[str, float]] = None,
        empire=None,
        race_registry=None,
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
            empire: PROJ-290 — optional viewing empire used to render the
                uncolonized-planet habitability section. Combined with
                `race_registry` below; either missing → section omitted.
            race_registry: PROJ-290 — optional `IRaceRegistry`. Required
                alongside `empire` to render the uncolonized habitability
                section. None preserves the pre-PROJ-290 rendering.
        """
        self.manager = manager
        self.rect = rect
        self.planet = planet
        self.container = container
        self._init_portrait_surface = portrait_surface
        self.production_rates = production_rates or {}
        self._resource_icons: Dict[str, pygame.Surface] = {}
        self._resource_grid_items: List = []
        # PROJ-290 — stored so `update_planet` can default to the
        # construction-time values when it's called without new deps.
        self._empire = empire
        self._race_registry = race_registry

        # Load resource icons
        self._load_resource_icons(icon_size=20)

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
            html_text=format_planet_info(
                planet, empire=empire, race_registry=race_registry,
            ),
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
        production_rates: Optional[Dict[str, float]] = None,
        empire=None,
        race_registry=None,
    ):
        """
        Update display for a new planet.

        Args:
            planet: Planet object to display
            portrait_surface: Optional pygame Surface for planet portrait
            production_rates: Optional per-resource production rates for the grid
            empire: PROJ-290 — override the construction-time empire.
                When None, the panel reuses whatever was passed to
                `__init__` (both default to None → no habitability section).
            race_registry: PROJ-290 — override the construction-time
                `IRaceRegistry`. Same fallback contract as `empire`.
        """
        self.planet = planet
        self.production_rates = production_rates or {}
        if empire is not None:
            self._empire = empire
        if race_registry is not None:
            self._race_registry = race_registry

        # Update info text
        self.detail_text.html_text = format_planet_info(
            planet,
            empire=self._empire,
            race_registry=self._race_registry,
        )
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
                'TERRESTRIAL': PLANET_TERRESTRIAL,
                'GAS_GIANT': PLANET_GAS_GIANT,
                'ICE_GIANT': PLANET_ICE,
                'ROCKY': PLANET_ROCKY,
                'OCEANIC': PLANET_OCEANIC
            }
            base_color = type_colors.get(
                self.planet.planet_type.name,
                TEXT_DIM
            )

            # Simple gradient fill
            for y in range(150):
                fade = 1.0 - (y / 150.0) * 0.3
                color = tuple(int(c * fade) for c in base_color)
                pygame.draw.line(portrait_surf, color, (0, y), (150, y))

            # Add planet name text
            font = get_font(16, bold=True)
            text = font.render(self.planet.name[:20], True, WHITE)
            text_rect = text.get_rect(center=(75, 75))

            # Add shadow for readability
            from game.ui.colors import BLACK
            shadow = font.render(self.planet.name[:20], True, BLACK)
            shadow_rect = shadow.get_rect(center=(76, 76))
            portrait_surf.blit(shadow, shadow_rect)
            portrait_surf.blit(text, text_rect)

            # Add border
            pygame.draw.rect(portrait_surf, TEXT_LIGHT, (0, 0, 150, 150), 2)

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
                relative_rect=pygame.Rect(5, y_offset, 350, 25),
                text=display_text,
                manager=self.manager,
                container=self.complexes_container
            )
            self.complex_items.append(complex_label)

            y_offset += 30  # Gap between items

    def _build_resource_grid(self) -> None:
        """
        Build the resource grid panel with icons and rows for all 8 resource types.

        Rows: Qty (deposit quantity), Qual (deposit quality), Prod (harvest rate),
              Stored (current stockpile), Cap (max stockpile capacity).
        """
        # Clear any existing grid items
        for item in self._resource_grid_items:
            item.kill()
        self._resource_grid_items = []

        num_resources = len(ALL_RESOURCE_NAMES)
        grid_width = self.resource_panel.relative_rect.width
        label_col_width = 40  # Width for row labels
        col_w = (grid_width - label_col_width - 20) // num_resources

        # Row labels column (left side)
        row_labels = ["Qty", "Qual", "Prod", "Stor", "Cap"]
        row_y_offsets = [28, 48, 68, 88, 108]

        for label_text, y_offset in zip(row_labels, row_y_offsets):
            label = UILabel(
                relative_rect=pygame.Rect(5, y_offset, label_col_width, 20),
                text=label_text,
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(label)

        # Resource columns
        planet_deposits = self.planet.deposits or {}
        planet_stockpile = getattr(self.planet, 'stockpile', {}) or {}
        planet_max_stockpile = getattr(self.planet, 'max_stockpile', {}) or {}

        for i, resource_name in enumerate(ALL_RESOURCE_NAMES):
            col_x = label_col_width + 10 + i * col_w

            # Icon header (centered within column)
            icon_surf = self._resource_icons.get(resource_name)
            if icon_surf:
                icon_x = col_x + (col_w - 20) // 2
                icon_image = UIImage(
                    relative_rect=pygame.Rect(icon_x, 2, 20, 20),
                    image_surface=icon_surf,
                    manager=self.manager,
                    container=self.resource_panel
                )
                self._resource_grid_items.append(icon_image)

            # Get deposit data (quantity/quality)
            r_data = planet_deposits.get(resource_name, {})
            quantity = r_data.get('quantity', 0) if isinstance(r_data, dict) else 0
            quality = r_data.get('quality', 0) if isinstance(r_data, dict) else 0
            production = self.production_rates.get(resource_name, 0.0)
            stored = planet_stockpile.get(resource_name, 0.0)
            capacity = planet_max_stockpile.get(resource_name, 0.0)

            # Quantity label (deposit)
            qty_label = UILabel(
                relative_rect=pygame.Rect(col_x, 28, col_w, 20),
                text=format_compact_number(quantity) if quantity else "-",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(qty_label)

            # Quality label (deposit)
            qual_label = UILabel(
                relative_rect=pygame.Rect(col_x, 48, col_w, 20),
                text=f"{quality:.1f}" if quality else "-",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(qual_label)

            # Production label (harvest rate)
            prod_label = UILabel(
                relative_rect=pygame.Rect(col_x, 68, col_w, 20),
                text=format_compact_number(production) if production else "0",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(prod_label)

            # Stored label (current stockpile)
            stored_label = UILabel(
                relative_rect=pygame.Rect(col_x, 88, col_w, 20),
                text=format_compact_number(stored) if stored else "0",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(stored_label)

            # Capacity label (max stockpile)
            cap_label = UILabel(
                relative_rect=pygame.Rect(col_x, 108, col_w, 20),
                text=format_compact_number(capacity) if capacity else "0",
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(cap_label)

        # Staging yard items row (below resource grid)
        staging_yard = getattr(self.planet, 'staging_yard', None)
        if isinstance(staging_yard, list) and staging_yard:
            # Aggregate by name
            counts: dict = {}
            for item in staging_yard:
                name = item.get('name', 'Unknown')
                counts[name] = counts.get(name, 0) + 1
            parts = [f"{name} x{count}" if count > 1 else name
                     for name, count in counts.items()]
            staging_text = "Staging: " + ", ".join(parts)

            staging_label = UILabel(
                relative_rect=pygame.Rect(5, 132, self.resource_panel.relative_rect.width - 10, 20),
                text=staging_text,
                manager=self.manager,
                container=self.resource_panel
            )
            self._resource_grid_items.append(staging_label)

    def _update_resource_grid(self) -> None:
        """Refresh resource grid values when planet changes."""
        self._build_resource_grid()

    def _load_resource_icons(self, icon_size: int = 24) -> None:
        """
        Load resource portrait icons for the resource grid.

        Args:
            icon_size: Size of the square icons in pixels (default 24).
        """
        base_path = Paths.RESOURCE_PORTRAITS_DIR

        for resource in ALL_RESOURCE_NAMES:
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
                    color = RESOURCE_FALLBACK_COLORS.get(resource, TEXT_DIM)
                    surf.fill(color)
                    pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
                    self._resource_icons[resource] = surf
            else:
                # No filename mapped, create gray placeholder
                surf = pygame.Surface((icon_size, icon_size))
                surf.fill(TEXT_DIM)
                pygame.draw.rect(surf, WHITE, surf.get_rect(), 1)
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
        if self.resource_panel:
            self.resource_panel.kill()

        # Clean up main panel (contains all other elements)
        if self.panel:
            self.panel.kill()


# PROJ-288 Task 2.3: `compute_planet_production` (and its `_get_harvester_info`
# helper) moved to `game/strategy/services/planet_economy_projector.py` to fix
# the previous strategy-math-living-in-UI layer violation. Importers updated
# to pull directly from the new location.
