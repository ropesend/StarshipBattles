"""UI row widget for controlling a single component modifier.

Provides interactive controls (toggle, slider, buttons, text entry) for
adjusting modifier values in the ship builder's modifier panel.
"""
from __future__ import annotations

from typing import Any
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UIHorizontalSlider, UIPanel
from .modifier_logic import ModifierLogicService


class ModifierControlRow:
    """A single row in the modifier panel containing controls for one modifier.

    Lifecycle:
        1. __init__: Create instance with configuration (UI not built yet)
        2. build_ui(y): Construct pygame_gui elements at specified y position
        3. update(component, template): Sync state with component/template data
        4. handle_event(event): Process user interactions, trigger callbacks
        5. kill(): Destroy all UI elements for cleanup

    The row adapts its controls based on the modifier's control_type config:
        - 'linear': Slider + text entry for continuous values
        - 'linear_stepped': Slider + step buttons for discrete values
        - 'facing_selector': Preset buttons for common facing angles

    Attributes:
        manager: pygame_gui.UIManager for element creation.
        container: Parent UIPanel this row belongs to.
        mod_id: String identifier for the modifier (e.g., 'turret_mount').
        mod_def: ModifierDefinition with name, description, min/max values.
        config: Dict with control_type, step_buttons, presets, etc.
        is_active: Whether the modifier is currently applied to the component.
        current_value: Current numeric value of the modifier.
        component_context: The Component being edited (set during update).
    """

    def __init__(self, manager, container, width, mod_id, mod_def, config, on_change_callback,
                 modifier_logic: ModifierLogicService):
        """Initialize the modifier control row.

        Args:
            manager: pygame_gui.UIManager for creating UI elements.
            container: Parent UIPanel to contain this row's elements.
            width: Available width in pixels for laying out controls.
            mod_id: String identifier for the modifier.
            mod_def: ModifierDefinition object with metadata (name, description,
                min_val, max_val, default_val, readonly).
            config: Dict with UI configuration:
                - control_type: 'linear', 'linear_stepped', or 'facing_selector'
                - step_buttons: List of {label, mode, value} for step controls
                - presets: List of preset values for quick selection
                - slider_step: Increment for slider clicks
                - smart_floor: Boolean for special size mount behavior
            on_change_callback: Function(action, mod_id, value) called on changes:
                - action: 'toggle' or 'value_change'
                - mod_id: The modifier being changed
                - value: New state (bool for toggle, float for value_change)
        """
        self.manager = manager
        self.container = container # The panel this row sits in
        self.width = width
        self.mod_id = mod_id
        self.mod_def = mod_def
        self.config = config
        self.on_change_callback = on_change_callback
        self._logic = modifier_logic

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

    def _get_local_bounds(self) -> tuple:
        """Get modifier bounds and clamp current value.

        Returns:
            Tuple of (min_value, max_value, clamped_value) where clamped_value
            is current_value constrained to [min_value, max_value].

        Uses self._logic.get_local_min_max() when component context is
        available, otherwise falls back to mod_def defaults.
        """
        if self.component_context:
            min_v, max_v = self._logic.get_local_min_max(self.mod_id, self.component_context)
        else:
            min_v, max_v = self.mod_def.min_val, self.mod_def.max_val
        clamped = max(min_v, min(max_v, self.current_value))
        return min_v, max_v, clamped

    def _set_controls_enabled(self, enabled) -> None:
        """Enable or disable all value controls (entry, slider, buttons).

        Args:
            enabled: True to enable controls, False to disable.
        """
        if self.entry:
            if enabled:
                self.entry.enable()
            else:
                self.entry.disable()
        if self.slider:
            if enabled:
                self.slider.enable()
            else:
                self.slider.disable()
        for btn in self.buttons.keys():
            if enabled:
                btn.enable()
            else:
                btn.disable()

    def build_ui(self, y) -> Any:
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

    def _build_linear_controls(self, y, start_x, safe_id) -> None:
        """Build controls for linear/stepped modifier types.

        Creates a horizontal layout with:
        1. Text entry field (60px) for direct value input
        2. Preset buttons (if configured) for common values
        3. Step buttons (if configured) for increment/decrement
        4. Horizontal slider filling remaining width

        Args:
            y: Vertical position for elements.
            start_x: Horizontal starting position (after toggle button).
            safe_id: Sanitized modifier ID for pygame_gui object_id.
        """
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
            
        # Step Buttons - Render ALL on the left
        step_btns = self.config.get('step_buttons', [])
        btn_width = 30
        
        for b_def in step_btns:
            btn = UIButton(pygame.Rect(current_x, y, btn_width, 28), b_def['label'], manager=self.manager, container=self.container, object_id='#mini_arrow_btn')
            self.buttons[btn] = {'action': b_def['mode'], 'value': b_def['value']}
            self.ui_elements.append(btn)
            current_x += (btn_width + 2)
            
        current_x += 3 # Gap for slider
            
        # Slider - Takes remaining space
        safe_width = self.width - 20 # margin
        available_slider_width = safe_width - current_x
        if available_slider_width < 40: available_slider_width = 40
        
        self.slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, y, available_slider_width, 28),
            start_value=0, # Updated later
            value_range=(0.0, 100.0), # Updated later
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

    def _clear_ui(self) -> None:
        """Destroy all pygame_gui elements and reset internal references.

        Called during rebuild (build_ui) and final cleanup (kill).
        Ensures proper cleanup of pygame_gui resources.
        """
        for el in self.ui_elements:
            el.kill()
        self.ui_elements = []
        self.buttons = {}
        self.slider = None
        self.entry = None

    def update(self, component, template_modifiers) -> None:
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
            
        else:
            if self.mod_id in template_modifiers:
                is_active = True
                val = template_modifiers[self.mod_id]

        self.is_active = is_active
        self.current_value = val
        
        # 2. Update UI Text/Visuals
        check_char = 'x' if is_active else ' '
        
        self.toggle_btn.set_text(f"[{check_char}] {self.mod_def.name}")

        # Enable/Disable Controls and update values
        self._set_controls_enabled(self.is_active)
        if self.entry:
            self.entry.set_text(f"{val:.2f}")
        if self.is_active and self.slider:
            min_v, max_v, _ = self._get_local_bounds()
            self.slider.value_range = (min_v, max_v)
            self.slider.set_current_value(val)
                
        # Mandatory lock
        if component and self._logic.is_modifier_mandatory(self.mod_id, component):
            # Disable toggle so it can't be unchecked (visual cue + prevent click)
             self.toggle_btn.disable()
        else:
             self.toggle_btn.enable()

    def handle_event(self, event) -> bool:
        """Handle internal events. Returns True if a change occurred."""
        # Only process events that have a UI element (pygame_gui events)
        if not hasattr(event, 'ui_element'):
            return False

        if not self.is_active and event.ui_element != self.toggle_btn:
            return False
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.toggle_btn:
                # Toggle Logic
                if self.component_context and self._logic.is_modifier_mandatory(self.mod_id, self.component_context):
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

                min_v, max_v, _ = self._get_local_bounds()
                smart_floor = self.config.get('smart_floor', False)

                new_val = self.current_value
                if mode == 'set_value':
                    new_val = float(step)
                elif mode == 'delta_add':
                    new_val = self.current_value + step
                elif mode == 'delta_sub':
                    new_val = self.current_value - step
                elif mode == 'snap_floor':
                    new_val = self._logic.calculate_snap_value(self.current_value, step, -1, min_v, max_v, smart_floor)
                elif mode == 'snap_ceil':
                    new_val = self._logic.calculate_snap_value(self.current_value, step, 1, min_v, max_v, smart_floor)

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
                    min_v, max_v, _ = self._get_local_bounds()
                    val = max(min_v, min(max_v, val))
                    self.on_change_callback('value_change', self.mod_id, val)
                    return True
                except ValueError:
                    pass
        
        return False

    def kill(self) -> None:
        self._clear_ui()
