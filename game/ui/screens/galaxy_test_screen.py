"""
Galaxy Test Screen - Testing tool for galaxy and star system generation.

Provides two modes:
1. Galaxy Layout - Test galaxy generation (system positions + warp lanes only)
2. System Inspector - Test single system generation with detailed physics inspection
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
from game.strategy.data.planet import PlanetType


# Planet type colors for visualization
PLANET_TYPE_COLORS = {
    PlanetType.CONTINENTAL: (70, 130, 70),   # Green-ish (Earth-like)
    PlanetType.ARID: (180, 140, 80),         # Sandy brown
    PlanetType.PELAGIC: (50, 80, 180),       # Deep blue (Ocean)
    PlanetType.MAGMA: (200, 50, 30),         # Red-orange (Lava)
    PlanetType.CRYOPLANET: (180, 200, 220),  # Ice white-blue
    PlanetType.BARREN: (130, 130, 130),      # Grey (Rock)
    PlanetType.JOVIAN: (200, 160, 100),      # Jupiter tan
    PlanetType.ICE_GIANT: (100, 150, 200),   # Neptune blue
    PlanetType.CHTHONIAN: (100, 80, 60),     # Dark brown
    PlanetType.ICE_DWARF: (200, 210, 230),   # Light ice
    PlanetType.PLANETOID: (90, 90, 90),      # Dark grey
}


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
        # min_zoom=0.0003 allows viewing 100,000 hex radius (2M pixel world) on ~1600px canvas
        self.camera = Camera(self.canvas_width, self.canvas_height)
        self.camera.min_zoom = 0.0003
        self.camera.max_zoom = 3.0
        self.camera.zoom = 0.1
        self.camera.target_zoom = 0.1

        # UI Manager
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height))

        # Galaxy data (for GALAXY mode)
        self.galaxy = None
        self.generation_time = 0.0
        self.system_count = 100
        self.galaxy_radius = 4000  # Galaxy radius in hex units (matches GameConfig default)
        self.galaxy_type = "spiral"
        self.galaxy_seed = None

        # Star system data (for SYSTEM mode)
        self.test_system = None
        self.system_seed = None
        self.selected_blueprint = "random"  # Blueprint selection
        self.selected_object = None  # Currently selected star or planet for inspection

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

        # Galaxy radius label
        radius_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Galaxy Radius (hexes):",
            manager=self.ui_manager
        )
        self._ui_elements.append(radius_label)
        y += 25

        # Galaxy radius slider (star systems are ~101 hexes across, need spacing)
        self.galaxy_radius_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 80, 25),
            start_value=self.galaxy_radius,
            value_range=(500, 100000),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.galaxy_radius_slider)

        # Galaxy radius value label
        self.galaxy_radius_value = UILabel(
            relative_rect=pygame.Rect(sidebar_x + self.SIDEBAR_WIDTH - 70, y, 60, 25),
            text=str(self.galaxy_radius),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.galaxy_radius_value)
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
        """Create UI for System Inspector mode."""
        self._clear_ui()

        # Update canvas width for sidebar
        self.canvas_width = self.screen_width - self.SIDEBAR_WIDTH
        self.camera.width = self.canvas_width

        sidebar_x = self.canvas_width + 10
        y = 10

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            text="System Inspector",
            manager=self.ui_manager
        )
        self._ui_elements.append(title)
        y += 40

        # Blueprint label
        blueprint_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Blueprint:",
            manager=self.ui_manager
        )
        self._ui_elements.append(blueprint_label)
        y += 25

        # Blueprint dropdown - load available blueprints
        blueprint_options = self._get_blueprint_options()
        self.blueprint_dropdown = UIDropDownMenu(
            options_list=blueprint_options,
            starting_option=self.selected_blueprint,
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            manager=self.ui_manager
        )
        self._ui_elements.append(self.blueprint_dropdown)
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
        self.system_seed_input = UITextEntryLine(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 30),
            manager=self.ui_manager,
            placeholder_text="Random seed..."
        )
        self._ui_elements.append(self.system_seed_input)
        y += 40

        # Generate button
        self.btn_generate_system = UIButton(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 40),
            text="Generate System",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.btn_generate_system)
        y += 50

        # Separator line (just a label)
        sep_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 5),
            text="─" * 30,
            manager=self.ui_manager
        )
        self._ui_elements.append(sep_label)
        y += 15

        # System info section
        info_header = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Info:",
            manager=self.ui_manager
        )
        self._ui_elements.append(info_header)
        y += 25

        # System info display
        self.system_info_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 100),
            text="Click 'Generate' to create a system",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.system_info_label)
        y += 110

        # Inspector section (shows selected object details)
        inspector_header = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Inspector (click object):",
            manager=self.ui_manager
        )
        self._ui_elements.append(inspector_header)
        y += 25

        # Inspector panel (multi-line display for selected object)
        self.inspector_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, self.SIDEBAR_WIDTH - 20, 200),
            text="No object selected.\nClick a star or planet to inspect.",
            manager=self.ui_manager
        )
        self._ui_elements.append(self.inspector_label)
        y += 210

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

    def _get_blueprint_options(self):
        """Get list of available system blueprint names."""
        try:
            from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
            loader = SystemBlueprintsLoader()
            data = loader.load()
            blueprints = list(data.get("blueprints", {}).keys())
            # Add "random" option at the start
            return ["random"] + sorted(blueprints)
        except Exception as e:
            log_info(f"Failed to load blueprints: {e}")
            return ["random"]

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
        self.galaxy_radius = int(self.galaxy_radius_slider.get_current_value())
        self.galaxy_type = self.galaxy_type_dropdown.selected_option[0]

        log_info(f"Generating galaxy: type={self.galaxy_type}, count={self.system_count}, radius={self.galaxy_radius}, seed={self.galaxy_seed}")

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
        log_info(f"  Strategy setup: {t2-t1:.3f}s")

        # Generate systems (positions only, no stars/planets yet)
        # min_dist=400 matches production GameSession (star systems are ~101 hexes across)
        self.galaxy.generate_systems(
            count=self.system_count,
            min_dist=400,
            placement_strategy=strategy,
            rng=rng
        )
        t3 = time.perf_counter()
        log_info(f"  System placement: {t3-t2:.3f}s")

        # Generate warp lanes
        self.galaxy.generate_warp_lanes()
        t4 = time.perf_counter()
        log_info(f"  Warp lane generation: {t4-t3:.3f}s")

        self.generation_time = time.perf_counter() - start_time
        log_info(f"  Total generation: {self.generation_time:.3f}s")

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
        self._center_camera_on_galaxy()
        t6 = time.perf_counter()
        log_info(f"  Camera centering: {t6-t5:.3f}s")

        log_info(f"Galaxy generated: {len(self.galaxy.systems)} systems, {warp_count} warp lanes in {self.generation_time:.2f}s")

    def _generate_system(self):
        """Generate a new star system using selected blueprint and seed."""
        from game.strategy.data.galaxy import StarSystem
        from game.strategy.data.stars import StarGenerator
        from game.strategy.data.planet_gen import PlanetGenerator
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader

        # Get seed from input or generate random
        seed_text = self.system_seed_input.get_text().strip()
        if seed_text:
            try:
                self.system_seed = int(seed_text)
            except ValueError:
                self.system_seed = hash(seed_text) % (2**31)
        else:
            self.system_seed = random.randint(0, 2**31 - 1)

        rng = random.Random(self.system_seed)

        # Get selected blueprint
        self.selected_blueprint = self.blueprint_dropdown.selected_option[0]

        # Create system
        self.test_system = StarSystem(
            name=f"Test System {self.system_seed % 1000}",
            global_location=HexCoord(0, 0)
        )

        # Load blueprint if not random
        blueprint = None
        if self.selected_blueprint != "random":
            try:
                loader = SystemBlueprintsLoader()
                data = loader.load()
                blueprint = loader.get_blueprint(self.selected_blueprint, data)
            except Exception as e:
                log_info(f"Failed to load blueprint '{self.selected_blueprint}': {e}")

        # Generate stars
        star_gen = StarGenerator()
        if blueprint:
            stars = star_gen.generate_from_blueprint(self.test_system.name, blueprint)
        else:
            stars = star_gen.generate_system_stars(self.test_system.name)

        # Add stars to system
        for star in stars:
            self.test_system.stars.append(star)

        # Generate planets with blueprint constraints
        planet_gen = PlanetGenerator()
        planets = planet_gen.generate_system_bodies(
            self.test_system.name,
            self.test_system.stars,
            blueprint  # Pass blueprint for planet_count, planet_mass constraints
        )
        for planet in planets:
            self.test_system.planets.append(planet)

        # Clear selection
        self.selected_object = None

        # Build system info
        blueprint_name = self.selected_blueprint if self.selected_blueprint != "random" else "Random"
        info_lines = [
            f"Name: {self.test_system.name}",
            f"Blueprint: {blueprint_name}",
            f"Seed: {self.system_seed}",
            f"Stars: {len(self.test_system.stars)}",
            f"Planets: {len(self.test_system.planets)}",
        ]

        self.system_info_label.set_text("\n".join(info_lines))
        self.inspector_label.set_text("No object selected.\nClick a star or planet to inspect.")

        # Center camera on system and fit to view
        self._center_camera_on_system()

        log_info(f"Generated system: {self.test_system.name}, blueprint={blueprint_name}, stars={len(self.test_system.stars)}, planets={len(self.test_system.planets)}")

    def _center_camera_on_system(self):
        """Center the camera on the generated star system."""
        if not self.test_system:
            return

        # Find bounds of all objects
        all_objects = list(self.test_system.stars) + list(self.test_system.planets)
        if not all_objects:
            return

        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        for obj in all_objects:
            px, py = hex_to_pixel(obj.location, self.HEX_SIZE)
            min_x = min(min_x, px)
            max_x = max(max_x, px)
            min_y = min(min_y, py)
            max_y = max(max_y, py)

        # Center camera
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position = pygame.math.Vector2(center_x, center_y)

        # Fit zoom (with padding)
        margin = 200
        width = max_x - min_x + margin
        height = max_y - min_y + margin

        zoom_x = self.canvas_width / width if width > 0 else 1.0
        zoom_y = self.canvas_height / height if height > 0 else 1.0
        self.camera.zoom = min(zoom_x, zoom_y, 2.0)  # Cap at 2x
        self.camera.zoom = max(0.1, self.camera.zoom)  # Floor at 0.1x
        self.camera.target_zoom = self.camera.zoom

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

    def _handle_system_click(self, mx: int, my: int):
        """Handle click in system view to select objects for inspection."""
        if not self.test_system:
            return

        click_pos = pygame.math.Vector2(mx, my)
        best_match = None
        best_dist = float('inf')
        click_threshold = 20  # Pixels

        # Check stars first (larger, higher priority)
        for star in self.test_system.stars:
            px, py = hex_to_pixel(star.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            dist = (click_pos - screen_pos).length()
            star_radius = max(8, int(star.diameter_hexes * self.HEX_SIZE * self.camera.zoom * 0.5))

            if dist < star_radius + click_threshold and dist < best_dist:
                best_match = star
                best_dist = dist

        # Check planets
        for planet in self.test_system.planets:
            px, py = hex_to_pixel(planet.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            dist = (click_pos - screen_pos).length()

            if dist < click_threshold and dist < best_dist:
                best_match = planet
                best_dist = dist

        # Update selection
        self.selected_object = best_match
        self._update_inspector_panel()

    def _update_inspector_panel(self):
        """Update the inspector panel with selected object's physics data."""
        if not hasattr(self, 'inspector_label'):
            return

        if self.selected_object is None:
            self.inspector_label.set_text("No object selected.\nClick a star or planet to inspect.")
            return

        from game.strategy.data.stars import Star
        from game.strategy.data.planet import Planet

        obj = self.selected_object
        lines = []

        if isinstance(obj, Star):
            lines = self._format_star_info(obj)
        elif isinstance(obj, Planet):
            lines = self._format_planet_info(obj)

        self.inspector_label.set_text("\n".join(lines))

    def _format_star_info(self, star) -> list:
        """Format star properties for display."""
        lines = [
            f"★ {star.name}",
            f"Type: {star.star_type.name}",
            f"Mass: {star.mass:.3f} M☉",
            f"Temp: {star.temperature:.0f} K",
            f"Luminosity: {star.luminosity:.3f} L☉",
            f"Diameter: {star.diameter_hexes:.1f} hexes",
            f"Age: {star.age/1e9:.2f} Gyr",
        ]

        # Add spectrum summary
        spec = star.spectrum
        visible = spec.blue + spec.green + spec.red
        total = spec.get_total_output()
        if total > 0:
            lines.append(f"Visible %: {100*visible/total:.1f}%")

        return lines

    def _format_planet_info(self, planet) -> list:
        """Format planet properties for display with physics derivation."""
        from game.strategy.data.planet_physics import (
            calculate_escape_velocity,
            calculate_surface_gravity,
            MASS_EARTH
        )

        lines = [
            f"● {planet.name}",
            f"Type: {planet.planet_type.name}",
            "",
            "=== Physical Properties ===",
            f"Mass: {planet.mass:.2e} kg",
            f"  ({planet.mass/MASS_EARTH:.3f} M⊕)",
            f"Radius: {planet.radius:.2e} m",
            f"  ({planet.radius/6.371e6:.3f} R⊕)",
            f"Density: {planet.density:.0f} kg/m³",
        ]

        # Derived values
        g = planet.surface_gravity
        v_esc = calculate_escape_velocity(planet.mass, planet.radius)

        lines.extend([
            "",
            "=== Derived ===",
            f"Surface g: {g:.2f} m/s²",
            f"  ({g/9.81:.2f} g)",
            f"Escape v: {v_esc:.0f} m/s",
        ])

        # Surface conditions
        lines.extend([
            "",
            "=== Surface Conditions ===",
            f"Temp: {planet.surface_temperature:.0f} K",
            f"  ({planet.surface_temperature - 273:.0f} °C)",
            f"Pressure: {planet.surface_pressure:.0f} Pa",
            f"  ({planet.surface_pressure/101325:.3f} atm)",
            f"Water: {planet.surface_water*100:.1f}%",
        ])

        # Atmosphere (top gases)
        if planet.atmosphere:
            lines.append("")
            lines.append("=== Atmosphere ===")
            sorted_gases = sorted(planet.atmosphere.items(), key=lambda x: x[1], reverse=True)
            for gas, pressure in sorted_gases[:3]:
                lines.append(f"  {gas}: {pressure:.0f} Pa")

        # Classification reasoning
        lines.append("")
        lines.append("=== Classification ===")
        lines.append(self._get_classification_reason(planet))

        return lines

    def _get_classification_reason(self, planet) -> str:
        """Get a brief explanation of why the planet has its classification."""
        ptype = planet.planet_type

        reasons = {
            PlanetType.JOVIAN: f"Mass > 1e26 kg (gas giant)",
            PlanetType.ICE_GIANT: f"Mass 1e25-1e26 kg range",
            PlanetType.CONTINENTAL: f"Earth-like: 255-330K, water 10-85%",
            PlanetType.ARID: f"Low water (<20%) at habitable temp",
            PlanetType.PELAGIC: f"High water (>85%) ocean world",
            PlanetType.MAGMA: f"Extreme heat (>700K) or activity",
            PlanetType.CRYOPLANET: f"Cold (<255K) with volatiles",
            PlanetType.BARREN: f"Rocky with minimal atmosphere",
            PlanetType.CHTHONIAN: f"Stripped giant core",
            PlanetType.ICE_DWARF: f"Small, cold, icy (<170K)",
            PlanetType.PLANETOID: f"Mass < dwarf threshold",
        }

        return reasons.get(ptype, "Unknown classification")

    def update(self, dt: float):
        """Update the screen."""
        self.camera.update(dt)
        self.ui_manager.update(dt)

        # Update FPS
        self.current_fps = self.fps_clock.get_fps()
        if hasattr(self, 'fps_label'):
            self.fps_label.set_text(f"FPS: {self.current_fps:.1f}")

        # Update slider value displays
        if self.mode == self.MODE_GALAXY:
            if hasattr(self, 'system_count_slider'):
                current_val = int(self.system_count_slider.get_current_value())
                self.system_count_value.set_text(str(current_val))
            if hasattr(self, 'galaxy_radius_slider'):
                current_val = int(self.galaxy_radius_slider.get_current_value())
                self.galaxy_radius_value.set_text(str(current_val))

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
        """Draw the star system with orbital rings, stars, and planets."""
        if not self.test_system:
            return

        # Clip to canvas area
        canvas_rect = pygame.Rect(0, 0, self.canvas_width, self.canvas_height)
        screen.set_clip(canvas_rect)

        # Get system center (primary star location)
        center_hex = HexCoord(0, 0)
        center_px, center_py = hex_to_pixel(center_hex, self.HEX_SIZE)
        center_screen = self.camera.world_to_screen(pygame.math.Vector2(center_px, center_py))

        # Draw orbital rings for each unique orbit distance
        orbit_distances = set(p.orbit_distance for p in self.test_system.planets)
        for orbit_dist in orbit_distances:
            # Orbit radius in pixels (orbit_distance is in hex rings)
            orbit_radius = orbit_dist * self.HEX_SIZE * self.camera.zoom
            if orbit_radius > 5:  # Only draw if visible
                pygame.draw.circle(
                    screen,
                    (40, 45, 55),  # Dark grey orbit ring
                    (int(center_screen.x), int(center_screen.y)),
                    int(orbit_radius),
                    1  # Line width
                )

        # Draw stars
        for star in self.test_system.stars:
            px, py = hex_to_pixel(star.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            # Star size based on diameter in hexes
            radius = max(8, int(star.diameter_hexes * self.HEX_SIZE * self.camera.zoom * 0.5))

            # Star color
            color = star.color if hasattr(star, 'color') else (255, 255, 200)

            # Draw glow effect
            glow_radius = radius + 4
            glow_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.circle(screen, glow_color, (int(screen_pos.x), int(screen_pos.y)), glow_radius)
            pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Selection highlight
            if self.selected_object == star:
                pygame.draw.circle(screen, (255, 255, 0), (int(screen_pos.x), int(screen_pos.y)), radius + 6, 2)

            # Star name label
            font = pygame.font.SysFont("arial", 12)
            text = font.render(star.name, True, (220, 220, 220))
            screen.blit(text, (screen_pos.x + radius + 5, screen_pos.y - 6))

        # Draw planets
        for planet in self.test_system.planets:
            px, py = hex_to_pixel(planet.location, self.HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.camera.world_to_screen(world_pos)

            # Planet size based on radius (normalized)
            # Use log scale for better visualization of size differences
            base_size = 4
            if planet.radius > 1e7:  # Gas giant range
                base_size = 10
            elif planet.radius > 5e6:  # Super-earth range
                base_size = 7
            elif planet.radius > 1e6:  # Earth-like
                base_size = 5
            radius = max(3, int(base_size * self.camera.zoom))

            # Planet color from type
            color = PLANET_TYPE_COLORS.get(planet.planet_type, (100, 150, 200))
            pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Selection highlight
            if self.selected_object == planet:
                pygame.draw.circle(screen, (255, 255, 0), (int(screen_pos.x), int(screen_pos.y)), radius + 4, 2)

            # Planet name label (only if zoomed in enough)
            if self.camera.zoom >= 0.3:
                font = pygame.font.SysFont("arial", 10)
                text = font.render(planet.name, True, (180, 180, 180))
                screen.blit(text, (screen_pos.x + radius + 3, screen_pos.y - 5))

        # Remove clip
        screen.set_clip(None)

    def handle_event(self, event: pygame.event):
        """Handle pygame events."""
        # Let pygame_gui process ALL events first (needed for dropdowns, sliders, etc.)
        self.ui_manager.process_events(event)

        # Then check for pygame_gui generated events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_click(event.ui_element)
            return

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

            # Click detection for system inspector
            if self.mode == self.MODE_SYSTEM and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    if mx < self.canvas_width:  # Only in canvas area
                        self._handle_system_click(mx, my)

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
