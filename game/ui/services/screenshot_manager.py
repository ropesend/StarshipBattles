"""
Screenshot Manager - Singleton for capturing screenshots.

DUP-UI2-001: Clipboard copy now uses shared tkinter_utils module.
"""
import os
import datetime
import subprocess

import pygame

from game.core.constants import ENABLE_SCREENSHOTS
from game.core.paths import Paths
import logging

logger = logging.getLogger(__name__)
from game.core.singleton import SingletonMeta
from game.ui.services.tkinter_utils import copy_to_clipboard


class ScreenshotManager(metaclass=SingletonMeta):
    """
    Singleton manager for capturing screenshots.

    Thread Safety:
        - Instance creation is thread-safe via SingletonMeta

    Usage:
        manager = ScreenshotManager.instance()
        manager.capture(surface, label="battle_end")

    Testing:
        - Use reset() to destroy instance completely
    """

    def __init__(self):
        self._setup()

    def _setup(self):
        self.enabled = ENABLE_SCREENSHOTS
        self.base_dir = Paths.SCREENSHOTS_DIR
        if self.enabled and not os.path.exists(self.base_dir):
            try:
                os.makedirs(self.base_dir)
                logger.info(f"Created screenshot directory: {self.base_dir}")
            except OSError as e:
                logger.error(f"Failed to create screenshot directory: {e}")
                self.enabled = False

    def capture(self, surface=None, region=None, label=None):
        """Capture a screenshot.

        Args:
            surface: The surface to capture. If None, captures the main display.
            region: Optional pygame.Rect to crop the screenshot.
            label: Optional label to append to the filename.
        """
        if not self.enabled:
            return

        if surface is None:
            surface = pygame.display.get_surface()

        if surface is None:
            logger.warning("Screenshot failed: No display surface found.")
            return

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}"
            if label:
                filename += f"_{label}"
            filename += ".png"
            
            filepath = os.path.join(self.base_dir, filename)

            if region:
                # Handle region clipping
                # Ensure region is valid for the surface
                surf_rect = surface.get_rect()
                clip_rect = region.clip(surf_rect)
                
                if clip_rect.width > 0 and clip_rect.height > 0:
                    sub_surface = surface.subsurface(clip_rect)
                    pygame.image.save(sub_surface, filepath)
                else:
                    logger.warning(f"Screenshot region {region} is outside surface bounds {surf_rect}.")
                    return
            else:
                pygame.image.save(surface, filepath)

            abs_path = os.path.abspath(filepath)
            logger.info(f"Screenshot saved: {abs_path}")
            self._copy_to_clipboard(abs_path)

        except (pygame.error, IOError, OSError) as e:
            logger.error(f"Error saving screenshot to {filepath}: {e}")

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard using Tkinter or Windows clip.

        Args:
            text: Text to copy to clipboard (typically a file path)
        """
        # Try Tkinter first (cross-platform if available)
        if copy_to_clipboard(text):
            return

        # Fallback to Windows clip using subprocess (safer than os.system)
        if os.name == 'nt':
            try:
                # Use subprocess.run with input instead of shell command
                # This avoids command injection vulnerabilities
                subprocess.run(
                    ['clip'],
                    input=text.strip().encode('utf-8'),
                    check=False
                )
            except Exception as clip_err:  # Intentional broad catch: subprocess clipboard fallback, platform-dependent
                logger.warning(f"Clipboard copy failed (clip): {clip_err}")

    def capture_strategy_layer(self, scene, include_ui=True, include_subwindows=True, label=None):
        """Capture a screenshot of the strategy layer with control over which layers are included.

        This method renders the strategy scene to a temporary surface and captures it,
        allowing selective inclusion of UI panels and sub-windows.

        Args:
            scene: The StrategyScreen instance to capture.
            include_ui: Whether to include UI panels (sidebar, top bar). Default True.
            include_subwindows: Whether to include modal sub-windows. Default True.
            label: Optional label to append to the filename.
        """
        if not self.enabled:
            return

        try:
            screen_width = scene.screen_width
            screen_height = scene.screen_height

            if include_ui:
                # Capture full screen with all layers
                capture_surface = pygame.Surface((screen_width, screen_height))

                # Draw the base strategy layer (galaxy map)
                scene._renderer.draw(capture_surface)

                # Draw UI layer - StrategyScreen always has .ui
                if scene.ui:
                    scene.ui.draw(capture_surface)

                # Draw sub-windows if requested
                if include_subwindows:
                    # Check for active sub-window screens
                    if scene.build_queue_screen:
                        scene.build_queue_screen.draw(capture_surface)

                self.capture(surface=capture_surface, label=label)
            else:
                # Capture viewport only (exclude sidebar and top bar)
                # StrategyScreen always has these class constants
                sidebar_width = scene.SIDEBAR_WIDTH
                top_bar_height = scene.TOP_BAR_HEIGHT

                viewport_width = screen_width - sidebar_width
                viewport_height = screen_height - top_bar_height

                if viewport_width > 0 and viewport_height > 0:
                    capture_surface = pygame.Surface((viewport_width, viewport_height))

                    # Draw only the galaxy map portion
                    full_surface = pygame.Surface((screen_width, screen_height))
                    scene._renderer.draw(full_surface)

                    # Blit the viewport region to our capture surface
                    viewport_rect = pygame.Rect(0, top_bar_height, viewport_width, viewport_height)
                    capture_surface.blit(full_surface, (0, 0), viewport_rect)

                    self.capture(surface=capture_surface, label=label)
                else:
                    logger.warning("Cannot capture viewport: invalid dimensions")

        except (pygame.error, IOError, OSError, AttributeError) as e:
            logger.error(f"Error capturing strategy layer: {e}")

    def show_toast(
        self,
        manager,
        screen_width: int,
        message: str = "Screenshot saved!",
        y_pos: int = 80
    ) -> None:
        """Show a brief toast notification for screenshot feedback.

        DUP-UI1-001: Consolidates duplicate toast implementations from
        planet_list_window, build_queue_screen, and strategy_input_handler.

        Args:
            manager: pygame_gui UIManager to create the window on.
            screen_width: Width of the screen for centering the toast.
            message: The message to display. Default "Screenshot saved!".
            y_pos: Vertical position for the toast center. Default 80.
        """
        try:
            import pygame_gui.windows
            from game.ui.config import UIConfig

            toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)
            toast_rect.center = (screen_width // 2, y_pos)
            pygame_gui.windows.UIMessageWindow(
                rect=toast_rect,
                html_message=f"<b>{message}</b><br>Path copied to clipboard",
                manager=manager,
                window_title="Screenshot"
            )
        except Exception as e:  # Intentional broad catch: UI toast is informational, any failure is non-critical
            logger.warning(f"Failed to show screenshot toast: {e}")
