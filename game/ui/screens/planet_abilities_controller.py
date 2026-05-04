"""Controller for PlanetAbilitiesWindow (PROJ-329C Phase 1).

Owns the facade-side queries that PlanetAbilitiesWindow used to call
inline during ``_build_ui``: scanning a planet's facilities for
toggleable abilities, deciding which environment editors are available,
formatting per-component status strings, and dispatching
``IssuePlanetOrderCommand`` when a toggle button is clicked.

The controller does NOT touch ``pygame_gui`` widgets. Widget construction
lives in ``PlanetAbilitiesUiBuilder`` (in the screen module). The
controller is constructed in Stage 1 of the screen ``__init__`` (cheap;
no facade I/O), and its query methods are called from the builder during
Stage 3.

Pattern reference: PROJ-328 Phase C ``transfer_controller.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from game.core.patterns.layer_iterator import iter_keyed_components
from game.strategy.data.component_activation_state import ActivationPhase
from game.strategy.engine.commands import IssuePlanetOrderCommand

if TYPE_CHECKING:
    pass


# Abilities that can be toggled (have activation_time and deactivation_time)
TOGGLEABLE_ABILITIES = {
    'PlanetaryShield': 'Planetary Shield',
    'GeologicStabilizer': 'Geologic Stabilizer',
    'StellarStabilizer': 'Stellar Stabilizer',
    'WarpFieldStabilizer': 'Warp Field Stabilizer',
    'GravityModifier': 'Gravity Modifier',
    'RadiationShield': 'Radiation Shield',
    'ShieldModifier': 'Shield Modifier',
    'DamageModifier': 'Damage Modifier',
    'ShieldProjection': 'Shield Projector',
}

# Environment editor buttons — shown when planet has the corresponding ability
ENVIRONMENT_EDITORS = [
    ('AtmosphereModifier', 'Atmosphere'),
    ('GravityModifier', 'Gravity'),
    ('WaterModifier', 'Water'),
    ('RadiationShield', 'Radiation'),
]

# Food allocation (PROJ-284 Phase 4) — shown on any colony with populations.
FOOD_EDITOR_LABEL = 'Food'
FOOD_EDITOR_TYPE = 'food'


class PlanetAbilitiesController:
    """Facade-coupled queries + command dispatch for PlanetAbilitiesWindow.

    All facade I/O for the window flows through this controller. The
    builder calls ``scan_abilities`` / ``get_available_editors`` /
    ``should_show_food_editor`` to assemble row data for widget
    construction; ``get_component_status`` powers status-label refresh;
    ``toggle_ability`` issues commands when a toggle button is pressed.
    """

    def __init__(self, planet, facade, component_registry=None) -> None:
        self.planet = planet
        self.facade = facade
        self.component_registry = component_registry

    # ---- Read queries (called by the UI builder) ----

    def should_show_food_editor(self) -> bool:
        """PROJ-284 Phase 4: show the Food button on any colony that
        has at least one population."""
        populations = getattr(self.planet, 'populations', None) or []
        return len(populations) > 0

    def get_available_editors(self) -> List[tuple]:
        """Return list of (ability_key, label) for editors where the
        planet has the facility."""
        from game.strategy.services.component_inspector import (
            extract_abilities_from_component,
        )
        from game.core.patterns.layer_iterator import iter_components

        present_abilities = set()
        for facility in getattr(self.planet, 'facilities', []):
            if not getattr(facility, 'is_operational', True):
                continue
            for comp in iter_components(facility.design_data):
                abilities = extract_abilities_from_component(
                    comp, self.component_registry
                )
                present_abilities.update(abilities.keys())

        return [
            (key, label) for key, label in ENVIRONMENT_EDITORS
            if key in present_abilities
        ]

    def scan_abilities(self) -> List[Dict]:
        """Scan planet facilities for toggleable abilities at per-component
        granularity."""
        from game.strategy.services.component_inspector import (
            extract_abilities_from_component,
        )

        raw_entries: List[Dict[str, Any]] = []
        for facility in self.planet.facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            for comp_key, layer_name, comp in iter_keyed_components(
                facility.design_data
            ):
                abilities = extract_abilities_from_component(
                    comp, self.component_registry
                )
                for ability_name, display_name in TOGGLEABLE_ABILITIES.items():
                    if ability_name in abilities:
                        ability_data = abilities[ability_name]
                        if (
                            isinstance(ability_data, dict)
                            and 'activation_time' in ability_data
                        ):
                            raw_entries.append({
                                'ability_name': ability_name,
                                'display_name': display_name,
                                'facility_id': facility.instance_id,
                                'facility_name': facility.name,
                                'component_key': comp_key,
                            })

        # Add instance labels when multiple entries share the same
        # ability_name.
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

    def get_component_status(self, facility_id: str, component_key: str) -> str:
        """Get display status for a specific component's activation state."""
        facility = next(
            (
                f for f in self.planet.facilities
                if f.instance_id == facility_id
            ),
            None,
        )
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

    def is_component_active(self, facility_id: str, component_key: str) -> bool:
        """True iff the component is currently ACTIVE or ACTIVATING."""
        facility = next(
            (
                f for f in self.planet.facilities
                if f.instance_id == facility_id
            ),
            None,
        )
        if facility is None:
            return False
        state = facility.get_activation_state(component_key)
        return state.phase in (ActivationPhase.ACTIVE, ActivationPhase.ACTIVATING)

    # ---- Command emission ----

    def toggle_ability(
        self,
        facility_id: str,
        component_key: str,
        ability_name: str,
        is_active: bool,
    ) -> Optional[Any]:
        """Dispatch an activate/deactivate command. Returns the result."""
        order_type = "DEACTIVATE_ABILITY" if is_active else "ACTIVATE_ABILITY"
        cmd = IssuePlanetOrderCommand(
            planet_id=self.planet.id,
            order_type=order_type,
            facility_instance_id=facility_id,
            ability_name=ability_name,
            component_key=component_key,
        )
        return self.facade.handle_command(cmd)


__all__ = [
    "PlanetAbilitiesController",
    "TOGGLEABLE_ABILITIES",
    "ENVIRONMENT_EDITORS",
    "FOOD_EDITOR_LABEL",
    "FOOD_EDITOR_TYPE",
]
