"""
System Mode Helper - Handles star system inspector functionality.

Extracts system generation, inspection, rendering, and UI management from the main screen.
"""
import json
import random
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIDropDownMenu

import logging

from game.ui.fonts import get_font
from game.ui.colors import TEXT_LIGHT, TEXT_MUTED, FLEET_SELECTED, GRID_LINE, PLANET_TERRESTRIAL, STAR_FALLBACK

logger = logging.getLogger(__name__)
from game.core.hex_math import hex_to_pixel, HexCoord
from game.strategy.data.planet import PlanetType
from game.ui.screens.galaxy_test.constants import PLANET_TYPE_COLORS, SIDEBAR_WIDTH, HEX_SIZE


class SystemModeHelper:
    """
    Helper class for star system inspector mode.

    Manages system generation, object selection/inspection, UI elements,
    and rendering for the system inspector mode of GalaxyTestScreen.
    """

    def __init__(self, screen):
        """
        Initialize the system mode helper.

        Args:
            screen: Parent GalaxyTestScreen instance for accessing camera,
                   ui_manager, and canvas dimensions.
        """
        self.screen = screen

        # System state
        self.test_system = None
        self.system_seed = None
        self.selected_blueprint = "random"
        self.selected_object = None  # Currently selected star or planet for inspection

        # UI element references (set during create_ui)
        self.blueprint_dropdown = None
        self.system_seed_input = None
        self.btn_generate_system = None
        self.system_info_label = None
        self.inspector_label = None
        self.fps_label = None
        self.btn_back = None

    def create_ui(self) -> list:
        """
        Create UI elements for system inspector mode.

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
            text="System Inspector",
            manager=self.screen.ui_manager
        )
        elements.append(title)
        y += 40

        # Blueprint label
        blueprint_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Blueprint:",
            manager=self.screen.ui_manager
        )
        elements.append(blueprint_label)
        y += 25

        # Blueprint dropdown - load available blueprints
        blueprint_options = self._get_blueprint_options()
        self.blueprint_dropdown = UIDropDownMenu(
            options_list=blueprint_options,
            starting_option=self.selected_blueprint,
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 30),
            manager=self.screen.ui_manager
        )
        elements.append(self.blueprint_dropdown)
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
        self.system_seed_input = UITextEntryLine(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 30),
            manager=self.screen.ui_manager,
            placeholder_text="Random seed..."
        )
        elements.append(self.system_seed_input)
        y += 40

        # Generate button
        self.btn_generate_system = UIButton(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 40),
            text="Generate System",
            manager=self.screen.ui_manager
        )
        elements.append(self.btn_generate_system)
        y += 50

        # Separator line (just a label)
        sep_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 5),
            text="─" * 30,
            manager=self.screen.ui_manager
        )
        elements.append(sep_label)
        y += 15

        # System info section
        info_header = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="System Info:",
            manager=self.screen.ui_manager
        )
        elements.append(info_header)
        y += 25

        # System info display
        self.system_info_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 100),
            text="Click 'Generate' to create a system",
            manager=self.screen.ui_manager
        )
        elements.append(self.system_info_label)
        y += 110

        # Inspector section (shows selected object details)
        inspector_header = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, 150, 25),
            text="Inspector (click object):",
            manager=self.screen.ui_manager
        )
        elements.append(inspector_header)
        y += 25

        # Inspector panel (multi-line display for selected object)
        self.inspector_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 200),
            text="No object selected.\nClick a star or planet to inspect.",
            manager=self.screen.ui_manager
        )
        elements.append(self.inspector_label)
        y += 210

        # FPS display
        self.fps_label = UILabel(
            relative_rect=pygame.Rect(sidebar_x, y, SIDEBAR_WIDTH - 20, 25),
            text="FPS: --",
            manager=self.screen.ui_manager
        )
        elements.append(self.fps_label)

        # Back button at bottom
        self.btn_back = UIButton(
            relative_rect=pygame.Rect(sidebar_x, self.screen.screen_height - 50, SIDEBAR_WIDTH - 20, 40),
            text="Back",
            manager=self.screen.ui_manager
        )
        elements.append(self.btn_back)

        return elements

    def _get_blueprint_options(self) -> list:
        """Get list of available system blueprint names."""
        try:
            from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
            loader = SystemBlueprintsLoader()
            data = loader.load()
            blueprints = list(data.get("blueprints", {}).keys())
            # Add "random" option at the start
            return ["random"] + sorted(blueprints)
        except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load blueprints: {e}")
            return ["random"]

    def generate(self):
        """Generate a new star system using selected blueprint and seed."""
        from game.strategy.data.galaxy import StarSystem
        from game.strategy.data.stars import StarGenerator
        from game.strategy.data.planet_gen import PlanetGenerator
        from game.strategy.generation.planet_image_registry import PlanetImageRegistry
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
            except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load blueprint '{self.selected_blueprint}': {e}")

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
        image_registry = PlanetImageRegistry()
        planet_gen = PlanetGenerator(image_registry)
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
        self._center_camera()

        logger.info(f"Generated system: {self.test_system.name}, blueprint={blueprint_name}, stars={len(self.test_system.stars)}, planets={len(self.test_system.planets)}")

    def _center_camera(self):
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
            px, py = hex_to_pixel(obj.location, HEX_SIZE)
            min_x = min(min_x, px)
            max_x = max(max_x, px)
            min_y = min(min_y, py)
            max_y = max(max_y, py)

        # Center camera
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.screen.camera.position = pygame.math.Vector2(center_x, center_y)

        # Fit zoom (with padding)
        margin = 200
        width = max_x - min_x + margin
        height = max_y - min_y + margin

        zoom_x = self.screen.canvas_width / width if width > 0 else 1.0
        zoom_y = self.screen.canvas_height / height if height > 0 else 1.0
        self.screen.camera.zoom = min(zoom_x, zoom_y, 2.0)  # Cap at 2x
        self.screen.camera.zoom = max(0.1, self.screen.camera.zoom)  # Floor at 0.1x
        self.screen.camera.target_zoom = self.screen.camera.zoom

    def handle_click(self, mx: int, my: int):
        """Handle click in system view to select objects for inspection."""
        if not self.test_system:
            return

        click_pos = pygame.math.Vector2(mx, my)
        best_match = None
        best_dist = float('inf')
        click_threshold = 20  # Pixels

        # Check stars first (larger, higher priority)
        for star in self.test_system.stars:
            px, py = hex_to_pixel(star.location, HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.screen.camera.world_to_screen(world_pos)

            dist = (click_pos - screen_pos).length()
            star_radius = max(8, int(star.diameter_hexes * HEX_SIZE * self.screen.camera.zoom * 0.5))

            if dist < star_radius + click_threshold and dist < best_dist:
                best_match = star
                best_dist = dist

        # Check planets
        for planet in self.test_system.planets:
            px, py = hex_to_pixel(planet.location, HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.screen.camera.world_to_screen(world_pos)

            dist = (click_pos - screen_pos).length()

            if dist < click_threshold and dist < best_dist:
                best_match = planet
                best_dist = dist

        # Update selection
        self.selected_object = best_match
        self._update_inspector_panel()

    def _update_inspector_panel(self):
        """Update the inspector panel with selected object's physics data."""
        if self.inspector_label is None:
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

    def draw(self, screen_surface: pygame.Surface):
        """Draw the star system with orbital rings, stars, and planets."""
        if not self.test_system:
            return

        # Clip to canvas area
        canvas_rect = pygame.Rect(0, 0, self.screen.canvas_width, self.screen.canvas_height)
        screen_surface.set_clip(canvas_rect)

        # Get system center (primary star location)
        center_hex = HexCoord(0, 0)
        center_px, center_py = hex_to_pixel(center_hex, HEX_SIZE)
        center_screen = self.screen.camera.world_to_screen(pygame.math.Vector2(center_px, center_py))

        # Draw orbital rings for each unique orbit distance
        orbit_distances = set(p.orbit_distance for p in self.test_system.planets)
        for orbit_dist in orbit_distances:
            # Orbit radius in pixels (orbit_distance is in hex rings)
            orbit_radius = orbit_dist * HEX_SIZE * self.screen.camera.zoom
            if orbit_radius > 5:  # Only draw if visible
                pygame.draw.circle(
                    screen_surface,
                    GRID_LINE,  # Dark grey orbit ring
                    (int(center_screen.x), int(center_screen.y)),
                    int(orbit_radius),
                    1  # Line width
                )

        # Draw stars
        for star in self.test_system.stars:
            px, py = hex_to_pixel(star.location, HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.screen.camera.world_to_screen(world_pos)

            # Star size based on diameter in hexes
            radius = max(8, int(star.diameter_hexes * HEX_SIZE * self.screen.camera.zoom * 0.5))

            # Star color
            color = star.color if hasattr(star, 'color') else STAR_FALLBACK

            # Draw glow effect
            glow_radius = radius + 4
            glow_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.circle(screen_surface, glow_color, (int(screen_pos.x), int(screen_pos.y)), glow_radius)
            pygame.draw.circle(screen_surface, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Selection highlight
            if self.selected_object == star:
                pygame.draw.circle(screen_surface, FLEET_SELECTED, (int(screen_pos.x), int(screen_pos.y)), radius + 6, 2)

            # Star name label
            font = get_font(12)
            text = font.render(star.name, True, TEXT_LIGHT)
            screen_surface.blit(text, (screen_pos.x + radius + 5, screen_pos.y - 6))

        # Draw planets
        for planet in self.test_system.planets:
            px, py = hex_to_pixel(planet.location, HEX_SIZE)
            world_pos = pygame.math.Vector2(px, py)
            screen_pos = self.screen.camera.world_to_screen(world_pos)

            # Planet size based on radius (normalized)
            # Use log scale for better visualization of size differences
            base_size = 4
            if planet.radius > 1e7:  # Gas giant range
                base_size = 10
            elif planet.radius > 5e6:  # Super-earth range
                base_size = 7
            elif planet.radius > 1e6:  # Earth-like
                base_size = 5
            radius = max(3, int(base_size * self.screen.camera.zoom))

            # Planet color from type
            color = PLANET_TYPE_COLORS.get(planet.planet_type, PLANET_TERRESTRIAL)
            pygame.draw.circle(screen_surface, color, (int(screen_pos.x), int(screen_pos.y)), radius)

            # Selection highlight
            if self.selected_object == planet:
                pygame.draw.circle(screen_surface, FLEET_SELECTED, (int(screen_pos.x), int(screen_pos.y)), radius + 4, 2)

            # Planet name label (only if zoomed in enough)
            if self.screen.camera.zoom >= 0.3:
                font = get_font(10)
                text = font.render(planet.name, True, TEXT_MUTED)
                screen_surface.blit(text, (screen_pos.x + radius + 3, screen_pos.y - 5))

        # Remove clip
        screen_surface.set_clip(None)

    def update_fps_display(self, fps: float):
        """Update the FPS display label."""
        if self.fps_label:
            self.fps_label.set_text(f"FPS: {fps:.1f}")
