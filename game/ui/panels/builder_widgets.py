"""
Builder Widgets - UI components for the Design Workshop.

PROJ-38: Added registries parameter for dependency injection.
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIScrollingContainer
from typing import Optional, TYPE_CHECKING
from game.core.registry import get_default_registry_provider
from game.core.logger import log_info, log_debug

from game.ui.screens.builder.modifier_logic import ModifierLogic
from game.ui.screens.builder.modifier_config import MODIFIER_UI_CONFIG, DEFAULT_CONFIG
from game.ui.screens.builder.modifier_row import ModifierControlRow

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


class ModifierEditorPanel:
    """
    Panel for editing component modifiers with scrolling support.

    Uses UIScrollingContainer to handle overflow when many modifiers are present.
    """

    def __init__(self, manager, container, width, on_change_callback,
                 *, registries: Optional['GameRegistries'] = None):
        """
        Initialize the ModifierEditorPanel.

        PROJ-38: Added registries parameter for DI.

        Args:
            manager: pygame_gui UIManager
            container: Parent container
            width: Panel width
            on_change_callback: Callback when modifier changes
            registries: Optional GameRegistries for DI
        """
        self.manager = manager
        self.container = container
        self.width = width
        self.on_change_callback = on_change_callback
        self._registries = registries

        # State
        self.editing_component = None
        self.is_readonly = False
        self._panel_height = 300  # Default, updated by layout()

        # UI Elements
        self.extra_ui_elements = []  # Headers, global buttons
        self.modifier_rows = {}  # mod_id -> ModifierControlRow
        self.scroll_container = None  # UIScrollingContainer for modifier rows
        self._cached_scroll_position = 0  # Preserve scroll on rebuild

    def _get_modifiers(self):
        """PROJ-38: Get modifiers from registries or provider fallback."""
        if self._registries is not None:
            return self._registries.modifiers
        return get_default_registry_provider().get_modifiers()

    def rebuild(self, editing_component, is_readonly=False):
        """Rebuild/Update the modifier UI based on current state."""
        self.editing_component = editing_component
        self.is_readonly = is_readonly

        if self.editing_component:
            # Ensure mandatory modifiers are present in data model
            ModifierLogic.ensure_mandatory_modifiers(self.editing_component)

    def set_panel_height(self, height):
        """Set the available height for the modifier panel."""
        self._panel_height = height

    def layout(self, start_y):
        """Update layout and reconciliation with scrolling support."""
        # Cache scroll position before clearing
        if self.scroll_container:
            self._cached_scroll_position = self.scroll_container.vert_scroll_bar.scroll_position if hasattr(self.scroll_container, 'vert_scroll_bar') and self.scroll_container.vert_scroll_bar else 0

        self._clear_extra_ui()
        self._clear_scroll_container()

        y = start_y

        # 1. Header & Global Controls (outside scroll container)
        if self.editing_component:
            title_text = f"── Editing: {self.editing_component.name} ──"

            settings_label = UILabel(
                relative_rect=pygame.Rect(10, y, self.width - 20, 28),
                text=title_text,
                manager=self.manager,
                container=self.container
            )
            self.extra_ui_elements.append(settings_label)
            y += 32

            self.clear_settings_btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.width - 20, 28),
                text="✕ Deselect Component",
                manager=self.manager,
                container=self.container
            )
            self.extra_ui_elements.append(self.clear_settings_btn)
            y += 35

            # 2. Calculate content height and create scroll container
            scroll_start_y = y
            available_scroll_height = self._panel_height - scroll_start_y + start_y

            # Calculate total content height needed
            current_mod_ids = []
            content_height = 0
            row_height = 28  # Compact row height
            for mod_id, mod_def in self._get_modifiers().items():
                if ModifierLogic.is_modifier_allowed(mod_id, self.editing_component):
                    current_mod_ids.append(mod_id)
                    content_height += row_height + 2  # 2px gap between rows

            # Create scroll container
            self.scroll_container = UIScrollingContainer(
                relative_rect=pygame.Rect(0, scroll_start_y, self.width, available_scroll_height),
                manager=self.manager,
                container=self.container,
                allow_scroll_x=False
            )
            self.scroll_container.set_scrollable_area_dimensions((self.width - 20, max(content_height, available_scroll_height)))
            self.extra_ui_elements.append(self.scroll_container)

            # 3. Build modifier rows inside scroll container
            row_y = 0
            modifiers = self._get_modifiers()
            for mod_id in current_mod_ids:
                mod_def = modifiers[mod_id]
                self._ensure_row(mod_id, mod_def, row_y, self.scroll_container)

                row = self.modifier_rows[mod_id]

                # Update Position if needed (re-layout)
                if not hasattr(row, 'y') or row.y != row_y:
                    row.build_ui(row_y)

                row.update(self.editing_component, is_readonly=self.is_readonly)
                row_y += row.height + 2  # 2px gap

            # Remove stale rows
            active_set = set(current_mod_ids)
            existing_set = set(self.modifier_rows.keys())
            to_remove = existing_set - active_set
            for mid in to_remove:
                self.modifier_rows[mid].kill()
                del self.modifier_rows[mid]

            # Restore scroll position
            if self._cached_scroll_position > 0 and self.scroll_container.vert_scroll_bar:
                self.scroll_container.vert_scroll_bar.scroll_position = min(
                    self._cached_scroll_position,
                    self.scroll_container.vert_scroll_bar.scrollable_height
                )
        else:
            # No component selected - show message
            self._clear_all_rows()

            msg_label = UILabel(
                relative_rect=pygame.Rect(10, y, self.width - 20, 28),
                text="── Component Modifiers ──",
                manager=self.manager,
                container=self.container
            )
            self.extra_ui_elements.append(msg_label)
            y += 35

            hint_label = UILabel(
                relative_rect=pygame.Rect(10, y, self.width - 20, 28),
                text="Select a component to edit modifiers",
                manager=self.manager,
                container=self.container
            )
            self.extra_ui_elements.append(hint_label)

    def _clear_scroll_container(self):
        """Clear the scroll container and all modifier rows.

        When the scroll container is killed, all UI elements inside it are also killed.
        We must clear self.modifier_rows to ensure rows are rebuilt with fresh UI
        when a new scroll container is created.
        """
        if self.scroll_container:
            self.scroll_container.kill()
            self.scroll_container = None
        # Clear modifier rows - their UI elements were killed with the scroll container
        # This ensures build_ui() is called for all rows when layout() runs
        self._clear_all_rows()

    def _clear_all_rows(self):
        """Clear all modifier rows."""
        for row in self.modifier_rows.values():
            row.kill()
        self.modifier_rows = {}
            
    def _ensure_row(self, mod_id, mod_def, y, container=None):
        """Ensure a modifier row exists, creating it if necessary.

        Args:
            mod_id: Modifier ID
            mod_def: Modifier definition
            y: Y position for the row
            container: Optional container (uses scroll_container or self.container)
        """
        target_container = container if container else self.container
        row_width = self.width - 20 if container else self.width  # Account for scrollbar

        if mod_id not in self.modifier_rows:
            # Create new
            config = MODIFIER_UI_CONFIG.get(mod_id, DEFAULT_CONFIG)
            row = ModifierControlRow(
                self.manager, target_container, row_width,
                mod_id, mod_def, config, self._on_row_change
            )
            row.build_ui(y)
            self.modifier_rows[mod_id] = row
        else:
            # Update container reference if it changed
            row = self.modifier_rows[mod_id]
            if row.container != target_container:
                row.container = target_container
                row.width = row_width

    def _clear_extra_ui(self):
        for el in self.extra_ui_elements:
            el.kill()
        self.extra_ui_elements = []

    def _on_row_change(self, action_type, mod_id, value):
        """Callback from rows."""
        if not self.editing_component:
            return

        if action_type == 'toggle':
            # Value is bool (active)
            if value:
                self.editing_component.add_modifier(mod_id)
                # Set initial
                m = self.editing_component.get_modifier(mod_id)
                if m:
                    m.value = ModifierLogic.get_initial_value(mod_id, self.editing_component)
            else:
                self.editing_component.remove_modifier(mod_id)

            self.editing_component.recalculate_stats()
            self.on_change_callback()

        elif action_type == 'value_change':
            m = self.editing_component.get_modifier(mod_id)
            if m:
                m.value = value
                self.editing_component.recalculate_stats()
                self.on_change_callback()

        # Refresh row UI (enable/digits)
        if mod_id in self.modifier_rows:
            self.modifier_rows[mod_id].update(self.editing_component, is_readonly=self.is_readonly)

    def handle_event(self, event):
        """Processes events."""
        # 1. Check Global Buttons
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:
                return ('clear_settings', None)

        # 2. Delegate to Rows (only when editing a component)
        if self.editing_component:
            for row in self.modifier_rows.values():
                if row.handle_event(event):
                    # Row handled it and requested update
                    return ('refresh_ui', None)  # Force builder update

        return None
