"""
Camera navigation operations for strategy scene.
Handles focus, zoom, and selection cycling.

Extracted from StrategyScene to reduce file size and improve testability.
"""
import pygame
from game.core.logger import log_debug
from game.strategy.data.hex_math import hex_to_pixel, HexCoord
from game.strategy.data.galaxy import StarSystem


class CameraNavigator:
    """Manages camera focus and zoom operations."""

    def __init__(self, scene):
        """
        Initialize camera navigator.

        Args:
            scene: StrategyScene instance providing camera, systems, etc.
        """
        self.scene = scene

    @property
    def camera(self):
        return self.scene.camera

    @property
    def systems(self):
        return self.scene.systems

    @property
    def HEX_SIZE(self):
        return self.scene.HEX_SIZE

    def center_on(self, obj):
        """
        Center camera on a game object (Planet, Fleet, System).

        Args:
            obj: Game object with location attribute
        """
        target_hex = self._resolve_global_hex(obj)

        if target_hex:
            fx, fy = hex_to_pixel(target_hex, self.HEX_SIZE)
            self.camera.position.x = fx
            self.camera.position.y = fy
            log_debug(f"Camera centered on {obj} at {target_hex}")
        else:
            log_debug(f"Could not center camera on {obj}")

    def _resolve_global_hex(self, obj):
        """
        Resolve object to its global hex coordinate.

        Args:
            obj: Game object (Planet, Fleet, or System)

        Returns:
            HexCoord or None if resolution failed
        """
        if hasattr(obj, 'location'):
            # Planet: location is local to system
            if hasattr(obj, 'planet_type'):
                sys = next((s for s in self.systems if obj in s.planets), None)
                if sys:
                    return sys.global_location + obj.location
            # Fleet: location is global
            elif hasattr(obj, 'ships'):
                return obj.location
            # System: has global_location
            elif hasattr(obj, 'global_location'):
                return obj.global_location
        return None

    def zoom_to_galaxy(self):
        """
        Zoom out to show entire galaxy (Shift+G).

        Calculates bounds of all systems and sets zoom to fit them all.
        """
        if not self.systems:
            return

        all_positions = []
        for sys in self.systems:
            px, py = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            all_positions.append((px, py))

        if not all_positions:
            return

        min_x = min(p[0] for p in all_positions)
        max_x = max(p[0] for p in all_positions)
        min_y = min(p[1] for p in all_positions)
        max_y = max(p[1] for p in all_positions)

        # Center camera
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position.x = center_x
        self.camera.position.y = center_y

        # Calculate zoom to fit all systems with margin
        width = max_x - min_x + 600
        height = max_y - min_y + 600

        zoom_x = self.camera.width / width if width > 0 else 1.0
        zoom_y = self.camera.height / height if height > 0 else 1.0
        fit_zoom = min(zoom_x, zoom_y)

        # Set zoom (instant for this shortcut)
        self.camera.target_zoom = max(self.camera.min_zoom, min(self.camera.max_zoom, fit_zoom))
        self.camera.zoom = self.camera.target_zoom

        log_debug(f"Galaxy View: zoom={self.camera.zoom:.2f}")

    def zoom_to_system(self, target_sys=None):
        """
        Zoom to 2x on a system (Shift+S).

        Args:
            target_sys: Specific system to zoom to, or None to use last selected
        """
        if not target_sys:
            target_sys = self.scene.last_selected_system

        # Fallback: infer from selected object
        if not target_sys and self.scene.selected_object:
            if isinstance(self.scene.selected_object, StarSystem):
                target_sys = self.scene.selected_object
            elif hasattr(self.scene.selected_object, 'location'):
                target_sys = next(
                    (s for s in self.systems
                     if self.scene.selected_object in s.planets
                     or self.scene.selected_object in s.warp_points),
                    None
                )

        if not target_sys:
            log_debug("No system selected for Shift+S zoom")
            return

        # Center on system
        px, py = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)
        self.camera.position.x = px
        self.camera.position.y = py

        # Set zoom to 2x (instant for this shortcut)
        self.camera.target_zoom = 2.0
        self.camera.zoom = 2.0

        log_debug(f"System View: {target_sys.name} at zoom=2.0")

    def cycle_selection(self, obj_type, direction):
        """
        Cycle through colonies or fleets.

        Args:
            obj_type: 'colony' or 'fleet'
            direction: 1 for next, -1 for previous

        Returns:
            The newly selected object, or None if no targets available
        """
        targets = []
        if obj_type == 'colony':
            targets = self.scene.current_empire.colonies
        elif obj_type == 'fleet':
            targets = self.scene.current_empire.fleets

        if not targets:
            log_debug(f"No {obj_type}s to cycle.")
            return None

        # Find current index
        current_idx = -1
        if self.scene.selected_object in targets:
            current_idx = targets.index(self.scene.selected_object)

        # Calculate next index with wrap-around
        next_idx = (current_idx + direction) % len(targets)
        return targets[next_idx]
