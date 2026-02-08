"""
Build Queue Drag Handler - Manages drag-and-drop state machine for build queue.

Extracted from build_queue_screen.py as part of PROJ-63.
Updated in PROJ-67 Phase 4 to support BuildContext protocol (Planet or Fleet).
Updated in PROJ-69 Phase 4 to accept construction_queue list directly and
disable drag operations in multi-select mode.
"""
from __future__ import annotations

import pygame
from typing import TYPE_CHECKING, Dict, Optional, Callable, List, Any

from game.core.logger import log_info, log_debug

if TYPE_CHECKING:
    from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader
    from game.strategy.systems.design_library import DesignLibrary
    import pygame_gui.elements as ui


class BuildQueueDragHandler:
    """
    Handles drag-and-drop operations for the build queue screen.

    Manages:
    - Design item dragging from available designs list
    - Queue item reordering via drag
    - Drag preview rendering
    - Click vs drag detection using threshold

    PROJ-69: Drag operations are disabled in multi-select mode since
    reordering across multiple queues is ambiguous.
    """

    def __init__(
        self,
        portrait_loader: 'BuildQueuePortraitLoader',
        design_library: 'DesignLibrary',
        on_add_to_queue: Callable[[str, int, str, Optional[int]], None],
        on_refresh_queue: Callable[[], None],
        on_refresh_design_report: Callable[[str], None]
    ):
        """
        Initialize the drag handler.

        Args:
            portrait_loader: BuildQueuePortraitLoader instance for loading icons
            design_library: DesignLibrary for scanning designs during drag start
            on_add_to_queue: Callback(design_id, turns, category, index) to add item to queue
            on_refresh_queue: Callback to refresh queue display after reorder
            on_refresh_design_report: Callback(design_id) to update design report on selection
        """
        self.portrait_loader = portrait_loader
        self.design_library = design_library
        self.on_add_to_queue = on_add_to_queue
        self.on_refresh_queue = on_refresh_queue
        self.on_refresh_design_report = on_refresh_design_report

        # Drag state
        self.dragged_item: Optional[dict] = None
        self.drag_preview: Optional[pygame.Surface] = None
        self.drag_start_pos: Optional[tuple] = None
        self.drag_threshold: int = 10  # Pixels to move before starting drag
        self._pending_queue_index: Optional[int] = None

        # Selection state (shared between drag and selection)
        self.selected_design: Optional[str] = None

    @property
    def is_dragging(self) -> bool:
        """Return True if currently dragging an item."""
        return self.dragged_item is not None

    def handle_mouse_down(
        self,
        event: pygame.event.Event,
        items_scrollable: Any,
        queue_items: List[Any],
        construction_queue: Optional[List[Dict[str, Any]]],
        selected_category: str,
        multi_select_active: bool = False
    ) -> bool:
        """
        Handle mouse button down event for drag initiation.

        Args:
            event: pygame MOUSEBUTTONDOWN event
            items_scrollable: Scrollable container with design items
            queue_items: List of queue item UI panels
            construction_queue: The active queue's construction list (or None)
            selected_category: Currently selected design category
            multi_select_active: If True, disable all drag operations

        Returns:
            True if event was handled, False otherwise
        """
        if event.button != 1:  # Only handle left click
            return False

        # PROJ-69: Disable drag in multi-select mode
        if multi_select_active:
            return False

        # Check if mouse is over a design button in the items list
        for element in items_scrollable.get_container().elements:
            if hasattr(element, 'design_id'):
                abs_rect = element.get_abs_rect()
                if abs_rect.collidepoint(event.pos):
                    design_id = element.design_id
                    self.selected_design = design_id

                    # Update design report panel
                    self.on_refresh_design_report(design_id)

                    # Start dragging
                    designs = self.design_library.scan_designs()
                    design = next((d for d in designs if d.design_id == design_id), None)
                    if design:
                        # Load portrait icon for drag preview (48px for cursor visibility)
                        portrait = self.portrait_loader.load_design_portrait(design, 48)
                        self.dragged_item = {
                            'design_id': design.design_id,
                            'name': design.name,
                            'category': selected_category,
                            'portrait': portrait
                        }
                    log_info(f"Started drag from mouse down: {self.selected_design}")
                    return True

        # Check if mouse is over a queue item panel - track for potential drag
        for element in queue_items:
            if element.get_abs_rect().collidepoint(event.pos):
                idx = getattr(element, 'queue_index', -1)
                if idx != -1:
                    # Store start position for drag threshold check
                    self.drag_start_pos = event.pos
                    self._pending_queue_index = idx  # Track which item might be dragged
                    return True
                break

        return False

    def handle_mouse_motion(
        self,
        event: pygame.event.Event,
        construction_queue: List[Dict[str, Any]],
        multi_select_active: bool = False
    ) -> bool:
        """
        Handle mouse motion event for drag threshold detection.

        Args:
            event: pygame MOUSEMOTION event
            construction_queue: The active queue's construction list
            multi_select_active: If True, disable all drag operations

        Returns:
            True if drag was started, False otherwise
        """
        # PROJ-69: Disable drag in multi-select mode
        if multi_select_active:
            return False

        if not (event.buttons[0] and self.drag_start_pos and self._pending_queue_index is not None):
            return False

        # Check if we've moved past drag threshold
        dx = abs(event.pos[0] - self.drag_start_pos[0])
        dy = abs(event.pos[1] - self.drag_start_pos[1])

        if dx > self.drag_threshold or dy > self.drag_threshold:
            # Start actual drag - pick up from queue
            idx = self._pending_queue_index
            if idx < len(construction_queue):
                item = construction_queue.pop(idx)
                design_id = item.get('design_id', 'Unknown')
                item_type = item.get('type', 'ship')

                # Load portrait icon for drag preview
                portrait = self.portrait_loader.load_queue_item_portrait(design_id, item_type, 48)

                self.dragged_item = {
                    'design_id': design_id,
                    'name': design_id,
                    'category': item_type,
                    'turns': item.get('turns_remaining', 0),
                    'source': 'queue',
                    'portrait': portrait
                }
                log_info(f"Picked up {self.dragged_item['design_id']} from queue at pos {idx}")
                self.on_refresh_queue()

            # Clear pending state
            self._pending_queue_index = None
            self.drag_start_pos = None
            return True

        return False

    def handle_mouse_up(
        self,
        event: pygame.event.Event,
        build_queue_panel: Any,
        queue_scrollable: Any,
        construction_queue: List[Dict[str, Any]],
        multi_select_active: bool = False
    ) -> Optional[int]:
        """
        Handle mouse button up event for drop or click-select.

        Args:
            event: pygame MOUSEBUTTONUP event
            build_queue_panel: Panel containing the build queue
            queue_scrollable: Scrollable container for queue items
            construction_queue: The active queue's construction list
            multi_select_active: If True, disable all drag operations

        Returns:
            Selected queue index if click-select occurred, None otherwise
        """
        if event.button != 1:  # Only handle left click
            return None

        # PROJ-69: Disable drag operations in multi-select mode
        if multi_select_active:
            # Clear any stale pending state
            self._pending_queue_index = None
            self.drag_start_pos = None
            self.dragged_item = None
            return None

        selected_queue_index = None

        # Check if this was a click (not a drag) on a queue item - select it
        if self._pending_queue_index is not None and not self.dragged_item:
            # This was a click without dragging - select the item
            selected_queue_index = self._pending_queue_index
            log_info(f"Selected queue item at index {selected_queue_index}")
            self.on_refresh_queue()  # Refresh to show selection highlight

        # Clear pending drag state
        self._pending_queue_index = None
        self.drag_start_pos = None

        if self.dragged_item:
            # Track if we need to refresh (item came from queue)
            came_from_queue = self.dragged_item.get('source') == 'queue'

            # Check if dropped over build queue panel
            if build_queue_panel.rect.collidepoint(event.pos):
                # Calculate insertion index based on vertical mouse position
                rel_y = event.pos[1] - queue_scrollable.get_abs_rect().top

                # Estimate index: each item is ~65 pixels high
                estimated_idx = rel_y // 65
                insert_idx = max(0, min(int(estimated_idx), len(construction_queue)))

                turns = self.dragged_item.get('turns', 1)
                self.on_add_to_queue(
                    self.dragged_item['design_id'],
                    turns,
                    self.dragged_item['category'],
                    insert_idx
                )
                log_info(f"Dropped {self.dragged_item['design_id']} into queue at index {insert_idx}")
            else:
                log_info(f"Dropped {self.dragged_item['design_id']} outside - removed from queue or cancelled drag")
                # If item came from queue and dropped outside, refresh to show removal
                if came_from_queue:
                    self.on_refresh_queue()

            # Clear drag state
            self.dragged_item = None

        return selected_queue_index

    def draw_drag_preview(self, screen: pygame.Surface) -> None:
        """
        Draw the drag preview icon following the cursor.

        Args:
            screen: pygame surface to draw on
        """
        if not self.dragged_item:
            return

        mouse_pos = pygame.mouse.get_pos()
        portrait = self.dragged_item.get('portrait')

        if portrait:
            # Icon follows cursor - offset slightly so icon is visible
            icon_x = mouse_pos[0] + 8
            icon_y = mouse_pos[1] + 8
            icon_size = portrait.get_width()

            # Draw drop shadow for depth
            shadow_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 100))
            screen.blit(shadow_surf, (icon_x + 3, icon_y + 3))

            # Draw the portrait icon
            screen.blit(portrait, (icon_x, icon_y))

            # Draw bright border around icon
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(screen, (150, 220, 255), icon_rect, 2)
        else:
            # Fallback: simple colored square with name if no portrait
            icon_size = 48
            icon_x = mouse_pos[0] + 8
            icon_y = mouse_pos[1] + 8

            # Draw colored placeholder
            color_map = {
                'ship': (80, 100, 180),
                'complex': (80, 180, 100),
                'satellite': (180, 100, 80),
                'fighter': (180, 180, 80),
            }
            color = color_map.get(self.dragged_item.get('category', 'ship'), (100, 100, 100))

            placeholder = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            placeholder.fill(color)
            screen.blit(placeholder, (icon_x, icon_y))

            # Draw border
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            pygame.draw.rect(screen, (150, 220, 255), icon_rect, 2)
