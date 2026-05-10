# Decomposition Design: workshop_viewmodel.py

**Current size:** 873 lines (single `WorkshopViewModel` class spanning lines 35–873)
**Target post-split:** every resulting module <500 lines

> **Last verified:** 2026-04-27 — Initial design after reading the full target file, all 6 sibling `workshop_*.py` files, `docs/03_CONVENTIONS.md` §1.3 / §1.6, and grep of all production + test callers.

---

## Current responsibilities

The class is already organized into labelled sections via `─────` dividers. They map cleanly onto the following clusters:

1. **Lifecycle & DI** (L49–100) — `__init__` requires `WorkshopContext.registries`, constructs `VehicleDesignService`, defines `_require_ship` guard.
2. **Ship state property** (L102–124) — `ship` getter/setter, `_emit_ship_updated`, `notify_ship_changed`. Owns the `Ship` reference and the SHIP_UPDATED event.
3. **Selection state** (L126–235) — `selected_components`, `primary_selection`, `select_component`, `_normalize_selection`, `_handle_append_selection`, `_emit_selection_changed`, `clear_selection`. Multi-select with append/toggle and homogeneity rule.
4. **Drag state** (L237–249) — `dragged_item` property; emits DRAG_STATE_CHANGED.
5. **Available components catalog** (L251–265) — `available_components` property + `refresh_available_components` (pulls from `_registries.components`).
6. **Hull layer visibility** (L267–285) — `show_hull_layer` property + `toggle_hull_layer`; emits HULL_LAYER_VISIBILITY_CHANGED.
7. **Modifier sync** (L287–319) — `on_modifier_changed`, `_sync_modifiers_to_selection`. Cross-cuts Selection + Ship — copies modifiers from primary to siblings.
8. **Ship operations: result accessors** (L321–338) — `last_result`, `last_errors`, `last_warnings` proxy `DesignResult`.
9. **Ship CRUD via VehicleDesignService** (L340–528) — `create_default_ship`, `add_component`, `add_component_bulk`, `add_component_instance`, `remove_component`, `pick_up_component`, `change_ship_class`, `validate_design`, `get_available_components_for_layer`, `get_ship_summary`, `clear_design`. All thin delegates that capture `_last_result` and re-emit `notify_ship_changed`.
10. **Ship attribute setters** (L570–657) — `set_ship_name`, `set_ship_theme`, `set_ship_movement_policy`, `set_ship_targeting_policy`, `set_ship_design_role`. Each follows the pattern: guard → no-change short-circuit → mutate → emit.
11. **Layer resolution + quick-add** (L663–749) — `resolve_target_layer`, `quick_add_component`. Uses `LayerRestrictionDefinitionRule` to find valid layers for component placement.
12. **Component movement between layers** (L755–873) — `resolve_move_target`, `move_component`, `move_component_group`. Layer-walk algorithms + reverse-index batch removal.

**Observation:** The design.md sketch hypothesized "view-state + command handling + validation likely entangled." In practice the file is **not** badly entangled — the section dividers reflect real cohesion boundaries. The challenge is purely **size**, not cohesion. Validation per se is a single one-line delegate (`validate_design`); what looks like validation is actually **layer-restriction resolution** for placement (quick-add) and movement.

---

## Proposed sub-modules

All paths obey `docs/03_CONVENTIONS.md` §1.3: workshop files live **directly** in `game/ui/screens/` as `workshop_*.py` — **NOT** in a `workshop/` subdirectory.

Strategy: extract three cohesive helper modules that the slimmed `WorkshopViewModel` composes. The `WorkshopViewModel` class **remains the public API surface** (Option A — no caller migration needed beyond the existing `gui.viewmodel.*` access pattern, which is already a delegation seam).

### 1. `game/ui/screens/workshop_viewmodel.py` (slimmed core)

| | |
|--|--|
| **Responsibility** | Lifecycle, DI, state ownership, public façade. Composes the three helper modules below. Thin delegators for everything that's been extracted. |
| **Symbols** | `WorkshopViewModel` (class, public API unchanged); private helpers: `__init__`, `_require_ship`, `_emit_ship_updated`, `_emit_selection_changed`, `notify_ship_changed`, properties (`ship`, `selected_components`, `primary_selection`, `dragged_item`, `available_components`, `show_hull_layer`, `last_result`, `last_errors`, `last_warnings`), `clear_selection`, `select_component`, `refresh_available_components`, `toggle_hull_layer`, `on_modifier_changed`. Delegators for the operations exposed by helpers below (one-liners). |
| **Estimated LOC** | ~310 |
| **Depends on** | `workshop_viewmodel_selection.py`, `workshop_viewmodel_ship_ops.py`, `workshop_viewmodel_layer_ops.py`, `WorkshopContext`, `VehicleDesignService`, `BuilderEvents`, `LayerType` |

