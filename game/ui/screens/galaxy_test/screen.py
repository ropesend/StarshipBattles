"""
Galaxy Test Screen - Testing tool for galaxy and star system generation.

Provides two modes:
1. Galaxy Layout - Test galaxy generation (system positions + warp lanes only)
2. System Inspector - Test single system generation with detailed physics inspection
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel

import logging

logger = logging.getLogger(__name__)
from game.ui.renderer.camera import Camera
from game.ui.screens.galaxy_test.constants import SIDEBAR_WIDTH
from game.ui.screens.galaxy_test.galaxy_mode import GalaxyModeHelper
from game.ui.screens.galaxy_test.system_mode import SystemModeHelper
from game.ui.colors import BG_GALAXY, PANEL_BG


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

        # Galaxy mode helper (for GALAXY mode)
        self.galaxy_helper = GalaxyModeHelper(self)

        # System mode helper (for SYSTEM mode)
        self.system_helper = SystemModeHelper(self)

        # FPS tracking
        self.fps_clock = pygame.time.Clock()
        self.current_fps = 0.0

        # UI elements (created per-mode)
        self._ui_elements = []

        # Create initial menu UI
        self._create_menu_ui()

        logger.info("GalaxyTestScreen: Initialized")

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
        self._ui_elements = self.galaxy_helper.create_ui()

    def _create_system_ui(self):
        """Create UI for System Inspector mode."""
        self._clear_ui()
        self._ui_elements = self.system_helper.create_ui()

    def update(self, dt: float):
        """Update the screen."""
        self.camera.update(dt)
        self.ui_manager.update(dt)

        # Update FPS
        self.current_fps = self.fps_clock.get_fps()
        if self.mode == self.MODE_SYSTEM:
            self.system_helper.update_fps_display(self.current_fps)

        # Update slider value displays
        if self.mode == self.MODE_GALAXY:
            self.galaxy_helper.update_slider_displays()

    def draw(self, screen: pygame.Surface):
        """Draw the screen."""
        # Track FPS
        self.fps_clock.tick()

        # Clear background
        screen.fill(BG_GALAXY)

        if self.mode == self.MODE_MENU:
            # Just draw UI for menu
            pass
        elif self.mode == self.MODE_GALAXY:
            self.galaxy_helper.draw(screen)
        elif self.mode == self.MODE_SYSTEM:
            self.system_helper.draw(screen)

        # Draw sidebar background for non-menu modes
        if self.mode != self.MODE_MENU:
            sidebar_rect = pygame.Rect(self.canvas_width, 0, SIDEBAR_WIDTH, self.screen_height)
            pygame.draw.rect(screen, PANEL_BG, sidebar_rect)

        # Draw UI
        self.ui_manager.draw_ui(screen)

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
                        self.system_helper.handle_click(mx, my)

    def _handle_button_click(self, button):
        """Handle UI button clicks."""
        if button == getattr(self, 'btn_galaxy', None):
            self._go_to_galaxy_mode()
        elif button == getattr(self, 'btn_system', None):
            self._go_to_system_mode()
        elif button == getattr(self, 'btn_close', None):
            self._on_close()
        elif button == getattr(self.system_helper, 'btn_back', None) or button == getattr(self.galaxy_helper, 'btn_back', None):
            self._go_to_menu()
        elif button == getattr(self.galaxy_helper, 'btn_generate', None):
            self.galaxy_helper.generate()
        elif button == getattr(self.system_helper, 'btn_generate_system', None):
            self.system_helper.generate()

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
        logger.info("GalaxyTestScreen: Closing")
        if self.on_close_callback:
            self.on_close_callback()

    def handle_resize(self, width: int, height: int):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height

        if self.mode == self.MODE_MENU:
            self.canvas_width = width
        else:
            self.canvas_width = width - SIDEBAR_WIDTH

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
