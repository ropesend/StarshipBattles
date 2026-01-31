"""
Galaxy Test Screen - Testing tool for galaxy and star system generation.

Provides two modes:
1. Galaxy Layout - Test galaxy generation (system positions + warp lanes only)
2. Star System - Test single system generation (stars + planets only)
"""
import random
import time
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIDropDownMenu, UIHorizontalSlider

from game.core.logger import log_info
from game.ui.renderer.camera import Camera
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.hex_math import hex_to_pixel, HexCoord
from game.strategy.engine.game_config import VALID_GALAXY_TYPES


class GalaxyTestScreen:
    """
    Test screen for galaxy and star system generation.

    Two modes:
    - MENU: Select between Galaxy Layout and Star System testing
    - GALAXY: Test galaxy generation with system positions and warp lanes
    - SYSTEM: Test single star system generation with stars and planets
    """

    # Mode constants
    MODE_MENU = "menu"
    MODE_GALAXY = "galaxy"
    MODE_SYSTEM = "system"

    # Layout constants
    SIDEBAR_WIDTH = 320
    HEX_SIZE = 10.0

    def __init__(self, screen_width: int, screen_height: int, on_close_callback=None):
        """
        Initialize the galaxy test screen.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            on_close_callback: Function to call when closing the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_close_callback = on_close_callback

        # Current mode
        self.mode = self.MODE_MENU

        # Canvas area (excluding sidebar when in test modes)
        self.canvas_width = screen_width
        self.canvas_height = screen_height

        # Camera for pan/zoom
        self.camera = Camera(self.canvas_width, self.canvas_height)
        self.camera.min_zoom = 0.02
        self.camera.max_zoom = 3.0
        self.camera.zoom = 0.3
        self.camera.target_zoom = 0.3

        # UI Manager
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height))

        # Galaxy data (for GALAXY mode)
        self.galaxy = None
        self.generation_time = 0.0
        self.system_count = 100
        self.galaxy_type = "spiral"
        self.galaxy_seed = None

        # Star system data (for SYSTEM mode)
        self.test_system = None

        # FPS tracking
        self.fps_clock = pygame.time.Clock()
        self.current_fps = 0.0

        # UI elements (created per-mode)
        self._ui_elements = []

        # Create initial menu UI
        self._create_menu_ui()

        log_info("GalaxyTestScreen: Initialized")

    def _clear_ui(self):
        """Clear all UI elements."""
        for element in self._ui_elements:
            element.kill()
        self._ui_elements.clear()

    def _create_menu_ui(self):
        """Create the main menu UI with mode selection buttons."""
        self._clear_ui()

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(center_x - 200, center_y - 150, 400, 50),
            text="Galaxy Generation Test",
            manager=self.ui_manager
        )
        self._ui_elements.append(title)

        # Galaxy Layout button
        self.btn_galaxy = UIButton(
            relative_rect=pygame.Rect(center_x - 150, center_y - 50, 300, 60),
            text="Galaxy Layout Test",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_galaxy)

        # Star System button
        self.btn_system = UIButton(
            relative_rect=pygame.Rect(center_x - 150, center_y + 30, 300, 60),
            text="Star System Test",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_system)

        # Close button
        self.btn_close = UIButton(
            relative_rect=pygame.Rect(center_x - 100, center_y + 120, 200, 50),
            text="Back to Menu",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_close)

    def _create_galaxy_ui(self):
        """Create UI for galaxy layout testing mode."""
        self._clear_ui()

        # Update canvas width for sidebar
        self.canvas_width = self.screen_width - self.SIDEBAR_WIDTH
        self.camera.width = self.canvas_width

        sidebar_x = self.canvas_width + 10
        y = 10

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            text="Galaxy Layout Test",
            manager=self.ui_manager
        )
        self._ui_elements.append(title)
        y += 40

        # System count label
        count_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Count:",
            manager=self.ui_manager
        )
        self._ui_elements.append(count_label)
        y += 25

        # System count slider
        self.system_count_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 80, 25),
            start_value=self.system_count,
            value_range=(10, 2500),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.system_count_slider)

        # System count value label
        self.system_count_value = UILabel(
            relative_rect=pygame.Rect(sidebar_x + self.SIDEBAR_WIDTH - 70, y, 60, 25),
            text=str(self.system_count),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.system_count_value)
        y += 35

        # Galaxy type label
        type_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Galaxy Type:",
            manager=self.ui_manager
        )
        self._ui_elements.append(type_label)
        y += 25

        # Galaxy type dropdown
        galaxy_types = sorted(list(VALID_GALAXY_TYPES))
        self.galaxy_type_dropdown = UIDropDownMenu(
            options_list=galaxy_types,
            starting_option=self.galaxy_type,
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.galaxy_type_dropdown)
        y += 40

        # Seed label
        seed_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Seed (blank=random):",
            manager=self.ui_manager
        )
        self._ui_elements.append(seed_label)
        y += 25

        # Seed input
        self.seed_input = UITextEntryLine(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            manager=self.ui_manager,
            placeholder_text="Random seed..."
        )
        self._ui_elements.append(self.seed_input)
        y += 40

        # Generate button
        self.btn_generate = UIButton(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 40),
            text="Generate Galaxy",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_generate)
        y += 50

        # Stats section
        stats_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Statistics:",
            manager=self.ui_manager
        )
        self._ui_elements.append(stats_label)
        y += 30

        # Stats display
        self.stats_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 120),
            text="No galaxy generated yet",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.stats_label)
        y += 130

        # FPS display
        self.fps_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 25),
            text="FPS: --",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.fps_label)
        y += 35

        # Back button at bottom
        self.btn_back = UIButton(
            relative_rect=pygame.Rect(sidebar_x, self.screen_height - 50, self.SIDEBAR_WIDTH - 20, 40),
            text="Back",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_back)

    def _create_system_ui(self):
        """Create UI for star system testing mode."""
        self._clear_ui()

        # Update canvas width for sidebar
        self.canvas_width = self.screen_width - self.SIDEBAR_WIDTH
        self.camera.width = self.canvas_width

        sidebar_x = self.canvas_width + 10
        y = 10

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            text="Star System Test",
            manager=self.ui_manager
        )
        self._ui_elements.append(title)
        y += 40

        # Generate button
        self.btn_generate_system = UIButton(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 40),
            text="Generate New System",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_generate_system)
        y += 50

        # System info
        self.system_info_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 300),
            text="Click 'Generate' to create a system",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.system_info_label)
        y += 310

        # FPS display
        self.fps_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 25),
            text="FPS: --",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.fps_label)

        # Back button at bottom
        self.btn_back = UIButton(
            relative_rect=pygame.Rect(sidebar_x, self.screen_height - 50, self.SIDEBAR_WIDTH - 20, 40),
            text="Back",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_back)

    def _generate_galaxy(self):
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
        self.galaxy_type = self.galaxy_type_dropdown.selected_option[0]

        log_info(f"Generating galaxy: type={self.galaxy_type}, count={self.system_count}, seed={self.galaxy_seed}")

        # Create galaxy
        start_time = time.perf_counter()

        self.galaxy = Galaxy(radius=8000)

        # Get placement strategy based on type
        from game.strategy.generation.placement_strategies import (
            RandomPlacementStrategy,
            DensityBasedPlacementStrategy
        )
        from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
        from game.strategy.generation.density.density_map import DensityMap

        rng = random.Random(self.galaxy_seed)

        if self.galaxy_type == "random":
            strategy = RandomPlacementStrategy()
        else:
            loader = GalaxyLayoutsLoader()
            layouts = loader.load()
            layout_config = loader.get_layout_config(self.galaxy_type, layouts)
            density_map = DensityMap.from_config(layout_config, self.galaxy.radius)
            strategy = DensityBasedPlacementStrategy(density_map)

        # Generate systems (positions only, no stars/planets yet)
        self.galaxy.generate_systems(
            count=self.system_count,
            min_dist=80,
            placement_strategy=strategy,
            rng=rng
        )

        # Generate warp lanes
        self.galaxy.generate_warp_lanes()

        self.generation_time = time.perf_counter() - start_time

        # Count warp connections
        warp_count = sum(len(sys.warp_points) for sys in self.galaxy.systems.values()) // 2

        # Update stats
        self.stats_label.set_text(
            f"Systems: {len(self.galaxy.systems)}\n"
            f"Warp Lanes: {warp_count}\n"
            f"Gen Time: {self.generation_time:.2f}s\n"
            f"Seed: {self.galaxy_seed}"
        )

        # Center camera on galaxy
        self._center_camera_on_galaxy()

        log_info(f"Galaxy generated: {len(self.galaxy.systems)} systems, {warp_count} warp lanes in {self.generation_time:.2f}s")

    def _generate_system(self):
        """Generate a new star system for testing."""
        from game.strategy.data.star_system import StarSystem
        from game.strategy.data.stars import StarGenerator
        from game.strategy.data.planet_gen import PlanetGenerator

        # Create a test system
        seed = random.randint(0, 2**31 - 1)
        rng = random.Random(seed)

        self.test_system = StarSystem(
            name=f"Test System {seed % 1000}",
            global_location=HexCoord(0, 0)
        )

        # Generate stars
        star_gen = StarGenerator()
        stars = star_gen.generate_system_stars(self.test_system, rng)

        # Generate planets
        planet_gen = PlanetGenerator()
        for star in stars:
            planet_gen.generate_planets_for_star(self.test_system, star, rng)

        # Build system info
        info_lines = [
            f"Name: {self.test_system.name}",
            f"Seed: {seed}",
            f"Stars: {len(self.test_system.stars)}",
            f"Planets: {len(self.test_system.planets)}",
            ""
        ]

        for star in self.test_system.stars:
            info_lines.append(f"Star: {star.name}")
            info_lines.append(f"  Type: {star.stellar_type}")
            info_lines.append(f"  Mass: {star.mass:.2f} solar")
            info_lines.append("")

        for planet in self.test_system.planets[:5]:  # Show first 5 planets
            info_lines.append(f"Planet: {planet.name}")
            info_lines.append(f"  Type: {planet.planet_type.name}")
            info_lines.append("")

        if len(self.test_system.planets) > 5:
            info_lines.append(f"... and {len(self.test_system.planets) - 5} more")

        self.system_info_label.set_text("\n".join(info_lines))

        # Reset camera for system view
        self.camera.position = pygame.math.Vector2(0, 0)
        self.camera.zoom = 1.0
        self.camera.target_zoom = 1.0

    def _center_camera_on_galaxy(self):
        """Center the camera on the generated galaxy."""
        if not self.galaxy or not self.galaxy.systems:
            return

        # Find bounds
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        for sys in self.galaxy.systems.values():
            px, py = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            min_x = min(min_x, px)
            max_x = max(max_x, px)
            min_y = min(min_y, py)
            max_y = max(max_y, py)

        # Center camera
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position = pygame.math.Vector2(center_x, center_y)

        # Fit zoom
        margin = 200
        width = max_x - min_x + margin
        height = max_y - min_y + margin

        zoom_x = self.canvas_width / width if width > 0 else 1.0
        zoom_y = self.canvas_height / height if height > 0 else 1.0
        self.camera.zoom = min(zoom_x, zoom_y)
        self.camera.target_zoom = self.camera.zoom
        self.camera.zoom = max(self.camera.min_zoom, min(self.camera.max_zoom, self.camera.zoom))

    def update(self, dt: float):
        """Update the screen."""
        self.camera.update(dt)
        self.ui_manager.update(dt)

        # Update FPS
        self.current_fps = self.fps_clock.get_fps()
        if hasattr(self, 'fps_label'):
            self.fps_label.set_text(f"FPS: {self.current_fps:.1f}")

        # Update system count display
        if self.mode == self.MODE_GALAXY and hasattr(self, 'system_count_slider'):
            current_val = int(self.system_count_slider.get_current_value())
            self.system_count_value.set_text(str(current_val))

    def draw(self, screen: pygame.Surface):
        """Draw the screen."""
        # Track FPS
        self.fps_clock.tick()

        # Clear background
        screen.fill((15, 20, 30))

        if self.mode == self.MODE_MENU:
            # Just draw UI for menu
            pass
        elif self.mode == self.MODE_GALAXY:
            self._draw_galaxy(screen)
        elif self.mode == self.MODE_SYSTEM:
            self._draw_system(screen)

        # Draw sidebar background for non-menu modes
        if self.mode != self.MODE_MENU:
            sidebar_rect = pygame.Rect(self.canvas_width, 0, self.SIDEBAR_WIDTH, self.screen_height)
            pygame.draw.rect(screen, (30, 35, 45), sidebar_rect)

        # Draw UI
        self.ui_manager.draw_ui(screen)

    def _draw_galaxy(self, screen: pygame.Surface):
        """Draw the galaxy layout (dots and warp lanes only)."""
        if not self.galaxy:
            return

        # Clip to canvas area
        canvas_rect = pygame.Rect(0, 0, self.canvas_width, self.canvas_height)
        screen.set_clip(canvas_rect)

        # Draw warp lanes first (behind systems)
        self._draw_warp_lanes(screen)

        # Draw systems as dots
        for sys in self.galaxy.systems.values():
            px, py = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            # Skip if off-screen
            if not (0 <= screen_pos.x <= self.canvas_width and 0 <= screen_pos.y <= self.canvas_height):
                continue

            # Draw dot
            radius = max(2, int(4 * self.camera.zoom))
            pygame.draw.circle(screen, (200, 200, 100), (int(screen_pos.x), int(screen_pos.y)), radius)

        # Remove clip
        screen.set_clip(None)

    def _draw_warp_lanes(self, screen: pygame.Surface):
        """Draw warp lane connections."""
        if not self.galaxy:
            return

        drawn_pairs = set()

        for sys in self.galaxy.systems.values():
            sx, sy = hex_to_pixel(sys.global_location, self.HEX_SIZE)

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
                tx, ty = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)

                scr_a = self.camera.world_to_screen(pygame.math.Vector2(sx, sy))
                scr_b = self.camera.world_to_screen(pygame.math.Vector2(tx, ty))

                # Viewport culling
                margin = 50
                if not ((-margin <= scr_a.x <= self.canvas_width + margin and
                         -margin <= scr_a.y <= self.canvas_height + margin) or
                        (-margin <= scr_b.x <= self.canvas_width + margin and
                         -margin <= scr_b.y <= self.canvas_height + margin)):
                    continue

                # Draw line
                pygame.draw.line(screen, (50, 50, 100),
                               (int(scr_a.x), int(scr_a.y)),
                               (int(scr_b.x), int(scr_b.y)), 1)

    def _draw_system(self, screen: pygame.Surface):
        """Draw the star system (stars and planets only)."""
        if not self.test_system:
            return

        # Clip to canvas area
        canvas_rect = pygame.Rect(0, 0, self.canvas_width, self.canvas_height)
        screen.set_clip(canvas_rect)

        # Draw stars
        for star in self.test_system.stars:
            px, py = hex_to_pixel(star.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            # Star size based on mass
            radius = max(10, int(star.diameter_hexes * self.HEX_SIZE * self.camera.zoom))

            # Star color
            color = star.color if hasattr(star, 'color') else (255, 255, 200)
            pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Star name
            font = pygame.font.SysFont("arial", 12)
            text = font.render(star.name, True, (200, 200, 200))
            screen.blit(text, (screen_pos.x + radius + 5, screen_pos.y - 6))

        # Draw planets
        for planet in self.test_system.planets:
            px, py = hex_to_pixel(planet.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            # Planet size
            radius = max(3, int(5 * self.camera.zoom))

            # Planet color from type
            color = planet.planet_type.color if hasattr(planet.planet_type, 'color') else (100, 150, 200)
            pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Planet name (only if zoomed in enough)
            if self.camera.zoom >= 0.5:
                font = pygame.font.SysFont("arial", 10)
                text = font.render(planet.name, True, (180, 180, 180))
                screen.blit(text, (screen_pos.x + radius + 3, screen_pos.y - 5))

        # Remove clip
        screen.set_clip(None)

    def handle_event(self, event: pygame.event):
        """Handle pygame events."""
        # Check for pygame_gui button events first
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_click(event.ui_element)
            return

        # Let pygame_gui process the event
        self.ui_manager.process_events(event)

        # ESC to go back
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == self.MODE_MENU:
                    self._on_close()
                else:
                    self._go_to_menu()
                return

        # Camera controls for non-menu modes
        if self.mode != self.MODE_MENU:
            # Pass scroll events to camera
            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if mx < self.canvas_width:
                    self.camera.update_input(0, [event])

    def _handle_button_click(self, button):
        """Handle UI button clicks."""
        if button == getattr(self, 'btn_galaxy', None):
            self._go_to_galaxy_mode()
        elif button == getattr(self, 'btn_system', None):
            self._go_to_system_mode()
        elif button == getattr(self, 'btn_close', None):
            self._on_close()
        elif button == getattr(self, 'btn_back', None):
            self._go_to_menu()
        elif button == getattr(self, 'btn_generate', None):
            self._generate_galaxy()
        elif button == getattr(self, 'btn_generate_system', None):
            self._generate_system()

    def _go_to_menu(self):
        """Return to the mode selection menu."""
        self.mode = self.MODE_MENU
        self.canvas_width = self.screen_width
        self.camera.width = self.canvas_width
        self._create_menu_ui()

    def _go_to_galaxy_mode(self):
        """Enter galaxy layout testing mode."""
        self.mode = self.MODE_GALAXY
        self._create_galaxy_ui()

    def _go_to_system_mode(self):
        """Enter star system testing mode."""
        self.mode = self.MODE_SYSTEM
        self._create_system_ui()
        # Reset camera
        self.camera.position = pygame.math.Vector2(0, 0)
        self.camera.zoom = 1.0
        self.camera.target_zoom = 1.0

    def _on_close(self):
        """Close the screen and return to main menu."""
        log_info("GalaxyTestScreen: Closing")
        if self.on_close_callback:
            self.on_close_callback()

    def handle_resize(self, width: int, height: int):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height

        if self.mode == self.MODE_MENU:
            self.canvas_width = width
        else:
            self.canvas_width = width - self.SIDEBAR_WIDTH

        self.canvas_height = height
        self.camera.width = self.canvas_width
        self.camera.height = self.canvas_height

        # Recreate UI
        self.ui_manager = pygame_gui.UIManager((width, height))

        if self.mode == self.MODE_MENU:
            self._create_menu_ui()
        elif self.mode == self.MODE_GALAXY:
            self._create_galaxy_ui()
        elif self.mode == self.MODE_SYSTEM:
            self._create_system_ui()

    def handle_input(self, dt: float, events: list):
        """Handle continuous input for camera control."""
        if self.mode != self.MODE_MENU:
            mx, my = pygame.mouse.get_pos()
            if mx < self.canvas_width:
                self.camera.update_input(dt, events)
