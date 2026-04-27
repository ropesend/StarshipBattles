"""UI-layer protocols (PROJ-65 / PROJ-106)."""

from typing import Any, Protocol, TypeGuard, runtime_checkable

from game.core.protocols.common import _has_attrs


@runtime_checkable
class IScene(Protocol):
    """
    Protocol for game scenes (PROJ-65).

    Scenes are the main UI states (menu, battle, workshop, etc.) that
    handle events, update logic, and render to the screen.
    """
    def handle_event(self, event: Any) -> None:
        """Handle a pygame event."""
        ...

    def update(self, dt: float) -> None:
        """Update scene logic. dt is time since last frame in seconds."""
        ...

    def draw(self, screen: Any) -> None:
        """Draw the scene to the screen surface."""
        ...

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize to new dimensions."""
        ...


@runtime_checkable
class ICamera(Protocol):
    """
    Protocol for camera/viewport abstraction (PROJ-106).

    Enables the research layer to depend on a camera interface without
    importing the concrete Camera class from game.ui.renderer.

    The camera handles:
    - Coordinate transformations between world and screen space
    - Viewport dimensions
    - Zoom level for scaling
    """
    @property
    def width(self) -> int:
        """Viewport width in pixels."""
        ...

    @property
    def height(self) -> int:
        """Viewport height in pixels."""
        ...

    @property
    def zoom(self) -> float:
        """Current zoom level (1.0 = 100%)."""
        ...

    @property
    def position(self) -> Any:
        """Camera world position (center of viewport). Returns Vector2-like object."""
        ...

    def world_to_screen(self, world_pos: Any) -> Any:
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_pos: Position in world space (tuple or Vector2-like)

        Returns:
            Position in screen space (Vector2-like)
        """
        ...

    def screen_to_world(self, screen_pos: Any) -> Any:
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_pos: Position in screen space (tuple or Vector2-like)

        Returns:
            Position in world space (Vector2-like)
        """
        ...

    def update(self, dt: float) -> None:
        """
        Update camera state (smooth zoom, target following, etc).

        Args:
            dt: Delta time in seconds
        """
        ...

    def update_input(self, dt: float, events: list) -> None:
        """
        Process input events for camera control.

        Args:
            dt: Delta time in seconds
            events: List of input events
        """
        ...


def is_camera(obj: Any) -> TypeGuard[ICamera]:
    """Check if obj has camera attributes (width, height, zoom, world_to_screen)."""
    return _has_attrs(obj, 'width', 'height', 'zoom', 'world_to_screen')
