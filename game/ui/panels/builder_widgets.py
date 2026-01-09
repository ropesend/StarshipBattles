import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIHorizontalSlider
from game.core.registry import get_modifier_registry
from game.core.logger import log_info, log_debug

from ui.builder.modifier_logic import ModifierLogic
from ui.builder.modifier_config import MODIFIER_UI_CONFIG, DEFAULT_CONFIG
from ui.builder.modifier_row import ModifierControlRow
from ui.builder.preset_ui import PresetManagerUI

class ModifierEditorPanel:
    def __init__(self, manager, container, width, preset_manager, on_change_callback):
        self.manager = manager
        self.container = container
        self.width = width
        self.preset_manager = preset_manager
        self.on_change_callback = on_change_callback
        
        # State
        self.editing_component = None
        self.template_modifiers = {}
        
        # UI Elements
        self.extra_ui_elements = [] # Headers, global buttons
        self.modifier_rows = {} # mod_id -> ModifierControlRow
        
        # Preset UI Sub-Component
        self.preset_ui = PresetManagerUI(manager, container, width, preset_manager)
        
    def rebuild(self, editing_component, template_modifiers, is_readonly=False):
        """Rebuild/Update the modifier UI based on current state."""
        self.editing_component = editing_component
        self.template_modifiers = template_modifiers
        self.is_readonly = is_readonly
        
        if self.editing_component:
            # Ensure mandatory modifiers are present in data model
            ModifierLogic.ensure_mandatory_modifiers(self.editing_component)

    def layout(self, start_y):
        """Update layout and reconciliation."""
        self._clear_extra_ui()
        
        y = start_y
        
        # 1. Header & Global Controls
        if self.editing_component:
            title_text = f"── Editing: {self.editing_component.name} ──"
            btn_text = "✕ Deselect Component"
        else:
            title_text = "── New Component Settings ──"
            btn_text = "🔄 Clear Settings"
            
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
            text=btn_text,
            manager=self.manager,
            container=self.container
        )
        self.extra_ui_elements.append(self.clear_settings_btn)
        y += 35
        
        # 2. Reconcile Rows
        current_mod_ids = []
        
        for mod_id, mod_def in get_modifier_registry().items():
            # Check availability
            allowed = False
            if self.editing_component:
                allowed = ModifierLogic.is_modifier_allowed(mod_id, self.editing_component)
            else:
                allowed = True
                
            if allowed:
                current_mod_ids.append(mod_id)
                self._ensure_row(mod_id, mod_def, y)
                
                # Update Row Height
                row = self.modifier_rows[mod_id]
                
                # Update Position if needed (re-layout)
                if not hasattr(row, 'y') or row.y != y:
                     row.build_ui(y)
                
                row.update(self.editing_component, self.template_modifiers, is_readonly=self.is_readonly)
                y += row.height
        
        # Remove stale rows
        active_set = set(current_mod_ids)
        existing_set = set(self.modifier_rows.keys())
        to_remove = existing_set - active_set
        for mid in to_remove:
            self.modifier_rows[mid].kill()
            del self.modifier_rows[mid]
            
        # 3. Presets (Template Mode)
        if not self.editing_component:
            y = self.preset_ui.layout(y)
        else:
            self.preset_ui.clear()
            
    def _ensure_row(self, mod_id, mod_def, y):
        if mod_id not in self.modifier_rows:
            # Create new
            config = MODIFIER_UI_CONFIG.get(mod_id, DEFAULT_CONFIG)
            row = ModifierControlRow(self.manager, self.container, self.width, mod_id, mod_def, config, self._on_row_change)
            row.build_ui(y)
            self.modifier_rows[mod_id] = row

    def _clear_extra_ui(self):
        for el in self.extra_ui_elements:
            el.kill()
        self.extra_ui_elements = []

    def _on_row_change(self, action_type, mod_id, value):
        """Callback from rows."""
        if action_type == 'toggle':
             # Value is bool (active)
             if self.editing_component:
                 if value:
                     self.editing_component.add_modifier(mod_id)
                     # Set initial
                     m = self.editing_component.get_modifier(mod_id)
                     if m: m.value = ModifierLogic.get_initial_value(mod_id, self.editing_component)
                 else:
                     self.editing_component.remove_modifier(mod_id)
                     
                 self.editing_component.recalculate_stats()
                 self.on_change_callback()
             else:
                 if value:
                     self.template_modifiers[mod_id] = ModifierLogic.get_initial_value(mod_id, None)
                 else:
                     if mod_id in self.template_modifiers:
                         del self.template_modifiers[mod_id]
                         
        elif action_type == 'value_change':
             if self.editing_component:
                 m = self.editing_component.get_modifier(mod_id)
                 if m:
                     m.value = value
                     self.editing_component.recalculate_stats()
                     self.on_change_callback()
             else:
                 if mod_id in self.template_modifiers:
                     self.template_modifiers[mod_id] = value
                     
        # Refresh row UI (enable/digits)
        if mod_id in self.modifier_rows:
            self.modifier_rows[mod_id].update(self.editing_component, self.template_modifiers)

    def handle_event(self, event):
        """Processes events."""
        # 1. Check Global Buttons
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:
                return ('clear_settings', None)
            

        # 2. delegate to Preset UI
        if not self.editing_component:
             res = self.preset_ui.handle_event(event, self.template_modifiers)
             if res: return res

        # 3. Delegate to Rows
        for row in self.modifier_rows.values():
            if row.handle_event(event):
                # Row handled it and requested update
                return ('refresh_ui', None) # Force builder update

        return None
