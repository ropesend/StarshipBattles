# PROJ-433: component_inspector split — design

## Source

PROJ-425 Codex consult on shipped TD-06 work (2026-05-17). Codex reviewed the ShipInstance slimming completion and identified three follow-ups. Finding 2 was the `component_inspector.py` LOC overrun: 537 LOC after PROJ-425 Phase 2 added the per-instance layer-view helpers — above the 500-LOC convention. Codex explicitly recommended a separate small project rather than reopening PROJ-425, so this project is spun out.

PROJ-425's own findings_ledger flagged the split as deferred at the time:

> [Projects/active_projects/PROJ-425/findings_ledger.md, §"Phase 2"]
>
> `component_inspector.py` LOC: 537 (was 391; +146). Above the 500-LOC guideline but already-shared infrastructure module — split deferred as the additions are cohesive ship-introspection helpers; revisit if it grows further.

Codex's consult is the "revisit" trigger.

## Finding

`game/strategy/services/component_inspector.py` exposes 15 public helpers via `__all__`:

```python
# game/strategy/services/component_inspector.py:18-35

__all__ = [
    "get_component_abilities",
    "extract_abilities_from_component",
    "get_component_type",
    "get_component_threshold",
    "iterate_design_components",
    "iter_facility_ability_entries",
    "ship_has_ability",
    "find_ship_with_ability",
    "count_ability",
    "list_ship_abilities",
    "get_ability_list",
    "has_warp_capability",
    "iter_components_by_layer",
    "damaged_components_by_layer",
    "count_damaged_components",
    "lookup_design_max_hp",
]
```

(15 names listed plus `extract_abilities_from_component` brings the module to 16 public functions, plus one private helper `_get_component_registry`.)

The module groups two cohesive but distinct surfaces:

### Surface A — Ability iteration (pre-line 404)

File: `game/strategy/services/component_inspector.py:1-401`.

Functions in source order:

- `get_component_abilities(comp_def)` — line 38.
- `extract_abilities_from_component(comp, registries=None)` — line 58.
- `_get_component_registry(registries)` — line 91 (private).
- `get_component_type(comp_def)` — line 104.
- `get_component_threshold(comp_def, default)` — line 122.
- `iterate_design_components(...)` — line 141.
- `ship_has_ability(...)` — line 192.
- `find_ship_with_ability(...)` — line 216.
- `count_ability(...)` — line 237.
- `list_ship_abilities(...)` — line 263.
- `get_ability_list(...)` — line 286.
- `iter_facility_ability_entries(...)` — line 312.
- `lookup_design_max_hp(ship, comp_id)` — line 367.

These helpers iterate component definitions and pull abilities / types / thresholds. `lookup_design_max_hp` is a borderline case (it is consumed by the layer block as a helper), so Phase 1 will decide its destination module based on Phase 0 grep results.

### Surface B — Layer view (line 404 onward, PROJ-425 Phase 2 additions)

File: `game/strategy/services/component_inspector.py:404-501`.

Functions in source order:

- `iter_components_by_layer(ship)` — line 404.
- `damaged_components_by_layer(ship)` — line 458.
- `count_damaged_components(ship)` — line 496.

Plus `has_warp_capability(ship)` at line 504 — currently lives in Surface B's region but logically it is an ability query, not a layer view. Phase 1 will move it into `component_abilities.py`.

These helpers walk `ship.design_data['layers']` joined with `ship.components` (`ComponentState`) to produce instance-level views.

## Target shape

Two new modules at `game/strategy/services/`:

- **`component_abilities.py`** — Surface A helpers + `has_warp_capability`. Estimated ~440-450 LOC. Materially under 500.
- **`component_layers.py`** — Surface B helpers (`iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`). Plus `lookup_design_max_hp` if Phase 0 confirms it has no consumers outside the layer block. Estimated ~140-160 LOC.

The module surface options for `component_inspector.py` itself:

- **Option A — re-export shim:** Keep `game/strategy/services/component_inspector.py` as a one-line-per-name re-export so existing imports continue to work without caller migration. ~20 LOC.
- **Option B — caller migration:** Delete `component_inspector.py` and migrate all import sites to the new module paths. Bigger blast radius but no shim debt.

Phase 0's final task locks Option A vs. B based on caller count.

## Existing test coverage

- `tests/unit/strategy/services/test_component_inspector.py` (and adjacent files) — Surface A coverage.
- `tests/unit/strategy/services/test_component_inspector_layers.py` (added by PROJ-425 Phase 2) — Surface B coverage; 6 tests.

Both suites stay green throughout Phase 1; only their import lines change (and only if Option B is chosen).

## Risk register

- **Module-level `__all__` drift:** the split must preserve every exported name. Phase 0 task: snapshot the current `__all__` set as a literal in a focused test that fails if any name disappears.
- **`lookup_design_max_hp` placement:** consumed by the layer block but is itself a design-data lookup. Phase 0 grep determines whether any non-layer consumer exists; if so, it goes in `component_abilities.py`, otherwise `component_layers.py`.
- **Re-export shim debt (Option A):** the shim itself contributes ~20 LOC and a future agent has to remember to delete it. Document the "delete the shim once callers migrate" task in `decisions.md` if Option A is chosen.
- **Circular imports:** `component_layers.py` will likely need a `TYPE_CHECKING`-guarded import of `ShipInstance`, mirroring the current `component_inspector.py:14-15` pattern. Verify before Phase 1's first commit.
