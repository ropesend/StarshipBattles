"""
WorkshopEventRouter - Extracted event handling logic from DesignWorkshopScreen (renamed from BuilderEventRouter).

This class handles all event routing for the Design Workshop screen using
a composition + delegation pattern.

PROJ-38: Access registries via gui.context.registries for DI.

Cross-layer imports (acceptable for UI):
- LayerType: Runtime - layer selection events and validation
"""
from __future__ import annotations

from typing import Any
import pygame
import pygame_gui
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.windows import UIConfirmationDialog

import logging

from game.core.profiling import profile_block
# PROJ-50: Removed get_default_registry_provider - using strict DI
from game.core.constants import LayerType  # Canonical location for LayerType

logger = logging.getLogger(__name__)


class WorkshopEventRouter:
    """Routes events to appropriate handlers in the Design Workshop.

    Uses composition pattern - receives reference to DesignWorkshopScreen and
    delegates to its components as needed.
    """

    def __init__(self, gui: 'DesignWorkshopScreen'):
        """Initialize with reference to the parent GUI.

        Args:
            gui: The DesignWorkshopScreen instance to route events for.
        """
        self.gui = gui

    def _get_vehicle_classes(self) -> Any:
        """PROJ-50: Get vehicle_classes from context registries (required)."""
        return self.gui.context.registries.vehicle_classes

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

        # Pass to component modifier grid panel
        gui.component_modifier_grid_panel.handle_event(event)

        # Pass to detail panel
        gui.detail_panel.handle_event(event)

        # Pass to stats panel (collapse/expand headers) — only for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            from game.ui.panels.design_stats_panel import DesignStatsPanel
            stats_panel = getattr(getattr(gui, 'right_panel', None), 'stats_panel', None)
            if isinstance(stats_panel, DesignStatsPanel) and stats_panel.handle_event(event):
                stats_panel.rebuild(gui.ship)
                gui.right_panel._sync_from_stats_panel()
                gui.right_panel.update_stats_display(gui.ship)
                return True

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
            
        elif act_type == 'quick_add':
            self._handle_quick_add(data)

        elif act_type == 'move_individual':
            self._handle_move_individual(data)

        elif act_type == 'move_group':
            self._handle_move_group(data)

        elif act_type == 'clear_settings':
            with profile_block("Builder: Clear Settings"):
                gui.controller.selected_component = None
                gui.on_selection_changed(None)
                gui.rebuild_modifier_ui()
                logger.debug("Deselected component")
                
        elif act_type == 'toggle_layer':
            # Layer header toggle - already handled by callback
            pass
            
        return True
    
    def _handle_quick_add(self, data) -> None:
        """Handle quick-add from component palette '+' button."""
        gui = self.gui
        with profile_block("Builder: Quick Add"):
            component_id = data['component_id']
            selected_layer = data.get('selected_layer')
            count = data.get('count', 1)

            success = gui.viewmodel.quick_add_component(
                component_id,
                selected_layer=selected_layer,
                count=count,
            )
            if success:
                gui.layer_panel.rebuild()
                gui.update_stats()
            else:
                errors = gui.viewmodel.last_errors
                if errors:
                    gui.show_error(f"Cannot add: {', '.join(errors)}")

    def _handle_move_individual(self, data) -> None:
        """Handle moving a single component up/down between layers."""
        gui = self.gui
        with profile_block("Builder: Move Individual"):
            component, source_layer, direction = data
            target_layer = gui.viewmodel.resolve_move_target(component, source_layer, direction)
            if target_layer is None:
                return

            # Find the component's index in its source layer
            try:
                idx = gui.ship.layers[source_layer].components.index(component)
            except ValueError:
                return

            success = gui.viewmodel.move_component(source_layer, idx, target_layer)
            if success:
                gui.layer_panel.rebuild()
                gui.update_stats()

    def _handle_move_group(self, data) -> None:
        """Handle moving a component group (stack) up/down between layers."""
        gui = self.gui
        with profile_block("Builder: Move Group"):
            group_key, source_layer, direction = data

            # Resolve target from the representative component
            from game.ui.screens.builder.grouping_strategies import get_component_group_key
            rep_comp = None
            for c in gui.ship.layers[source_layer].components:
                if get_component_group_key(c) == group_key:
                    rep_comp = c
                    break
            if rep_comp is None:
                return

            target_layer = gui.viewmodel.resolve_move_target(rep_comp, source_layer, direction)
            if target_layer is None:
                return

            success = gui.viewmodel.move_component_group(group_key, source_layer, target_layer)
            if success:
                gui.layer_panel.rebuild()
                gui.update_stats()

    def _handle_select_component_type(self, data) -> None:
        """Handle component type selection from palette."""
        gui = self.gui
        with profile_block("Builder: Select Component Type"):
            c = data
            # Clear Layer Panel Selection (avoid confusion)
            gui.layer_panel.selected_group_key = None
            gui.layer_panel.selected_component_id = None
            gui.on_selection_changed(None)
            gui.layer_panel.rebuild()

            # Clone component with default modifiers.
            # Attach to the design-in-progress BEFORE recalculate_stats so
            # `=ship_class_mass` formulas (bridge mass, warp_drive, armor
            # variants, etc.) resolve via component.ship.max_mass_budget.
            # See docs/02_PATTERNS.md Pattern 3 and
            # docs/guides/component_system.md. Mirrors the fix in
            # game/ui/screens/builder/interaction_controller.py:95-99 for
            # the shift-drop path.
            gui.controller.dragged_item = c.clone()
            gui.controller.dragged_item.ship = gui.ship
            gui.controller.dragged_item.recalculate_stats()

            # Set as selected so modifiers panel updates
            gui.on_selection_changed(gui.controller.dragged_item)
    
    def _handle_select_group(self, data) -> None:
        """Handle group selection in layer panel."""
        gui = self.gui
        with profile_block("Builder: Select Group"):
            # Check modifier keys for multi-select
            keys = pygame.key.get_pressed()
            append = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if not append:
                gui.left_panel.deselect_all()
            
            # data is group_key - collect all components matching the group
            from game.ui.screens.builder.grouping_strategies import get_component_group_key
            comps = [c for c in gui.ship.get_all_components()
                     if get_component_group_key(c) == data]
            
            gui.on_selection_changed(comps, append=append)
            
            # Rebuild layer panel now that builder state is updated
            gui.layer_panel.rebuild()
    
    def _handle_select_individual(self, data) -> None:
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
    
    def _handle_remove_group(self, data) -> None:
        """Handle removing one component from a group.

        Args:
            data: Tuple of (group_key, layer_type) for targeted deletion.
        """
        gui = self.gui
        from game.ui.screens.builder.grouping_strategies import get_component_group_key

        group_key, target_layer = data

        # Find last component in this group to remove (within target layer)
        found_idx = -1
        if target_layer in gui.ship.layers:
            comps = gui.ship.layers[target_layer].components
            for idx in range(len(comps) - 1, -1, -1):
                c = comps[idx]
                if get_component_group_key(c) == group_key:
                    found_idx = idx
                    break

        if found_idx >= 0:
            gui.viewmodel.remove_component(target_layer, found_idx)
            gui.update_stats()
    
    def _handle_remove_individual(self, data) -> None:
        """Handle removing an individual component.

        Args:
            data: Tuple of (component, layer_type) for targeted deletion.
        """
        gui = self.gui
        comp, target_layer = data

        # Remove from the target layer
        if target_layer in gui.ship.layers:
            for idx, c in enumerate(gui.ship.layers[target_layer].components):
                if c is comp:
                    gui.viewmodel.remove_component(target_layer, idx)
                    break

        # Remove from selection list if present
        if gui.selected_components:
            gui.selected_components = [x for x in gui.selected_components if x[2] is not comp]
            gui.on_selection_changed(gui.selected_components)

        gui.update_stats()
    
    def _handle_add_component(self, act_type, data) -> None:
        """Handle adding a component (cloned from group or individual).

        Args:
            act_type: 'add_individual' or 'add_group'
            data: Tuple of (component_or_group_key, layer_type) for targeted addition.
        """
        gui = self.gui
        target_comp = None
        target_layer = None

        if act_type == 'add_individual':
            target_comp, target_layer = data
        else:
            # add_group: unpack group_key and layer
            group_key, target_layer = data

            # Find first component of group in target layer
            from game.ui.screens.builder.grouping_strategies import get_component_group_key
            if target_layer in gui.ship.layers:
                for c in gui.ship.layers[target_layer].components:
                    if get_component_group_key(c) == group_key:
                        target_comp = c
                        break

        if target_comp:
            # Clone
            from game.ui.screens.builder.modifier_utils import copy_modifiers
            new_comp = target_comp.clone()
            copy_modifiers(target_comp, new_comp)

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
            gui.save_ship()
        elif event.ui_element == gui.load_btn:
            gui.load_ship()
        elif event.ui_element == gui.clear_btn:
            gui.show_clear_confirmation()
        elif event.ui_element == gui.arc_toggle_btn:
            gui.show_firing_arcs = not gui.show_firing_arcs
            gui.arc_toggle_btn.set_text("Hide Firing Arcs" if gui.show_firing_arcs else "Show Firing Arcs")
        elif gui.hull_toggle_btn is not None and event.ui_element == gui.hull_toggle_btn:
            showing = gui.viewmodel.toggle_hull_layer()
            gui.hull_toggle_btn.set_text("Hide Hull" if showing else "Show Hull")
            gui.layer_panel.rebuild()
        elif event.ui_element == gui.target_btn:
            gui.on_select_target_pressed()
        elif gui.std_data_btn is not None and event.ui_element == gui.std_data_btn:
            gui.data_reloader.load_standard_data()
        elif gui.test_data_btn is not None and event.ui_element == gui.test_data_btn:
            gui.data_reloader.load_test_data()
        elif gui.select_data_btn is not None and event.ui_element == gui.select_data_btn:
            gui.data_reloader.on_select_data_pressed()
        elif gui.verbose_btn is not None and event.ui_element == gui.verbose_btn:
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
        elif event.ui_element == gui.right_panel.vehicle_type_dropdown:
            return self._handle_vehicle_type_dropdown(event)
        elif gui.right_panel.theme_dropdown is not None and event.ui_element == gui.right_panel.theme_dropdown:
            # Only allow theme change in standalone mode (integrated mode locks to empire theme)
            if gui.context.is_standalone():
                gui.viewmodel.set_ship_theme(event.text)
                gui.right_panel.update_portrait_image()
                logger.info(f"Changed theme to {event.text}")
            return True
        elif event.ui_element == gui.right_panel.movement_dropdown:
            return self._handle_movement_dropdown(event)
        elif event.ui_element == gui.right_panel.targeting_dropdown:
            return self._handle_targeting_dropdown(event)
        elif event.ui_element == gui.right_panel.role_dropdown:
            return self._handle_role_dropdown(event)

        return False
    
    def _apply_confirmation_dropdown(
        self,
        new_value,
        current_value,
        pending_action: tuple,
        dialog_size: tuple,
        dialog_message: str,
        dialog_title: str,
    ) -> bool:
        """Shared body for confirmation-based dropdown handlers (PROJ-375).

        Used by `_handle_class_dropdown` and `_handle_vehicle_type_dropdown`,
        which differ only in the dialog sizing, message, and pending-action
        tuple. If the ship has no components, runs the action immediately;
        otherwise opens a `UIConfirmationDialog`.
        """
        gui = self.gui
        if new_value == current_value:
            return True

        gui.pending_action = pending_action

        if gui.ship.has_components():
            width, height = dialog_size
            gui.confirm_dialog = UIConfirmationDialog(
                pygame.Rect(
                    (gui.width - width) // 2,
                    (gui.height - height) // 2,
                    width, height,
                ),
                manager=gui.ui_manager,
                action_long_desc=dialog_message,
                window_title=dialog_title,
            )
        else:
            gui.execute_pending_action()
        return True

    def _apply_resolver_dropdown(
        self,
        selected_name: str,
        resolver,
        setter,
        kind_label: str,
    ) -> bool:
        """Shared body for resolver-based dropdown handlers (PROJ-375).

        Used by `_handle_movement_dropdown`, `_handle_targeting_dropdown`,
        and `_handle_role_dropdown`. The resolver is a callable
        `(selected_name) -> id_or_None` so movement/targeting (options-list
        lookup) and role (registry-loop) share the same dispatch surface.
        Logs a warning if the resolver returns None.
        """
        resolved_id = resolver(selected_name)
        if resolved_id is None:
            logger.warning("No %s found for display name '%s'", kind_label, selected_name)
            return True
        setter(resolved_id)
        return True

    def _handle_class_dropdown(self, event) -> bool:
        """Handle ship class dropdown change."""
        new_class = event.text
        return self._apply_confirmation_dropdown(
            new_value=new_class,
            current_value=self.gui.ship.ship_class,
            pending_action=('change_class', new_class),
            dialog_size=(600, 400),
            dialog_message=(
                f"Change class to {new_class}?<br><br>Warning: This will "
                "attempt to refit existing components.<br>Some items may be "
                "resized or lost if they don't fit."
            ),
            dialog_title="Confirm Refit",
        )

    def _handle_vehicle_type_dropdown(self, event) -> bool:
        """Handle vehicle type dropdown change."""
        new_type = event.text
        if new_type == self.gui.ship.vehicle_type:
            return True
        # Determine default class for this type
        classes = self._get_vehicle_classes()
        valid_classes = [
            (n, classes[n].get('max_mass', 0))
            for n, c in classes.items() if c.get('type', 'Ship') == new_type
        ]
        valid_classes.sort(key=lambda x: x[1])
        target_class = valid_classes[0][0] if valid_classes else "Escort"
        return self._apply_confirmation_dropdown(
            new_value=new_type,
            current_value=self.gui.ship.vehicle_type,
            pending_action=('change_type', target_class),
            dialog_size=(400, 200),
            dialog_message=(
                f"Change type to {new_type}?<br><br>"
                "<b>WARNING: This will CLEAR the current design.</b>"
            ),
            dialog_title="Confirm Type Change",
        )

    def _handle_movement_dropdown(self, event) -> bool:
        """Handle movement policy dropdown change."""
        from game.ui.screens.builder.right_panel import _MOVEMENT_OPTIONS
        return self._apply_resolver_dropdown(
            selected_name=event.text,
            resolver=lambda name: next(
                (pid for pid, n in _MOVEMENT_OPTIONS if n == name), None
            ),
            setter=self.gui.viewmodel.set_ship_movement_policy,
            kind_label="movement policy",
        )

    def _handle_targeting_dropdown(self, event) -> bool:
        """Handle targeting policy dropdown change."""
        from game.ui.screens.builder.right_panel import _TARGETING_OPTIONS
        return self._apply_resolver_dropdown(
            selected_name=event.text,
            resolver=lambda name: next(
                (pid for pid, n in _TARGETING_OPTIONS if n == name), None
            ),
            setter=self.gui.viewmodel.set_ship_targeting_policy,
            kind_label="targeting policy",
        )

    def _handle_role_dropdown(self, event) -> bool:
        """Handle design role dropdown change."""
        from game.strategy.data.design_role_registry import get_default_design_role_registry

        registry = get_default_design_role_registry()
        return self._apply_resolver_dropdown(
            selected_name=event.text,
            resolver=lambda name: next(
                (r.id for r in registry.all() if r.display_name == name), None
            ),
            setter=self.gui.viewmodel.set_ship_design_role,
            kind_label="design role",
        )

    def _handle_confirmation(self, event) -> bool:
        """Handle confirmation dialog confirmed events."""
        gui = self.gui
        if event.ui_element == gui.confirm_dialog:
            gui.execute_pending_action()
            return True
        return False
    
    def _handle_right_click(self, event) -> bool:  # noqa: ARG002
        """Handle right-click events."""
        # Preset deletion removed - no longer applicable
        return False
    
