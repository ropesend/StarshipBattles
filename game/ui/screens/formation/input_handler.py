"""FormationInputHandler - Manages event handling state machine for formation editor.

Extracted from FormationEditorScreen to separate input handling concerns from
rendering and business logic.
"""

from __future__ import annotations

import math
import pygame
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from pygame import Rect


class FormationInputHandler:
    """Manages input state machine for the formation editor.

    States:
    - IDLE: No active interaction
    - DRAGGING_ITEMS: Moving selected arrows
    - BOX_SELECT: Drawing selection marquee
    - RESIZING_GROUP: Resizing selection group via handles
    - PANNING: Panning the camera
    - POTENTIAL_CLICK: Mouse down, waiting to distinguish click from drag

    Responsibilities:
    - Track interaction state
    - Store drag/resize context
    - Calculate new positions during drag/resize
    - Detect arrow clicks
    - Calculate box selection results
    """

    # Minimum drag distance to distinguish from click (pixels)
    DRAG_THRESHOLD = 5

    def __init__(self) -> None:
        """Initialize the input handler in IDLE state."""
        self.state = 'IDLE'

        # Drag context
        self.drag_start_world: Optional[Tuple[float, float]] = None
        self.drag_start_screen: Optional[Tuple[int, int]] = None
        self.drag_offsets: Dict[int, Tuple[float, float]] = {}

        # Resize context
        self.resize_handle: Optional[str] = None
        self.initial_group_bounds: Optional[pygame.Rect] = None
        self.initial_arrow_positions: Dict[int, Tuple[float, float]] = {}
        self.resize_aspect_ratio: Optional[float] = None

    def reset_state(self) -> None:
        """Reset to IDLE state and clear all interaction data."""
        self.state = 'IDLE'
        self.drag_start_world = None
        self.drag_start_screen = None
        self.drag_offsets = {}
        self.resize_handle = None
        self.initial_group_bounds = None
        self.initial_arrow_positions = {}
        self.resize_aspect_ratio = None

    # --- State Transitions ---

    def start_panning(
        self,
        screen_pos: Tuple[int, int],
        camera_pan: List[float]
    ) -> None:
        """Enter panning state.

        Args:
            screen_pos: Current mouse position in screen coords
            camera_pan: Current camera pan offset [x, y]
        """
        self.state = 'PANNING'
        self.drag_start_screen = screen_pos
        self.drag_start_world = camera_pan[:]

    def start_dragging_items(
        self,
        world_pos: Tuple[float, float],
        arrows: List[List[float]],
        selected_indices: Set[int]
    ) -> None:
        """Enter item dragging state.

        Args:
            world_pos: Mouse position in world coords
            arrows: List of arrow [x, y] positions
            selected_indices: Set of selected arrow indices
        """
        self.state = 'DRAGGING_ITEMS'
        self.drag_start_world = world_pos
        self.drag_offsets = {}

        for idx in selected_indices:
            self.drag_offsets[idx] = (
                arrows[idx][0] - world_pos[0],
                arrows[idx][1] - world_pos[1]
            )

    def start_resizing_group(
        self,
        handle_name: str,
        bounds: pygame.Rect,
        arrows: List[List[float]],
        selected: Set[int],
        screen_pos: Tuple[int, int],
        grid_size: int
    ) -> None:
        """Enter group resizing state.

        Args:
            handle_name: Handle being dragged ('TL', 'TR', 'BL', 'BR', 'T', 'B', 'L', 'R')
            bounds: Current selection bounds in world coords
            arrows: List of arrow positions
            selected: Set of selected indices
            screen_pos: Mouse position in screen coords
            grid_size: Grid size for aspect ratio calculation
        """
        self.state = 'RESIZING_GROUP'
        self.resize_handle = handle_name
        self.initial_group_bounds = bounds
        self.drag_start_screen = screen_pos

        self.initial_arrow_positions = {
            i: (arrows[i][0], arrows[i][1])
            for i in selected
        }

        # Calculate aspect ratio for corner handles
        w = max(1, bounds.width + grid_size * 2)
        h = max(1, bounds.height + grid_size * 2)

        if len(handle_name) == 2:  # Corner handle (TL, TR, BL, BR)
            self.resize_aspect_ratio = w / h
        else:
            self.resize_aspect_ratio = None

    def start_box_select(
        self,
        screen_pos: Tuple[int, int],
        world_pos: Tuple[float, float]
    ) -> None:
        """Enter box selection state.

        Args:
            screen_pos: Mouse position in screen coords
            world_pos: Mouse position in world coords
        """
        self.state = 'BOX_SELECT'
        self.drag_start_screen = screen_pos
        self.drag_start_world = world_pos

    def start_potential_click(
        self,
        screen_pos: Tuple[int, int],
        world_pos: Tuple[float, float]
    ) -> None:
        """Enter potential click state (waiting to distinguish click from drag).

        Args:
            screen_pos: Mouse position in screen coords
            world_pos: Mouse position in world coords
        """
        self.state = 'POTENTIAL_CLICK'
        self.drag_start_screen = screen_pos
        self.drag_start_world = world_pos

    def should_transition_to_box_select(
        self,
        current_screen_pos: Tuple[int, int]
    ) -> bool:
        """Check if drag distance exceeds threshold for box select.

        Args:
            current_screen_pos: Current mouse position

        Returns:
            True if should transition to BOX_SELECT state
        """
        if self.drag_start_screen is None:
            return False

        dist = math.hypot(
            current_screen_pos[0] - self.drag_start_screen[0],
            current_screen_pos[1] - self.drag_start_screen[1]
        )
        return dist > self.DRAG_THRESHOLD

    # --- Panning Calculations ---

    def calculate_pan_delta(
        self,
        current_screen_pos: Tuple[int, int]
    ) -> List[float]:
        """Calculate new camera pan position.

        Args:
            current_screen_pos: Current mouse position

        Returns:
            New camera pan [x, y]
        """
        if self.drag_start_screen is None or self.drag_start_world is None:
            return [0, 0]

        dx = current_screen_pos[0] - self.drag_start_screen[0]
        dy = current_screen_pos[1] - self.drag_start_screen[1]

        return [
            self.drag_start_world[0] + dx,
            self.drag_start_world[1] + dy
        ]

    # --- Item Dragging Calculations ---

    def calculate_new_positions(
        self,
        world_pos: Tuple[float, float],
        snap_func: Callable[[float], float]
    ) -> Dict[int, List[float]]:
        """Calculate new arrow positions during drag.

        Args:
            world_pos: Current mouse position in world coords
            snap_func: Function to snap values to grid

        Returns:
            Dict mapping arrow index to new [x, y] position
        """
        new_positions: Dict[int, List[float]] = {}

        for idx, (off_x, off_y) in self.drag_offsets.items():
            target_x = world_pos[0] + off_x
            target_y = world_pos[1] + off_y
            new_positions[idx] = [snap_func(target_x), snap_func(target_y)]

        return new_positions

    # --- Box Select Calculations ---

    def get_selection_box(
        self,
        current_screen_pos: Tuple[int, int]
    ) -> pygame.Rect:
        """Get the current selection box rectangle.

        Args:
            current_screen_pos: Current mouse position in screen coords

        Returns:
            Selection rectangle in screen coords (normalized)
        """
        if self.drag_start_screen is None:
            return pygame.Rect(0, 0, 0, 0)

        sx, sy = self.drag_start_screen
        mx, my = current_screen_pos

        return pygame.Rect(
            min(sx, mx), min(sy, my),
            abs(mx - sx), abs(my - sy)
        )

    def find_arrows_in_box(
        self,
        screen_pos: Tuple[int, int],
        arrows: List[List[float]],
        screen_to_world: Callable[[float, float], Tuple[float, float]]
    ) -> Set[int]:
        """Find all arrows within the selection box.

        Args:
            screen_pos: Current mouse position (end of box)
            arrows: List of arrow [x, y] positions
            screen_to_world: Coordinate transform function

        Returns:
            Set of arrow indices inside the box
        """
        if self.drag_start_world is None:
            return set()

        start_wx, start_wy = self.drag_start_world
        end_wx, end_wy = screen_to_world(screen_pos[0], screen_pos[1])

        l = min(start_wx, end_wx)
        r = max(start_wx, end_wx)
        t = min(start_wy, end_wy)
        b = max(start_wy, end_wy)

        box_rect = pygame.Rect(l, t, r - l, b - t)

        selected: Set[int] = set()
        for i, (ax, ay) in enumerate(arrows):
            if box_rect.collidepoint(ax, ay):
                selected.add(i)

        return selected

    # --- Resize Calculations ---

    def calculate_resize_positions(
        self,
        screen_pos: Tuple[int, int],
        screen_to_world: Callable[[float, float], Tuple[float, float]],
        snap_func: Callable[[float], float],
        grid_size: int
    ) -> Dict[int, List[float]]:
        """Calculate new arrow positions during resize.

        Args:
            screen_pos: Current mouse position in screen coords
            screen_to_world: Coordinate transform function
            snap_func: Function to snap values to grid
            grid_size: Grid size for padding calculations

        Returns:
            Dict mapping arrow index to new [x, y] position
        """
        if self.initial_group_bounds is None:
            return {}

        wx, wy = screen_to_world(screen_pos[0], screen_pos[1])
        wx = snap_func(wx)
        wy = snap_func(wy)

        padding = grid_size
        b = self.initial_group_bounds
        l, t, r, bot = b.left, b.top, b.right, b.bottom
        nl, nt, nr, nb = l, t, r, bot

        h = self.resize_handle

        # Adjust bounds based on handle
        if h and 'L' in h:
            nl = min(wx + padding, nr - 10)
        if h and 'R' in h:
            nr = max(wx - padding, nl + 10)
        if h and 'T' in h:
            nt = min(wy + padding, nb - 10)
        if h and 'B' in h:
            nb = max(wy - padding, nt + 10)

        # Apply aspect ratio for corner handles
        if self.resize_aspect_ratio and h:
            current_padded_w = (nr - nl) + padding * 2
            current_padded_h = (nb - nt) + padding * 2

            if 'L' in h or 'R' in h:
                target_padded_h = current_padded_w / self.resize_aspect_ratio
                target_h_content = target_padded_h - padding * 2

                if 'T' in h:
                    nt = nb - target_h_content
                elif 'B' in h:
                    nb = nt + target_h_content

            elif 'T' in h or 'B' in h:
                target_padded_w = current_padded_h * self.resize_aspect_ratio
                target_w_content = target_padded_w - padding * 2

                if 'L' in h:
                    nl = nr - target_w_content
                elif 'R' in h:
                    nr = nl + target_w_content

        # Calculate scale factors
        old_w = max(1, r - l)
        old_h = max(1, bot - t)
        new_w = max(1, nr - nl)
        new_h = max(1, nb - nt)

        scale_x = new_w / old_w
        scale_y = new_h / old_h

        # Apply scale to all positions
        new_positions: Dict[int, List[float]] = {}
        for idx, (orig_x, orig_y) in self.initial_arrow_positions.items():
            rel_x = orig_x - l
            rel_y = orig_y - t
            new_x = nl + rel_x * scale_x
            new_y = nt + rel_y * scale_y
            new_positions[idx] = [new_x, new_y]

        return new_positions

    # --- Click Detection ---

    def get_arrow_at(
        self,
        world_pos: Tuple[float, float],
        arrows: List[List[float]],
        world_to_screen: Callable[[float, float], Tuple[float, float]],
        click_radius: int = 25
    ) -> Optional[int]:
        """Find arrow at given position.

        Args:
            world_pos: Click position in world coords
            arrows: List of arrow [x, y] positions
            world_to_screen: Coordinate transform function
            click_radius: Hit detection radius in screen pixels

        Returns:
            Index of clicked arrow (topmost), or None
        """
        mx, my = world_to_screen(world_pos[0], world_pos[1])

        # Check in reverse order (topmost first)
        for i in range(len(arrows) - 1, -1, -1):
            ax, ay = arrows[i]
            sx, sy = world_to_screen(ax, ay)
            dist = math.hypot(mx - sx, my - sy)
            if dist < click_radius:
                return i

        return None
