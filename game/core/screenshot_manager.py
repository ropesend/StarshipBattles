import os
import datetime
import pygame
import logging
import threading
from game.core.constants import ROOT_DIR, DEBUG_SCREENSHOTS, SCREENSHOT_DIR

logger = logging.getLogger(__name__)

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
                logger.info(f"Created screenshot directory: {self.base_dir}")
            except OSError as e:
                logger.error(f"Failed to create screenshot directory: {e}")
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

        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")

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
