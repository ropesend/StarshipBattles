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

from game.core.patterns.layer_iterator import iter_components
from game.strategy.data.order_types import OrderType

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
        """Build ability rows."""
        container = self.get_container()
        y = 10

        # Scan planet facilities for toggleable abilities
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

        for ability_name, display_name, facility_id, facility_name in abilities_found:
            # Ability name + facility
            name_text = f"{display_name} ({facility_name})"
            name_lbl = UILabel(
                relative_rect=pygame.Rect(10, y, 250, self.ROW_HEIGHT),
                text=name_text,
                manager=self.ui_manager,
                container=container,
            )
            self._widgets.append(name_lbl)

            # Status label
            status = self._get_ability_status(ability_name)
            status_lbl = UILabel(
                relative_rect=pygame.Rect(265, y, 150, self.ROW_HEIGHT),
                text=status,
                manager=self.ui_manager,
                container=container,
            )
            self._widgets.append(status_lbl)
            self._status_labels[ability_name] = status_lbl

            # Toggle button
            active_abilities = getattr(self.planet, 'active_abilities', {})
            is_active = active_abilities.get(ability_name, False)

            btn_text = "Deactivate" if is_active else "Activate"
            btn = UIButton(
                relative_rect=pygame.Rect(420, y + 2, 90, self.ROW_HEIGHT - 4),
                text=btn_text,
                manager=self.ui_manager,
                container=container,
            )
            btn._ability_name = ability_name
            btn._facility_id = facility_id
            btn._is_active = is_active
            self._widgets.append(btn)
            self._toggle_buttons[ability_name] = btn

            y += self.ROW_HEIGHT

    def _scan_abilities(self) -> List[tuple]:
        """Scan planet facilities for toggleable abilities.

        Returns list of (ability_name, display_name, facility_id, facility_name).
        """
        from game.strategy.services.component_inspector import extract_abilities_from_component

        results = []
        for facility in self.planet.facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            for comp in iter_components(facility.design_data):
                abilities = extract_abilities_from_component(comp, self.component_registry)
                for ability_name, display_name in TOGGLEABLE_ABILITIES.items():
                    if ability_name in abilities:
                        ability_data = abilities[ability_name]
                        # Must have activation_time to be toggleable
                        if isinstance(ability_data, dict) and 'activation_time' in ability_data:
                            # Avoid duplicates
                            if not any(r[0] == ability_name for r in results):
                                results.append((
                                    ability_name,
                                    display_name,
                                    facility.instance_id,
                                    facility.name,
                                ))
        return results

    def _get_ability_status(self, ability_name: str) -> str:
        """Get display status for an ability including tick progress."""
        active_abilities = getattr(self.planet, 'active_abilities', {})
        is_active = active_abilities.get(ability_name, False)

        # Check for pending activation/deactivation orders
        for order in self.planet.orders:
            target = order.target if isinstance(order.target, dict) else {}
            order_ability = target.get('ability_name', '')

            # Generic ability orders
            if order.type == OrderType.ACTIVATE_ABILITY and order_ability == ability_name:
                progress = order.execution_progress
                return f"Activating ({progress} ticks)"
            if order.type == OrderType.DEACTIVATE_ABILITY and order_ability == ability_name:
                progress = order.execution_progress
                return f"Deactivating ({progress} ticks)"

        return "Active" if is_active else "Inactive"

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle button clicks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ability_name = getattr(event.ui_element, '_ability_name', None)
            facility_id = getattr(event.ui_element, '_facility_id', None)
            is_active = getattr(event.ui_element, '_is_active', None)

            if ability_name and facility_id is not None:
                order_type = "DEACTIVATE_ABILITY" if is_active else "ACTIVATE_ABILITY"

                from game.strategy.engine.commands import IssuePlanetOrderCommand
                cmd = IssuePlanetOrderCommand(
                    planet_id=self.planet.id,
                    order_type=order_type,
                    facility_instance_id=facility_id,
                    ability_name=ability_name,
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
                    if ability_name in self._status_labels:
                        self._status_labels[ability_name].set_text(
                            self._get_ability_status(ability_name)
                        )
                return True

        return super().process_event(event)
