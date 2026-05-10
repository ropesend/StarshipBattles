# ComponentState API Sufficiency — Phase 1 Task 1.3

**Date:** 2026-04-16
**Source:** `game/strategy/data/component_state.py`

## Fields on `ComponentState`

```python
@dataclass
class ComponentState:
    component_id: str
    instance_index: int
    current_hp: float
    is_active: bool = True
```

Helpers:
- `component_state_key(component_id, instance_index) -> str` — L23
- `to_dict` / `from_dict` — serialization round-trip

## Plan-required API surface

| Required | Present? | Notes |
|---|---|---|
| `current_hp: int` (or float) | ✅ | `float`, int coerced |
| `is_destroyed: bool` | derivable | `current_hp <= 0` |
| `is_operational: bool` | derivable | `is_active and current_hp > 0` |
| keyed access via `component_state_key` | ✅ | helper exported |

## Gaps

**None blocking.** All reads currently made via the legacy
`component_damage.get(comp_id)` can be restated as
`components[component_state_key(comp_id, idx)].current_hp` with a
fallback to `max_hp` when the key is missing.

The `_lookup_damage` fuzzy fallback in `ship_design_stats.py:103-114`
(which accepts `comp_id_0` suffixed keys) is **not** needed once the
migration is done — the canonical key format is always
`{comp_id}#{instance_index}`.

## Threshold / effectiveness logic lives in:

- `ship_stats_calculator.py::get_component_effectiveness` (DEAD)
- `ship_design_stats.py` relies on `ship.recalculate_stats()` which
  applies its own effectiveness via the simulation layer. That path
  reads each component's `current_hp` directly off the simulation-layer
  `Component`, not off a Dict. So the migration in Phase 2 only needs
  to push per-instance HP INTO the simulation Ship, not implement
  effectiveness.

**Verdict:** No Phase 1.5 extension needed. Proceed to Phase 2 as
planned — but see [Dead Module Finding](component_damage_callsite_audit.md#dead-module-finding)
before starting.
