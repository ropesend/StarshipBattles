"""
WorkshopEventRouter - Extracted event handling logic from DesignWorkshopGUI (renamed from BuilderEventRouter).

This class handles all event routing for the Design Workshop screen using
a composition + delegation pattern.
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.windows import UIConfirmationDialog

from game.core.profiling import profile_block
from game.core.registry import get_modifier_registry, get_vehicle_classes
from game.simulation.entities.ship import LayerType

from game.core.logger import log_error, log_info, log_warning, log_debug


class WorkshopEventRouter:
    """Routes events to appropriate handlers in the Design Workshop.

    Uses composition pattern - receives reference to DesignWorkshopGUI and
    delegates to its components as needed.
    """

    def __init__(self, gui: 'DesignWorkshopGUI'):
        """Initialize with reference to the parent GUI.

        Args:
            gui: The DesignWorkshopGUI instance to route events for.
        """
        self.gui = gui
    
    def handle_event(self, event) -> bool:
        """Route events to appropriate handlers.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            True if the event was consumed, False otherwise.
        """
        gui = self.gui
        
        gui.ui_manager.process_events(event)
        
        # Pass to panels
        action = gui.left_panel.handle_event(event)
        if not action:
            action = gui.layer_panel.handle_event(event)
            
        if not action:
            action = gui.modifier_panel.handle_event(event)

        if action:
            if isinstance(action, bool):
                return True
            
            return self._handle_panel_action(action)
        
        # Pass to weapons panel
        gui.weapons_report_panel.handle_event(event)
        
        # Pass to controller
        gui.controller.handle_event(event)
        
        # Handle pygame_gui events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            return self._handle_button_pressed(event)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            return self._handle_dropdown_changed(event)
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            return self._handle_confirmation(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            return self._handle_right_click(event)
        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        
        return False
    
    def _handle_panel_action(self, action) -> bool:
        """Handle actions returned by panel event handlers."""
        gui = self.gui
        act_type, data = action
        
        if act_type == 'refresh_ui':
            gui.update_stats()
            
        elif act_type == 'select_component_type':
            self._handle_select_component_type(data)
            
        elif act_type == 'select_group':
            self._handle_select_group(data)
            
        elif act_type == 'select_individual':
            self._handle_select_individual(data)
            
        elif act_type == 'remove_group':
            self._handle_remove_group(data)
            
        elif act_type == 'remove_individual':
            self._handle_remove_individual(data)
            
        elif act_type == 'add_group' or act_type == 'add_individual':
            self._handle_add_component(act_type, data)
            
        elif act_type == 'apply_preset':
            gui.template_modifiers = data
            gui.rebuild_modifier_ui()
            
        elif act_type == 'clear_settings':
            with profile_block("Builder: Clear Settings"):
                gui.controller.selected_component = None
                gui.template_modifiers = {}
                gui.on_selection_changed(None)
                gui.rebuild_modifier_ui()
                log_debug("Cleared settings or deselected component")
                
        elif act_type == 'toggle_layer':
            # Layer header toggle - already handled by callback
            pass
            
        return True
    
    def _handle_select_component_type(self, data):
        """Handle component type selection from palette."""
        gui = self.gui
        with profile_block("Builder: Select Component Type"):
            c = data
            # Clear Layer Panel Selection (avoid confusion)
            gui.layer_panel.selected_group_key = None
            gui.layer_panel.selected_component_id = None
            gui.on_selection_changed(None)
            gui.layer_panel.rebuild()
            
            gui.controller.dragged_item = c.clone()
            # Apply template modifiers
            mods = get_modifier_registry()
            for m_id, val in gui.template_modifiers.items():
                if m_id in mods:
                    mod_def = mods[m_id]
                    allow = True
                    if mod_def.restrictions:
                        if 'allow_types' in mod_def.restrictions and c.type_str not in mod_def.restrictions['allow_types']:
                            allow = False
                    if allow:
                        gui.controller.dragged_item.add_modifier(m_id)
                        m = gui.controller.dragged_item.get_modifier(m_id)
                        if m:
                            m.value = val
            gui.controller.dragged_item.recalculate_stats()
            
            # Set as selected so modifiers panel updates
            gui.on_selection_changed(gui.controller.dragged_item)
    
    def _handle_select_group(self, data):
        """Handle group selection in layer panel."""
        gui = self.gui
        with profile_block("Builder: Select Group"):
            # Check modifier keys for multi-select
            keys = pygame.key.get_pressed()
            append = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if not append:
                gui.left_panel.deselect_all()
            
            # data is group_key - collect all components matching the group
            from ui.builder.grouping_strategies import get_component_group_key
            comps = [c for c in gui.ship.get_all_components()
                     if get_component_group_key(c) == data]
            
            gui.on_selection_changed(comps, append=append)
            
            # Rebuild layer panel now that builder state is updated
            gui.layer_panel.rebuild()
    
    def _handle_select_individual(self, data):
        """Handle individual component selection."""
        gui = self.gui
        with profile_block("Builder: Select Individual"):
            keys = pygame.key.get_pressed()
            is_ctrl = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            is_shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if not (is_ctrl or is_shift):
                gui.left_panel.deselect_all()
                
            if is_shift and gui.selected_component:
                # Range Selection
                start_comp = gui.selected_component[2]
                end_comp = data
                range_comps = gui.layer_panel.get_range_selection(start_comp, end_comp)
                gui.on_selection_changed(range_comps, append=is_ctrl, toggle=False)
            else:
                # Single Click (Toggle if Ctrl)
                gui.on_selection_changed(data, append=is_ctrl, toggle=is_ctrl)
            
            # Rebuild layer panel now that builder state is updated
            gui.layer_panel.rebuild()
    
    def _handle_remove_group(self, data):
        """Handle removing one component from a group."""
        gui = self.gui
        from ui.builder.grouping_strategies import get_component_group_key
        
        # Find Last Component in this group to remove
        found_layer = None
        found_idx = -1
        
        # Iterate backwards to find one instance
        for l_type, layers in gui.ship.layers.items():
            comps = layers['components']
            for idx in range(len(comps) - 1, -1, -1):
                c = comps[idx]
                if get_component_group_key(c) == data:
                    found_layer = l_type
                    found_idx = idx
                    break
            if found_layer:
                break
        
        if found_layer:
            gui.viewmodel.remove_component(found_layer, found_idx)
            gui.update_stats()
    
    def _handle_remove_individual(self, data):
        """Handle removing an individual component."""
        gui = self.gui
        removed = False
        for l_type, layers in gui.ship.layers.items():
            for idx, c in enumerate(layers['components']):
                if c is data:
                    gui.viewmodel.remove_component(l_type, idx)
                    removed = True
                    break
            if removed:
                break
        
        # Remove from selection list if present
        if gui.selected_components:
            gui.selected_components = [x for x in gui.selected_components if x[2] is not data]
            gui.on_selection_changed(gui.selected_components)
        
        gui.update_stats()
    
    def _handle_add_component(self, act_type, data):
        """Handle adding a component (cloned from group or individual)."""
        gui = self.gui
        target_comp = None
        
        if act_type == 'add_individual':
            target_comp = data
        else:
            # Find first component of group using ship helper
            from ui.builder.grouping_strategies import get_component_group_key
            for c in gui.ship.get_all_components():
                if get_component_group_key(c) == data:
                    target_comp = c
                    break
                    
        if target_comp:
            # Clone
            new_comp = target_comp.clone()
            for m in target_comp.modifiers:
                new_comp.add_modifier(m.definition.id)
                nm = new_comp.get_modifier(m.definition.id)
                if nm:
                    nm.value = m.value
            new_comp.recalculate_stats()
            
            # Find layer of original using ship helper
            target_layer = None
            for l_type, comp in gui.ship.iter_components():
                if comp is target_comp:
                    target_layer = l_type
                    break
                    
            if target_layer:
                success = gui.viewmodel.add_component_instance(new_comp, target_layer)
                if success:
                    gui.update_stats()
                else:
                    errors = gui.viewmodel.last_errors
                    gui.show_error(f"Cannot add: {', '.join(errors) if errors else 'Validation failed'}")
    
    def _handle_button_pressed(self, event) -> bool:
        """Handle UI button press events."""
        gui = self.gui
        
        if event.ui_element == gui.start_btn:
            gui.on_start_battle(None)
        elif event.ui_element == gui.save_btn:
            gui._save_ship()
        elif event.ui_element == gui.load_btn:
            gui._load_ship()
        elif event.ui_element == gui.clear_btn:
            gui._show_clear_confirmation()
        elif event.ui_element == gui.arc_toggle_btn:
            gui.show_firing_arcs = not gui.show_firing_arcs
            gui.arc_toggle_btn.set_text("Hide Firing Arcs" if gui.show_firing_arcs else "Show Firing Arcs")
        elif hasattr(gui, 'hull_toggle_btn') and event.ui_element == gui.hull_toggle_btn:
            showing = gui.viewmodel.toggle_hull_layer()
            gui.hull_toggle_btn.set_text("Hide Hull" if showing else "Show Hull")
            gui.layer_panel.rebuild()
        elif event.ui_element == gui.target_btn:
            gui._on_select_target_pressed()
        elif hasattr(gui, 'std_data_btn') and event.ui_element == gui.std_data_btn:
            gui._load_standard_data()
        elif hasattr(gui, 'test_data_btn') and event.ui_element == gui.test_data_btn:
            gui._load_test_data()
        elif hasattr(gui, 'select_data_btn') and event.ui_element == gui.select_data_btn:
            gui._on_select_data_pressed()
        elif hasattr(gui, 'verbose_btn') and event.ui_element == gui.verbose_btn:
            gui.weapons_report_panel.verbose_tooltip = not gui.weapons_report_panel.verbose_tooltip
        elif event.ui_element == gui.detail_panel.details_btn:
            gui.detail_panel.show_details_popup()
        else:
            return False
        
        return True
    
    def _handle_dropdown_changed(self, event) -> bool:
        """Handle dropdown menu change events."""
        gui = self.gui
        
        if event.ui_element == gui.right_panel.class_dropdown:
            return self._handle_class_dropdown(event)
        elif hasattr(gui, 'right_panel') and hasattr(gui.right_panel, 'vehicle_type_dropdown') and event.ui_element == gui.right_panel.vehicle_type_dropdown:
            return self._handle_vehicle_type_dropdown(event)
        elif hasattr(gui.right_panel, 'theme_dropdown') and event.ui_element == gui.right_panel.theme_dropdown:
            # Only allow theme change in standalone mode (integrated mode locks to empire theme)
            if gui.context.is_standalone():
                gui.ship.theme_id = event.text
                gui.right_panel.update_portrait_image()
                log_info(f"Changed theme to {event.text}")
            return True
        elif event.ui_element == gui.right_panel.ai_dropdown:
            return self._handle_ai_dropdown(event)
        
        return False
    
    def _handle_class_dropdown(self, event) -> bool:
        """Handle ship class dropdown change."""
        gui = self.gui
        new_class = event.text
        if new_class == gui.ship.ship_class:
            return True
        
        gui.pending_action = ('change_class', new_class)
        
        # Check if ship has components using ship helper
        if gui.ship.has_components():
            msg = f"Change class to {new_class}?<br><br>Warning: This will attempt to refit existing components.<br>Some items may be resized or lost if they don't fit."
            gui.confirm_dialog = UIConfirmationDialog(
                pygame.Rect((gui.width - 600) // 2, (gui.height - 400) // 2, 600, 400),
                manager=gui.ui_manager,
                action_long_desc=msg,
                window_title="Confirm Refit"
            )
        else:
            gui._execute_pending_action()
        
        return True
    
    def _handle_vehicle_type_dropdown(self, event) -> bool:
        """Handle vehicle type dropdown change."""
        gui = self.gui
        new_type = event.text
        if new_type == getattr(gui.ship, 'vehicle_type', "Ship"):
            return True
        
        # Determine default class for this type
        classes = get_vehicle_classes()
        valid_classes = [(n, classes[n].get('max_mass', 0)) for n, c in classes.items() if c.get('type', 'Ship') == new_type]
        valid_classes.sort(key=lambda x: x[1])
        target_class = valid_classes[0][0] if valid_classes else "Escort"
        
        gui.pending_action = ('change_type', target_class)
        
        # Check if ship has components using ship helper
        if gui.ship.has_components():
            msg = f"Change type to {new_type}?<br><br><b>WARNING: This will CLEAR the current design.</b>"
            gui.confirm_dialog = UIConfirmationDialog(
                pygame.Rect((gui.width - 400) // 2, (gui.height - 200) // 2, 400, 200),
                manager=gui.ui_manager,
                action_long_desc=msg,
                window_title="Confirm Type Change"
            )
        else:
            gui._execute_pending_action()
        
        return True
    
    def _handle_ai_dropdown(self, event) -> bool:
        """Handle AI strategy dropdown change."""
        gui = self.gui
        from game.ai.controller import StrategyManager
        selected_name = event.text
        manager = StrategyManager.instance()
        for strategy_id, strat in manager.strategies.items():
            if strat.get('name', '') == selected_name:
                gui.ship.ai_strategy = strategy_id
                break
        else:
            gui.ship.ai_strategy = event.text.lower().replace(' ', '_')
        return True
    
    def _handle_confirmation(self, event) -> bool:
        """Handle confirmation dialog confirmed events."""
        gui = self.gui
        if event.ui_element == gui.confirm_dialog:
            gui._execute_pending_action()
            return True
        return False
    
    def _handle_right_click(self, event) -> bool:
        """Handle right-click events (preset deletion)."""
        gui = self.gui
        for preset_name, btn in getattr(gui, 'preset_buttons', []):
            if btn.rect.collidepoint(event.pos):
                gui.preset_manager.delete_preset(preset_name)
                gui.left_panel.rebuild_modifier_ui()
                log_info(f"Deleted preset: {preset_name}")
                return True
        return False
    
    def _handle_keydown(self, event) -> bool:
        """Handle keyboard events."""
        gui = self.gui
        
        if event.key == pygame.K_F12:
            # Full screenshot
            gui.screenshot_manager.capture(label="full_window")
            return True
        elif event.key == pygame.K_F11:
            # Focused screenshot centered on mouse
            mx, my = pygame.mouse.get_pos()
            size = 1024
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (mx, my)
            gui.screenshot_manager.capture(region=rect, label="mouse_focus")
            return True
        elif event.key == pygame.K_F10:
            # Debug Sequence Trigger
            gui._debug_sequence_capture()
            return True
        
        return False
