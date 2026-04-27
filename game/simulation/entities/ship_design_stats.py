"""
Ship Design Stats — Single source of truth for computing stats from design JSON.

Replaces the strategy layer's ShipStatsCalculator by using Ship.from_dict()
+ recalculate_stats(), ensuring one code path for all stat calculations.

Returns a dict matching the interface contract that ShipInstance.get_calculated_stats()
callers expect.
"""
from typing import Any, Dict, Optional, TYPE_CHECKING

from game.core.registry import GameRegistries
from game.simulation.entities.ship import Ship
from game.core.component_state import component_state_key

if TYPE_CHECKING:
    from game.core.component_state import ComponentState


def calculate_design_stats(
    design_data: Dict[str, Any],
    registries: GameRegistries,
    components: Optional[Dict[str, "ComponentState"]] = None,
    component_toggles: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    """Calculate ship stats from design JSON using the simulation Ship.

    This is the canonical way to compute stats from a design dict.
    Uses Ship.from_dict() + recalculate_stats() so all stat calculations
    go through the single simulation code path.

    Args:
        design_data: Serialized ship design with 'layers', 'ship_class', etc.
        registries: GameRegistries with components, modifiers, vehicle_classes.
        components: Optional dict of `ComponentState` keyed by
            `component_state_key(component_id, instance_index)`. When
            provided, each per-instance `current_hp` is applied to the
            matching Ship component before recalculation. Components
            with no entry start at full HP.
        component_toggles: Optional dict of component_id -> enabled.
            If provided, components can be toggled off before recalculation.

    Returns:
        Dict with keys: max_hp, mass, resource_storage, cargo_storage,
        pod_storage_mass, strategic_movement, warp_max_tonnage,
        warp_resource_costs.
    """
    # Apply toggles by filtering the design data before Ship creation
    effective_design = design_data
    if component_toggles:
        import copy
        effective_design = copy.deepcopy(design_data)
        for layer_name, comps in effective_design.get('layers', {}).items():
            if isinstance(comps, list):
                effective_design['layers'][layer_name] = [
                    c for c in comps
                    if component_toggles.get(c.get('id', ''), True)
                ]

    # PROJ-254: No fallback to expected_stats — let errors propagate.
    # If Ship.from_dict() fails, that's a real error (invalid design data).
    ship = Ship.from_dict(effective_design, registries=registries)

    # Apply per-instance damage: iterate components by per-id occurrence
    # index so identical components are disambiguated.
    if components:
        per_id_index: Dict[str, int] = {}
        for _layer_type, comp in ship.iter_components():
            idx = per_id_index.get(comp.id, 0)
            per_id_index[comp.id] = idx + 1
            cs = components.get(component_state_key(comp.id, idx))
            if cs is not None and cs.current_hp < comp.max_hp:
                comp.current_hp = cs.current_hp

    ship.recalculate_stats()

    # Build resource_storage dict from Ship's ResourceRegistry
    resource_storage = {}
    for name in ship.resources.get_resource_names():
        max_val = ship.resources.get_max_value(name)
        if max_val > 0:
            resource_storage[name] = max_val

    # Build consumption dicts from component abilities
    from game.simulation.interfaces import is_resource_consumption
    per_hex: Dict[str, float] = {}
    per_turn: Dict[str, float] = {}
    for _lt, comp in ship.iter_components():
        if not comp.is_active:
            continue
        for ab in comp.ability_instances:
            if is_resource_consumption(ab):
                trigger = getattr(ab, 'trigger', 'constant')
                rt = ab.resource_type
                if trigger == 'strategic_per_hex' and rt:
                    per_hex[rt] = per_hex.get(rt, 0) + ab.amount
                elif trigger == 'per_turn' and rt:
                    per_turn[rt] = per_turn.get(rt, 0) + ab.amount

    return {
        'max_hp': ship.max_hp,
        'mass': ship.mass,
        'resource_storage': resource_storage,
        'cargo_storage': dict(ship.cargo_storage),
        'pod_storage_mass': ship.pod_storage_mass,
        'strategic_movement': ship.total_strategic_movement,
        'warp_max_tonnage': ship.warp_max_tonnage,
        'warp_resource_costs': dict(ship.warp_resource_costs),
        'resource_consumption_per_hex': per_hex,
        'resource_consumption_per_turn': per_turn,
    }
