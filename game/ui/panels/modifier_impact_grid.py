"""
ModifierImpactGrid - A grid widget showing modifier effects on component stats.

Displays a matrix with:
- Column headers: stat names (rotated 45 degrees)
- Rows: one per modifier showing its contribution to each stat
- Footer row: net value for each stat

Only shows stats that are actually affected (not at default values).
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIWindow
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component


class ModifierImpactGrid:
    """
    Grid widget displaying how modifiers affect component stats.

    Features:
    - Rotated column headers for stat names
    - Per-modifier rows showing contribution values
    - Net value footer row
    - Color coding: green for buffs, red for debuffs
    """

    # Layout constants
    ROW_HEIGHT = 22  # Slightly smaller for more rows
    HEADER_HEIGHT = 50  # Space for rotated headers (reduced)
    COLUMN_WIDTH = 50  # Slightly narrower columns
    NAME_COLUMN_WIDTH = 100  # Narrower name column
    PADDING = 5
    TITLE_HEIGHT = 20  # Height of title area

    # Colors
    COLOR_HEADER_BG = (40, 40, 50)
    COLOR_ROW_BG = (30, 30, 40)
    COLOR_ROW_ALT_BG = (35, 35, 45)
    COLOR_FOOTER_BG = (50, 50, 60)
    COLOR_TEXT = (200, 200, 200)
    COLOR_BUFF = (100, 255, 100)  # Green for positive
    COLOR_DEBUFF = (255, 100, 100)  # Red for negative
    COLOR_NEUTRAL = (180, 180, 180)  # Gray for neutral

    def __init__(self, manager: pygame_gui.UIManager, container, rect: pygame.Rect):
        """
        Initialize the ModifierImpactGrid.

        Args:
            manager: pygame_gui UIManager
            container: Parent container (UIPanel or similar)
            rect: Position and size of the grid
        """
        self.manager = manager
        self.container = container
        self.rect = rect

        # Create background panel
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container,
            object_id='#modifier_impact_grid'
        )

        # State
        self.current_component: Optional['Component'] = None
        self.stat_columns: List[str] = []  # Stat keys to display as columns
        self.modifier_rows: List[Dict[str, Any]] = []  # Per-modifier data

        # Scrolling state
        self.scroll_offset_y = 0  # Vertical scroll offset in pixels
        self.max_visible_rows = 0  # Calculated based on rect height

        # UI elements for cleanup
        self._ui_elements: List = []

        # Expand button and popup references
        self.expand_btn: Optional[UIButton] = None
        self.expanded_window: Optional[UIWindow] = None
        self.expanded_grid: Optional['ModifierImpactGrid'] = None

        # Fonts
        self.font = pygame.font.SysFont("Arial", 11)
        self.header_font = pygame.font.SysFont("Arial", 10)
        self.net_font = pygame.font.SysFont("Arial", 11, bold=True)

        # Cached surfaces for headers (rotated text)
        self._header_cache: Dict[str, pygame.Surface] = {}

    def update(self, component: Optional['Component']):
        """
        Update the grid with data from a component.

        Args:
            component: Component to display modifier effects for, or None
        """
        self.current_component = component
        self._clear_ui()

        if not component:
            self.stat_columns = []
            self.modifier_rows = []
            return

        # Get modifier stat summary from component
        summary = component.get_modifier_stat_summary()

        # Get stats this component's abilities actually consume
        component_stats = self._get_component_consumed_stats(component)

        # Filter to only affected stats that the component actually uses
        self.stat_columns = self._get_affected_stats(summary, component_stats)

        # Build row data for each modifier
        self.modifier_rows = []
        effects = component.get_all_modifier_effects()

        # Group effects by modifier
        modifier_effects: Dict[str, Dict[str, Any]] = {}
        for effect in effects:
            mod_id = effect.source_modifier_id
            if mod_id not in modifier_effects:
                modifier_effects[mod_id] = {
                    'name': effect.source_modifier_name,
                    'stats': {}
                }
            modifier_effects[mod_id]['stats'][effect.stat_key] = {
                'value': effect.value,
                'operation': effect.operation
            }

        for mod_id, mod_data in modifier_effects.items():
            self.modifier_rows.append({
                'id': mod_id,
                'name': mod_data['name'],
                'stats': mod_data['stats']
            })

        # Store summary for net values
        self._stat_summary = summary

        # Build the UI
        self._build_ui()

    def _get_component_consumed_stats(self, component: 'Component') -> Optional[set]:
        """
        Get all stat keys that this component's abilities actually consume.

        This filters the grid to only show stats the component can be affected by.
        For example, weapons consume damage_mult/range_mult but not thrust_mult.

        Args:
            component: The component to check

        Returns:
            Set of stat_key strings that the component's abilities use,
            or None if the component has no ability_instances (show all stats)
        """
        if not hasattr(component, 'ability_instances') or not component.ability_instances:
            return None  # No filtering - show all affected stats

        stat_keys = set()
        for ability in component.ability_instances:
            ability_class = ability.__class__
            # Get stat keys from STAT_BINDINGS
            if hasattr(ability_class, 'STAT_BINDINGS'):
                for binding in ability_class.STAT_BINDINGS:
                    stat_keys.add(binding.stat_key.value)

        return stat_keys if stat_keys else None

    def _get_affected_stats(self, summary: Dict[str, Dict], filter_stats: Optional[set] = None) -> List[str]:
        """
        Get list of stat keys that are actually affected (not at default).

        Args:
            summary: Stat summary from component.get_modifier_stat_summary()
            filter_stats: Optional set of stat keys to filter to (component's consumed stats).
                          If None, all affected stats are returned.

        Returns:
            List of stat_key strings for stats that have changed
        """
        affected = []
        for stat_key, data in summary.items():
            # If filter provided, skip stats not in the filter
            if filter_stats is not None and stat_key not in filter_stats:
                continue

            operation = data.get('operation', 'multiply')
            net_value = data.get('net_value', 0)

            # Default values
            if operation == 'multiply':
                default = 1.0
            else:
                default = 0.0

            # Check if different from default (with tolerance)
            if abs(net_value - default) > 0.001:
                affected.append(stat_key)

        return affected

    def _format_stat_name(self, stat_key: str) -> str:
        """
        Format stat key for display (remove _mult/_add suffix, title case).

        Args:
            stat_key: Raw stat key like 'mass_mult' or 'arc_add'

        Returns:
            Formatted name like 'Mass' or 'Arc'
        """
        # Remove common suffixes
        name = stat_key
        for suffix in ['_mult', '_add', '_set']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break

        # Handle special cases
        name = name.replace('_', ' ').title()

        # Abbreviations
        if name.lower() == 'hp':
            return 'HP'

        return name

    def _format_value(self, value: float, operation: str) -> str:
        """
        Format a modifier value for display with 4 significant digits.

        Args:
            value: The numeric value
            operation: 'multiply', 'add', or 'set'

        Returns:
            Formatted string like 'x73.73' or '+90'
        """
        if operation == 'multiply':
            return f"x{self._format_sig_digits(value)}"
        elif operation == 'add':
            formatted = self._format_sig_digits(value)
            if value >= 0:
                return f"+{formatted}"
            else:
                return formatted
        elif operation == 'set':
            return f"={self._format_sig_digits(value)}"
        return str(value)

    def _format_sig_digits(self, value: float, sig_digits: int = 4) -> str:
        """
        Format a value to a specified number of significant digits.

        Examples:
            1000.73 -> '1001'
            350.76 -> '350.8'
            73.725 -> '73.73'
            1.131 -> '1.131'
            0.617 -> '0.617'

        Args:
            value: The numeric value
            sig_digits: Number of significant digits (default 4)

        Returns:
            Formatted string
        """
        abs_val = abs(value)

        if abs_val == 0:
            return "0"

        if abs_val >= 1000:
            # No decimals for values >= 1000
            return f"{round(value)}"
        elif abs_val >= 100:
            # 1 decimal place for values >= 100
            return f"{value:.1f}"
        elif abs_val >= 10:
            # 2 decimal places for values >= 10
            return f"{value:.2f}"
        else:
            # 3 decimal places for values < 10
            return f"{value:.3f}"

    def _get_value_color(self, value: float, operation: str) -> tuple:
        """
        Get color for a value based on whether it's a buff or debuff.

        Args:
            value: The numeric value
            operation: 'multiply', 'add', or 'set'

        Returns:
            RGB tuple for the color
        """
        if operation == 'multiply':
            if value > 1.0:
                return self.COLOR_BUFF
            elif value < 1.0:
                return self.COLOR_DEBUFF
            else:
                return self.COLOR_NEUTRAL
        elif operation == 'add':
            if value > 0:
                return self.COLOR_BUFF
            elif value < 0:
                return self.COLOR_DEBUFF
            else:
                return self.COLOR_NEUTRAL
        return self.COLOR_NEUTRAL

    def _get_rotated_header(self, text: str) -> pygame.Surface:
        """
        Get a rotated header surface, using cache.

        Args:
            text: Header text

        Returns:
            Rotated pygame Surface
        """
        if text not in self._header_cache:
            surf = self.header_font.render(text, True, self.COLOR_TEXT)
            rotated = pygame.transform.rotate(surf, 45)
            self._header_cache[text] = rotated
        return self._header_cache[text]

    def _build_ui(self):
        """Build the grid UI elements."""
        if not self.stat_columns:
            # No affected stats - show message
            msg = UILabel(
                relative_rect=pygame.Rect(10, 10, self.rect.width - 20, 24),
                text="No modifier effects to display",
                manager=self.manager,
                container=self.panel
            )
            self._ui_elements.append(msg)
            return

        # Title
        title = UILabel(
            relative_rect=pygame.Rect(5, 2, self.NAME_COLUMN_WIDTH, 20),
            text="── Modifier Impact ──",
            manager=self.manager,
            container=self.panel
        )
        self._ui_elements.append(title)

        # Expand button in upper-right corner
        btn_size = 24
        self.expand_btn = UIButton(
            relative_rect=pygame.Rect(self.rect.width - btn_size - 5, 2, btn_size, btn_size - 4),
            text="⬜",  # Unicode expand icon
            manager=self.manager,
            container=self.panel,
            object_id='#expand_grid_btn',
            tool_tip_text="Expand to larger view"
        )
        self._ui_elements.append(self.expand_btn)

        # We'll draw the actual grid content in draw() method
        # since pygame_gui doesn't have a native grid/table

    def draw(self, screen: pygame.Surface):
        """
        Draw the grid content on top of the panel.

        Called from the parent UI's draw method.

        Args:
            screen: Surface to draw on
        """
        if not self.stat_columns or not self.current_component:
            return

        # Get the panel's absolute screen position
        abs_rect = self.panel.get_abs_rect()
        base_x = abs_rect.x
        base_y = abs_rect.y + self.TITLE_HEIGHT  # Below title

        # Set up clipping for the content area (below title and header)
        content_area = pygame.Rect(
            base_x,
            base_y + self.HEADER_HEIGHT,
            abs_rect.width,
            abs_rect.height - self.TITLE_HEIGHT - self.HEADER_HEIGHT
        )
        old_clip = screen.get_clip()

        # Draw column headers (rotated) - above clip area
        header_y = base_y
        for i, stat_key in enumerate(self.stat_columns):
            header_x = base_x + self.NAME_COLUMN_WIDTH + (i * self.COLUMN_WIDTH) + 5

            stat_name = self._format_stat_name(stat_key)
            rotated = self._get_rotated_header(stat_name)

            # Position rotated header (center of rotation is bottom-left)
            screen.blit(rotated, (header_x, header_y))

        # Apply clipping for rows
        screen.set_clip(content_area.clip(old_clip))

        # Draw modifier rows (with scroll offset)
        row_y = base_y + self.HEADER_HEIGHT - self.scroll_offset_y
        for row_idx, row_data in enumerate(self.modifier_rows):
            # Skip rows above visible area
            if row_y + self.ROW_HEIGHT < content_area.top:
                row_y += self.ROW_HEIGHT
                continue
            # Stop if below visible area
            if row_y > content_area.bottom:
                break

            # Alternating row background
            bg_color = self.COLOR_ROW_ALT_BG if row_idx % 2 else self.COLOR_ROW_BG
            row_rect = pygame.Rect(base_x, row_y, abs_rect.width, self.ROW_HEIGHT)
            pygame.draw.rect(screen, bg_color, row_rect)

            # Modifier name (truncated)
            name_surf = self.font.render(row_data['name'][:12], True, self.COLOR_TEXT)
            screen.blit(name_surf, (base_x + 3, row_y + 3))

            # Values for each stat
            for col_idx, stat_key in enumerate(self.stat_columns):
                cell_x = base_x + self.NAME_COLUMN_WIDTH + (col_idx * self.COLUMN_WIDTH)

                stat_data = row_data['stats'].get(stat_key)
                if stat_data:
                    value = stat_data['value']
                    operation = stat_data['operation']
                    text = self._format_value(value, operation)
                    color = self._get_value_color(value, operation)

                    value_surf = self.font.render(text, True, color)
                    # Center in cell
                    text_x = cell_x + (self.COLUMN_WIDTH - value_surf.get_width()) // 2
                    screen.blit(value_surf, (text_x, row_y + 3))

            row_y += self.ROW_HEIGHT

        # Restore clipping before drawing footer
        screen.set_clip(old_clip)

        # Draw net values footer (at bottom of grid, outside clip area)
        if hasattr(self, '_stat_summary'):
            # Footer position - at bottom of panel (use absolute position)
            footer_y = abs_rect.y + abs_rect.height - self.ROW_HEIGHT
            footer_rect = pygame.Rect(base_x, footer_y, abs_rect.width, self.ROW_HEIGHT)
            pygame.draw.rect(screen, self.COLOR_FOOTER_BG, footer_rect)

            # "Net" label
            net_label = self.net_font.render("Net:", True, self.COLOR_TEXT)
            screen.blit(net_label, (base_x + 3, footer_y + 3))

            # Net value for each stat
            for col_idx, stat_key in enumerate(self.stat_columns):
                cell_x = base_x + self.NAME_COLUMN_WIDTH + (col_idx * self.COLUMN_WIDTH)

                stat_data = self._stat_summary.get(stat_key, {})
                net_value = stat_data.get('net_value', 1.0)
                operation = stat_data.get('operation', 'multiply')

                text = self._format_value(net_value, operation)
                color = self._get_value_color(net_value, operation)

                value_surf = self.net_font.render(text, True, color)
                text_x = cell_x + (self.COLUMN_WIDTH - value_surf.get_width()) // 2
                screen.blit(value_surf, (text_x, footer_y + 3))

    def handle_event(self, event) -> bool:
        """
        Handle pygame events for scrolling and button clicks.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        # Handle expand button click
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'expand_btn') and event.ui_element == self.expand_btn:
                self.show_expanded_popup()
                return True

        if event.type == pygame.MOUSEWHEEL:
            # Check if mouse is over the grid (use absolute position)
            mx, my = pygame.mouse.get_pos()
            abs_rect = self.panel.get_abs_rect()
            if abs_rect.collidepoint(mx, my):
                # Calculate scroll
                total_content_height = (len(self.modifier_rows) + 1) * self.ROW_HEIGHT
                visible_height = abs_rect.height - self.TITLE_HEIGHT - self.HEADER_HEIGHT - self.ROW_HEIGHT
                max_scroll = max(0, total_content_height - visible_height)

                # Scroll direction (event.y is positive for up, negative for down)
                self.scroll_offset_y -= event.y * self.ROW_HEIGHT

                # Clamp
                self.scroll_offset_y = max(0, min(max_scroll, self.scroll_offset_y))
                return True

        return False

    def _clear_ui(self):
        """Clear all dynamically created UI elements."""
        for element in self._ui_elements:
            element.kill()
        self._ui_elements = []
        self._header_cache.clear()

    def kill(self):
        """Clean up all UI elements."""
        self._clear_ui()
        if self.panel and self.panel.alive():
            self.panel.kill()

    def set_position(self, pos: tuple):
        """Set the position of the grid panel."""
        self.rect.topleft = pos
        self.panel.set_position(pos)

    def show_expanded_popup(self):
        """
        Show an expanded popup window with a larger view of the grid.

        Creates a UIWindow approximately 4x the size of the current grid
        containing a larger ModifierImpactGrid instance.
        """
        if not self.current_component:
            return

        # Calculate expanded size (approximately 4x area = 2x each dimension)
        expanded_width = 600
        expanded_height = 500

        # Center on screen (rough estimate, actual screen size not available)
        # Use a reasonable default position
        win_x = 200
        win_y = 100

        # Create the popup window
        self.expanded_window = UIWindow(
            rect=pygame.Rect(win_x, win_y, expanded_width, expanded_height),
            manager=self.manager,
            window_display_title=f"Modifier Impact: {self.current_component.name}",
            resizable=True
        )

        # Create a larger grid inside the window
        grid_rect = pygame.Rect(5, 5, expanded_width - 30, expanded_height - 60)
        self.expanded_grid = ModifierImpactGrid(
            self.manager,
            self.expanded_window,
            grid_rect
        )
        self.expanded_grid.update(self.current_component)
        self.expanded_grid.panel.show()
