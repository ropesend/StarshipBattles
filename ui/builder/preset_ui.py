import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel
import tkinter as tk
from tkinter import simpledialog

# Hidden root window for dialogs
tk_root = tk.Tk()
tk_root.withdraw()

class PresetManagerUI:
    """
    Handles the UI for saving, loading, and listing modifier presets.
    """
    def __init__(self, manager, container, width, preset_manager):
        self.manager = manager
        self.container = container
        self.width = width
        self.preset_manager = preset_manager
        
        self.ui_elements = [] # Generic storage for labels
        self.preset_buttons = [] # (name, btn)
        self.preset_delete_buttons = [] # (name, btn)
        self.save_preset_btn = None
        
    def layout(self, start_y):
        """Constructs the preset UI."""
        self.clear()
        y = start_y
        
        y += 10
        self.save_preset_btn = UIButton(
            relative_rect=pygame.Rect(10, y, self.width - 20, 28),
            text="💾 Save Current Settings",
            manager=self.manager,
            container=self.container
        )
        self.ui_elements.append(self.save_preset_btn)
        y += 35
        
        presets = self.preset_manager.get_all_presets()
        if presets:
            preset_label = UILabel(
                relative_rect=pygame.Rect(10, y, 200, 20),
                text="Saved Presets:",
                manager=self.manager,
                container=self.container
            )
            self.ui_elements.append(preset_label)
            y += 22
            
        for preset_name in presets.keys():
            safe_id = preset_name.replace(' ', '_').replace('.', '_')
            
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.width - 60, 28),
                text=f"📋 {preset_name}",
                manager=self.manager,
                container=self.container,
                object_id=f'#preset_{safe_id}'
            )
            self.preset_buttons.append((preset_name, btn))
            self.ui_elements.append(btn)
            
            del_btn = UIButton(
                relative_rect=pygame.Rect(self.width - 45, y, 35, 28),
                text="🗑",
                manager=self.manager,
                container=self.container,
                object_id=f'#preset_del_{safe_id}'
            )
            self.preset_delete_buttons.append((preset_name, del_btn))
            self.ui_elements.append(del_btn)
            y += 30
            
        return y
        
    def clear(self):
        for el in self.ui_elements:
            el.kill()
        self.ui_elements = []
        self.preset_buttons = []
        self.preset_delete_buttons = []
        self.save_preset_btn = None
        
    def handle_event(self, event, template_modifiers):
        """Returns (action_type, data) or None."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.save_preset_btn and event.ui_element == self.save_preset_btn:
                if template_modifiers:
                    preset_name = simpledialog.askstring("Save Preset", "Enter preset name:", parent=tk_root)
                    if preset_name:
                         self.preset_manager.save_preset(preset_name, template_modifiers)
                         return ('refresh_ui', None)

            for p_name, btn in self.preset_buttons:
                 if event.ui_element == btn:
                     preset = self.preset_manager.get_preset(p_name)
                     if preset:
                         return ('apply_preset', dict(preset))
                         
            for p_name, btn in self.preset_delete_buttons:
                 if event.ui_element == btn:
                     self.preset_manager.delete_preset(p_name)
                     return ('refresh_ui', None)
                     
        return None