Sections retained in the core file: 1, 2, 3 (kept inline because selection state lives here and is shared with the sub-helpers via the instance), 4, 5, 6, 8 (result accessors are trivial passthroughs).

### 2. `game/ui/screens/workshop_viewmodel_ship_ops.py` (NEW)

| | |
|--|--|
| **Responsibility** | All `VehicleDesignService`-backed CRUD operations + ship attribute setters. Stateless helper that takes a `WorkshopViewModel` reference and operates on it. |
| **Symbols** | `class WorkshopShipOps`<br>&nbsp;&nbsp;`__init__(viewmodel, ship_service)`<br>&nbsp;&nbsp;`create_default_ship(ship_class)`<br>&nbsp;&nbsp;`add_component(component_id, layer)`<br>&nbsp;&nbsp;`add_component_bulk(component_id, layer, count)`<br>&nbsp;&nbsp;`add_component_instance(component, layer)`<br>&nbsp;&nbsp;`remove_component(layer, index)`<br>&nbsp;&nbsp;`pick_up_component(layer, index)`<br>&nbsp;&nbsp;`change_ship_class(new_class, migrate_components)`<br>&nbsp;&nbsp;`validate_design()`<br>&nbsp;&nbsp;`get_available_components_for_layer(layer)`<br>&nbsp;&nbsp;`get_ship_summary()`<br>&nbsp;&nbsp;`clear_design()`<br>&nbsp;&nbsp;`set_ship_name(name)`<br>&nbsp;&nbsp;`set_ship_theme(theme_id)`<br>&nbsp;&nbsp;`set_ship_movement_policy(policy_id)`<br>&nbsp;&nbsp;`set_ship_targeting_policy(policy_id)`<br>&nbsp;&nbsp;`set_ship_design_role(role_id)` |
| **Estimated LOC** | ~290 |
| **Depends on** | `VehicleDesignService`, `DesignResult`, `LayerType`, `VEHICLE_DEFAULT`, `ValidationException`, `ErrorCode` |

The helper writes to `viewmodel._last_result` and calls `viewmodel.notify_ship_changed()` / `viewmodel._emit_ship_updated()` exactly as today. It is a refactor of internal organisation, not behavior.

### 3. `game/ui/screens/workshop_viewmodel_selection.py` (NEW)

| | |
|--|--|
| **Responsibility** | Selection-set algorithms (normalisation, append/toggle/homogeneity) and modifier broadcast across multi-selection. **State** still lives on `WorkshopViewModel` — this module only contains pure-ish algorithms. |
| **Symbols** | `normalize_selection(items, ship)` — module-level function returning normalized `List[Tuple[LayerType, int, Component]]`.<br>`apply_append_selection(current, incoming, toggle)` — pure function returning the new selection list.<br>`sync_modifiers_to_selection(primary_component, selection)` — copies modifiers from primary to siblings using `builder.modifier_utils.copy_modifiers`. |
| **Estimated LOC** | ~120 |
| **Depends on** | `LayerType`, `Component`, `Ship`, `game.ui.screens.builder.modifier_utils.copy_modifiers` |

The viewmodel's `select_component`, `_normalize_selection`, `_handle_append_selection`, `_sync_modifiers_to_selection` shrink to thin wrappers calling these module-level functions. Event emission stays on the viewmodel.

### 4. `game/ui/screens/workshop_viewmodel_layer_ops.py` (NEW)

| | |
|--|--|
| **Responsibility** | Layer-restriction-driven placement and movement algorithms. Reads ship state, returns target `LayerType` decisions. Quick-add and move-component orchestration. |
| **Symbols** | `class WorkshopLayerOps`<br>&nbsp;&nbsp;`__init__(viewmodel, ship_service, registries)`<br>&nbsp;&nbsp;`resolve_target_layer(component, selected_layer)`<br>&nbsp;&nbsp;`resolve_move_target(component, source_layer, direction)`<br>&nbsp;&nbsp;`quick_add_component(component_id, selected_layer, count)`<br>&nbsp;&nbsp;`move_component(source_layer, index, target_layer)`<br>&nbsp;&nbsp;`move_component_group(group_key, source_layer, target_layer)` |
| **Estimated LOC** | ~190 |
| **Depends on** | `LayerType`, `LayerRestrictionDefinitionRule`, `create_component`, `game.ui.screens.builder.grouping_strategies.get_component_group_key` |

