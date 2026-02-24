"""
Galaxy Mode Helper - Handles galaxy layout testing functionality.

Extracts galaxy generation, rendering, and UI management from the main screen.
"""
import random
import time
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIDropDownMenu, UIHorizontalSlider

import logging

logger = logging.getLogger(__name__)
from game.strategy.data.galaxy import Galaxy
from game.core.hex_math import hex_to_pixel
from game.strategy.engine.game_config import VALID_GALAXY_TYPES
from game.ui.screens.galaxy_test.constants import SIDEBAR_WIDTH, HEX_SIZE


class GalaxyModeHelper:
    """
    Helper class for galaxy layout testing mode.

    Manages galaxy generation, UI elements, and rendering for the
    galaxy layout test mode of GalaxyTestScreen.
    """

    def __init__(self, screen):
        """
        Initialize the galaxy mode helper.

        Args:
            screen: Parent GalaxyTestScreen instance for accessing camera,
                   ui_manager, and canvas dimensions.
        """
        self.screen = screen

        # Galaxy state
        self.galaxy = None
        self.generation_time = 0.0
        self.system_count = 100
        self.galaxy_radius = 4000  # Galaxy radius in hex units (matches GameConfig default)
        self.galaxy_type = "spiral"
        self.galaxy_seed = None

        # UI element references (set during create_ui)
        self.system_count_slider = None
        self.system_count_value = None
        self.galaxy_radius_slider = None
        self.galaxy_radius_value = None
        self.galaxy_type_dropdown = None
        self.seed_input = None
        self.btn_generate = None
        self.stats_label = None
        self.fps_label = None
        self.btn_back = None

    def create_ui(self):
        """
        Create UI for galaxy layout testing mode.

        Returns:
            List of UI elements created.
        """
        elements = []

        # Update canvas width for sidebar
        self.screen.canvas_width = self.screen.screen_width - SIDEBAR_WIDTH
        self.screen.camera.width = self.screen.canvas_width

        sidebar_x = self.screen.canvas_width + 10
        y = 10

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 30),
            text="Galaxy Layout Test",
            manager=self.screen.ui_manager
        )
        elements.append(title)
        y += 40

        # System count label
        count_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Count:",
            manager=self.screen.ui_manager
        )
        elements.append(count_label)
        y += 25

        # System count slider
        self.system_count_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 80, 25),
            start_value=self.system_count,
            value_range=(10, 2500),
            manager=self.screen.ui_manager
        )
        elements.append(self.system_count_slider)

        # System count value label
        self.system_count_value = UILabel(
            relative_rect=pygame.Rect(sidebar_x + SIDEBAR_WIDTH - 70, y, 60, 25),
            text=str(self.system_count),
            manager=self.screen.ui_manager
        )
        elements.append(self.system_count_value)
        y += 35

        # Galaxy radius label
        radius_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Galaxy Radius (hexes):",
            manager=self.screen.ui_manager
        )
        elements.append(radius_label)
        y += 25

        # Galaxy radius slider (star systems are ~101 hexes across, need spacing)
        self.galaxy_radius_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 80, 25),
            start_value=self.galaxy_radius,
            value_range=(500, 100000),
            manager=self.screen.ui_manager
        )
        elements.append(self.galaxy_radius_slider)

        # Galaxy radius value label
        self.galaxy_radius_value = UILabel(
            relative_rect=pygame.Rect(sidebar_x + SIDEBAR_WIDTH - 70, y, 60, 25),
            text=str(self.galaxy_radius),
            manager=self.screen.ui_manager
        )
        elements.append(self.galaxy_radius_value)
        y += 35

        # Galaxy type label
        type_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Galaxy Type:",
            manager=self.screen.ui_manager
        )
        elements.append(type_label)
        y += 25

        # Galaxy type dropdown
        galaxy_types = sorted(list(VALID_GALAXY_TYPES))
        self.galaxy_type_dropdown = UIDropDownMenu(
            options_list=galaxy_types,
            starting_option=self.galaxy_type,
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 30),
            manager=self.screen.ui_manager
        )
        elements.append(self.galaxy_type_dropdown)
        y += 40

        # Seed label
        seed_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Seed (blank=random):",
            manager=self.screen.ui_manager
        )
        elements.append(seed_label)
        y += 25

        # Seed input
        self.seed_input = UITextEntryLine(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 30),
            manager=self.screen.ui_manager,
            placeholder_text="Random seed..."
        )
        elements.append(self.seed_input)
        y += 40

        # Generate button
        self.btn_generate = UIButton(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 40),
            text="Generate Galaxy",
            manager=self.screen.ui_manager
        )
        elements.append(self.btn_generate)
        y += 50

        # Stats section
        stats_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Statistics:",
            manager=self.screen.ui_manager
        )
        elements.append(stats_label)
        y += 30

        # Stats display
        self.stats_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 120),
            text="No galaxy generated yet",
            manager=self.screen.ui_manager
        )
        elements.append(self.stats_label)
        y += 130

        # FPS display
        self.fps_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 25),
            text="FPS: --",
            manager=self.screen.ui_manager
        )
        elements.append(self.fps_label)
        y += 35

        # Back button at bottom
        self.btn_back = UIButton(
            relative_rect=pygame.Rect(sidebar_x, self.screen.screen_height - 50, SIDEBAR_WIDTH - 20, 40),
            text="Back",
            manager=self.screen.ui_manager
        )
        elements.append(self.btn_back)

        return elements

    def generate(self):
        """Generate a new galaxy for testing."""
        # Get seed
        seed_text = self.seed_input.get_text().strip()
        if seed_text:
            try:
                self.galaxy_seed = int(seed_text)
            except ValueError:
                self.galaxy_seed = hash(seed_text) % (2**31)
        else:
            self.galaxy_seed = random.randint(0, 2**31 - 1)

        # Seed RNG
        random.seed(self.galaxy_seed)

        # Get settings
        self.system_count = int(self.system_count_slider.get_current_value())
        self.galaxy_radius = int(self.galaxy_radius_slider.get_current_value())
        self.galaxy_type = self.galaxy_type_dropdown.selected_option[0]

        logger.info(f"Generating galaxy: type={self.galaxy_type}, count={self.system_count}, radius={self.galaxy_radius}, seed={self.galaxy_seed}")

        # Create galaxy
        start_time = time.perf_counter()

        self.galaxy = Galaxy(radius=self.galaxy_radius)

        # Get placement strategy based on type
        from game.strategy.generation.placement_strategies import (
            RandomPlacementStrategy,
            DensityBasedPlacementStrategy
        )
        from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
        from game.strategy.generation.density.density_map import DensityMap

        rng = random.Random(self.galaxy_seed)

        t1 = time.perf_counter()
        if self.galaxy_type == "random":
            strategy = RandomPlacementStrategy()
        else:
            # Use load_and_scale to properly scale density values for galaxy radius
            loader = GalaxyLayoutsLoader()
            scaled_config = loader.load_and_scale(self.galaxy_type, self.galaxy.radius)
            density_map = DensityMap.from_config(scaled_config, self.galaxy.radius)
            strategy = DensityBasedPlacementStrategy(density_map)
        t2 = time.perf_counter()
        logger.info(f"  Strategy setup: {t2-t1:.3f}s")

        # Generate systems (positions only, no stars/planets yet)
        # min_dist=400 matches production GameSession (star systems are ~101 hexes across)
        self.galaxy.generate_systems(
            count=self.system_count,
            min_dist=400,
            placement_strategy=strategy,
            rng=rng
        )
        t3 = time.perf_counter()
        logger.info(f"  System placement: {t3-t2:.3f}s")

        # Generate warp lanes
        self.galaxy.generate_warp_lanes()
        t4 = time.perf_counter()
        logger.info(f"  Warp lane generation: {t4-t3:.3f}s")

        self.generation_time = time.perf_counter() - start_time
        logger.info(f"  Total generation: {self.generation_time:.3f}s")

        # Count warp connections
        warp_count = sum(len(sys.warp_points) for sys in self.galaxy.systems.values()) // 2

        # Update stats
        self.stats_label.set_text(
            f"Systems: {len(self.galaxy.systems)}\n"
            f"Warp Lanes: {warp_count}\n"
            f"Radius: {self.galaxy_radius} hexes\n"
            f"Gen Time: {self.generation_time:.2f}s\n"
            f"Seed: {self.galaxy_seed}"
        )

        # Center camera on galaxy
        t5 = time.perf_counter()
        self._center_camera()
        t6 = time.perf_counter()
        logger.info(f"  Camera centering: {t6-t5:.3f}s")

        logger.info(f"Galaxy generated: {len(self.galaxy.systems)} systems, {warp_count} warp lanes in {self.generation_time:.2f}s")

    def _center_camera(self):
        """Center the camera on the generated galaxy."""
        if not self.galaxy or not self.galaxy.systems:
            return

        # Find bounds
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        for sys in self.galaxy.systems.values():
            px, py = hex_to_pixel(sys.global_location, HEX_SIZE)
            min_x = min(min_x, px)
            max_x = max(max_x, px)
            min_y = min(min_y, py)
            max_y = max(max_y, py)

        # Center camera
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.screen.camera.position = pygame.math.Vector2(center_x, center_y)

        # Fit zoom
        margin = 200
        width = max_x - min_x + margin
        height = max_y - min_y + margin

        zoom_x = self.screen.canvas_width / width if width > 0 else 1.0
        zoom_y = self.screen.canvas_height / height if height > 0 else 1.0
        self.screen.camera.zoom = min(zoom_x, zoom_y)
        self.screen.camera.target_zoom = self.screen.camera.zoom
        self.screen.camera.zoom = max(self.screen.camera.min_zoom, min(self.screen.camera.max_zoom, self.screen.camera.zoom))

    def update_slider_displays(self):
        """Update slider value display labels."""
        if self.system_count_slider:
            current_val = int(self.system_count_slider.get_current_value())
            self.system_count_value.set_text(str(current_val))
        if self.galaxy_radius_slider:
            current_val = int(self.galaxy_radius_slider.get_current_value())
            self.galaxy_radius_value.set_text(str(current_val))

    def draw(self, screen_surface: pygame.Surface):
        """
        Draw the galaxy layout (dots and warp lanes only).

        Args:
            screen_surface: Pygame surface to draw on.
        """
        if not self.galaxy:
            return

        # Clip to canvas area
        canvas_rect = pygame.Rect(0, 0, self.screen.canvas_width, self.screen.canvas_height)
        screen_surface.set_clip(canvas_rect)

        # Draw warp lanes first (behind systems)
        self._draw_warp_lanes(screen_surface)

        # Draw systems as dots
        for sys in self.galaxy.systems.values():
            px, py = hex_to_pixel(sys.global_location, HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.screen.camera.world_to_screen(world_pos)

            # Skip if off-screen
            if not (0 <= screen_pos.x <= self.screen.canvas_width and 0 <= screen_pos.y <= self.screen.canvas_height):
                continue

            # Draw dot
            radius = max(2, int(4 * self.screen.camera.zoom))
            pygame.draw.circle(screen_surface, (200, 200, 100), (int(screen_pos.x), int(screen_pos.y)), radius)

        # Remove clip
        screen_surface.set_clip(None)

    def _draw_warp_lanes(self, screen_surface: pygame.Surface):
        """Draw warp lane connections."""
        if not self.galaxy:
            return

        drawn_pairs = set()

        for sys in self.galaxy.systems.values():
            sx, sy = hex_to_pixel(sys.global_location, HEX_SIZE)

            for wp in sys.warp_points:
                target_sys = self.galaxy.get_system_by_name(wp.destination_id)
                if not target_sys:
                    continue

                # Avoid drawing the same lane twice
                pair_key = tuple(sorted([sys.name, target_sys.name]))
                if pair_key in drawn_pairs:
                    continue
                drawn_pairs.add(pair_key)

                # Get endpoints
                tx, ty = hex_to_pixel(target_sys.global_location, HEX_SIZE)

                scr_a = self.screen.camera.world_to_screen(pygame.math.Vector2(sx, sy))
                scr_b = self.screen.camera.world_to_screen(pygame.math.Vector2(tx, ty))

                # Viewport culling
                margin = 50
                if not ((-margin <= scr_a.x <= self.screen.canvas_width + margin and
                         -margin <= scr_a.y <= self.screen.canvas_height + margin) or
                        (-margin <= scr_b.x <= self.screen.canvas_width + margin and
                         -margin <= scr_b.y <= self.screen.canvas_height + margin)):
                    continue

                # Draw line
                pygame.draw.line(screen_surface, (50, 50, 100),
                               (int(scr_a.x), int(scr_a.y)),
                               (int(scr_b.x), int(scr_b.y)), 1)
