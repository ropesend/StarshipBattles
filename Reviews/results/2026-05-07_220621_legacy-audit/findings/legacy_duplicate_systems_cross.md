# Cross-System Duplicate-Systems Report

## Summary
- Pairs Analyzed: 4
- Clear Legacy: 2
- Ambiguous: 1
- Intentional Split (NOT findings): 1
- Total Findings: 3
- Critical: 0 | Major: 0 | Minor: 2 | Info: 1

---

## Phase 1 Name-Pair Drift Validation

### Pair 1: `_get_harvester_info` → `get_harvester_info` (underscore_pair)

**Verdict: CLEAR LEGACY — MINOR**

| | Legacy | Canonical |
|---|---|---|
| Symbol | `_get_harvester_info` | `get_harvester_info` |
| File | `game/strategy/services/planet_economy_projector.py:234` | `game/strategy/engine/harvesting_engine.py:94` |
| Call sites | 1 (same file, line 224) | 1 (`game/strategy/engine/empire_economy_calculator.py:23`) |

Both extract `ResourceHarvester` ability data from a component entry. The legacy implementation inlines the logic: checks inline abilities dict, then falls back to registry via `get_component_abilities`. The canonical implementation is a thin wrapper around `_get_ability_info` (line 48), which handles the same two paths (inline abilities → registry fallback) plus a third: string component IDs.

**Behavioral divergence:**
- `_get_harvester_info` returns `Optional[dict]`; canonical returns `dict | list | None`.
- `_get_harvester_info` hardcodes `"ResourceHarvester"`; `_get_ability_info` is generic.
- Both fall back from inline abilities to registry lookup via `get_component_abilities` — same logical path.
- Caller at `planet_economy_projector.py:224` treats the result as a dict (`.get("resource_type", "")`, `.get("base_harvest_rate", 0.0)`). Since `ResourceHarvester` is always a single dict (never a list), consolidating is safe.

**Migration effort:** 1 production call site in `planet_economy_projector.py`. Update line 224 to call `get_harvester_info` and remove `_get_harvester_info`. If the return type widening (`dict | list | None`) is a concern, add a `isinstance` guard for the list case.

---

### Pair 2: `_iter_components` → `iter_components` (underscore_pair)

**Verdict: CLEAR LEGACY — MINOR**

| | Legacy | Canonical |
|---|---|---|
| Symbol | `_iter_components` | `iter_components` |
| File | `game/ui/screens/battle_setup/spec_compiler.py:419` | `game/core/patterns/layer_iterator.py:42` |
| Call sites | 1 (same file, line 413) | 16+ across `game/strategy/` and `game/ui/` |

The legacy implementation only handles list-format layers (`layer_data = [...]`). The canonical `iter_components` handles both list and dict formats (`{"components": [...]}`), plus yields string component IDs as well as dicts. The battle setup spec compiler's usage at line 413 only sees list-format data in practice, so the narrower behavior hasn't caused bugs — but it's still a latent format-handling gap.

**Additionally,** `planet_economy_projector.py:220-231` manually iterates layers with the same list-only pattern:
```python
for layer_data in design_data.get("layers", {}).values():
    if not isinstance(layer_data, list):
        continue
    for comp in layer_data:
```
This is a secondary non-canonical iteration site. It should also migrate to `iter_components` when the harvester function is consolidated (Pair 1).

**Migration effort:**
- 1 call site in `spec_compiler.py:413`.
- 1 secondary site in `planet_economy_projector.py:220` (naturally resolved when Pair 1 is addressed).
- Remove `_iter_components` from `spec_compiler.py`, import `iter_components` from `game.core.patterns.layer_iterator`.

---

### Pair 3: `ModifierManager` → `ModifierService` (manager_service_overlap)

**Verdict: INTENTIONAL SPLIT — NOT a finding**

| | ModifierManager | ModifierService |
|---|---|---|
| File | `game/simulation/components/modifier_manager.py:31` | `game/simulation/services/modifier_service.py:16` |
| Role | Stateful delegate for one Component's modifier list | Service for cross-cutting modifier validation rules |
| Owns | `_modifiers` list (per-component instance) | `_modifiers` modifier_registry dict (global) |
| Key operations | `add_modifier`, `remove_modifier`, `get_modifier`, query/summary | `is_modifier_allowed`, `is_modifier_mandatory`, `get_initial_value`, `ensure_mandatory_modifiers` |

