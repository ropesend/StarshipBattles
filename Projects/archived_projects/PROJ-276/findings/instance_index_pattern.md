# `instance_index` Access Pattern — Phase 1 Task 1.4

**Date:** 2026-04-16

## The per-`component_id` counter pattern

`instance_index` is defined as the **zero-based occurrence index of the
component within the ship, counted per `component_id`** (not per
layer, not globally). Three seeker missile components produce indices
0, 1, 2 — even if they're split across layers.

## Canonical implementations (already in the codebase)

### 1. `ship_instance.py::_build_full_hp_components_from_design` (L72-88)

```python
components: Dict[str, ComponentState] = {}
per_id_index: Dict[str, int] = {}
for _layer_type, layer_data in ship.layers.items():
    for comp in getattr(layer_data, "components", []):
        comp_id = getattr(comp, "id", None)
        if not comp_id:
            continue
        idx = per_id_index.get(comp_id, 0)
        per_id_index[comp_id] = idx + 1
        key = component_state_key(comp_id, idx)
        components[key] = ComponentState(...)
```

### 2. `ship_instance_bridge.py::to_ship` (L91-103)

```python
per_id_index: Dict[str, int] = {}
for layer_data in ship.layers.values():
    for comp in layer_data.components:
        idx = per_id_index.get(comp.id, 0)
        per_id_index[comp.id] = idx + 1
        key = component_state_key(comp.id, idx)
        cs = self._ship.components.get(key)
        ...
```

### 3. `ship_instance_bridge.py::update_from_ship` (L150-167)

Same per-id counter loop, but rebuilds from post-battle Ship.

### 4. `post_battle_hook.py::_apply_survivor_outcome` (L142-152)

Uses `instance_index` from `BattleOutcome.components` directly — the
engine supplies the index in the outcome payload.

## What this means for Phase 2 (`ship_design_stats.py` migration)

The production read path is:

```python
# ship_design_stats.py:58-62 (current)
if component_damage:
    for layer_type, comp in ship.iter_components():
        hp = _lookup_damage(comp.id, comp.max_hp, component_damage)
        if hp < comp.max_hp:
            comp.current_hp = hp
```

Post-migration signature changes from `component_damage: Dict[str,
int]` to `components: Dict[str, ComponentState]` (with the `{id}#{idx}`
keys). The loop becomes:

```python
if components:
    per_id_index: Dict[str, int] = {}
    for layer_type, comp in ship.iter_components():
        idx = per_id_index.get(comp.id, 0)
        per_id_index[comp.id] = idx + 1
        cs = components.get(component_state_key(comp.id, idx))
        if cs and cs.current_hp < comp.max_hp:
            comp.current_hp = cs.current_hp
```

This is a one-site migration — no helper needed, the pattern is
small and clear enough to inline at the three call sites that need it.

## No helper proposal

The per-id counter is a four-line pattern and appears in exactly four
places post-migration (three of which already exist). Not worth a
helper method. If it grows beyond that, the natural home would be a
classmethod on `ComponentState` like
`ComponentState.iter_from_ship(ship) -> Iterator[Tuple[str, Component, int]]`
— but not yet.
