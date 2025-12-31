import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UIHorizontalSlider, UIPanel
from ui.builder.modifier_logic import ModifierLogic

class ModifierControlRow:
    """
    A single row in the modifier panel containing controls for one modifier.
    """
    def __init__(self, manager, container, width, mod_id, mod_def, config, on_change_callback):
        self.manager = manager
        self.container = container # The panel this row sits in
        self.width = width
        self.mod_id = mod_id
        self.mod_def = mod_def
        self.config = config
        self.on_change_callback = on_change_callback
        
        self.ui_elements = [] # Keep track for destruction
        self.buttons = {} # Map button -> data
        self.slider = None
        self.entry = None
        
        self.current_value = 0.0
        self.is_active = False
        self.component_context = None # Set during update
        
        self.height = 32 # Default height
        
        # We don't build layout in __init__ because we might be pooled? 
        # Actually standard practice is build in init for UI widget. 
        # For pooling, we might just hide/show or update data.
        # But to keep it simple first, let's build.
        # Wait, if we use container, we need to know Y position. 
        # So we likely need a `layout(y)` method.

    def build_ui(self, y):
        """Constructs the UI elements at the given y position."""
        self._clear_ui()
        self.y = y
        
        # 1. Main Toggle Button / Label
        safe_mod_id = self.mod_id.replace(' ', '_').replace('.', '_')
        
        self.toggle_btn = UIButton(
            relative_rect=pygame.Rect(10, y, 170, 28),
            text=f"[ ] {self.mod_def.name}",
            manager=self.manager,
            container=self.container,
            object_id=f'#mod_{safe_mod_id}',
            tool_tip_text=self.mod_def.description
        )
        self.ui_elements.append(self.toggle_btn)
        
        # 2. Controls Area
        # If linear/stepped, we need entry and sliders
        if self.config.get('control_type') in ['linear', 'linear_stepped', 'facing_selector']:
            self._build_linear_controls(y, 185, safe_mod_id)
            
        return self.height

    def _build_linear_controls(self, y, start_x, safe_id):
        current_x = start_x
        
        # Entry
        entry_w = 60
        self.entry = UITextEntryLine(
            relative_rect=pygame.Rect(current_x, y, entry_w, 28),
            manager=self.manager,
            container=self.container,
            object_id=f'#entry_{safe_id}'
        )
        self.ui_elements.append(self.entry)
        current_x += entry_w + 5
        
        # Presets (Facing)
        if 'presets' in self.config:
            for val in self.config['presets']:
                btn = UIButton(
                    relative_rect=pygame.Rect(current_x, y, 32, 28),
                    text=str(val),
                    manager=self.manager,
                    container=self.container
                )
                self.buttons[btn] = {'action': 'set_value', 'value': val}
                self.ui_elements.append(btn)
                current_x += 34
            current_x += 5
            
        # Step Buttons & Slider logic
        step_btns = self.config.get('step_buttons', [])
        
        # Calculate width logic
        btn_width = 25
        total_btn_width = sum((btn_width + 2) for b in step_btns)
        
        safe_width = self.width - 40
        available_slider_width = safe_width - current_x - total_btn_width - 5
        if available_slider_width < 40: available_slider_width = 40
        
        # Determine local range
        local_min, local_max = 0, 100 # Defaults, updated in update()
        
        for btn_def in step_btns:
            # Slider Placeholder in list? No, our list implies order: Before Slider / After Slider?
            # The config list I wrote had ">" labels.
            # Let's assume the config list contains ALL buttons.
            # And we need to place the slider in the middle?
            # Or just place buttons before/after?
            # My config example: <<, <, <, >, >, >>. No "SLIDER" marker.
            # Let's check logic: negative delta = left, positive = right?
            # Simple heuristic: 'sub' mode or value < current? 
            # Actually, standard is: Decrements Left, Slider, Increments Right.
            
            is_decrement = btn_def.get('mode') == 'delta_sub' or btn_def.get('mode') == 'snap_floor'
            
            # If we just switched from decrement to increment, place slider?
            # Or just use two lists? 
            # Let's iterate. If we hit the first increment and haven't placed slider, place it?
            pass

        # Split buttons
        left_btns = [b for b in step_btns if b['mode'] in ['delta_sub', 'snap_floor']]
        right_btns = [b for b in step_btns if b['mode'] in ['delta_add', 'snap_ceil']]
        
        # Render Left
        for b_def in left_btns:
            btn = UIButton(pygame.Rect(current_x, y, btn_width, 28), b_def['label'], manager=self.manager, container=self.container)
            self.buttons[btn] = {'action': b_def['mode'], 'value': b_def['value']}
            self.ui_elements.append(btn)
            current_x += (btn_width + 2)
            
        # Render Slider
        self.slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, y, available_slider_width, 28),
            start_value=0, # Updated later
            value_range=(0, 100), # Updated later
            manager=self.manager,
            container=self.container,
            object_id=f'#slider_{safe_id}',
            click_increment=self.config.get('slider_step', 0.01)
        )
        if hasattr(self.slider, 'enable_arrow_buttons'):
            self.slider.enable_arrow_buttons = False
            self.slider.rebuild()
            
        self.ui_elements.append(self.slider)
        current_x += available_slider_width + 5
        
        # Render Right
        for b_def in right_btns:
            btn = UIButton(pygame.Rect(current_x, y, btn_width, 28), b_def['label'], manager=self.manager, container=self.container)
            self.buttons[btn] = {'action': b_def['mode'], 'value': b_def['value']}
            self.ui_elements.append(btn)
            current_x += (btn_width + 2)

    def _clear_ui(self):
        for el in self.ui_elements:
            el.kill()
        self.ui_elements = []
        self.buttons = {}
        self.slider = None
        self.entry = None

    def update(self, component, template_modifiers):
        """Updates the row state based on the current component or template."""
        self.component_context = component
        
        # 1. Determine State (Active/Value)
        is_active = False
        val = self.mod_def.min_val
        
        if component:
            mod = component.get_modifier(self.mod_id)
            if mod:
                is_active = True
                val = mod.value
            
            # Check mandatory status (Auto-set if needed)
            if ModifierLogic.is_modifier_mandatory(self.mod_id, component) and not is_active:
                # Should have been handled by Logic ensure, but visually treat as active
                # Actually, main panel should ensure logic. 
                # If we are here and it's mandatory but missing, it's inactive.
                pass
        else:
            if self.mod_id in template_modifiers:
                is_active = True
                val = template_modifiers[self.mod_id]

        self.is_active = is_active
        self.current_value = val
        
        # 2. Update UI Text/Visuals
        check_char = 'x' if is_active else ' '
        
        # Readonly check
        if self.mod_def.readonly or (component and ModifierLogic.is_modifier_mandatory(self.mod_id, component)):
             # Even if mandatory, we show [x] or [AUTO]?
             # Let's keep [x] but maybe disable toggle
             pass
             
        self.toggle_btn.set_text(f"[{check_char}] {self.mod_def.name}")
        
        # Enable/Disable Controls
        if self.is_active:
            if self.entry: 
                self.entry.enable()
                self.entry.set_text(f"{val:.2f}")
            if self.slider: 
                self.slider.enable()
                # Update Range
                min_v, max_v = ModifierLogic.get_local_min_max(self.mod_id, component) if component else (self.mod_def.min_val, self.mod_def.max_val)
                self.slider.value_range = (min_v, max_v)
                self.slider.set_current_value(val)
                
            for btn in self.buttons.keys():
                btn.enable()
        else:
            if self.entry: 
                self.entry.disable()
                self.entry.set_text(f"{val:.2f}") # Show default/last
            if self.slider: 
                self.slider.disable()
            for btn in self.buttons.keys():
                btn.disable()
                
        # Mandatory lock
        if component and ModifierLogic.is_modifier_mandatory(self.mod_id, component):
            # Toggle button should be disabled so it can't be unchecked
             # But keep it visible to show it's active
             # NOTE: disabling button grays it out. Maybe we just trap the click?
             # For now, disable is safest.
             pass
             # self.toggle_btn.disable() # (Optional choice)

    def handle_event(self, event):
        """Handle internal events. Returns True if a change occurred."""
        # Only process events that have a UI element (pygame_gui events)
        if not hasattr(event, 'ui_element'):
            return False

        if not self.is_active and event.ui_element != self.toggle_btn:
            return False
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.toggle_btn:
                # Toggle Logic
                if self.component_context and ModifierLogic.is_modifier_mandatory(self.mod_id, self.component_context):
                    return False # Ignore click on mandatory
                
                # Active Flip
                new_active = not self.is_active
                self.on_change_callback('toggle', self.mod_id, new_active)
                return True
                
            elif event.ui_element in self.buttons:
                # Step Button
                action = self.buttons[event.ui_element]
                mode = action['action']
                step = action['value']
                
                min_v, max_v = ModifierLogic.get_local_min_max(self.mod_id, self.component_context) if self.component_context else (self.mod_def.min_val, self.mod_def.max_val)
                
                smart_floor = self.config.get('smart_floor', False)
                
                new_val = self.current_value
                if mode == 'set_value':
                    new_val = float(step)
                elif mode == 'delta_add':
                    new_val = self.current_value + step
                elif mode == 'delta_sub':
                    new_val = self.current_value - step
                elif mode == 'snap_floor':
                    new_val = ModifierLogic.calculate_snap_value(self.current_value, step, -1, min_v, max_v, smart_floor)
                elif mode == 'snap_ceil':
                    new_val = ModifierLogic.calculate_snap_value(self.current_value, step, 1, min_v, max_v, smart_floor)
                    
                # Clamp
                new_val = max(min_v, min(max_v, new_val))
                
                if new_val != self.current_value:
                    self.on_change_callback('value_change', self.mod_id, new_val)
                    return True

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.slider:
                val = self.slider.get_current_value()
                if val != self.current_value:
                    self.on_change_callback('value_change', self.mod_id, val)
                    # Don't return True immediately for throttling? 
                    # User requested immediate update in review.
                    return True
                    
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.entry:
                try:
                    val = float(self.entry.get_text())
                    min_v, max_v = ModifierLogic.get_local_min_max(self.mod_id, self.component_context) if self.component_context else (self.mod_def.min_val, self.mod_def.max_val)
                    val = max(min_v, min(max_v, val))
                    self.on_change_callback('value_change', self.mod_id, val)
                    return True
                except ValueError:
                    pass
        
        return False

    def kill(self):
        self._clear_ui()
