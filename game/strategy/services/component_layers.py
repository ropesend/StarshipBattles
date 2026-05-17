"""Per-instance layer-view helpers for ``ShipInstance``.

PROJ-433: extracted from ``component_inspector.py``. These helpers were
added by PROJ-425 Phase 2 (TD-06) and join a ship design's layer entries
with the per-instance ``ComponentState`` map to produce instance-level
views (current HP, damage status, layer grouping). They are the second
half of the ``component_inspector`` split — the ability-iteration helpers
live in ``game.strategy.services.component_abilities``.

``lookup_design_max_hp`` ships here because its only consumer is
``iter_components_by_layer`` (PROJ-433 Phase 0 grep). Keeping it next to
its caller avoids cross-module coupling between the two new modules.

The legacy ``game.strategy.services.component_inspector`` module is now a
thin re-export shim that re-exports both new modules' public surfaces.
"""
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.component_state import ComponentInstanceView, component_state_key


if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


__all__ = [
    "iter_components_by_layer",
    "damaged_components_by_layer",
    "count_damaged_components",
    "lookup_design_max_hp",
]


def lookup_design_max_hp(
    ship: 'ShipInstance', comp_id: str
) -> Optional[int]:
    """Look up a component's design max HP from available registries.

    PROJ-425 Phase 2: extracted from ``ShipInstance._lookup_design_max_hp``.

    Returns None when the registry is unavailable, the component is
    unknown, or the registry stores a formula instead of a concrete
    numeric value. This is only a legacy/missing-state fallback; normal
    ship creation persists computed per-instance ``ComponentState.max_hp``.
    """
    components = None
    if ship._registries is not None:
        components = ship._registries.get_components()
    else:
        try:
            from game.core.registry import get_default_registry_provider
            components = get_default_registry_provider().get_components()
        except Exception:  # Intentional broad catch: registry may be absent in legacy save context
            return None

    comp = components.get(comp_id)
    if comp is None:
        return None
    if isinstance(comp, dict):
        raw = comp.get('max_hp', comp.get('hp'))
    else:
        raw = getattr(comp, 'max_hp', None) or getattr(comp, 'hp', None)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def iter_components_by_layer(
    ship: 'ShipInstance',
) -> Dict[str, List[ComponentInstanceView]]:
    """Return every component on a ship grouped by layer.

    PROJ-425 Phase 2: extracted from ``ShipInstance.iter_all_components_by_layer``.

    Walks ``ship.design_data['layers']`` in source order; joins each entry
    with ``ship.components`` via ``component_state_key(component_id,
    instance_index)``. When the key is missing, looks up max HP from the
    component registry and emits a full-HP active view. If the registry
    is unavailable or the component is unknown, the instance is skipped.

    The HULL layer is filtered out — the Fleet Report panel does not
    display it. Other unrecognised layer names pass through.
    """
    result: Dict[str, List[ComponentInstanceView]] = {}
    per_id_index: Dict[str, int] = {}
    for layer_name, components in ship.design_data.get('layers', {}).items():
        if layer_name == 'HULL':
            continue
        views: List[ComponentInstanceView] = []
        for entry in components:
            comp_id = entry.get('id') if isinstance(entry, dict) else entry
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            key = component_state_key(comp_id, idx)
            state = ship.components.get(key)
            if state is not None:
                max_hp = int(state.max_hp)
                current_hp = int(state.current_hp)
                is_active = bool(state.is_active)
            else:
                fallback_max_hp = lookup_design_max_hp(ship, comp_id)
                if fallback_max_hp is None:
                    continue
                max_hp = fallback_max_hp
                current_hp = fallback_max_hp
                is_active = True
            views.append(
                ComponentInstanceView(
                    component_id=comp_id,
                    instance_index=idx,
                    current_hp=current_hp,
                    max_hp=max_hp,
                    is_active=is_active,
                )
            )
        result[layer_name] = views
    return result


def damaged_components_by_layer(
    ship: 'ShipInstance',
) -> Dict[str, List[Tuple[str, int]]]:
    """Return damaged component instances grouped by layer.

    PROJ-425 Phase 2: extracted from ``ShipInstance.get_damaged_components_by_layer``.

    Walks the design's layers to map each ``component_id`` to its layer,
    then iterates per-instance ``ship.components`` picking out the ones
    whose ``current_hp`` is below ``max_hp``.

    Returns a dict mapping layer name to a list of
    ``(component_state_key, current_hp)`` tuples for each damaged instance.
    """
    damaged_states = [
        (key, cs) for key, cs in ship.components.items() if cs.is_damaged
    ]
    if not damaged_states:
        return {}

    comp_id_to_layer: Dict[str, str] = {}
    for layer_name, components in ship.design_data.get('layers', {}).items():
        for comp_entry in components:
            comp_id = (
                comp_entry.get('id') if isinstance(comp_entry, dict)
                else comp_entry
            )
            if comp_id:
                comp_id_to_layer[comp_id] = layer_name

    result: Dict[str, List[Tuple[str, int]]] = {}
    for key, cs in damaged_states:
        layer_name = comp_id_to_layer.get(cs.component_id, 'UNKNOWN')
        result.setdefault(layer_name, []).append((key, int(cs.current_hp)))

    return result


def count_damaged_components(ship: 'ShipInstance') -> int:
    """Count damaged component instances on a ship.

    PROJ-425 Phase 2: extracted from ``ShipInstance.get_damaged_component_count``.
    """
    return sum(1 for cs in ship.components.values() if cs.is_damaged)
