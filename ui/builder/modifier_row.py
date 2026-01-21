import json
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UIHorizontalSlider
from pygame_gui.windows import UIMessageWindow
from ui.builder.modifier_logic import ModifierLogic
from game.simulation.components.modifier_effects import ModifierEffectEvaluator

class ModifierControlRow:
    """
    A single row in the modifier panel containing controls for one modifier.

    Compact layout: Name Label | Value Entry | Slider | JSON Button
    """
    def __init__(self, manager, container, width, mod_id, mod_def, config, on_change_callback):
        self.manager = manager
        self.container = container  # The panel this row sits in
        self.width = width
        self.mod_id = mod_id
        self.mod_def = mod_def
        self.config = config
        self.on_change_callback = on_change_callback

        self.ui_elements = []  # Keep track for destruction
        self.buttons = {}  # Map button -> data
        self.slider = None
        self.entry = None
        self.name_label = None
        self.json_btn = None

        self.current_value = 0.0
        self.is_active = False
        self.component_context = None  # Set during update

        self.height = 28  # Compact single-row layout

    def _generate_tooltip(self) -> str:
        """Generate enhanced tooltip with description and all effect details."""
        try:
            lines = []

            # Add description
            if self.mod_def.description:
                lines.append(self.mod_def.description)
                lines.append("")

            # Get effects from modifier definition
            effects = self.mod_def.effects if hasattr(self.mod_def, 'effects') else []
            if effects:
                param_value = self.current_value if self.current_value > 0 else self.mod_def.default_val

                # Convert to dict for evaluator
                mod_dict = {
                    'id': self.mod_def.id,
                    'name': self.mod_def.name,
                    'effects': effects,
                }

                # Evaluate effects
                evaluated = ModifierEffectEvaluator.evaluate_modifier(mod_dict, param_value)

                if evaluated:
                    lines.append("Effects at current value:")
                    for effect in evaluated:
                        stat = effect.stat_key.replace('_', ' ').title()
                        if effect.operation == 'multiply':
                            lines.append(f"  {stat}: x{effect.value:.2f}")
                        elif effect.operation == 'add':
                            sign = '+' if effect.value >= 0 else ''
                            lines.append(f"  {stat}: {sign}{effect.value:.1f}")
                        elif effect.operation == 'set':
                            lines.append(f"  {stat}: ={effect.value:.0f}")

            # Add range info
            lines.append("")
            lines.append(f"Range: {self.mod_def.min_val:.1f} - {self.mod_def.max_val:.1f}")

            return "\n".join(lines)
        except Exception:
            # Fallback to basic description if introspection fails
            return self.mod_def.description if self.mod_def.description else self.mod_def.name

    def build_ui(self, y):
        """Constructs the UI elements at the given y position.

        Compact layout: Name Button (150px) | Value Entry (50px) | Slider (dynamic) | JSON Button (28px)
        """
        self._clear_ui()
        self.y = y

        safe_mod_id = self.mod_id.replace(' ', '_').replace('.', '_')

        # 1. Name Button (styled as label but with tooltip support)
        self.name_label = UIButton(
            relative_rect=pygame.Rect(10, y, 150, 28),
            text=self.mod_def.name,
            manager=self.manager,
            container=self.container,
            object_id='#modifier_name_btn',
            tool_tip_text=self._generate_tooltip()
        )
        self.ui_elements.append(self.name_label)

        # 2. Controls Area - always build for linear/stepped types
        if self.config.get('control_type') in ['linear', 'linear_stepped', 'facing_selector']:
            self._build_linear_controls(y, 165, safe_mod_id)

        return self.height

    def _build_linear_controls(self, y, start_x, safe_id):
        """Build compact controls: Entry | Step Buttons | Slider | JSON Button."""
        current_x = start_x

        # Reserve space for JSON button at end (28px + 5px margin)
        json_btn_width = 28
        right_margin = 10

        # Entry (50px)
        entry_w = 50
        self.entry = UITextEntryLine(
            relative_rect=pygame.Rect(current_x, y, entry_w, 28),
            manager=self.manager,
            container=self.container,
            object_id=f'#entry_{safe_id}'
        )
        self.ui_elements.append(self.entry)
        current_x += entry_w + 3

        # Presets (Facing) - compact 28px buttons
        if 'presets' in self.config:
            for val in self.config['presets']:
                btn = UIButton(
                    relative_rect=pygame.Rect(current_x, y, 28, 28),
                    text=str(val),
                    manager=self.manager,
                    container=self.container
                )
                self.buttons[btn] = {'action': 'set_value', 'value': val}
                self.ui_elements.append(btn)
                current_x += 30
            current_x += 3

        # Step Buttons - compact 26px buttons
        step_btns = self.config.get('step_buttons', [])
        btn_width = 26

        for b_def in step_btns:
            btn = UIButton(
                pygame.Rect(current_x, y, btn_width, 28),
                b_def['label'],
                manager=self.manager,
                container=self.container,
                object_id='#mini_arrow_btn'
            )
            self.buttons[btn] = {'action': b_def['mode'], 'value': b_def['value']}
            self.ui_elements.append(btn)
            current_x += btn_width + 2

        current_x += 3  # Gap for slider

        # Slider - Takes remaining space before JSON button
        slider_end_x = self.width - json_btn_width - right_margin - 5
        slider_width = slider_end_x - current_x
        if slider_width < 40:
            slider_width = 40

        self.slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, y, slider_width, 28),
            start_value=0,  # Updated later
            value_range=(0.0, 100.0),  # Updated later
            manager=self.manager,
            container=self.container,
            object_id=f'#slider_{safe_id}',
            click_increment=self.config.get('slider_step', 0.01)
        )
        if hasattr(self.slider, 'enable_arrow_buttons'):
            self.slider.enable_arrow_buttons = False
            self.slider.rebuild()

        self.ui_elements.append(self.slider)
        current_x += slider_width + 5

        # JSON Button at end
        self.json_btn = UIButton(
            relative_rect=pygame.Rect(self.width - json_btn_width - right_margin, y, json_btn_width, 28),
            text="{ }",
            manager=self.manager,
            container=self.container,
            object_id='#json_btn',
            tool_tip_text="Show modifier definition as JSON"
        )
        self.ui_elements.append(self.json_btn)

    def _clear_ui(self):
        for el in self.ui_elements:
            el.kill()
        self.ui_elements = []
        self.buttons = {}
        self.slider = None
        self.entry = None
        self.name_label = None
        self.json_btn = None

    def update(self, component, is_readonly=False):
        """Updates the row state based on the current component."""
        self.component_context = component
        self.is_readonly = is_readonly

        # 1. Determine State (Active/Value)
        # All visible modifiers are always active when a component is selected
        is_active = False
        val = self.mod_def.min_val

        if component:
            mod = component.get_modifier(self.mod_id)
            if mod:
                is_active = True
                val = mod.value

        self.is_active = is_active
        self.current_value = val

        # 2. Update tooltip with current value effects
        if self.name_label:
            self.name_label.set_tooltip(self._generate_tooltip())

        # 3. Enable/Disable Controls based on active state
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
                self.entry.set_text(f"{val:.2f}")  # Show default/last
            if self.slider:
                self.slider.disable()
            for btn in self.buttons.keys():
                btn.disable()

        # Readonly lock - disable all controls
        if self.is_readonly:
            if self.entry:
                self.entry.disable()
            if self.slider:
                self.slider.disable()
            for btn in self.buttons.keys():
                btn.disable()

        # JSON button always enabled (read-only operation)
        if self.json_btn:
            self.json_btn.enable()

    def handle_event(self, event):
        """Handle internal events. Returns True if a change occurred."""
        # Only process events that have a UI element (pygame_gui events)
        if not hasattr(event, 'ui_element'):
            return False

        # JSON button is always handled (read-only operation)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.json_btn:
            self._show_json_popup()
            return True

        # Skip other events if not active or readonly
        if not self.is_active or self.is_readonly:
            return False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
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

    def _show_json_popup(self):
        """Show a popup window with the modifier definition as JSON."""
        # Build modifier definition dict
        mod_dict = {
            'id': self.mod_def.id,
            'name': self.mod_def.name,
            'description': self.mod_def.description,
            'type': getattr(self.mod_def, 'type', 'unknown'),
            'min_val': self.mod_def.min_val,
            'max_val': self.mod_def.max_val,
            'default_val': self.mod_def.default_val,
            'current_value': self.current_value,
        }

        # Add effects if present
        if hasattr(self.mod_def, 'effects') and self.mod_def.effects:
            mod_dict['effects'] = self.mod_def.effects

        # Format as pretty JSON
        json_text = json.dumps(mod_dict, indent=2, default=str)

        # Create popup window
        UIMessageWindow(
            rect=pygame.Rect(100, 100, 500, 400),
            html_message=f"<pre>{json_text}</pre>",
            manager=self.manager,
            window_title=f"Modifier: {self.mod_def.name}"
        )

    def kill(self):
        self._clear_ui()
