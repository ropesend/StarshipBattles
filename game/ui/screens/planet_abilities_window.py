"""Planet Abilities Window — List and toggle all activatable abilities on a planet.

Shows each toggleable ability with its current status and a toggle button.
Status displays: Active, Inactive, Activating (ticks), Deactivating (ticks).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Any
import logging

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel

from game.core.patterns.layer_iterator import iter_keyed_components
from game.strategy.data.component_activation_state import ActivationPhase

logger = logging.getLogger(__name__)

# Abilities that can be toggled (have activation_time and deactivation_time)
TOGGLEABLE_ABILITIES = {
    'PlanetaryShield': 'Planetary Shield',
    'GeologicStabilizer': 'Geologic Stabilizer',
    'StellarStabilizer': 'Stellar Stabilizer',
    'WarpFieldStabilizer': 'Warp Field Stabilizer',
}


class PlanetAbilitiesWindow(UIWindow):
    """Window listing all toggleable abilities on a planet with toggle buttons."""

    ROW_HEIGHT = 36

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet,
        facade,
        component_registry=None,
    ):
        super().__init__(
            relative_rect,
            manager,
            window_display_title=f"Abilities: {planet.name}",
            resizable=False,
        )
        self.planet = planet
        self.facade = facade
        self.component_registry = component_registry
        self._toggle_buttons: Dict[str, UIButton] = {}
        self._status_labels: Dict[str, UILabel] = {}
        self._widgets = []
        self._build_ui()

    def _build_ui(self):
        """Build ability rows — one per activatable component instance."""
        container = self.get_container()
        y = 10

        # Scan planet facilities for toggleable abilities (per-component granularity)
        abilities_found = self._scan_abilities()

        if not abilities_found:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 350, 30),
                text="No toggleable abilities on this planet.",
                manager=self.ui_manager,
                container=container,
            )
            self._widgets.append(lbl)
            return

        for entry in abilities_found:
            ability_name = entry['ability_name']
            display_name = entry['display_name']
            facility_id = entry['facility_id']
            facility_name = entry['facility_name']
            component_key = entry['component_key']
            instance_label = entry['instance_label']
            row_key = f"{facility_id}:{component_key}"

            # Ability name + facility + instance number
            name_text = f"{display_name} ({facility_name}{instance_label})"
            name_lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 290, self.ROW_HEIGHT),
                text=name_text,
                manager=self.ui_manager,
                container=container,
            )
            self._widgets.append(name_lbl)

            # Status from component_state (source of truth)
            status = self._get_component_status(facility_id, component_key)
            status_lbl = UILabel(
                relative_rect=pygame.Rect(305, y, 110, self.ROW_HEIGHT),
                text=status,
                manager=self.ui_manager,
                container=container,
            )
            self._widgets.append(status_lbl)
            self._status_labels[row_key] = status_lbl

            # Determine active state from component_state
            facility = next((f for f in self.planet.facilities if f.instance_id == facility_id), None)
            is_active = False
            if facility:
                state = facility.get_activation_state(component_key)
                is_active = state.phase in (ActivationPhase.ACTIVE, ActivationPhase.ACTIVATING)

            btn_text = "Deactivate" if is_active else "Activate"
            btn = UIButton(
                relative_rect=pygame.Rect(420, y + 2, 90, self.ROW_HEIGHT - 4),
                text=btn_text,
                manager=self.ui_manager,
                container=container,
            )
            btn._ability_name = ability_name
            btn._facility_id = facility_id
            btn._component_key = component_key
            btn._is_active = is_active
            self._widgets.append(btn)
            self._toggle_buttons[row_key] = btn

            y += self.ROW_HEIGHT

    def _scan_abilities(self) -> List[Dict]:
        """Scan planet facilities for toggleable abilities at per-component granularity.

        Returns list of dicts with keys: ability_name, display_name, facility_id,
        facility_name, component_key, instance_label.

        Each activatable component gets its own entry — no deduplication by ability name.
        When multiple instances of the same ability exist, they get numbered labels
        (e.g., " #1", " #2").
        """
        from game.strategy.services.component_inspector import extract_abilities_from_component

        raw_entries = []
        for facility in self.planet.facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            for comp_key, layer_name, comp in iter_keyed_components(facility.design_data):
                abilities = extract_abilities_from_component(comp, self.component_registry)
                for ability_name, display_name in TOGGLEABLE_ABILITIES.items():
                    if ability_name in abilities:
                        ability_data = abilities[ability_name]
                        if isinstance(ability_data, dict) and 'activation_time' in ability_data:
                            raw_entries.append({
                                'ability_name': ability_name,
                                'display_name': display_name,
                                'facility_id': facility.instance_id,
                                'facility_name': facility.name,
                                'component_key': comp_key,
                            })

        # Add instance labels when multiple entries share the same ability_name
        ability_counts: Dict[str, int] = {}
        for entry in raw_entries:
            name = entry['ability_name']
            ability_counts[name] = ability_counts.get(name, 0) + 1

        ability_indices: Dict[str, int] = {}
        for entry in raw_entries:
            name = entry['ability_name']
            if ability_counts[name] > 1:
                idx = ability_indices.get(name, 0) + 1
                ability_indices[name] = idx
                entry['instance_label'] = f" #{idx}"
            else:
                entry['instance_label'] = ""

        return raw_entries

    def _get_component_status(self, facility_id: str, component_key: str) -> str:
        """Get display status for a specific component's activation state."""
        facility = next((f for f in self.planet.facilities if f.instance_id == facility_id), None)
        if not facility:
            return "Unknown"

        state = facility.get_activation_state(component_key)

        if state.phase == ActivationPhase.ACTIVATING:
            remaining = state.required_ticks - state.progress_ticks
            return f"Activating ({remaining})"
        elif state.phase == ActivationPhase.DEACTIVATING:
            remaining = state.required_ticks - state.progress_ticks
            return f"Deactivating ({remaining})"
        elif state.phase == ActivationPhase.ACTIVE:
            return "Active"
        return "Inactive"

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle button clicks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ability_name = getattr(event.ui_element, '_ability_name', None)
            facility_id = getattr(event.ui_element, '_facility_id', None)
            component_key = getattr(event.ui_element, '_component_key', None)
            is_active = getattr(event.ui_element, '_is_active', None)

            if ability_name and facility_id is not None and component_key:
                order_type = "DEACTIVATE_ABILITY" if is_active else "ACTIVATE_ABILITY"

                from game.strategy.engine.commands import IssuePlanetOrderCommand
                cmd = IssuePlanetOrderCommand(
                    planet_id=self.planet.id,
                    order_type=order_type,
                    facility_instance_id=facility_id,
                    ability_name=ability_name,
                    component_key=component_key,
                )
                result = self.facade.handle_command(cmd)
                if result and not result.is_valid:
                    logger.warning(f"Ability toggle failed: {result.message}")
                else:
                    # Update button state
                    new_active = not is_active
                    event.ui_element._is_active = new_active
                    event.ui_element.set_text("Deactivate" if new_active else "Activate")
                    # Update status label
                    row_key = f"{facility_id}:{component_key}"
                    if row_key in self._status_labels:
                        self._status_labels[row_key].set_text(
                            self._get_component_status(facility_id, component_key)
                        )
                return True

        return super().process_event(event)
