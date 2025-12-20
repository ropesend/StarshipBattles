"""
Ship Builder using pygame_gui for a professional UI.
"""
import json
import math
import tkinter
from tkinter import filedialog

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu, 
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from ship import Ship, LayerType, SHIP_CLASSES
from components import (
    get_all_components, MODIFIER_REGISTRY, Bridge, Weapon, 
    BeamWeapon, ProjectileWeapon, Engine, Thruster, Armor, Tank, Generator
)
from sprites import SpriteManager

# Initialize Tkinter root and hide it (for file dialogs)
tk_root = tkinter.Tk()
tk_root.withdraw()

# Colors
BG_COLOR = (20, 20, 30)
PANEL_BG = '#1e1e28'
SHIP_VIEW_BG = (10, 10, 20)

# Logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BuilderSceneGUI:
    def __init__(self, screen_width, screen_height, on_start_battle):
        self.width = screen_width
        self.height = screen_height
        self.on_start_battle = on_start_battle
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager(
            (screen_width, screen_height),
            theme_path=None  # Use default theme
        )
        
        # Ship being built
        self.ship = Ship("Custom Ship", screen_width // 2, screen_height // 2, (100, 100, 255))
        
        # Available components
        self.available_components = get_all_components()
        
        # Template modifiers for new components
        self.template_modifiers = {}
        
        # Dragging state
        self.dragged_item = None
        self.selected_component = None  # (layer, index, component)
        self.hovered_component = None
        
        # Error display
        self.error_message = ""
        self.error_timer = 0
        
        # Firing arc display
        self.show_firing_arcs = False
        
        # Sprite manager
        self.sprite_mgr = SpriteManager.get_instance()
        
        # Layout dimensions
        self.left_panel_width = 280
        self.right_panel_width = 280
        self.bottom_bar_height = 60
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create all pygame_gui UI elements."""
        
        # === LEFT PANEL: Component List ===
        self.left_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.left_panel_width, self.height - self.bottom_bar_height),
            manager=self.ui_manager,
            object_id='#left_panel'
        )
        
        # Component list title
        UILabel(
            relative_rect=pygame.Rect(10, 5, 200, 25),
            text="Components",
            manager=self.ui_manager,
            container=self.left_panel
        )
        
        # Component selection list
        component_names = [f"{c.name} ({c.mass}t)" for c in self.available_components]
        self.component_list = UISelectionList(
            relative_rect=pygame.Rect(5, 35, self.left_panel_width - 10, 300),
            item_list=component_names,
            manager=self.ui_manager,
            container=self.left_panel,
            allow_multi_select=False
        )
        
        # Modifier settings title
        UILabel(
            relative_rect=pygame.Rect(10, 345, 200, 25),
            text="New Component Settings",
            manager=self.ui_manager,
            container=self.left_panel
        )
        
        # Modifier buttons will be created dynamically
        self.modifier_buttons = []
        self._rebuild_modifier_ui()
        
        # === RIGHT PANEL: Stats & Settings ===
        self.right_panel = UIPanel(
            relative_rect=pygame.Rect(self.width - self.right_panel_width, 0, 
                                      self.right_panel_width, self.height - self.bottom_bar_height),
            manager=self.ui_manager,
            object_id='#right_panel'
        )
        
        y = 10
        
        # Ship Name
        UILabel(
            relative_rect=pygame.Rect(10, y, 60, 25),
            text="Name:",
            manager=self.ui_manager,
            container=self.right_panel
        )
        self.name_entry = UITextEntryLine(
            relative_rect=pygame.Rect(70, y, 195, 30),
            manager=self.ui_manager,
            container=self.right_panel
        )
        self.name_entry.set_text(self.ship.name)
        y += 40
        
        # Ship Class Dropdown
        UILabel(
            relative_rect=pygame.Rect(10, y, 60, 25),
            text="Class:",
            manager=self.ui_manager,
            container=self.right_panel
        )
        class_options = list(SHIP_CLASSES.keys())
        self.class_dropdown = UIDropDownMenu(
            options_list=class_options,
            starting_option=self.ship.ship_class,
            relative_rect=pygame.Rect(70, y, 195, 30),
            manager=self.ui_manager,
            container=self.right_panel
        )
        y += 40
        
        # AI Strategy Dropdown
        UILabel(
            relative_rect=pygame.Rect(10, y, 60, 25),
            text="AI:",
            manager=self.ui_manager,
            container=self.right_panel
        )
        ai_options = ["Max Range", "Attack Run", "Kamikaze", "Flee"]
        ai_display = self.ship.ai_strategy.replace('_', ' ').title()
        self.ai_dropdown = UIDropDownMenu(
            options_list=ai_options,
            starting_option=ai_display,
            relative_rect=pygame.Rect(70, y, 195, 30),
            manager=self.ui_manager,
            container=self.right_panel
        )
        y += 50
        
        # Ship Stats Section
        UILabel(
            relative_rect=pygame.Rect(10, y, 150, 25),
            text="── Ship Stats ──",
            manager=self.ui_manager,
            container=self.right_panel
        )
        y += 30
        
        # Stats labels (will be updated dynamically)
        self.stat_labels = {}
        stat_names = [
            'mass', 'radius', 'max_speed', 'turn_rate', 'acceleration',
            'thrust', 'max_hp', 'energy_gen', 'max_fuel', 'max_ammo', 
            'max_energy', 'weapon_range'
        ]
        
        for stat in stat_names:
            self.stat_labels[stat] = UILabel(
                relative_rect=pygame.Rect(10, y, 255, 20),
                text=f"{stat}: --",
                manager=self.ui_manager,
                container=self.right_panel
            )
            y += 22
        
        y += 10
        
        # Requirements Section
        UILabel(
            relative_rect=pygame.Rect(10, y, 150, 25),
            text="── Requirements ──",
            manager=self.ui_manager,
            container=self.right_panel
        )
        y += 30
        
        self.requirements_label = UILabel(
            relative_rect=pygame.Rect(10, y, 255, 60),
            text="✓ All requirements met",
            manager=self.ui_manager,
            container=self.right_panel
        )
        
        # === BOTTOM BAR: Buttons ===
        btn_y = self.height - self.bottom_bar_height + 10
        btn_w = 140
        btn_h = 40
        spacing = 10
        total_width = btn_w * 4 + spacing * 3
        start_x = (self.width - total_width) // 2
        
        self.clear_btn = UIButton(
            relative_rect=pygame.Rect(start_x, btn_y, btn_w, btn_h),
            text="Clear Design",
            manager=self.ui_manager
        )
        
        self.save_btn = UIButton(
            relative_rect=pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h),
            text="Save",
            manager=self.ui_manager
        )
        
        self.load_btn = UIButton(
            relative_rect=pygame.Rect(start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h),
            text="Load",
            manager=self.ui_manager
        )
        
        self.start_btn = UIButton(
            relative_rect=pygame.Rect(start_x + (btn_w + spacing) * 3, btn_y, btn_w, btn_h),
            text="Start Battle",
            manager=self.ui_manager
        )
        
        # Firing arc toggle (in center area)
        self.arc_toggle_btn = UIButton(
            relative_rect=pygame.Rect(
                self.left_panel_width + 10,
                self.height - self.bottom_bar_height - 40,
                150, 30
            ),
            text="Show Firing Arcs",
            manager=self.ui_manager
        )
        
        # Confirmation dialog reference
        self.confirm_dialog = None
        
        # Update stats display
        self._update_stats_display()
        
    def _rebuild_modifier_ui(self):
        """Rebuild modifier toggle buttons and sliders."""
        # Clear existing
        for btn in self.modifier_buttons:
            btn.kill()
        self.modifier_buttons = []
        
        # Clear existing sliders
        if hasattr(self, 'modifier_sliders'):
            for slider in self.modifier_sliders:
                slider.kill()
        self.modifier_sliders = []
        
        if hasattr(self, 'modifier_slider_labels'):
            for lbl in self.modifier_slider_labels:
                lbl.kill()
        self.modifier_slider_labels = []
        
        y = 375
        for mod_id, mod_def in MODIFIER_REGISTRY.items():
            is_active = mod_id in self.template_modifiers
            text = f"[{'x' if is_active else ' '}] {mod_def.name}"
            
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.left_panel_width - 20, 28),
                text=text,
                manager=self.ui_manager,
                container=self.left_panel,
                object_id=f'#mod_{mod_id}'
            )
            self.modifier_buttons.append(btn)
            y += 32
            
            # Add slider if active and has linear type
            if is_active and mod_def.type_str == 'linear':
                current_val = self.template_modifiers.get(mod_id, mod_def.min_val)
                
                # Value label
                val_lbl = UILabel(
                    relative_rect=pygame.Rect(15, y, self.left_panel_width - 30, 20),
                    text=f"{mod_def.param_name}: {current_val:.0f}",
                    manager=self.ui_manager,
                    container=self.left_panel
                )
                self.modifier_slider_labels.append(val_lbl)
                y += 22
                
                # Slider
                from pygame_gui.elements import UIHorizontalSlider
                slider = UIHorizontalSlider(
                    relative_rect=pygame.Rect(10, y, self.left_panel_width - 20, 25),
                    start_value=current_val,
                    value_range=(mod_def.min_val, mod_def.max_val),
                    manager=self.ui_manager,
                    container=self.left_panel,
                    object_id=f'#slider_{mod_id}'
                )
                self.modifier_sliders.append(slider)
                y += 30
                
                logger.debug(f"Created slider for {mod_id}: range={mod_def.min_val}-{mod_def.max_val}, val={current_val}")
            
    def _update_stats_display(self):
        """Update ship stats labels."""
        s = self.ship
        
        # Mass with color indicator
        mass_status = "✓" if s.mass_limits_ok else "✗"
        self.stat_labels['mass'].set_text(f"Mass: {s.mass:.0f} / {s.max_mass_budget} {mass_status}")
        
        self.stat_labels['radius'].set_text(f"Radius: {s.radius:.1f}")
        self.stat_labels['max_speed'].set_text(f"Max Speed: {s.max_speed:.0f}")
        self.stat_labels['turn_rate'].set_text(f"Turn Rate: {s.turn_speed:.0f} deg/s")
        self.stat_labels['acceleration'].set_text(f"Acceleration: {s.acceleration_rate:.2f}")
        self.stat_labels['thrust'].set_text(f"Total Thrust: {s.total_thrust:.0f}")
        self.stat_labels['max_hp'].set_text(f"Max HP: {s.max_hp:.0f}")
        self.stat_labels['energy_gen'].set_text(f"Energy Gen: {s.energy_gen_rate:.1f}/s")
        self.stat_labels['max_fuel'].set_text(f"Max Fuel: {s.max_fuel:.0f}")
        self.stat_labels['max_ammo'].set_text(f"Max Ammo: {s.max_ammo:.0f}")
        self.stat_labels['max_energy'].set_text(f"Max Energy: {s.max_energy:.0f}")
        self.stat_labels['weapon_range'].set_text(f"Max Weapon Range: {s.max_weapon_range:.0f}")
        
        # Update requirements
        has_bridge = any(isinstance(c, Bridge) for l in s.layers.values() for c in l['components'])
        if has_bridge and s.mass_limits_ok:
            self.requirements_label.set_text("✓ All requirements met")
        else:
            reqs = []
            if not has_bridge:
                reqs.append("⚠ Needs Bridge")
            if not s.mass_limits_ok:
                reqs.append("⚠ Over mass limit")
            self.requirements_label.set_text("\n".join(reqs))
            
    def update(self, dt):
        """Update builder state."""
        if self.error_timer > 0:
            self.error_timer -= dt
            
        # Update hover detection
        mx, my = pygame.mouse.get_pos()
        self.hovered_component = None
        self.hovered_palette_index = None  # Track which palette item is hovered
        
        # Check palette area for hover (before schematic)
        palette_list_rect = pygame.Rect(5, 35, self.left_panel_width - 10, 300)
        if palette_list_rect.collidepoint(mx, my):
            # Calculate which item is hovered based on y position
            relative_y = my - 35
            item_height = 25
            idx = relative_y // item_height
            if 0 <= idx < len(self.available_components):
                self.hovered_palette_index = idx
                self.hovered_component = self.available_components[idx]
        
        # Check ship schematic area for hover
        schematic_rect = pygame.Rect(
            self.left_panel_width, 0,
            self.width - self.left_panel_width - self.right_panel_width,
            self.height - self.bottom_bar_height
        )
        
        if schematic_rect.collidepoint(mx, my) and self.hovered_palette_index is None:
            found = self.get_component_at_pos((mx, my))
            if found:
                self.hovered_component = found[2]
                
        # Update ship name from entry
        if self.name_entry.get_text() != self.ship.name:
            self.ship.name = self.name_entry.get_text()
                
    def handle_event(self, event):
        """Handle pygame and pygame_gui events."""
        self.ui_manager.process_events(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_btn:
                self._try_start()
            elif event.ui_element == self.save_btn:
                self._save_ship()
            elif event.ui_element == self.load_btn:
                self._load_ship()
            elif event.ui_element == self.clear_btn:
                self._show_clear_confirmation()
            elif event.ui_element == self.arc_toggle_btn:
                self.show_firing_arcs = not self.show_firing_arcs
                text = "Hide Firing Arcs" if self.show_firing_arcs else "Show Firing Arcs"
                self.arc_toggle_btn.set_text(text)
            else:
                # Check modifier buttons
                for i, btn in enumerate(self.modifier_buttons):
                    if event.ui_element == btn:
                        mod_id = list(MODIFIER_REGISTRY.keys())[i]
                        if mod_id in self.template_modifiers:
                            del self.template_modifiers[mod_id]
                        else:
                            self.template_modifiers[mod_id] = MODIFIER_REGISTRY[mod_id].min_val
                        self._rebuild_modifier_ui()
                        break
                        
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # Handle slider value changes for modifiers
            for i, slider in enumerate(getattr(self, 'modifier_sliders', [])):
                if event.ui_element == slider:
                    # Find which modifier this slider belongs to
                    slider_idx = 0
                    for mod_id, mod_def in MODIFIER_REGISTRY.items():
                        if mod_id in self.template_modifiers and mod_def.type_str == 'linear':
                            if slider_idx == i:
                                self.template_modifiers[mod_id] = event.value
                                # Update label
                                if i < len(self.modifier_slider_labels):
                                    self.modifier_slider_labels[i].set_text(f"{mod_def.param_name}: {event.value:.0f}")
                                logger.debug(f"Slider {mod_id} changed to {event.value}")
                                break
                            slider_idx += 1
                    break
                    
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.class_dropdown:
                self.ship.ship_class = event.text
                self.ship.recalculate_stats()
                self._update_stats_display()
            elif event.ui_element == self.ai_dropdown:
                self.ship.ai_strategy = event.text.lower().replace(' ', '_')
                
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.component_list:
                # Start drag from palette
                idx = self.component_list.get_single_selection()
                if idx is not None:
                    # Find component by name match
                    for i, c in enumerate(self.available_components):
                        name_str = f"{c.name} ({c.mass}t)"
                        if name_str == idx:
                            self.dragged_item = c.clone()
                            # Apply template modifiers
                            for m_id, val in self.template_modifiers.items():
                                if m_id in MODIFIER_REGISTRY:
                                    mod_def = MODIFIER_REGISTRY[m_id]
                                    allow = True
                                    if mod_def.restrictions:
                                        if 'allow_types' in mod_def.restrictions and c.type_str not in mod_def.restrictions['allow_types']:
                                            allow = False
                                    if allow:
                                        self.dragged_item.add_modifier(m_id)
                                        m = self.dragged_item.get_modifier(m_id)
                                        if m:
                                            m.value = val
                            self.dragged_item.recalculate_stats()
                            break
                            
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirm_dialog:
                self._clear_design()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check for component click in schematic
                schematic_rect = pygame.Rect(
                    self.left_panel_width, 0,
                    self.width - self.left_panel_width - self.right_panel_width,
                    self.height - self.bottom_bar_height
                )
                if schematic_rect.collidepoint(event.pos) and not self.dragged_item:
                    found = self.get_component_at_pos(event.pos)
                    if found:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                            # Clone component
                            original = found[2]
                            self.dragged_item = original.clone()
                            for m in original.modifiers:
                                new_m = m.definition.create_modifier(m.value)
                                self.dragged_item.modifiers.append(new_m)
                            self.dragged_item.recalculate_stats()
                        elif self.selected_component == found:
                            # Pick up selected component
                            layer, index, comp = found
                            self.ship.remove_component(layer, index)
                            self.dragged_item = comp
                            self.selected_component = None
                        else:
                            # Select component
                            self.selected_component = found
                    else:
                        self.selected_component = None
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragged_item:
                self._handle_drop(event.pos)
                self.dragged_item = None
                # Note: pygame_gui UISelectionList doesn't have set_single_selection
                # The selection will remain but dragged_item is cleared
                
    def _try_start(self):
        """Validate and start battle."""
        if not self.ship.check_validity():
            self._show_error("Ship Invalid (Check Stats)")
            return
            
        has_bridge = any(isinstance(c, Bridge) for l in self.ship.layers.values() for c in l['components'])
        if not has_bridge:
            self._show_error("Ship needs a Bridge!")
            return
            
        self.on_start_battle(self.ship)
        
    def _save_ship(self):
        """Save ship design to file."""
        data = self.ship.to_dict()
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Saved ship to {filename}")
            except Exception as e:
                self._show_error(f"Save failed: {e}")
                
    def _load_ship(self):
        """Load ship design from file."""
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                new_ship = Ship.from_dict(data)
                new_ship.position = pygame.math.Vector2(self.width // 2, self.height // 2)
                new_ship.recalculate_stats()
                
                self.ship = new_ship
                self.name_entry.set_text(self.ship.name)
                self.class_dropdown.selected_option = self.ship.ship_class
                self.ai_dropdown.selected_option = self.ship.ai_strategy.replace('_', ' ').title()
                self._update_stats_display()
                print(f"Loaded ship from {filename}")
            except Exception as e:
                self._show_error(f"Load failed: {e}")
                
    def _show_clear_confirmation(self):
        """Show confirmation dialog for clearing design."""
        self.confirm_dialog = UIConfirmationDialog(
            rect=pygame.Rect((self.width // 2 - 150, self.height // 2 - 100), (300, 200)),
            action_long_desc="Clear all components and reset to default settings?",
            manager=self.ui_manager,
            window_title="Confirm Clear"
        )
        
    def _clear_design(self):
        """Clear all components and reset settings."""
        logger.info("Clearing ship design")
        
        # Clear all layers and reset their HP pools
        for layer_type, layer_data in self.ship.layers.items():
            layer_data['components'] = []
            layer_data['hp_pool'] = 0
            layer_data['max_hp_pool'] = 0
            layer_data['mass'] = 0
            layer_data['hp'] = 0
            logger.debug(f"Cleared layer {layer_type.name}")
            
        # Reset modifiers template
        self.template_modifiers = {}
        
        # Reset AI
        self.ship.ai_strategy = "max_range"
        self.ai_dropdown.selected_option = "Max Range"
        
        # Recalculate - this will reset mass properly
        self.ship.recalculate_stats()
        self._update_stats_display()
        self._rebuild_modifier_ui()
        
        self.selected_component = None
        logger.info(f"Design cleared. Ship mass now: {self.ship.mass}")
        
    def _show_error(self, msg):
        """Display error message."""
        self.error_message = msg
        self.error_timer = 3.0
        
    def get_component_at_pos(self, pos):
        """Returns (layer_type, index, component) or None."""
        mx, my = pos
        cx = self.left_panel_width + (self.width - self.left_panel_width - self.right_panel_width) // 2
        cy = (self.height - self.bottom_bar_height) // 2
        max_r = 250
        hit_radius = 25
        
        for ltype, data in self.ship.layers.items():
            if ltype == LayerType.CORE:
                radius = max_r * 0.1
            elif ltype == LayerType.INNER:
                radius = max_r * 0.35
            elif ltype == LayerType.OUTER:
                radius = max_r * 0.65
            elif ltype == LayerType.ARMOR:
                radius = max_r * 0.9
            else:
                continue
                
            comps = data['components']
            if not comps:
                continue
                
            angle_step = 360 / len(comps)
            current_angle = 0
            
            for i, comp in enumerate(comps):
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                d = math.hypot(mx - px, my - py)
                if d < hit_radius:
                    return (ltype, i, comp)
                    
                current_angle += angle_step
                
        return None
        
    def _handle_drop(self, pos):
        """Handle dropping a component."""
        cx = self.left_panel_width + (self.width - self.left_panel_width - self.right_panel_width) // 2
        cy = (self.height - self.bottom_bar_height) // 2
        max_r = 250
        
        dist = math.hypot(pos[0] - cx, pos[1] - cy)
        
        layer = None
        if dist < max_r * 0.2:
            layer = LayerType.CORE
        elif dist < max_r * 0.5:
            layer = LayerType.INNER
        elif dist < max_r * 0.8:
            layer = LayerType.OUTER
        elif dist < max_r * 1.0:
            layer = LayerType.ARMOR
            
        if layer:
            comp = self.dragged_item
            if layer in comp.allowed_layers:
                if self.ship.current_mass + comp.mass <= self.ship.max_mass_budget:
                    self.ship.add_component(comp, layer)
                    self._update_stats_display()
                else:
                    self._show_error("Mass Limit!")
            else:
                self._show_error(f"Cannot place {comp.name} in {layer.name}")
                
    def draw(self, screen):
        """Draw the builder scene."""
        # Background
        screen.fill(SHIP_VIEW_BG)
        
        # Draw schematic area background
        schematic_rect = pygame.Rect(
            self.left_panel_width, 0,
            self.width - self.left_panel_width - self.right_panel_width,
            self.height - self.bottom_bar_height
        )
        pygame.draw.rect(screen, SHIP_VIEW_BG, schematic_rect)
        
        # Draw ship schematic
        self._draw_schematic(screen)
        
        # Draw firing arcs if enabled
        if self.show_firing_arcs:
            self._draw_all_firing_arcs(screen)
        elif self.hovered_component and isinstance(self.hovered_component, Weapon):
            self._draw_component_firing_arc(screen, self.hovered_component)
            
        # Draw pygame_gui
        self.ui_manager.draw_ui(screen)
        
        # Draw component icons over the selection list items
        self._draw_component_icons(screen)
        
        # Draw tooltip (on top of everything)
        if self.hovered_component and not self.dragged_item:
            self._draw_tooltip(screen, self.hovered_component)
            
        # Draw dragged item
        if self.dragged_item:
            mx, my = pygame.mouse.get_pos()
            sprite = self.sprite_mgr.get_sprite(self.dragged_item.sprite_index)
            if sprite:
                screen.blit(sprite, (mx - 16, my - 16))
                
        # Draw error message
        if self.error_timer > 0:
            font = pygame.font.SysFont("Arial", 18)
            err_surf = font.render(self.error_message, True, (255, 100, 100))
            x = (self.width - err_surf.get_width()) // 2
            screen.blit(err_surf, (x, 50))
            
    def _draw_schematic(self, screen):
        """Draw the ship schematic."""
        cx = self.left_panel_width + (self.width - self.left_panel_width - self.right_panel_width) // 2
        cy = (self.height - self.bottom_bar_height) // 2
        max_r = 250
        
        # Draw rings
        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), max_r, 2)  # Armor
        pygame.draw.circle(screen, (200, 50, 50), (cx, cy), int(max_r * 0.8), 2)  # Outer
        pygame.draw.circle(screen, (50, 50, 200), (cx, cy), int(max_r * 0.5), 2)  # Inner
        pygame.draw.circle(screen, (200, 200, 200), (cx, cy), int(max_r * 0.2), 2)  # Core
        
        # Draw labels
        font = pygame.font.SysFont("Arial", 10)
        labels = [
            (max_r * 0.95, "ARMOR"),
            (max_r * 0.72, "OUTER"),
            (max_r * 0.42, "INNER"),
            (max_r * 0.1, "CORE")
        ]
        for r, text in labels:
            surf = font.render(text, True, (80, 80, 80))
            screen.blit(surf, (cx - surf.get_width() // 2, cy - r - 12))
        
        # Draw components
        for ltype, data in self.ship.layers.items():
            if ltype == LayerType.CORE:
                radius = max_r * 0.1
            elif ltype == LayerType.INNER:
                radius = max_r * 0.35
            elif ltype == LayerType.OUTER:
                radius = max_r * 0.65
            elif ltype == LayerType.ARMOR:
                radius = max_r * 0.9
            else:
                continue
                
            comps = data['components']
            if not comps:
                continue
                
            angle_step = 360 / len(comps)
            current_angle = 0
            
            for comp in comps:
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
                if sprite:
                    # Rotate sprite
                    has_facing = any(m.definition.id == 'facing' for m in comp.modifiers)
                    if has_facing and hasattr(comp, 'facing_angle'):
                        rotation_angle = -comp.facing_angle
                    else:
                        rotation_angle = -current_angle - 90
                        
                    rotated = pygame.transform.rotate(sprite, rotation_angle)
                    rect = rotated.get_rect(center=(int(px), int(py)))
                    screen.blit(rotated, rect)
                    
                    # Highlight selected
                    if self.selected_component and self.selected_component[2] == comp:
                        pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 20, 2)
                else:
                    pygame.draw.rect(screen, (0, 255, 0), (px - 10, py - 10, 20, 20))
                    
                current_angle += angle_step
    
    def _draw_component_icons(self, screen):
        """Draw component icons next to list items."""
        # The UISelectionList items start at y=35 in the left panel
        # Match the actual item height used by pygame_gui (usually around 20px)
        list_x = 8  # Left edge of icons
        list_y = 38  # First item Y position (inside panel)
        item_height = 20  # Matches pygame_gui default item height
        
        for i, comp in enumerate(self.available_components):
            sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
            if sprite:
                # Scale sprite to match text height
                scaled = pygame.transform.scale(sprite, (16, 16))
                screen.blit(scaled, (list_x, list_y + i * item_height + 2))
                
    def _draw_tooltip(self, screen, comp):
        """Draw component tooltip."""
        mx, my = pygame.mouse.get_pos()
        font = pygame.font.SysFont("Arial", 14)
        font_sm = pygame.font.SysFont("Arial", 12)
        
        # Build info lines
        lines = [
            (comp.name, (255, 255, 100)),
            (f"Type: {comp.type_str}", (200, 200, 200)),
            (f"Mass: {comp.mass:.1f}t", (200, 200, 200)),
            (f"HP: {comp.max_hp:.0f}", (200, 200, 200)),
        ]
        
        # Type-specific stats
        if hasattr(comp, 'damage'):
            lines.append((f"Damage: {comp.damage}", (255, 150, 150)))
        if hasattr(comp, 'range'):
            lines.append((f"Range: {comp.range}", (255, 150, 150)))
        if hasattr(comp, 'reload_time'):
            lines.append((f"Reload: {comp.reload_time}s", (255, 150, 150)))
        if hasattr(comp, 'firing_arc'):
            lines.append((f"Firing Arc: {comp.firing_arc}°", (255, 150, 150)))
        if hasattr(comp, 'thrust_force'):
            lines.append((f"Thrust: {comp.thrust_force}", (100, 255, 100)))
        if hasattr(comp, 'fuel_cost_per_sec'):
            lines.append((f"Fuel Cost: {comp.fuel_cost_per_sec}/s", (255, 200, 100)))
        if hasattr(comp, 'turn_speed') and comp.turn_speed > 0:
            lines.append((f"Turn Speed: {comp.turn_speed}", (100, 200, 255)))
        if hasattr(comp, 'capacity'):
            lines.append((f"Capacity: {comp.capacity}", (200, 200, 255)))
        if hasattr(comp, 'energy_generation_rate') and comp.energy_generation_rate > 0:
            lines.append((f"Energy Gen: {comp.energy_generation_rate}/s", (100, 200, 255)))
            
        # Modifiers
        if comp.modifiers:
            lines.append(("", (0, 0, 0)))
            lines.append(("Modifiers:", (150, 255, 150)))
            for m in comp.modifiers:
                lines.append((f"  • {m.definition.name}: {m.value:.0f}", (150, 255, 150)))
                
        # Calculate box size
        line_height = 18
        padding = 10
        max_width = max(font.size(l[0])[0] for l in lines) + padding * 2
        box_h = len(lines) * line_height + padding * 2
        box_w = max(max_width, 200)
        
        # Position
        box_x = mx + 15
        box_y = my + 15
        if box_x + box_w > self.width:
            box_x = mx - box_w - 15
        if box_y + box_h > self.height:
            box_y = my - box_h - 15
            
        # Draw box
        pygame.draw.rect(screen, (25, 25, 35), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (100, 100, 150), (box_x, box_y, box_w, box_h), 1)
        
        # Draw sprite
        sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
        if sprite:
            screen.blit(sprite, (box_x + box_w - 42, box_y + 8))
            
        # Draw text
        y = box_y + padding
        for text, color in lines:
            if text:
                surf = font_sm.render(text, True, color)
                screen.blit(surf, (box_x + padding, y))
            y += line_height
            
    def _draw_all_firing_arcs(self, screen):
        """Draw firing arcs for all weapons."""
        cx = self.left_panel_width + (self.width - self.left_panel_width - self.right_panel_width) // 2
        cy = (self.height - self.bottom_bar_height) // 2
        
        for ltype, data in self.ship.layers.items():
            for comp in data['components']:
                if isinstance(comp, Weapon):
                    self._draw_weapon_arc(screen, comp, cx, cy)
                    
    def _draw_component_firing_arc(self, screen, comp):
        """Draw firing arc for a specific component."""
        if isinstance(comp, Weapon):
            cx = self.left_panel_width + (self.width - self.left_panel_width - self.right_panel_width) // 2
            cy = (self.height - self.bottom_bar_height) // 2
            self._draw_weapon_arc(screen, comp, cx, cy)
            
    def _draw_weapon_arc(self, screen, weapon, cx, cy):
        """Draw a weapon's firing arc visualization."""
        # Get weapon properties
        arc_degrees = getattr(weapon, 'firing_arc', 20)
        weapon_range = getattr(weapon, 'range', 1000)
        facing = getattr(weapon, 'facing_angle', 0)
        
        # Scale range for display (max 300 pixels)
        display_range = min(weapon_range / 10, 300)
        
        # Calculate arc angles (in pygame coordinates)
        # 0 degrees = up (ship forward)
        start_angle = math.radians(90 - facing - arc_degrees / 2)
        end_angle = math.radians(90 - facing + arc_degrees / 2)
        
        # Color based on weapon type
        if isinstance(weapon, BeamWeapon):
            color = (100, 255, 255, 100)  # Cyan for beams
        else:
            color = (255, 200, 100, 100)  # Orange for projectiles
            
        # Draw arc wedge
        points = [(cx, cy)]
        for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 2):
            rad = math.radians(angle)
            x = cx + math.cos(rad) * display_range
            y = cy - math.sin(rad) * display_range
            points.append((x, y))
        points.append((cx, cy))
        
        if len(points) > 2:
            # Create surface for transparency
            arc_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(arc_surface, (*color[:3], 50), points)
            pygame.draw.lines(arc_surface, color[:3], True, points, 2)
            screen.blit(arc_surface, (0, 0))
            
        # Draw range label
        font = pygame.font.SysFont("Arial", 10)
        mid_angle = (start_angle + end_angle) / 2
        label_x = cx + math.cos(mid_angle) * (display_range + 15)
        label_y = cy - math.sin(mid_angle) * (display_range + 15)
        label = font.render(f"{weapon_range}", True, color[:3])
        screen.blit(label, (label_x - label.get_width() // 2, label_y - label.get_height() // 2))
        
    def process_ui_time(self, dt):
        """Update pygame_gui."""
        self.ui_manager.update(dt)
