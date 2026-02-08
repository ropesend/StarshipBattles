from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel, UIDropDownMenu, UIHorizontalSlider
from game.core.input_actions import InputAction
from game.core.logger import log_debug, log_info
from game.strategy.engine.commands import IssueTransferCommand

if TYPE_CHECKING:
    from game.core.input_mapper import InputMapper

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
        
        # --- Source ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Source:", self.ui_manager, container=self)
        self.drop_source = UIDropDownMenu(
            options_list=[],
            starting_option="",
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 150, element_h),
            manager=self.ui_manager,
            container=self
        )
        curr_y += element_h + padding
        
        # --- Target ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Target:", self.ui_manager, container=self)
        self.drop_target = UIDropDownMenu(
            options_list=[],
            starting_option="",
            relative_rect=pygame.Rect(110, curr_y, self.rect.width - 150, element_h),
            manager=self.ui_manager,
            container=self
        )
        curr_y += element_h + padding
        
        # --- Item/Cargo ---
        UILabel(pygame.Rect(padding, curr_y, 100, label_h), "Item:", self.ui_manager, container=self)
        self.drop_item = UIDropDownMenu(
            options_list=[],
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
        
        # Filter for colonized planets
        colonies = [p for p in planets if p.owner_id is not None]
        
        # 2. Build options
        self.available_sources = []
        for f in fleets:
            self.available_sources.append({'label': f"Fleet {f.id}", 'type': 'fleet', 'id': f.id})
        for c in colonies:
            self.available_sources.append({'label': f"Colony: {c.name}", 'type': 'colony', 'id': c.planet_id})
            
        source_labels = [s['label'] for s in self.available_sources]
        
        # Default select source_fleet if possible
        starting_option = ""
        for s in self.available_sources:
            if s['type'] == 'fleet' and s['id'] == self.source_fleet.id:
                starting_option = s['label']
                break
        
        self.drop_source = self._recreate_dropdown(self.drop_source, source_labels, starting_option)
        if starting_option:
            self._on_source_changed(starting_option)

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

    def _on_source_changed(self, label):
        """Update targets and cargo when source changes."""
        source = next((s for s in self.available_sources if s['label'] == label), None)
        if not source: return
        
        # 1. Populate Targets (all objects at hex except source)
        self.available_targets = [s for s in self.available_sources if s['label'] != label]
        target_labels = [t['label'] for t in self.available_targets]
        self.drop_target = self._recreate_dropdown(self.drop_target, target_labels, 
                                                  target_labels[0] if target_labels else "")
            
        # 2. Populate Cargo
        self._update_cargo_list(source)

    def _update_cargo_list(self, source):
        """Populate drop_item based on source content."""
        self.available_cargo = []
        
        if source['type'] == 'fleet':
            fleet_info = self.facade.get_fleet(source['id'])
            if not fleet_info: return
            
            passengers = getattr(fleet_info, 'passengers_current', 0)
            if passengers > 0:
                self.available_cargo.append({
                    'label': f"Passengers ({passengers})",
                    'type': 'passengers',
                    'species_id': None,
                    'max': passengers
                })
        elif source['type'] == 'colony':
            planet_info = self.facade.get_planet(source['id'])
            if not planet_info: return
            
            # population_details is a tuple of (race_id, count, happiness)
            if hasattr(planet_info, 'population_details'):
                for race_id, count, happiness in planet_info.population_details:
                    if count > 0:
                        self.available_cargo.append({
                            'label': f"Population: {race_id} ({count})",
                            'type': 'passengers',
                            'species_id': race_id,
                            'max': count
                        })
            else:
                passengers = getattr(planet_info, 'total_population', 0)
                if passengers > 0:
                    self.available_cargo.append({
                        'label': f"Population ({passengers})",
                        'type': 'passengers',
                        'species_id': None,
                        'max': passengers
                    })
                    
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
        self.slider_amount.set_current_value(max_val) # Default to all
        self.slider_amount.value_range = (0, max_val)
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
            elif event.ui_element == self.drop_item:
                # Find item and update slider
                item = next((c for c in self.available_cargo if c['label'] == event.text), None)
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
        source = next((s for s in self.available_sources if s['label'] == self.drop_source.selected_option), None)
        target = next((t for t in self.available_targets if t['label'] == self.drop_target.selected_option), None)
        item = next((c for c in self.available_cargo if c['label'] == self.drop_item.selected_option), None)
        
        if not source or not target or not item:
            log_debug("TransferDialog: Selection incomplete.")
            return
            
        amount = int(self.slider_amount.get_current_value())
        if amount == item['max']:
            amount = 0 # Engine convention: 0 = All
            
        # Determine direction and IDs
        # We always issue the order to the FLEET involved.
        fleet_id = None
        planet_id = None
        direction = None
        
        if source['type'] == 'fleet' and target['type'] == 'colony':
            fleet_id = source['id']
            planet_id = target['id']
            direction = 'unload'
        elif source['type'] == 'colony' and target['type'] == 'fleet':
            fleet_id = target['id']
            planet_id = source['id']
            direction = 'load'
        else:
            # Fleet-to-Fleet not supported yet (or same type)
            log_info(f"Transfer between {source['type']} and {target['type']} not supported.")
            return

        cmd = IssueTransferCommand(
            fleet_id=fleet_id,
            planet_id=planet_id,
            cargo_type=item['type'],
            direction=direction,
            amount=amount,
            species_id=item['species_id']
        )
        
        result = self.facade.handle_command(cmd)
        if result.is_valid:
            log_info(f"TransferDialog: Order issued successfully.")
            self.kill()
        else:
            log_info(f"TransferDialog: Validation failed: {result.message}")
            # Could show a popup error here
