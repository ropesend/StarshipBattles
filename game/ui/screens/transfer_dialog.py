"""
Transfer Dialog - Resource and cargo transfer between fleets and planets.

Handles transfer commands for moving resources between ships and colonies.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel, UIDropDownMenu, UIHorizontalSlider
from game.core.input_actions import InputAction
from game.core.logger import log_debug, log_info
from game.strategy.engine.commands import IssueTransferCommand

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper

class TransferDialog(UIWindow):
    """
    Hex-aware cargo and population transfer dialog.

    Allows selecting a source and target within the same sector, specifying
    cargo/species types, and the amount to transfer.
    """
    def __init__(self, relative_rect, manager, source_fleet, hex_coord, scene,
                 input_mapper: Optional['InputMapper'] = None):
        super().__init__(relative_rect, manager, window_display_title="Cargo & Population Transfer")
        self.source_fleet = source_fleet
        self.hex_coord = hex_coord
        self.scene = scene
        self.facade = scene.facade
        self._mapper = input_mapper
        
        # UI State
        self.available_sources = []
        self.available_targets = []
        self.available_cargo = [] # List of (label, type, species_id, max_amount)
        
        self._setup_ui()
        self._apply_tooltips()
        self._populate_initial_data()

    def _setup_ui(self):
        """Initialize UI elements."""
        padding = 10
        label_h = 20
        element_h = 30
        
        curr_y = padding
        
        # --- Sector ---
        UILabel(pygame.Rect(padding, curr_y, self.rect.width - 20, label_h), 
                f"Sector: {self.hex_coord}", 
                self.ui_manager, 
                container=self)
        curr_y += element_h + padding

        # --- Debug Info ---
        self.lbl_debug = UILabel(pygame.Rect(padding, curr_y, self.rect.width - 20, label_h), 
                                "Debug: Init", 
                                self.ui_manager, 
                                container=self)
        curr_y += element_h + padding

        # --- Source ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Source:", self.ui_manager, container=self)
        self.drop_source = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 150, element_h),
            manager=self.ui_manager,
            container=self
        )
        curr_y += element_h + padding
        
        # --- Target ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Target:", self.ui_manager, container=self)
        self.drop_target = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 150, element_h),
            manager=self.ui_manager,
            container=self
        )
        curr_y += element_h + padding
        
        # --- Item/Cargo ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Item:", self.ui_manager, container=self)
        self.drop_item = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 150, element_h),
            manager=self.ui_manager,
            container=self
        )
        curr_y += element_h + padding
        
        # --- Amount ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Amount:", self.ui_manager, container=self)
        self.slider_amount = UIHorizontalSlider(
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 200, element_h),
            start_value=0,
            value_range=(0, 100),
            manager=self.ui_manager,
            container=self
        )
        self.lbl_amount = UILabel(
            pygame.Rect(self.rect.width - 80, curr_y, 60, element_h),
            "0",
            self.ui_manager,
            container=self
        )
        curr_y += element_h + (padding * 2)
        
        # --- Buttons ---
        btn_w = 150
        self.btn_confirm = UIButton(
            pygame.Rect(padding, self.rect.height - 80, btn_w, 40),
            "Issue Order",
            self.ui_manager,
            container=self
        )
        self.btn_cancel = UIButton(
            pygame.Rect(self.rect.width - btn_w - padding - 30, self.rect.height - 80, btn_w, 40),
            "Cancel",
            self.ui_manager,
            container=self
        )

    def _populate_initial_data(self):
        """Find fleets and planets at the hex and populate dropdowns."""
        # 1. Get all objects at hex
        fleets = self.facade.get_fleets_at_hex(self.hex_coord)
        planets = self.facade.get_planets_at_hex(self.hex_coord)
        
        # Determine system name for debug
        sys_name = "Unknown"
        if planets:
            # Assuming planets have system reference or we can infer
            # PlanetInfo doesn't have system name usually, but let's check
            # We can use facade to get system
            sys = self.facade._session.galaxy.get_system_at_location(self.hex_coord) 
            if not sys:
                 from game.strategy.data.pathfinding import get_system_at_hex
                 sys = get_system_at_hex(self.facade._session.galaxy, self.hex_coord)
            if sys:
                sys_name = sys.name
            else:
                sys_name = "Failed"

        debug_msg = f"Sys: {sys_name} | Plts: {len(planets)} | Hex: {self.hex_coord}"
        if hasattr(self, 'lbl_debug'):
            self.lbl_debug.set_text(debug_msg)
        
        # Filter for colonized planets
        colonies = [p for p in planets if p.owner_id is not None]
        
        # 2. Build options
        self.available_sources = []
        
        # PROJ-FIX: Always add the source fleet to available sources, regardless of where we clicked
        log_info(f"TransferDialog._populate_initial_data: Scanning hex {self.hex_coord}")
        
        if self.source_fleet:
            # Check if already added (if clicked on fleet itself)
            fleet_in_list = any(f.fleet_id == self.source_fleet.id for f in fleets)
            if not fleet_in_list:
                # Add it manually since we are using it as source
                self.available_sources.append({'label': f"Fleet {self.source_fleet.id}", 'type': 'fleet', 'id': self.source_fleet.id})

        for f in fleets:
            self.available_sources.append({'label': f"Fleet {f.fleet_id}", 'type': 'fleet', 'id': f.fleet_id})
            
        # Add planets at this hex (facade now returns only those at this specific hex)
        for p in planets:
            if p.owner_id is not None:
                label = f"Colony: {p.name}"
                p_type = 'colony'
            else:
                label = f"Planet: {p.name} (Uncolonized)"
                p_type = 'planet'
            
            log_info(f"Adding source: {label} (Type: {p_type}, ID: {p.planet_id})")
            self.available_sources.append({'label': label, 'type': p_type, 'id': p.planet_id})
            
        source_labels = [s['label'] for s in self.available_sources]
        log_info(f"Final Source Labels: {source_labels}")
        
        # Default select source_fleet if possible
        starting_option = ""
        for s in self.available_sources:
            if s['type'] == 'fleet' and s['id'] == self.source_fleet.id:
                starting_option = s['label']
                break
        
        self.drop_source = self._recreate_dropdown(self.drop_source, source_labels, starting_option)
        # Always trigger changed handler to populate targets/cargo based on whatever is selected
        self._on_source_changed(self.drop_source.selected_option)

    def _recreate_dropdown(self, old_dropdown, options, selected):
        """Recreate a dropdown as UIDropDownMenu lacks an update method."""
        rect = old_dropdown.relative_rect
        container = old_dropdown.ui_container
        old_dropdown.kill()
        return UIDropDownMenu(
            options_list=options if options else [""],
            starting_option=selected if selected in options else (options[0] if options else ""),
            relative_rect=rect,
            manager=self.ui_manager,
            container=container
        )

    def _extract_dropdown_value(self, value):
        """Extract value from dropdown selection which might be a tuple (label, id)."""
        if isinstance(value, tuple):
            return value[0]
        return value

    def _on_source_changed(self, label):
        """Update targets and cargo when source changes."""
        label = self._extract_dropdown_value(label)
        
        source = next((s for s in self.available_sources if s['label'] == label), None)
        if not source: return
        
        # 1. Populate Targets (all objects at hex except source)
        self.available_targets = [s for s in self.available_sources if s['label'] != label]
        target_labels = [t['label'] for t in self.available_targets]
        self.drop_target = self._recreate_dropdown(self.drop_target, target_labels, 
                                                  target_labels[0] if target_labels else "")
            
        # 2. Populate Cargo
        # Need current target to populate bidirectional items
        curr_target_label = self._extract_dropdown_value(self.drop_target.selected_option)
        target = next((t for t in self.available_targets if t['label'] == curr_target_label), None)
        self._update_cargo_list(source, target)

    def _get_inventory_items(self, obj_info):
        """Extract inventory items from a fleet or planet object."""
        items = []
        if not obj_info: return items
        
        # Fleet
        if hasattr(obj_info, 'passengers_current'): # simple duck typing for fleet
            passengers = getattr(obj_info, 'passengers_current', 0)
            if passengers > 0:
                items.append({
                    'label': f"Passengers ({passengers})",
                    'type': 'passengers',
                    'species_id': None,
                    'max': passengers
                })
        # Colony/Planet
        elif hasattr(obj_info, 'population_details'): # distinct for colony
             # population_details is a tuple of (race_id, count, happiness)
            for race_id, count, happiness in obj_info.population_details:
                if count > 0:
                    items.append({
                        'label': f"Population: {race_id} ({count})",
                        'type': 'passengers',
                        'species_id': race_id,
                        'max': count
                    })
        elif hasattr(obj_info, 'total_population'): # planet fallback
            passengers = getattr(obj_info, 'total_population', 0)
            if passengers > 0:
                items.append({
                    'label': f"Population ({passengers})",
                    'type': 'passengers',
                    'species_id': None,
                    'max': passengers
                })
        return items

    def _update_cargo_list(self, source, target):
        """Populate drop_item based on source (unload) and target (load) content."""
        self.available_cargo = []
        
        # 1. Source Items (Default Direction)
        # Usually 'unload' if Source=Fleet, Target=Planet.
        # Or 'load' if Source=Planet, Target=Fleet.
        # Let's determine the PRIMARY direction based on Source Type.
        primary_direction = 'unload' # Default: Source gives to Target
        
        source_obj = None
        if source['type'] == 'fleet':
            source_obj = self.facade.get_fleet(source['id'])
            if target and target['type'] in ('colony', 'planet'):
                primary_direction = 'unload' # Fleet -> Planet
            elif target and target['type'] == 'fleet':
                primary_direction = 'unload' # Fleet -> Fleet
        elif source['type'] in ('colony', 'planet'):
            source_obj = self.facade.get_planet(source['id'])
            if target and target['type'] == 'fleet':
                 primary_direction = 'load' # Planet -> Fleet

        if source_obj:
            s_items = self._get_inventory_items(source_obj)
            for item in s_items:
                item['direction'] = primary_direction 
                # Keep original label for primary items
                self.available_cargo.append(item)

        # 2. Target Items (Reverse Direction)
        # If Target has items, we can "Load" them (or "Unload" them depending on perspective).
        # We want to enable moving items FROM target TO source.
        # The implicit command direction checks Source/Target types in _issue_order.
        # We need to explicitly override or set direction.
        
        target_obj = None
        reverse_direction = 'load' if primary_direction == 'unload' else 'unload'
        
        if target:
            if target['type'] == 'fleet':
                target_obj = self.facade.get_fleet(target['id'])
            elif target['type'] in ('colony', 'planet'):
                target_obj = self.facade.get_planet(target['id'])
                
            if target_obj:
                t_items = self._get_inventory_items(target_obj)
                for item in t_items:
                    item['direction'] = reverse_direction
                    # Differentiate label for items coming from Target
                    action_label = "Load" if reverse_direction == 'load' else "Pull"
                    item['label'] = f"{action_label}: {item['label']}"
                    self.available_cargo.append(item)

        item_labels = [c['label'] for c in self.available_cargo]
        self.drop_item = self._recreate_dropdown(self.drop_item, item_labels, 
                                                item_labels[0] if item_labels else "")
        if self.available_cargo:
            self._update_amount_ui(self.available_cargo[0]['max'])
        else:
            self._update_amount_ui(0)

    def _update_amount_ui(self, max_val):
        """Reset slider for a new item. Ensure max_val is int for slider.range."""
        max_val = int(max_val)
        self.slider_amount.value_range = (0, max_val)
        self.slider_amount.set_current_value(max_val)  # Default to all
        self.lbl_amount.set_text(str(max_val))

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        confirm_hint = self._mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
        if confirm_hint:
            self.btn_confirm.set_tooltip(f"Issue Order ({confirm_hint})")
        cancel_hint = self._mapper.get_display_text(InputAction.TRANSFER_CANCEL)
        if cancel_hint:
            self.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper.

        Args:
            event: A pygame KEYDOWN event.

        Returns:
            True if the event was handled.
        """
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["transfer"])
        if action == InputAction.TRANSFER_CONFIRM:
            self._issue_order()
            return True
        if action == InputAction.TRANSFER_CANCEL:
            self.kill()
            return True
        return False

    def process_event(self, event):
        """Handle UI events."""
        super().process_event(event)

        # Keyboard hotkeys via InputMapper
        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return
        
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.drop_source:
                self._on_source_changed(event.text)
            elif event.ui_element == self.drop_target:
                # Update cargo if target changes (since target inventory might change)
                source_label = self._extract_dropdown_value(self.drop_source.selected_option)
                target_label = self._extract_dropdown_value(event.text)
                source = next((s for s in self.available_sources if s['label'] == source_label), None)
                target = next((t for t in self.available_targets if t['label'] == target_label), None)
                if source:
                    self._update_cargo_list(source, target)
            elif event.ui_element == self.drop_item:
                # Find item and update slider
                text_val = self._extract_dropdown_value(event.text)
                item = next((c for c in self.available_cargo if c['label'] == text_val), None)
                if item:
                    self._update_amount_ui(item['max'])
                    
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.slider_amount:
                self.lbl_amount.set_text(str(int(event.value)))
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_cancel:
                self.kill()
            elif event.ui_element == self.btn_confirm:
                self._issue_order()

    def _issue_order(self):
        """Create and dispatch the transfer command."""
        source_label = self._extract_dropdown_value(self.drop_source.selected_option)
        target_label = self._extract_dropdown_value(self.drop_target.selected_option)
        item_label = self._extract_dropdown_value(self.drop_item.selected_option)
        
        source = next((s for s in self.available_sources if s['label'] == source_label), None)
        target = next((t for t in self.available_targets if t['label'] == target_label), None)
        item = next((c for c in self.available_cargo if c['label'] == item_label), None)
        
        if not source or not target or not item:
            log_debug("TransferDialog: Selection incomplete.")
            return
            
        amount = int(self.slider_amount.get_current_value())
        if amount == item['max']:
            amount = 0 # Engine convention: 0 = All
            
        # Determine direction and IDs
        # We check the item's 'direction' which was set in _update_cargo_list
        direction = item.get('direction', 'unload') # Fallback to unload
        
        fleet_id = None
        planet_id = None
        target_fleet_id = None
        
        # Determine IDs based on types
        if source['type'] == 'fleet' and target['type'] in ('colony', 'planet'):
            fleet_id = source['id']
            planet_id = target['id']
            # Direction is handled by item['direction']:
            # If item from source: 'unload' (Fleet -> Planet)
            # If item from target: 'load' (Planet -> Fleet)
        elif source['type'] in ('colony', 'planet') and target['type'] == 'fleet':
            fleet_id = target['id']
            planet_id = source['id']
            # Direction:
            # If item from source: 'load' (Planet -> Fleet)
            # If item from target: 'unload' (Fleet -> Planet) -> Wait, 'unload' for planet source means Planet->Fleet? No.
            # Wait. 'load' means "Move TO Fleet". 'unload' means "Move FROM Fleet".
            # If Source=Planet, Target=Fleet.
            # Primary item (from Planet) direction = 'load'. Correct.
            # Target item (from Fleet) direction = 'unload'. Correct.
        elif source['type'] == 'fleet' and target['type'] == 'fleet':
             # Fleet to Fleet
             # Source=FleetA, Target=FleetB.
             # Primary item (from FleetA): 'unload' (FleetA -> FleetB)
             # Target item (from FleetB): 'load' ?? No, Engine usually only supports 'unload' for inter-fleet?
             # Actually, if FleetA initiates, 'unload' means A->B. 'load' means B->A?
             # Let's hope logic supports it.
             # If direction='unload': fleet_id=source, target_fleet_id=target.
             # If direction='load': fleet_id=source, target_fleet_id=target (Load FROM target TO source).
             fleet_id = source['id']
             target_fleet_id = target['id']
        else:
            log_info(f"Transfer between {source['type']} and {target['type']} not supported.")
            return

        cmd = IssueTransferCommand(
            fleet_id=fleet_id,
            planet_id=planet_id,
            cargo_type=item['type'],
            direction=direction,
            amount=amount,
            species_id=item['species_id'],
            target_fleet_id=target_fleet_id
        )
        
        result = self.facade.handle_command(cmd)
        if result.is_valid:
            log_info(f"TransferDialog: Order issued successfully.")
            self.kill()
        else:
            log_info(f"TransferDialog: Validation failed: {result.message}")
            # Could show a popup error here

    def handle_external_selection(self, obj):
        """Update source/target selection based on an external selection (e.g. from map or list)."""
        from game.core.protocols import is_fleet, is_planet
        
        target_label = None
        if is_fleet(obj):
            target_label = f"Fleet {obj.id}"
        elif is_planet(obj):
            if obj.owner_id is not None:
                target_label = f"Colony: {obj.name}"
            else:
                target_label = f"Planet: {obj.name} (Uncolonized)"
            
        if not target_label:
            return
            
        # If the clicked object is in available_sources/targets, select it
        if target_label in [s['label'] for s in self.available_sources]:
            curr_source = self._extract_dropdown_value(self.drop_source.selected_option)
            
            if curr_source != target_label:
                # Check if it's already source
                # Update target if it matches in target list
                if target_label in [t['label'] for t in self.available_targets]:
                    # Update target dropdown
                    updated_labels = [t['label'] for t in self.available_targets]
                    self.drop_target = self._recreate_dropdown(self.drop_target, updated_labels, target_label)
                else:
                    # If not a target, assume source swap
                    updated_labels = [s['label'] for s in self.available_sources]
                    self.drop_source = self._recreate_dropdown(self.drop_source, updated_labels, target_label)
                    self._on_source_changed(target_label)
        elif target_label in [t['label'] for t in self.available_targets]:
            # Update target directly if it's a valid target
            updated_labels = [t['label'] for t in self.available_targets]
            self.drop_target = self._recreate_dropdown(self.drop_target, updated_labels, target_label)
