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
        self.step_btn_map = {} # btn_element -> (mod_id, step, direction/mode)
        
        self.preset_buttons = []
        self.preset_delete_buttons = []
        
        # State
        self.active_slider_mod_id = None
        self.extra_ui_elements = [] # Generic storage for labels/etc to kill

    def _calculate_snap_val(self, current, interval, direction, min_val, max_val):
        """Calculates the next snap value based on interval and direction."""
        if direction < 0:
            # Decrement
            remainder = current % interval
            if abs(remainder) < 0.001: # Float epsilon
                target = current - interval
            else:
                target = current - remainder
            return max(min_val, target)
        else:
            # Increment
            remainder = current % interval
            dist = interval - remainder
            # If we are very close to multiple, go to next
            if abs(remainder) < 0.001:
                target = current + interval
            else:
                target = current + dist
            return min(max_val, target)

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
        
        for el in self.extra_ui_elements:
            el.kill()
        self.extra_ui_elements = []
        
        # Step buttons are stored in map keys
        for btn in self.step_btn_map.keys():
             if btn.alive(): btn.kill()
        self.step_btn_map = {}
            
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
        self.extra_ui_elements.append(settings_label)
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
        self.extra_ui_elements.append(self.clear_settings_btn)
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
                
                # --- MANDATORY MODIFIER ENFORCEMENT ---
                if self.editing_component:
                    # Size Mount: Auto-apply to all, init 1
                    if mod_id == 'simple_size_mount':
                        if not self.editing_component.get_modifier(mod_id):
                            self.editing_component.add_modifier(mod_id)
                            m = self.editing_component.get_modifier(mod_id)
                            m.value = 1.0 # Init 1
                    
                    # Range Mount: Auto-apply to Projectile and Beam, init 0
                    elif mod_id == 'range_mount':
                        is_weapon = self.editing_component.type_str in ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']
                        if is_weapon and not self.editing_component.get_modifier(mod_id):
                             self.editing_component.add_modifier(mod_id)
                             m = self.editing_component.get_modifier(mod_id)
                             m.value = 0.0 # Init 0
                             
                    # Facing: Auto-apply to all weapons, default 0
                    elif mod_id == 'facing':
                         is_weapon = self.editing_component.type_str in ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']
                         if is_weapon and not self.editing_component.get_modifier(mod_id):
                                  self.editing_component.add_modifier(mod_id)
                                  m = self.editing_component.get_modifier(mod_id)
                                  m.value = 0.0 # Default 0

                existing_mod = self.editing_component.get_modifier(mod_id)
                is_active = existing_mod is not None
                current_val = existing_mod.value if is_active else mod_def.min_val
            else:
                is_active = mod_id in self.template_modifiers
                current_val = self.template_modifiers.get(mod_id, mod_def.min_val) if is_active else mod_def.min_val
                
            self.modifier_id_list.append(mod_id)
            
            # Sanitize ID for UI (pygame_gui doesn't allow spaces/dots in IDs)
            safe_mod_id = mod_id.replace(' ', '_').replace('.', '_')
            
            # Determine blocked state (non-removable)
            is_blocked = False
            if mod_id in ['simple_size_mount', 'range_mount', 'facing']:
                 is_blocked = True 
            
            text = f"[{'x' if is_active else ' '}] {mod_def.name}"
            is_readonly = getattr(mod_def, 'readonly', False)
            if is_readonly:
                # If readonly, we still show it but maybe different text?
                if is_active:
                     text = f"[AUTO] {mod_def.name}"
                else: 
                     text = f"[   ] {mod_def.name}" 
            
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, 170, 28),
                text=text,
                manager=self.manager,
                container=self.container,
                object_id=f'#mod_{safe_mod_id}'
            )
            if is_readonly: # Don't disable blocked ones, just prevent untoggling
                btn.disable()
            self.modifier_buttons.append(btn)
            
            if mod_def.type_str == 'linear':
                # Entry
                entry_x = 185
                entry_w = 60
                
                # Check for custom layouts spacing needs
                # Normal: Entry | << | < | Slider | > | >>
                
                entry = UITextEntryLine(
                    relative_rect=pygame.Rect(entry_x, y, entry_w, 28),
                    manager=self.manager,
                    container=self.container,
                    object_id=f'#entry_{safe_mod_id}'
                )
                entry.set_text(f"{current_val:.2f}")
                if not is_active: entry.disable()
                self.modifier_entries.append(entry)
                
                current_x = entry_x + entry_w + 5
                
                # --- Button Generation Logic ---
                btns_to_create = [] # List of (text, value, mode/direction)
                
                if mod_id == 'turret_mount' or mod_id == 'facing':
                    # << (90 snap), < (15 snap), < (1 delta)
                    btns_to_create = [
                        ('<<', 90, 'snap_floor'),
                        ('<', 15, 'snap_floor'),
                        ('<', 1, 'delta_sub'),
                        ('SLIDER', 0, 0),
                        ('>', 1, 'delta_add'),
                        ('>', 15, 'snap_ceil'),
                        ('>>', 90, 'snap_ceil')
                    ]
                elif mod_id == 'simple_size':
                    # << (100 snap), < (10 snap), < (1 delta)
                    btns_to_create = [
                        ('<<', 100, 'snap_smart_floor'), # Special 100 logic
                        ('<', 10, 'snap_floor'),
                        ('<', 1, 'delta_sub'),
                        ('SLIDER', 0, 0),
                        ('>', 1, 'delta_add'),
                        ('>', 10, 'snap_ceil'),
                        ('>>', 100, 'snap_ceil')
                    ]
                elif mod_id == 'range_mount':
                     btns_to_create = [
                        ('<<', 1.0, 'delta_sub'),
                        ('<', 0.1, 'delta_sub'),
                        ('SLIDER', 0, 0),
                        ('>', 0.1, 'delta_add'),
                        ('>>', 1.0, 'delta_add')
                     ]
                else:
                    # Standard Logic
                    step = 0.01
                    if mod_def.max_val - mod_def.min_val > 50: step = 1.0
                    elif mod_def.max_val - mod_def.min_val > 10: step = 0.1
                    
                    show_buttons = (mod_def.max_val - mod_def.min_val) >= 20
                    if show_buttons:
                         btns_to_create = [
                            ('<<', step * 10, 'delta_sub'),
                            ('<', step, 'delta_sub'),
                            ('SLIDER', 0, 0),
                            ('>', step, 'delta_add'),
                            ('>>', step * 10, 'delta_add')
                         ]
                    else:
                        btns_to_create = [('SLIDER', 0, 0)]
                        
                # --- Render Buttons ---
                
                # Pre-calculate buttons width to size slider
                btn_width = 25
                total_btn_width = 0
                for label, _, _ in btns_to_create:
                    if label != 'SLIDER':
                        total_btn_width += (btn_width + 2)
                
                safe_width = self.width - 40
                available_slider_width = safe_width - current_x - total_btn_width - 5
                
                # Check for Facing presets
                if mod_id == 'facing':
                    # Need space for 0, 90, 180, 270 buttons
                    # 4 buttons * 35px = 140px
                    available_slider_width -= 140
                
                if available_slider_width < 40: available_slider_width = 40

                for label, val, mode in btns_to_create:
                    if label == 'SLIDER':
                         # Create Slider
                         step_increment = 0.01
                         slider = UIHorizontalSlider(
                            relative_rect=pygame.Rect(current_x, y, available_slider_width, 28),
                            start_value=float(current_val),
                            value_range=(float(mod_def.min_val), float(mod_def.max_val)),
                            manager=self.manager,
                            container=self.container,
                            object_id=f'#slider_{safe_mod_id}',
                            click_increment=step_increment
                        )
                         if not is_active: slider.disable()
                         self.modifier_sliders.append(slider)
                         current_x += available_slider_width + 5
                         
                         # If Facing, add preset buttons here? "These buttons should be inline, the slider can just be smaller."
                         if mod_id == 'facing':
                             presets = [0, 90, 180, 270]
                             for p_val in presets:
                                 p_btn = UIButton(pygame.Rect(current_x, y, 32, 28), str(p_val), manager=self.manager, container=self.container)
                                 self.step_btn_map[p_btn] = (mod_id, p_val, 'set_value')
                                 if not is_active: p_btn.disable()
                                 current_x += 34
                         
                    else:
                        # Create Button
                        btn = UIButton(pygame.Rect(current_x, y, btn_width, 28), label, manager=self.manager, container=self.container)
                        self.step_btn_map[btn] = (mod_id, val, mode) # Store mode instead of direction
                        if not is_active: btn.disable()
                        current_x += (btn_width + 2)
            else:
                self.modifier_entries.append(None)
                self.modifier_sliders.append(None)
                
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
            self.extra_ui_elements.append(self.save_preset_btn)
            y += 35
            
            presets = self.preset_manager.get_all_presets()
            if presets:
                preset_label = UILabel(
                    relative_rect=pygame.Rect(10, y, 200, 20),
                    text="Saved Presets:",
                    manager=self.manager,
                    container=self.container
                )
                self.extra_ui_elements.append(preset_label)
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
                             # Check mandatory
                             if mod_id in ['simple_size_mount', 'range_mount', 'facing']:
                                  is_active = True
                             else:
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
                        
                         # Enable/Disable Step Buttons linked to this mod
                         for b, (m_id, _, _) in self.step_btn_map.items():
                             if m_id == mod_id:
                                 if is_active: b.enable()
                                 else: b.disable()

                         if self.editing_component:
                             self.editing_component.recalculate_stats()
                             self.on_change_callback() # Notify ship Update
                         
                         return ('refresh_ui', None)
            
            # Step Buttons
            # Step Buttons
            if event.ui_element in self.step_btn_map:
                mod_id, val_or_step, mode = self.step_btn_map[event.ui_element]
                
                # Find slider/entry indices
                try:
                    idx = self.modifier_id_list.index(mod_id)
                except ValueError:
                    return None
                    
                slider = self.modifier_sliders[idx]
                entry = self.modifier_entries[idx]
                
                if slider:
                     current = slider.get_current_value()
                     mod_def = MODIFIER_REGISTRY[mod_id]
                     
                     new_val = current
                     
                     if mode == 'set_value':
                         new_val = float(val_or_step)
                     elif mode == 'delta_add':
                         new_val = current + val_or_step
                     elif mode == 'delta_sub':
                         new_val = current - val_or_step
                     elif mode == 'snap_floor':
                         new_val = self._calculate_snap_val(current, val_or_step, -1, mod_def.min_val, mod_def.max_val)
                     elif mode == 'snap_ceil':
                         new_val = self._calculate_snap_val(current, val_or_step, 1, mod_def.min_val, mod_def.max_val)
                     elif mode == 'snap_smart_floor':
                         # Size mount special 100 step
                         if current <= 100:
                             new_val = max(mod_def.min_val, 1)
                         else:
                             new_val = self._calculate_snap_val(current, val_or_step, -1, mod_def.min_val, mod_def.max_val)
                     else:
                         # Fallback
                         pass

                     new_val = max(mod_def.min_val, min(mod_def.max_val, new_val))
                     
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