These serve genuinely different responsibilities. `ModifierManager` is a Component delegate (Facade/Delegate pattern #5) owning instance-level modifier state. `ModifierService` validates whether a modifier *can be* applied, independent of any specific component instance. The only shared method name is `__init__` (which the Phase 1 detector flagged). No consolidation is warranted.

---

## Narrative Pairs (Phase 1 did not catch)

### Pair 4: `ModifierService` vs `ModifierLogicService`

**Verdict: AMBIGUOUS — INFO (needs architectural decision)**

| | ModifierService | ModifierLogicService |
|---|---|---|
| File | `game/simulation/services/modifier_service.py:16` | `game/ui/screens/builder/modifier_logic.py:34` |
| Layer | Simulation (`game/simulation/services/`) | UI (`game/ui/screens/builder/`) |
| Imports by | 2 simulation files (`ship_component_manager.py` ×2) | 4 UI files (`detail_panel.py`, `builder_widgets.py`, `modifier_row.py`, `workshop_screen.py`) |

**Overlapping method signatures (7 of 8 match):**

| Method | ModifierService | ModifierLogicService |
|---|---|---|
| `is_modifier_allowed(mod_id, component)` | Own implementation (checks `mod_def.restrictions`) | Delegates to `ComponentService` |
| `get_mandatory_modifiers(component)` | Own implementation (iterates `_modifiers`) | Own implementation (iterates via `ComponentService`) |
| `is_modifier_mandatory(mod_id, component)` | Own implementation | Own implementation (delegates to `get_mandatory_modifiers`) |
| `ensure_mandatory_modifiers(component)` | Own implementation | Own implementation |
| `get_initial_value(mod_id, component)` | Own implementation (dispatch table + arc_set detection) | Own implementation (dispatch table + turret_mount special case) |
| `get_local_min_max(mod_id, component)` | Own implementation (arc_set min clamping) | Own implementation (turret_mount min clamping) |
| `_get_base_firing_arc(component)` | Own implementation (checks ALL ability values) | Own implementation (checks `_WEAPON_ABILITY_TYPES` only) |
| `calculate_snap_value(...)` | **absent** | UI-specific static method |

**Behavioral divergence — `_get_base_firing_arc`:**
- `ModifierService` (line 165-178): iterates `component.data.get('abilities', {})` checking ALL ability values for `firing_arc`.
- `ModifierLogicService` (line 131-147): only checks `_WEAPON_ABILITY_TYPES = ('ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility')`.

If a non-weapon ability ever contains a `firing_arc` key, the two implementations diverge.

**Behavioral divergence — `get_initial_value` / `get_local_min_max`:**
- `ModifierService` uses generic `_has_arc_set_effect(mod_def)` to detect any modifier with an `arc_set` effect, then clamps to base firing arc.
- `ModifierLogicService` hardcodes `mod_id == 'turret_mount'` as the trigger for arc-set clamping.

If a new modifier with an `arc_set` effect is added, `ModifierService` handles it generically while `ModifierLogicService` would need a code change.

**Recommendation:** This pair sits at a layer boundary. The simulation layer owns the canonical modifier rules; the UI layer reimplements them with subtle differences. Consolidation options:
1. **Short-term:** Move the shared logic to a `game/simulation/services/modifier_*` pure-function module that both can import. `ModifierLogicService` becomes a thin adapter over `ModifierService` methods + UI-specific `calculate_snap_value`.
2. **Long-term:** Formally declare one as canonical and deprecate the other. Given the architecture (simulation owns rules, UI adapts), `ModifierService` should be the canonical path.

**Call-site counts:** ModifierService has 2 production call sites (simulation layer). ModifierLogicService has 4 production call sites (UI builder). If consolidating FROM ModifierLogicService TO ModifierService: 4 migration points.

---

## Prioritized Consolidation Plan

| Priority | Pair | Severity | Call Sites (legacy) | Migration Effort |
|---|---|---|---|---|
| 1 | `_get_harvester_info` → `get_harvester_info` | MINOR | 1 | Replace call + remove function; add list guard |
| 2 | `_iter_components` → `iter_components` | MINOR | 1 (+1 related) | Replace call + remove function; secondary cleanup in planet_economy_projector.py |
| 3 | `ModifierService` vs `ModifierLogicService` | INFO | 6 total across both | Architectural decision required first; 4 UI call sites if consolidating to simulation path |

**Quick wins (Priority 1–2):** Two Phase 1 underscore-pair findings. Both have exactly one call site. Estimated effort: <15 minutes for both. The `_iter_components` fix also naturally covers the secondary non-canonical iteration in `planet_economy_projector.py` when that function is migrated.

**Requires decision (Priority 3):** The modifier service pair needs a design decision on whether `ModifierLogicService` should wrap `ModifierService` or remain independent. The behavioral divergence in `_get_base_firing_arc` makes this more than a simple rename.

---

## Intentional Splits Confirmed (NOT findings)

| Pair | Reason |
|---|---|
| `ModifierManager` / `ModifierService` | Different responsibilities: instance-level modifier state vs global validation rules |
| `SimulationDesignLoader` / `DesignLoaderAdapter` | Adapter pattern: UI facade over simulation loader |
| `VehicleDesignService` / `VehicleClassService` | Different layers + different concerns: ship creation/validation vs vehicle class metadata queries |
| `WorkshopDataLoader` / `WorkshopDataReloader` | Different responsibilities: file loading vs reload orchestration |
| `PlanetEconomyProjector` / `EmpireEconomyCalculator` | Different scopes: per-planet projection vs empire-wide aggregation |
| `StabilizerSpec` / `SuperweaponSpec` | Mirrored pattern for different game concepts (documented intentional) |
| `DesignValidator` / `ShipDesignValidator` / `ValidationService` | Layered validation: strategy wrapper → canonical simulation validator ← UI facade |
| Battle spec compilers (`build_manual_*`, `build_strategy_*`, `build_test_*`) | Pattern #13 intentional split by caller context |
| `BattleService` / `BattleUIService` | Different layers: simulation state vs UI rendering |