The two `resolve_*` algorithms become testable in isolation. Quick-add and move-component continue to drive viewmodel state via `viewmodel.notify_ship_changed()` and `viewmodel.add_component*`.

---

### LOC summary

| Module | Estimated LOC |
|---|---|
| `workshop_viewmodel.py` (core, slimmed) | ~310 |
| `workshop_viewmodel_ship_ops.py` (NEW) | ~290 |
| `workshop_viewmodel_selection.py` (NEW) | ~120 |
| `workshop_viewmodel_layer_ops.py` (NEW) | ~190 |
| **Total** | **~910** (vs 873 today; +37 from class boilerplate / imports) |

All four modules are <500 LOC, satisfying the PROJ-309 target.

---

## Public API surface

The public API is the `WorkshopViewModel` class. Every method/property listed in section §3.1–§3.10 of the responsibilities list is part of the public surface.

### Callers (production)

- `game/ui/screens/workshop_screen.py` — constructs the VM (L87) and uses `viewmodel.{ship, selected_components, available_components, create_default_ship, set_ship_theme, refresh_available_components, on_modifier_changed, change_ship_class, set_ship_name, clear_design}`.
- `game/ui/screens/workshop_event_router.py` — uses `viewmodel.{quick_add_component, last_errors, resolve_move_target, move_component, move_component_group, remove_component, add_component_instance, toggle_hull_layer, set_ship_theme, set_ship_movement_policy, set_ship_targeting_policy, set_ship_design_role}`.
- `game/ui/screens/workshop_data_reloader.py` — uses `viewmodel.{refresh_available_components, ship, create_default_ship, clear_selection}`.
- `game/ui/screens/workshop_ship_io.py` — uses `viewmodel.ship`.
- `game/ui/screens/builder/layer_panel.py` — uses `viewmodel.{show_hull_layer, resolve_move_target}`.

### Callers (tests)

23 test files import or reference the viewmodel. Headline test files that exercise the API broadly:

- `tests/unit/workshop/test_workshop_viewmodel.py`
- `tests/unit/workshop/test_quick_add.py`
- `tests/unit/workshop/test_move_component.py`
- `tests/unit/ui/screens/test_workshop_screen.py`
- `tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py`
- Eight `tests/unit/builder/test_*.py` files reach in via the screen-level fixture.

---

## Caller-update strategy

**Choice: Option A (re-export shim — but more accurately, keep the public class in place and refactor internals).**

**Justification:**

1. **The public seam is `gui.viewmodel.<method>`, not direct module imports of the inner concerns.** Production callers and tests both reach the viewmodel through the screen object (`gui.viewmodel`) or through fixture construction (`WorkshopViewModel(event_bus, w, h, context=...)`). Only `workshop_screen.py` imports the class symbol directly.
2. **Splitting the public surface across multiple classes (Option B) would force ~30 callsites to be updated** (e.g. `viewmodel.ship_ops.add_component(...)` instead of `viewmodel.add_component(...)`) **with no architectural benefit** — they're already going through one delegation hop, adding a second hop only inflates churn.
3. **The `WorkshopViewModel` class is already the MVVM "M" / VM seam** (per §1.6 of conventions). Replacing it with a constellation of public classes muddies the pattern.
4. **The helpers are implementation details.** They should be `_ship_ops`, `_layer_ops` private attributes; method calls forward through one-line delegators. This keeps the existing test surface intact and limits the diff to internal reorganisation.

Concretely, the diff is:

- **No call-site changes** in `workshop_screen.py`, `workshop_event_router.py`, `workshop_data_reloader.py`, `workshop_ship_io.py`, `builder/layer_panel.py`.
- **No test changes** — all 23 test files continue to use `viewmodel.<method>` exactly as today.
- The new helper modules (`workshop_viewmodel_ship_ops.py`, `_selection.py`, `_layer_ops.py`) are internal and may be unit-tested in isolation as a follow-up (not required for PROJ-309).

---

## Test plan

### Existing tests (must remain green, unchanged)

- `tests/unit/workshop/test_workshop_viewmodel.py` — exercises `select_component`, `add_component`, `remove_component`, `change_ship_class`, `clear_design`, etc.
- `tests/unit/workshop/test_quick_add.py` — exercises `resolve_target_layer`, `quick_add_component`.
- `tests/unit/workshop/test_move_component.py` — exercises `resolve_move_target`, `move_component`, `move_component_group`.
- `tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py` — exercises `pick_up_component`.
- `tests/unit/ui/screens/test_workshop_screen.py` — exercises VM construction + theme/name/policy setters via the screen.
- All 8 `tests/unit/builder/test_*.py` files that drive selection through the screen.

