"""
ResearchRenderer - Handles rendering the tech tree canvas.

Draws:
- Dependency lines between nodes
- Node rectangles with status colors
- Node labels (name, level, chance)

PROJ-147: Moved from game/research/ui/ to game/ui/research/ to fix architecture
layer violation. This module now correctly lives under the UI layer.
"""
import pygame
from typing import Dict, Tuple, Optional, TYPE_CHECKING

from game.core.protocols import ICamera
from game.research.data.tech_tree import TechTree
from game.research.data.research_tracker import ResearchTracker
from game.ui.colors import (
    RESEARCH_LOCKED, RESEARCH_AVAILABLE, RESEARCH_COMPLETED, RESEARCH_SELECTED,
    RESEARCH_LINE_UNMET, RESEARCH_LINE_MET, RESEARCH_LINE_NEGATED, RESEARCH_LINE_NEGATED_MET,
    RESEARCH_TEXT, RESEARCH_CHANCE, RESEARCH_ALLOCATION, TEXT_MUTED
)
from game.ui.fonts import get_font

if TYPE_CHECKING:
    from game.research.data.tech_node import TechNode
    from game.research.data.research_tracker import NodeState


class ResearchRenderer:
    """
    Renders the tech tree on the canvas area.

    Uses the Camera for coordinate transformations and viewport culling.
    """

    # Colors - imported from game.ui.colors for centralization
    COLOR_LOCKED = RESEARCH_LOCKED
    COLOR_AVAILABLE = RESEARCH_AVAILABLE
    COLOR_COMPLETED = RESEARCH_COMPLETED
    COLOR_SELECTED = RESEARCH_SELECTED
    COLOR_LINE = RESEARCH_LINE_UNMET
    COLOR_LINE_MET = RESEARCH_LINE_MET
    # PROJ-40/NEW-RES-007: Visual indicator for negated requirements
    COLOR_LINE_NEGATED = RESEARCH_LINE_NEGATED
    COLOR_LINE_NEGATED_MET = RESEARCH_LINE_NEGATED_MET
    COLOR_TEXT = RESEARCH_TEXT
    COLOR_CHANCE = RESEARCH_CHANCE
    COLOR_ALLOCATION = RESEARCH_ALLOCATION

    def __init__(self, tech_tree: TechTree, tracker: ResearchTracker,
                 node_positions: Dict[str, Tuple[float, float]],
                 camera: ICamera, node_width: int, node_height: int):
        """
        Initialize the renderer.

        Args:
            tech_tree: The tech tree structure
            tracker: Research tracker with current state
            node_positions: Mapping of node_id -> (world_x, world_y)
            camera: Camera for coordinate transformations
            node_width: Width of node rectangles
            node_height: Height of node rectangles
        """
        self.tech_tree = tech_tree
        self.tracker = tracker
        self.node_positions = node_positions
        self.camera = camera
        self.node_width = node_width
        self.node_height = node_height

    def _get_font(self, size: int) -> pygame.font.Font:
        """Get or create a font at the given size.

        PROJ-40/NEW-RES-002: Sizes are quantized to nearest 2 pixels to
        prevent unbounded cache growth during continuous zoom operations.
        Central get_font() handles actual caching.
        """
        # Quantize size to nearest 2 to bound cache growth
        quantized_size = max(8, (size // 2) * 2)
        return get_font(quantized_size)

    def draw(self, screen: pygame.Surface, selected_node_id: Optional[str],
             canvas_rect: pygame.Rect):
        """
        Draw the tech tree.

        Args:
            screen: Surface to draw on
            selected_node_id: Currently selected node ID (for highlighting)
            canvas_rect: Rectangle defining the canvas area
        """
        # Set clipping to canvas area
        screen.set_clip(canvas_rect)

        # Get current tech levels for status checks
        tech_levels = self.tracker.get_all_tech_levels()

        # Draw dependency lines first (behind nodes)
        self._draw_dependency_lines(screen, tech_levels)

        # Draw nodes
        self._draw_nodes(screen, selected_node_id, tech_levels)

        # Clear clipping
        screen.set_clip(None)

    def _draw_dependency_lines(self, screen: pygame.Surface,
                               tech_levels: Dict[str, int]):
        """Draw dependency lines between nodes.

        PROJ-40/NEW-RES-007: Negated requirements (NOT dependencies) are drawn
        in red with a dashed style to distinguish them from normal dependencies.
        """
        for node in self.tech_tree.nodes.values():
            if node.id not in self.node_positions:
                continue

            node_pos = self.node_positions[node.id]
            node_screen = self.camera.world_to_screen(node_pos)

            # Skip if node is off screen
            if not self._is_visible(node_screen):
                continue

            # Draw lines to all prerequisites
            for or_group in node.requirements:
                for req in or_group:
                    prereq_id = req.node_id
                    if prereq_id not in self.node_positions:
                        continue

                    prereq_pos = self.node_positions[prereq_id]
                    prereq_screen = self.camera.world_to_screen(prereq_pos)

                    # Check if prereq is met (for line color)
                    prereq_level = tech_levels.get(prereq_id, 0)
                    required_level = req.get_required_level()

                    # PROJ-40/NEW-RES-007: Handle negated requirements differently
                    if req.negate:
                        # Negated: must be BELOW target level
                        is_met = prereq_level < required_level
                        line_color = self.COLOR_LINE_NEGATED_MET if is_met else self.COLOR_LINE_NEGATED
                    else:
                        # Normal: must be AT OR ABOVE target level
                        is_met = prereq_level >= required_level
                        line_color = self.COLOR_LINE_MET if is_met else self.COLOR_LINE

                    # Draw line from prereq (right edge) to node (left edge)
                    half_w = (self.node_width / 2) * self.camera.zoom
                    start = (int(prereq_screen[0] + half_w), int(prereq_screen[1]))
                    end = (int(node_screen[0] - half_w), int(node_screen[1]))

                    if req.negate:
                        # PROJ-40/NEW-RES-007: Draw dashed line for negated requirements
                        self._draw_dashed_line(screen, line_color, start, end, 2, 8)
                    else:
                        pygame.draw.line(screen, line_color, start, end, 2)

    def _draw_dashed_line(self, screen: pygame.Surface, color: Tuple[int, int, int],
                          start: Tuple[int, int], end: Tuple[int, int],
                          width: int = 2, dash_length: int = 8):
        """Draw a dashed line between two points.

        PROJ-40/NEW-RES-007: Used to visually distinguish negated requirements.
        """
        import math
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return

        # Normalize direction
        dx /= length
        dy /= length

        # Draw dashes
        num_dashes = int(length / (dash_length * 2))
        for i in range(num_dashes + 1):
            dash_start = (
                int(start[0] + dx * (i * dash_length * 2)),
                int(start[1] + dy * (i * dash_length * 2))
            )
            dash_end = (
                int(min(start[0] + dx * (i * dash_length * 2 + dash_length), end[0])),
                int(min(start[1] + dy * (i * dash_length * 2 + dash_length), end[1]))
            )
            # Clamp to not exceed end point
            if (dash_end[0] - start[0]) * dx + (dash_end[1] - start[1]) * dy > length:
                dash_end = end
            pygame.draw.line(screen, color, dash_start, dash_end, width)

    def _draw_nodes(self, screen: pygame.Surface, selected_node_id: Optional[str],
                    tech_levels: Dict[str, int]):
        """Draw all visible nodes."""
        for node in self.tech_tree.nodes.values():
            if node.id not in self.node_positions:
                continue

            world_pos = self.node_positions[node.id]
            screen_pos = self.camera.world_to_screen(world_pos)

            # Skip if off screen (with margin for partial visibility)
            margin = max(self.node_width, self.node_height) * self.camera.zoom
            if not self._is_visible(screen_pos, margin):
                continue

            # Get node state
            state = self.tracker.get_state(node.id)
            status = node.get_status(state.current_level, tech_levels)

            # Determine colors
            if status == 'completed':
                fill_color = self.COLOR_COMPLETED
            elif status == 'available':
                fill_color = self.COLOR_AVAILABLE
            else:
                fill_color = self.COLOR_LOCKED

            # Calculate scaled dimensions
            scaled_w = int(self.node_width * self.camera.zoom)
            scaled_h = int(self.node_height * self.camera.zoom)

            # Create node rectangle
            rect = pygame.Rect(
                int(screen_pos[0] - scaled_w // 2),
                int(screen_pos[1] - scaled_h // 2),
                scaled_w,
                scaled_h
            )

            # Draw node background
            pygame.draw.rect(screen, fill_color, rect, border_radius=4)

            # Draw selection highlight
            if node.id == selected_node_id:
                pygame.draw.rect(screen, self.COLOR_SELECTED, rect, 3, border_radius=4)
            else:
                # Draw subtle border
                border_color = tuple(min(255, c + 30) for c in fill_color)
                pygame.draw.rect(screen, border_color, rect, 1, border_radius=4)

            # Draw RP allocation indicator (small bar at bottom)
            if state.rp_allocation > 0:
                indicator_height = max(3, int(4 * self.camera.zoom))
                indicator_rect = pygame.Rect(
                    rect.left + 2,
                    rect.bottom - indicator_height - 2,
                    rect.width - 4,
                    indicator_height
                )
                pygame.draw.rect(screen, self.COLOR_ALLOCATION, indicator_rect, border_radius=2)

            # Draw text if zoomed in enough
            if self.camera.zoom > 0.25:
                self._draw_node_text(screen, rect, node, state, status)

    def _draw_node_text(self, screen: pygame.Surface, rect: pygame.Rect,
                        node: 'TechNode', state: 'NodeState', status: str) -> None:
        """Draw text labels on a node."""
        # Calculate font size based on zoom
        base_size = 14
        font_size = int(base_size * self.camera.zoom)
        font = self._get_font(font_size)

        small_size = int(11 * self.camera.zoom)
        small_font = self._get_font(small_size)

        padding = int(5 * self.camera.zoom)
        y_offset = rect.top + padding

        # Node name (truncate if needed)
        name_text = node.name
        if font.size(name_text)[0] > rect.width - padding * 2:
            # Truncate with ellipsis
            while font.size(name_text + "...")[0] > rect.width - padding * 2 and len(name_text) > 3:
                name_text = name_text[:-1]
            name_text += "..."

        name_surf = font.render(name_text, True, self.COLOR_TEXT)
        screen.blit(name_surf, (rect.left + padding, y_offset))
        y_offset += name_surf.get_height() + 2

        # Level text
        level_text = f"Lv {state.current_level}/{node.max_levels}"
        level_surf = small_font.render(level_text, True, self.COLOR_TEXT)
        screen.blit(level_surf, (rect.left + padding, y_offset))

        # Breakthrough chance (right side of level row) - always show for available nodes
        if status == 'available':
            chance_pct = state.current_chance * 100
            chance_text = f"{chance_pct:.1f}%"
            chance_surf = small_font.render(chance_text, True, self.COLOR_CHANCE)
            chance_x = rect.right - chance_surf.get_width() - padding
            screen.blit(chance_surf, (chance_x, y_offset))

        y_offset += level_surf.get_height() + 2

        # RP allocation (always show, bottom of node)
        rp_text = f"{state.rp_allocation} RP"
        # Use different color based on whether RP is allocated
        rp_color = self.COLOR_ALLOCATION if state.rp_allocation > 0 else TEXT_MUTED
        rp_surf = small_font.render(rp_text, True, rp_color)
        rp_x = rect.left + padding
        rp_y = rect.bottom - rp_surf.get_height() - padding - int(4 * self.camera.zoom)
        screen.blit(rp_surf, (rp_x, rp_y))

    def _is_visible(self, screen_pos: Tuple[float, float], margin: float = 0) -> bool:
        """
        Check if a position is visible in the camera viewport.

        Args:
            screen_pos: Position in screen coordinates
            margin: Additional margin for partial visibility

        Returns:
            True if visible
        """
        return (-margin <= screen_pos[0] <= self.camera.width + margin and
                -margin <= screen_pos[1] <= self.camera.height + margin)
