"""
Planet Report Panel - Reusable widget for displaying planet information.

This widget encapsulates the planet detail display from the strategy screen,
showing planet portrait, comprehensive stats, and atmosphere composition graph.
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox, UIPanel, UIScrollingContainer, UILabel
from game.ui.screens.strategy_detail_fmt import format_planet_info
from game.ui.panels.strategy_widgets import AtmosphereGraph
from collections import Counter


class PlanetReportPanel:
    """
    Reusable panel that displays comprehensive planet information.

    Components:
    - Portrait (150x150 at 10, 10)
    - Info text (UITextBox with HTML in middle)
    - Atmosphere graph (150px wide at 10, 170)
    - Complexes list (scrollable, right side)
    """

    def __init__(self, manager, rect, planet, container=None):
        """
        Initialize planet report panel.

        Args:
            manager: pygame_gui UIManager
            rect: pygame.Rect for panel dimensions
            planet: Planet object to display
            container: Optional parent container
        """
        self.manager = manager
        self.rect = rect
        self.planet = planet
        self.container = container

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

        # Info text (170, 10, text_w, text_h) - adjusted to make room for complexes list
        text_w = rect.width - 180 - complexes_width - complexes_gap
        text_h = rect.height - 20
        self.detail_text = UITextBox(
            html_text=format_planet_info(planet),
            relative_rect=pygame.Rect(170, 10, text_w, text_h),
            manager=manager,
            container=self.panel
        )

        # Complexes list (scrollable, right side)
        complexes_x = rect.width - complexes_width - 10  # 10px margin from right edge
        self.complexes_container = UIScrollingContainer(
            relative_rect=pygame.Rect(complexes_x, 10, complexes_width, rect.height - 20),
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

        # Atmosphere graph (10, 170, 150, graph_h)
        graph_y = 170
        graph_h = rect.height - 180
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

        # Initial render
        self._update_portrait()
        self._update_graph()
        self._update_complexes_list()

    def update_planet(self, planet, portrait_surface=None):
        """
        Update display for a new planet.

        Args:
            planet: Planet object to display
            portrait_surface: Optional pygame Surface for planet portrait
        """
        self.planet = planet

        # Update info text
        self.detail_text.html_text = format_planet_info(planet)
        self.detail_text.rebuild()

        # Update portrait, graph, and complexes list
        self._update_portrait(portrait_surface)
        self._update_graph()
        self._update_complexes_list()

    def _update_portrait(self, portrait_surface=None):
        """Update planet portrait image."""
        if portrait_surface:
            # Use provided portrait surface (from strategy scene asset system)
            scaled = pygame.transform.smoothscale(portrait_surface, (150, 150))
            self.portrait_image.set_image(scaled)
        else:
            # Create placeholder portrait (gradient based on planet type)
            portrait_surf = pygame.Surface((150, 150))

            # Color based on planet type
            if hasattr(self.planet, 'planet_type'):
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
            else:
                base_color = (100, 100, 100)

            # Simple gradient fill
            for y in range(150):
                fade = 1.0 - (y / 150.0) * 0.3
                color = tuple(int(c * fade) for c in base_color)
                pygame.draw.line(portrait_surf, color, (0, y), (150, y))

            # Add planet name text
            font = pygame.font.SysFont("arial", 16, bold=True)
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
        # Clear existing items
        for item in self.complex_items:
            item.kill()
        self.complex_items = []

        # Check if planet has facilities
        if not hasattr(self.planet, 'facilities') or not self.planet.facilities:
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

    def get_height_required(self):
        """
        Get minimum height required for this panel.

        Returns:
            int: Minimum height in pixels (350px)
        """
        return 350

    def kill(self):
        """Clean up all UI elements."""
        if hasattr(self, 'panel'):
            self.panel.kill()
