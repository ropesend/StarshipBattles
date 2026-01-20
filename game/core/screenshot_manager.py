import os
import datetime
import pygame
import threading
from game.core.constants import ROOT_DIR, DEBUG_SCREENSHOTS, SCREENSHOT_DIR
from game.core.logger import log_error, log_info, log_warning

class ScreenshotManager:
    """
    Singleton manager for capturing screenshots.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        manager = ScreenshotManager.instance()
        manager.capture(surface, label="battle_end")

    Testing:
        - Use reset() to destroy instance completely
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if ScreenshotManager._instance is not None:
            raise Exception("ScreenshotManager is a singleton. Use ScreenshotManager.instance()")
        self._setup()

    @classmethod
    def instance(cls) -> 'ScreenshotManager':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton ScreenshotManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # Backwards compatibility alias
    get_instance = instance

    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def _setup(self):
        self.enabled = DEBUG_SCREENSHOTS
        self.base_dir = SCREENSHOT_DIR
        if self.enabled and not os.path.exists(self.base_dir):
            try:
                os.makedirs(self.base_dir)
                log_info(f"Created screenshot directory: {self.base_dir}")
            except OSError as e:
                log_error(f"Failed to create screenshot directory: {e}")
                self.enabled = False

    def capture(self, surface=None, region=None, label=None):
        """
        Capture a screenshot.
        :param surface: The surface to capture. If None, captures the main display.
        :param region: Optional pygame.Rect to crop the screenshot.
        :param label: Optional label to append to the filename.
        """
        if not self.enabled:
            return

        if surface is None:
            surface = pygame.display.get_surface()

        if surface is None:
            log_warning("Screenshot failed: No display surface found.")
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
                    log_warning(f"Screenshot region {region} is outside surface bounds {surf_rect}.")
                    return
            else:
                pygame.image.save(surface, filepath)

            abs_path = os.path.abspath(filepath)
            log_info(f"Screenshot saved: {abs_path}")
            self._copy_to_clipboard(abs_path)

        except Exception as e:
            log_error(f"Error saving screenshot: {e}")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard using Tkinter or Windows clip."""
        try:
            # Try Tkinter first (cross-platform if installed)
            import tkinter
            r = tkinter.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update() # Required to finalize clipboard
            r.destroy()
        except Exception:
            # Fallback to Windows clip
            if os.name == 'nt':
                os.system(f'echo {text.strip()}| clip')

    def capture_step(self, step_name, surface=None):
        """
        Capture a step in a sequence for debugging draw order.
        :param step_name: Name of the step (e.g., "1_background", "2_layer_1").
        :param surface: Optional surface to capture.
        """
        self.capture(surface=surface, label=f"STEP_{step_name}")

    def capture_strategy_layer(self, scene, include_ui=True, include_subwindows=True, label=None):
        """
        Capture a screenshot of the strategy layer with control over which layers are included.

        This method renders the strategy scene to a temporary surface and captures it,
        allowing selective inclusion of UI panels and sub-windows.

        :param scene: The StrategyScene instance to capture.
        :param include_ui: Whether to include UI panels (sidebar, top bar). Default True.
        :param include_subwindows: Whether to include modal sub-windows. Default True.
        :param label: Optional label to append to the filename.
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

                # Draw UI layer
                if hasattr(scene, 'ui') and scene.ui:
                    scene.ui.draw(capture_surface)

                # Draw sub-windows if requested
                if include_subwindows:
                    # Check for active sub-window screens
                    if hasattr(scene, 'build_queue_screen') and scene.build_queue_screen:
                        scene.build_queue_screen.draw(capture_surface)

                self.capture(surface=capture_surface, label=label)
            else:
                # Capture viewport only (exclude sidebar and top bar)
                sidebar_width = getattr(scene, 'SIDEBAR_WIDTH', 300)
                top_bar_height = getattr(scene, 'TOP_BAR_HEIGHT', 40)

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
                    log_warning("Cannot capture viewport: invalid dimensions")

        except Exception as e:
            log_error(f"Error capturing strategy layer: {e}")