Acceptance: full suite remains at 15405 passed, 2 skipped (post-PROJ-311 baseline) with no test edits.

### New contract tests (added in the same commit)

1. `tests/unit/workshop/test_workshop_viewmodel_selection_helpers.py` — exercise `normalize_selection`, `apply_append_selection` as pure functions (homogeneity rule, toggle semantics, tuple normalisation, dragged-template `(None, -1, comp)` shape).
2. `tests/unit/workshop/test_workshop_viewmodel_layer_ops.py` — exercise `WorkshopLayerOps.resolve_target_layer` and `resolve_move_target` with a hand-built `Ship` mock and stubbed `LayerRestrictionDefinitionRule` (or a real registries fixture) — covering: HULL exclusion, nearest-valid tiebreak (prefer inner), no valid layer → None, direction "up" / "down" search order.
3. `tests/unit/workshop/test_workshop_viewmodel_ship_ops.py` — verify `WorkshopShipOps` writes `_last_result` and triggers `notify_ship_changed` for each CRUD path. Existing higher-level tests already cover this implicitly; this lower-level test pins the contract for future edits.

These new tests are the safety net that makes future refactors of the helpers safe in isolation.

---

## Risks

1. **Coupling with existing workshop sibling delegates.** `workshop_event_router.py` and `workshop_data_reloader.py` reach in through `viewmodel.<method>`. Option A keeps every method name on the viewmodel, so no risk to siblings.
2. **Selection state is shared.** Selection state lives on `WorkshopViewModel._selected_components` and is read by `_sync_modifiers_to_selection`, `select_component`, `clear_selection`, and the layer-ops module (indirectly via `pick_up_component` → `clear_selection`). The selection helper file (`workshop_viewmodel_selection.py`) will be **stateless module-level functions**, not a class — they take the current selection list and return the new one. State remains owned by the viewmodel. This avoids the "two stores of truth" anti-pattern.
3. **`_emit_ship_updated` and `_emit_selection_changed`** must remain on the viewmodel (they touch `event_bus`). All ship-ops and layer-ops methods must call back into the viewmodel via `viewmodel.notify_ship_changed()` / `viewmodel._emit_ship_updated()`. This is the only place a circular reference exists, and it is identical to the existing pattern (e.g. `WorkshopShipIO` already takes `viewmodel` in its constructor).
4. **`builder/layer_panel.py` reaches `viewmodel.resolve_move_target` directly.** Under Option A this stays on the viewmodel (one-line delegator to `self._layer_ops.resolve_move_target(...)`). Zero call-site change.
5. **Modifier sync uses an inline import** (`from game.ui.screens.builder.modifier_utils import copy_modifiers` at L318). Moving this into `workshop_viewmodel_selection.py` is fine — it's a one-way UI→builder import, consistent with §1.3 (Workshop composes Builder).
6. **`pyc`/import-time cycles.** `workshop_viewmodel_*.py` siblings only import from `game.simulation`, `game.core`, `game.ui.colors`, `game.ui.screens.builder` — no back-import to `workshop_screen.py` or `workshop_event_router.py`. Safe.
7. **PROJ-282 MVVM contract.** §1.6 of conventions describes the VM as the M-of-MVVM. Splitting the implementation into private helpers does not violate this — the public class remains the viewmodel.

---

## Open questions

1. **Should `validate_design()` move into `WorkshopShipOps` or stay on the core viewmodel?** It's a pure delegate to the service. Proposed: move into `WorkshopShipOps` for cohesion with the other service-backed delegates. The viewmodel keeps a one-line forwarder.
2. **Should the new helper modules use `_underscored` private attribute names (e.g. `self._ship_ops`) or be tagged `__init_subclass__`-style?** Proposed: simple `self._ship_ops`, `self._selection_ops` (module-level for selection), `self._layer_ops` private attributes. Plain composition.
3. **Naming: `workshop_viewmodel_selection.py` vs `workshop_selection_helpers.py`?** Proposed: prefix with `workshop_viewmodel_` so the relationship to the VM is obvious in the flat directory layout (which already has 7 `workshop_*.py` files). This also keeps file ordering grouped under the VM in IDE listings.
4. **Should the layer-ops module take `registries` directly or pull from `viewmodel._registries`?** Proposed: pass `registries` in the constructor — keeps the helper independently testable without a full viewmodel.
5. **Future opportunity (out of scope):** `WorkshopShipOps` could be subsumed into `VehicleDesignService` if the service grew an event-emission protocol — but that would cross the UI→Simulation seam and is a larger architectural change beyond PROJ-309.
