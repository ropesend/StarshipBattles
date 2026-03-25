"""Reusable scroll state utility for UI panels and widgets.

Encapsulates the common pattern of scroll_offset + MOUSEWHEEL handling
that was previously duplicated across 14+ UI files.
"""
import pygame


class ScrollState:
    """Manages vertical scroll state for a scrollable area.

    Encapsulates offset tracking, clamping, mousewheel handling, and
    scroll ratio calculation (for scrollbar thumb positioning).

    Usage::

        self.scroll = ScrollState(step=20)

        # When content changes:
        self.scroll.content_height = total_content_height
        self.scroll.viewport_height = visible_area_height
        self.scroll.clamp()

        # In event handler:
        if event.type == pygame.MOUSEWHEEL:
            if self.scroll.handle_mousewheel(event):
                return True  # consumed

        # In draw:
        y = start_y - self.scroll.offset
    """

    __slots__ = ("offset", "content_height", "viewport_height", "step")

    def __init__(
        self,
        content_height: int = 0,
        viewport_height: int = 0,
        step: int = 20,
    ) -> None:
        self.offset: int = 0
        self.content_height: int = content_height
        self.viewport_height: int = viewport_height
        self.step: int = step

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def max_offset(self) -> int:
        """Maximum valid scroll offset (0 when content fits in viewport)."""
        return max(0, self.content_height - self.viewport_height)

    @property
    def can_scroll(self) -> bool:
        """True if content exceeds viewport."""
        return self.content_height > self.viewport_height

    @property
    def scroll_ratio(self) -> float:
        """Current scroll position as 0.0-1.0 ratio (for scrollbar thumb)."""
        mx = self.max_offset
        if mx <= 0:
            return 0.0
        return self.offset / mx

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def clamp(self) -> None:
        """Clamp offset to valid range [0, max_offset]."""
        self.offset = max(0, min(self.offset, self.max_offset))

    def reset(self) -> None:
        """Reset scroll offset to top."""
        self.offset = 0

    def set_from_ratio(self, ratio: float) -> None:
        """Set offset from a 0.0-1.0 ratio (for scrollbar drag).

        Args:
            ratio: Scroll position ratio, clamped to [0.0, 1.0].
        """
        ratio = max(0.0, min(1.0, ratio))
        self.offset = int(ratio * self.max_offset)

    def handle_mousewheel(self, event: pygame.event.Event) -> bool:
        """Process a MOUSEWHEEL event.

        Updates offset by ``step * -event.y`` (positive y = scroll up = decrease offset).

        Args:
            event: A ``pygame.MOUSEWHEEL`` event.

        Returns:
            True if the offset actually changed, False otherwise.
        """
        old = self.offset
        self.offset -= event.y * self.step
        self.clamp()
        return self.offset != old
