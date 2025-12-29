import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UITextEntryLine, UIHorizontalSlider
from components import MODIFIER_REGISTRY
from logger import log_info, log_debug
import tkinter as tk
from tkinter import simpledialog

# Hidden root window for dialogs
tk_root = tk.Tk()
tk_root.withdraw()

class ModifierEditorPanel:
    def __init__(self, manager, container, width, preset_manager, on_change_callback):
        self.manager = manager
        self.container = container
        self.width = width
        self.preset_manager = preset_manager
        self.on_change_callback = on_change_callback
        
        # UI Elements
        self.modifier_buttons = []
        self.modifier_sliders = []
        self.modifier_entries = []
        self.modifier_extra_ui = []
        self.preset_buttons = []
        self.preset_delete_buttons = []
        
        # State
        self.active_slider_mod_id = None

    def rebuild(self, editing_component, template_modifiers):
        """Rebuild the modifier UI based on current state."""
        self.editing_component = editing_component
        self.template_modifiers = template_modifiers
        
        # Clear existing
        self._clear_ui()
        
    def _clear_ui(self):
        for btn in self.modifier_buttons: btn.kill()
        self.modifier_buttons = []
        for slider in self.modifier_sliders: 
            if slider: slider.kill()
        self.modifier_sliders = []
        for entry in self.modifier_entries:
            if entry: entry.kill()
        self.modifier_entries = []
        for el in self.modifier_extra_ui:
            if el is None:
                continue
            if isinstance(el, dict):
                 # Handle special dict objects like step buttons
                 if el.get('type') == 'step_btns':
                     for btn in el.get('btns', []):
                         if btn: btn.kill()
            elif hasattr(el, 'kill'):
                el.kill()
        self.modifier_extra_ui = []
        for _, btn in self.preset_buttons: btn.kill()
        self.preset_buttons = []
        for _, btn in self.preset_delete_buttons: btn.kill()
        self.preset_delete_buttons = []

    def layout(self, start_y):
        """Construct the UI elements starting at start_y."""
        y = start_y
        
        # Title
        if self.editing_component:
            title_text = f"── Editing: {self.editing_component.name} ──"
        else:
            title_text = "── New Component Settings ──"
            
        settings_label = UILabel(
            relative_rect=pygame.Rect(10, y, self.width - 20, 28),
            text=title_text,
            manager=self.manager,
            container=self.container
        )
        self.modifier_extra_ui.append(settings_label)
        y += 32
        
        # Clear/Deselect Button
        if self.editing_component:
            btn_text = "✕ Deselect Component"
        else:
            btn_text = "🔄 Clear Settings"
            
        self.clear_settings_btn = UIButton(
            relative_rect=pygame.Rect(10, y, self.width - 20, 28),
            text=btn_text,
            manager=self.manager,
            container=self.container
        )
        self.modifier_extra_ui.append(self.clear_settings_btn)
        y += 35
        
        # Modifiers List
        self.modifier_id_list = []
        
        for mod_id, mod_def in MODIFIER_REGISTRY.items():
            # Check restrictions
            if self.editing_component:
                allow = True
                if mod_def.restrictions:
                    if 'allow_types' in mod_def.restrictions:
                        if self.editing_component.type_str not in mod_def.restrictions['allow_types']:
                            allow = False
                    if 'deny_types' in mod_def.restrictions:
                        if self.editing_component.type_str in mod_def.restrictions['deny_types']:
                            allow = False
                if not allow: continue
                
                existing_mod = self.editing_component.get_modifier(mod_id)
                is_active = existing_mod is not None
                current_val = existing_mod.value if is_active else mod_def.min_val
            else:
                is_active = mod_id in self.template_modifiers
                current_val = self.template_modifiers.get(mod_id, mod_def.min_val) if is_active else mod_def.min_val
                
            self.modifier_id_list.append(mod_id)
            
            # Sanitize ID for UI (pygame_gui doesn't allow spaces/dots in IDs)
            safe_mod_id = mod_id.replace(' ', '_').replace('.', '_')
            
            text = f"[{'x' if is_active else ' '}] {mod_def.name}"
            is_readonly = getattr(mod_def, 'readonly', False)
            if is_readonly:
                # If readonly, we still show it but maybe different text?
                # User requested "show on the left side... but it should not be clickacble"
                if is_active:
                     text = f"[AUTO] {mod_def.name}"
                else: 
                     text = f"[   ] {mod_def.name}" # Should not happen if auto-applied from template
            
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, 170, 28),
                text=text,
                manager=self.manager,
                container=self.container,
                object_id=f'#mod_{safe_mod_id}'
            )
            if is_readonly: 
                btn.disable()
            self.modifier_buttons.append(btn)
            
            if mod_def.type_str == 'linear':
                # Layout: Label (Already created as btn) | Entry | << | < | Slider | > | >>
                # Label Button Width: 170 (Existing)
                # Available Width = Self.width - 20 - 170 = ~230 (Assuming panel is 450?)
                # Wait, panel width passed to init.
                # Left Panel width is 450.
                # Label: 170. Entry: 50. <<: 25. < 25. > 25. >> 25.
                # Slider gets remainder.
                
                # Entry
                entry_x = 185
                entry_w = 60
                entry = UITextEntryLine(
                    relative_rect=pygame.Rect(entry_x, y, entry_w, 28),
                    manager=self.manager,
                    container=self.container,
                    object_id=f'#entry_{safe_mod_id}'
                )
                entry.set_text(f"{current_val:.2f}")
                if not is_active: entry.disable()
                self.modifier_entries.append(entry)
                
                # Define buttons if range allows large steps
                show_buttons = (mod_def.max_val - mod_def.min_val) >= 20
                
                current_x = entry_x + entry_w + 5
                
                slider_btns = []
                if show_buttons:
                    # << (-100)
                    btn_m100 = UIButton(pygame.Rect(current_x, y, 25, 28), "<<", manager=self.manager, container=self.container)
                    slider_btns.append(btn_m100)
                    current_x += 27
                    
                    # < (-10)
                    btn_m10 = UIButton(pygame.Rect(current_x, y, 25, 28), "<", manager=self.manager, container=self.container)
                    slider_btns.append(btn_m10)
                    current_x += 27
                    
                # Slider
                # Calculate remaining width for slider
                # Need space for right buttons if showing
                right_btns_w = 54 if show_buttons else 0
                slider_w = (self.width - 20) - current_x - right_btns_w - 5
                
                step = 0.01
                if mod_id == 'range_mount': step = 0.1
                elif mod_def.max_val - mod_def.min_val > 50: step = 1.0
                elif mod_def.max_val - mod_def.min_val > 10: step = 0.1
                
                slider = UIHorizontalSlider(
                    relative_rect=pygame.Rect(current_x, y, slider_w, 28),
                    start_value=float(current_val),
                    value_range=(float(mod_def.min_val), float(mod_def.max_val)),
                    manager=self.manager,
                    container=self.container,
                    object_id=f'#slider_{safe_mod_id}',
                    click_increment=step
                )
                if not is_active: slider.disable()
                self.modifier_sliders.append(slider)
                current_x += slider_w + 2
                
                if show_buttons:
                     # > (+10)
                    btn_p10 = UIButton(pygame.Rect(current_x, y, 25, 28), ">", manager=self.manager, container=self.container)
                    slider_btns.append(btn_p10)
                    current_x += 27
                    
                    # >> (+100)
                    btn_p100 = UIButton(pygame.Rect(current_x, y, 25, 28), ">>", manager=self.manager, container=self.container)
                    slider_btns.append(btn_p100)
                    
                # Store buttons for event handling (list of dicts or tuples?)
                # Store related to this modifier index
                if show_buttons:
                    # m100, m10, p10, p100
                    self.modifier_extra_ui.append({'type': 'step_btns', 'mod_id': mod_id, 'btns': slider_btns})
                    for b in slider_btns:
                        if not is_active: b.disable()
                else:
                    self.modifier_extra_ui.append(None)
                    
            else:
                self.modifier_entries.append(None)
                self.modifier_sliders.append(None)
                self.modifier_extra_ui.append(None)
                
            y += 32
            
        # Presets (only in template mode)
        if not self.editing_component:
            y += 10
            self.save_preset_btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.width - 20, 28),
                text="💾 Save Current Settings",
                manager=self.manager,
                container=self.container
            )
            self.modifier_extra_ui.append(self.save_preset_btn)
            y += 35
            
            presets = self.preset_manager.get_all_presets()
            if presets:
                preset_label = UILabel(
                    relative_rect=pygame.Rect(10, y, 200, 20),
                    text="Saved Presets:",
                    manager=self.manager,
                    container=self.container
                )
                self.modifier_extra_ui.append(preset_label)
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
                
                del_btn = UIButton(
                    relative_rect=pygame.Rect(self.width - 45, y, 35, 28),
                    text="🗑",
                    manager=self.manager,
                    container=self.container,
                    object_id=f'#preset_del_{safe_id}'
                )
                self.preset_delete_buttons.append((preset_name, del_btn))
                y += 30
    
    def handle_event(self, event):
        """Processes events and updates state. Returns (action_type, data) or None."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:
                return ('clear_settings', None)
            
            elif hasattr(self, 'save_preset_btn') and event.ui_element == self.save_preset_btn:
                if self.template_modifiers:
                    preset_name = simpledialog.askstring("Save Preset", "Enter preset name:", parent=tk_root)
                        
            # Preset Delete
            for preset_name, btn in self.preset_delete_buttons:
                if event.ui_element == btn:
                    self.preset_manager.delete_preset(preset_name)
                    return ('refresh_ui', None)
            
            # Preset Apply
            for preset_name, btn in self.preset_buttons:
                if event.ui_element == btn:
                    preset = self.preset_manager.get_preset(preset_name)
                    if preset:
                        return ('apply_preset', dict(preset))
            
            # Modifier Toggles
            for i, btn in enumerate(self.modifier_buttons):
                if event.ui_element == btn and i < len(self.modifier_id_list):
                    mod_id = self.modifier_id_list[i]
                    mod_def = MODIFIER_REGISTRY[mod_id]

                    if self.editing_component:
                         # Update component directly
                         if self.editing_component.get_modifier(mod_id):
                             self.editing_component.remove_modifier(mod_id)
                             is_active = False
                         else:
                             self.editing_component.add_modifier(mod_id)
                             is_active = True
                         
                         # Immediate UI feedback
                         btn.set_text(f"[{'x' if is_active else ' '}] {mod_def.name}")
                         
                         # Enable/Disable slider/entry and extra UI
                         if i < len(self.modifier_sliders) and self.modifier_sliders[i]:
                             if is_active:
                                 self.modifier_sliders[i].enable()
                                 # Ensure value is synced
                                 if self.editing_component:
                                     m = self.editing_component.get_modifier(mod_id)
                                     val = m.value if m else mod_def.min_val
                                 else:
                                     val = self.template_modifiers.get(mod_id, mod_def.min_val)
                                 self.modifier_sliders[i].set_current_value(val)
                             else:
                                 self.modifier_sliders[i].disable()

                         if i < len(self.modifier_entries) and self.modifier_entries[i]:
                             if is_active:
                                 self.modifier_entries[i].enable()
                                 if self.editing_component:
                                     m = self.editing_component.get_modifier(mod_id)
                                     val = m.value if m else mod_def.min_val
                                 else:
                                     val = self.template_modifiers.get(mod_id, mod_def.min_val)
                                 self.modifier_entries[i].set_text(f"{val:.2f}")
                             else:
                                 self.modifier_entries[i].disable()
                        
                         # Enable/Disable Step Buttons
                         extra = self.modifier_extra_ui[i] if i < len(self.modifier_extra_ui) else None
                         if isinstance(extra, dict) and extra.get('type') == 'step_btns':
                             for b in extra['btns']:
                                 if is_active: b.enable()
                                 else: b.disable()

                         if self.editing_component:
                             self.editing_component.recalculate_stats()
                             self.on_change_callback() # Notify ship Update
                         
                         return ('refresh_ui', None)
            
            # Additional check: Step Buttons Pressed
            # Loop through buttons?
            # modifier_extra_ui maps 1:1 with modifier index (mostly)
            # Actually extra UI for label/button is separate list?
            # Wait, self.modifier_extra_ui has mixed content (Labels, Buttons, and None/Dicts for rows)
            # My logic in layout:
            # 0: Label
            # 1: Clear Btn
            # Then loop modifiers: append dict or None.
            # So indices align with self.modifier_id_list IF we account for the first 2.
            # No, I appended to modifier_extra_ui INSIDE the loop. 
            # I must be careful. 
            # Review layout:
            # self.modifier_extra_ui.append(settings_label) -> Index 0
            # self.modifier_extra_ui.append(self.clear_settings_btn) -> Index 1
            # Loop: self.modifier_extra_ui.append(...) -> Index 2+i
            
            # Start loop at 0 for modifiers, check index + 2 in extra_ui
            for i, extra in enumerate(self.modifier_extra_ui):
                 if isinstance(extra, dict) and extra.get('type') == 'step_btns':
                     btns = extra['btns']
                     # [m100, m10, p10, p100]
                     delta = 0
                     if event.ui_element == btns[0]: delta = -100
                     elif event.ui_element == btns[1]: delta = -10
                     elif event.ui_element == btns[2]: delta = 10
                     elif event.ui_element == btns[3]: delta = 100
                     
                     if delta != 0:
                         # Find which modifier this is
                         # extra_ui index i corresponds to modifier index i - 2
                         mod_index = i - 2
                         if 0 <= mod_index < len(self.modifier_id_list):
                             mod_id = self.modifier_id_list[mod_index]
                             slider = self.modifier_sliders[mod_index]
                             entry = self.modifier_entries[mod_index]
                             
                             if slider:
                                 current = slider.get_current_value()
                                 mod_def = MODIFIER_REGISTRY[mod_id]
                                 new_val = max(mod_def.min_val, min(mod_def.max_val, current + delta))
                                 
                                 slider.set_current_value(new_val)
                                 if entry: entry.set_text(f"{new_val:.2f}")
                                 
                                 # Update model
                                 if self.editing_component:
                                     m = self.editing_component.get_modifier(mod_id)
                                     if m:
                                         m.value = new_val
                                         self.editing_component.recalculate_stats()
                                         self.on_change_callback()
                                 else:
                                     if mod_id in self.template_modifiers:
                                         self.template_modifiers[mod_id] = new_val

                                 return ('refresh_ui', None)
                         
             
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
             for i, slider in enumerate(self.modifier_sliders):
                 if slider and event.ui_element == slider and i < len(self.modifier_id_list):
                     mod_id = self.modifier_id_list[i]
                     val = slider.get_current_value()
                     
                     if self.editing_component:
                         m = self.editing_component.get_modifier(mod_id)
                         if m:
                             m.value = val
                             if i < len(self.modifier_entries) and self.modifier_entries[i]:
                                 self.modifier_entries[i].set_text(f"{val:.2f}")
                                 
                             # Immediate update (User requested immediate vs throttled)
                             if self.editing_component:
                                 self.editing_component.recalculate_stats()
                                 self.on_change_callback()

                     else:
                         if mod_id in self.template_modifiers:
                             self.template_modifiers[mod_id] = val
                             if i < len(self.modifier_entries) and self.modifier_entries[i]:
                                 self.modifier_entries[i].set_text(f"{val:.2f}")
                     break

        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED or event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            for i, entry in enumerate(self.modifier_entries):
                if entry and event.ui_element == entry and i < len(self.modifier_id_list):
                    try:
                        new_val = float(event.text)
                        mod_id = self.modifier_id_list[i]
                        mod_def = MODIFIER_REGISTRY.get(mod_id)
                        if mod_def:
                            new_val = max(mod_def.min_val, min(mod_def.max_val, new_val))
                            
                            if self.editing_component:
                                m = self.editing_component.get_modifier(mod_id)
                                if m:
                                    m.value = new_val
                                    self.editing_component.recalculate_stats()
                                    self.on_change_callback()
                            else:
                                if mod_id in self.template_modifiers:
                                    self.template_modifiers[mod_id] = new_val
                            
                            if i < len(self.modifier_sliders) and self.modifier_sliders[i]:
                                self.modifier_sliders[i].set_current_value(new_val)
                            
                            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                                entry.set_text(f"{new_val:.2f}")
                    except ValueError:
                        pass
                    break
        
        return None
