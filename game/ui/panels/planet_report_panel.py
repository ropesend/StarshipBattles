"""
Planet Report Panel - Reusable widget for displaying planet information.

This widget encapsulates the planet detail display from the strategy screen,
showing planet portrait, comprehensive stats, and atmosphere composition graph.
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox, UIPanel
from game.ui.screens.strategy_detail_fmt import format_planet_info
from game.ui.panels.strategy_widgets import AtmosphereGraph


class PlanetReportPanel:
    """
    Reusable panel that displays comprehensive planet information.

    Components:
    - Portrait (150x150 at 10, 10)
    - Info text (UITextBox with HTML at 170, 10)
    - Atmosphere graph (150px wide at 10, 170)
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

        # Info text (170, 10, text_w, text_h)
        text_w = rect.width - 180
        text_h = rect.height - 20
        self.detail_text = UITextBox(
            html_text=format_planet_info(planet),
            relative_rect=pygame.Rect(170, 10, text_w, text_h),
            manager=manager,
            container=self.panel
        )

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

        # Create atmosphere graph renderer
        self.graph = AtmosphereGraph(width=150, height=graph_h)

        # Initial render
        self._update_portrait()
        self._update_graph()

    def update_planet(self, planet):
        """
        Update display for a new planet.

        Args:
            planet: Planet object to display
        """
        self.planet = planet

        # Update info text
        self.detail_text.html_text = format_planet_info(planet)
        self.detail_text.rebuild()

        # Update portrait and graph
        self._update_portrait()
        self._update_graph()

    def _update_portrait(self):
        """Update planet portrait image."""
        # Create placeholder portrait (gradient based on planet type)
        portrait_surface = pygame.Surface((150, 150))

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
            pygame.draw.line(portrait_surface, color, (0, y), (150, y))

        # Add planet name text
        font = pygame.font.SysFont("arial", 16, bold=True)
        text = font.render(self.planet.name[:20], True, (255, 255, 255))
        text_rect = text.get_rect(center=(75, 75))

        # Add shadow for readability
        shadow = font.render(self.planet.name[:20], True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(76, 76))
        portrait_surface.blit(shadow, shadow_rect)
        portrait_surface.blit(text, text_rect)

        # Add border
        pygame.draw.rect(portrait_surface, (200, 200, 200), (0, 0, 150, 150), 2)

        # Update UIImage
        self.portrait_image.set_image(portrait_surface)

    def _update_graph(self):
        """Update atmosphere graph visualization."""
        # Render atmosphere graph
        graph_surface = self.graph.render(self.planet, vertical=False)

        # Update UIImage
        self.graph_image.set_image(graph_surface)

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
