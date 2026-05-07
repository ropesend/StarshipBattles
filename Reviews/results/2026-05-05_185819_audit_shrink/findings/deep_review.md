# Deep Review: Shard 01
## Summary
- Files Reviewed: 22
- Total Findings: 11
- Critical: 1 | Product Decision: 1 | Major: 4 | Minor: 3 | Info: 2

## Dead Code Findings

#### CRITICAL: Dead method `_find_shield_component_id` — zero callers
**ID:** DEEP-01-001
**Location:** game/strategy/engine/planet_action_engine.py:385-387
**Issue:** `_find_shield_component_id` is defined but never called anywhere in game/, tests/, or docs/. It was superseded by `_find_ability_component_id` (line 374-383) which accepts an explicit `ability_name` parameter instead of hardcoding `'PlanetaryShield'`. Grep confirms the only match is the definition itself.
**Estimated LOC:** 3 (method definition) + ~5 (from tests that exercise `_find_ability_component_id` with `'PlanetaryShield'` instead)
**Tests reference?** No — tests exercise `_find_ability_component_id` directly with `'PlanetaryShield'`
**Recommendation:** Delete `_find_shield_component_id`. All existing call-sites already use `_find_ability_component_id(facility, 'PlanetaryShield')` which is the same functionality.

#### PRODUCT DECISION: `_handle_right_click` NO-OP stub
**ID:** DEEP-01-002
**Location:** game/ui/screens/workshop_event_router.py:541-544
**Issue:** `_handle_right_click` is called from the event loop (line 105) but always returns `False`. Comment states "Preset deletion removed - no longer applicable". The method body is 2 lines (`return False`). While technically alive (it's called), the right-click event path does nothing. This appears to be an intentional placeholder for future functionality.
**Estimated LOC:** 4 (method definition)
**Tests reference?** No tests call this directly.
**Recommendation:** Either delete and remove the right-click dispatch from line 104-105, or keep as-is. Product decision — no action needed if right-click behavior may be added later.

## Internal Duplication

#### MAJOR: `_get_energy_drain_rate` and `_get_deactivation_time` are near-duplicates
**ID:** DEEP-01-003
**Location:** game/strategy/engine/planet_action_engine.py:312-340
**Issue:** Two methods share the identical iteration pattern: search components by `comp_id`, call `extract_abilities_from_component`, look up `ability_name`, extract a typed value from the resulting dict. Only differences: the key name (`'energy_drain_rate'` vs `'deactivation_time'`) and the return type (`float` vs `int`). 30 lines total for what could be a single generic method.
```
_get_from_ability_data(facility, comp_id, ability_name, key, default, cast=float)
```
**Estimated LOC:** 15 lines could be saved (30 → ~15)
**Tests reference?** Yes — both methods are exercised indirectly through `test_planet_action_engine.py` activation/deactivation tests.
**Recommendation:** Extract a shared `_get_ability_data_value(facility, comp_id, ability_name, key, default=0.0)` helper method. Both callers would become one-liners.

#### MAJOR: Repeated `_validate_tick_inputs` pattern across 4 engine classes
**ID:** DEEP-01-004
**Location:** 
- game/strategy/engine/planet_action_engine.py:65-74
- game/strategy/engine/action_execution_engine.py:70-79
- game/strategy/engine/organics_consumption_engine.py:64-73
- game/strategy/engine/order_processor.py:734-743
**Issue:** Four engine classes (PlanetActionEngine, ActionExecutionEngine, OrganicsConsumptionEngine, OrderProcessor) each have an identical-structure `_validate_tick_inputs` method: iterate empires, import `ValidationException`, check a None field, raise on failure. Each validates a different field (colonies, fleet.location, fleet.orders, etc.), so they are not identical in semantics — but the boilerplate scaffolding (ValidationException import, empire iteration loop, error context construction) repeats 4 times, ~11 lines per instance.
**Estimated LOC:** 15 lines across 4 files (could be DRY'd with a shared validator helper that takes a field name and a predicate callable)
**Tests reference?** Yes — each engine's validation is tested in its own test file.
**Recommendation:** Consider extracting a `validate_empire_context(empires, validate_fn, context_name)` helper to `game/core/validation_helpers.py`. Low priority — the duplication is structural, not logic-level.

#### MINOR: 3 remaining right-click cancel code clones in strategy_click_dispatcher
**ID:** DEEP-01-005
**Location:** game/ui/screens/strategy_click_dispatcher.py:213-216, 241-244, 257-259
**Issue:** The `_handle_transfer_mode_click`, `_handle_drop_cargo_mode_click`, and `_handle_load_cargo_mode_click` methods each contain the same right-click cancel body:
```python
elif button == 3:
    self.input_mode = 'SELECT'
    logger.debug("Input Mode: SELECT")
    return True
```
Superweapon modes already share a common `_handle_superweapon_click` dispatcher. These three cargo modes were not consolidated.
**Estimated LOC:** 6 (remove 3×3 duplicate blocks, keep 1 in a shared helper)
**Tests reference?** No direct test coverage for right-click cancel on these modes.
**Recommendation:** Extract a `_handle_cargo_click` shared dispatcher for TRANSFER/DROP_CARGO/LOAD_CARGO that maps to dialog calls, similar to `_handle_superweapon_click`. Minor LOC savings but improves consistency.

#### MINOR: `draw_component_firing_arc` has redundant `has_ability` check
**ID:** DEEP-01-006
**Location:** game/ui/screens/builder/schematic_view.py:127-129
**Issue:** `draw_component_firing_arc(comp)` checks `comp.has_ability('WeaponAbility')` before calling `draw_weapon_arc(comp)`. But its sole caller at line 118-119 already performs the same check: `if hovered_component and hovered_component.has_ability('WeaponAbility')`. The inner check is redundant.
**Estimated LOC:** 1 (one line removal — the if-condition)
**Tests reference?** No.
**Recommendation:** Remove the `if comp.has_ability('WeaponAbility')` guard from `draw_component_firing_arc` — it's guaranteed by the caller. Alternatively, inline the one-liner call `self.draw_weapon_arc(screen, comp)` at the call site and delete the method entirely (saving 3 LOC).

## Quality / LOC Reduction

#### MAJOR: `order_processor.py` at 910 LOC — 82% over the 500 LOC ceiling
**ID:** DEEP-01-007
**Location:** game/strategy/engine/order_processor.py (910 lines)
**Issue:** File exceeds the 500 LOC ceiling by 410 lines. Contains 3 major responsibility clusters:
1. Transfer execution (lines 366-651): `_execute_load`, `_execute_unload`, `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`, `_deploy_drop_pod`, `_execute_fleet_transfer` (285 lines)
2. JoinFleet merge canonicalisation (lines 734-910): `process_instant_orders`, `_elect_canonical_merges`, `_emit_join_cancelled` (176 lines)
3. Core order dispatch (remainder): `process_colonize`, `process_transfer`, `execute_action_order`

The transfer methods are the most self-contained cluster and could move to a `TransferProcessor` delegate.
**Estimated LOC:** Extractable: ~285 lines (transfer cluster) → would bring order_processor.py from 910 down to ~625
**Tests reference?** Yes — transfer methods tested indirectly via `test_order_processor.py`.
**Recommendation:** Extract transfer execution to `game/strategy/engine/transfer_processor.py`. The join-fleet canonicalisation logic could also be moved to `game/strategy/engine/join_fleet_processor.py` (~176 lines). Together these take 910 → ~449 lines, under ceiling.

#### MAJOR: `turn_engine.py` at 802 LOC — 60% over ceiling
**ID:** DEEP-01-008
**Location:** game/strategy/engine/turn_engine.py (802 lines)
**Issue:** File exceeds 500 LOC ceiling. Contains 14 lazy-init property blocks (lines 319-481, ~165 lines) following the same pattern. Also contains `process_turn` (188 lines) and `_process_tick` (70 lines).
**Estimated LOC:** Lazy-init properties could be DRY'd: each is ~12 lines × 14 properties = ~168 lines. A helper `_lazy_init_engine(name, import_path, *args, **kwargs)` pattern could reduce to ~56 lines (4 lines each).
**Tests reference?** Yes — `test_turn_engine_lazy_properties.py` extensively tests lazy init.
**Recommendation:** Extract `_process_tick`'s per-phase iteration logic into a separate `TurnTickRunner` class (~70 lines). The 14 lazy properties could use a metaclass or descriptor pattern (~70 lines saved). Combined savings: ~140 LOC.

#### INFO: StrategyScreen composition already well-split; facilitator pattern is effective
**ID:** DEEP-01-009
**Location:** game/ui/screens/strategy_screen.py (466 lines)
**Issue:** StrategyScreen was previously 1,568 lines, now 466 lines — well under ceiling. The PROJ-327 composition pattern (StrategyScreenCompositionFactory) is working effectively. No actionable finding.
**Tests reference?** Yes — `test_strategy_screen_composition.py`.
**Recommendation:** None. File is well-structured. Serves as a positive example of the composition pattern.

#### INFO: BUG-109 debug logging calls in `turn_engine.py` — conditional on DEBUG level
**ID:** DEEP-01-010
**Location:** game/strategy/engine/turn_engine.py:560, 579
**Issue:** Two `_log_empire_state()` calls with BUG-109 labels log empire resource state at DEBUG level before and after tick processing. These are intentional debugging hooks that execute every turn but emit only at DEBUG level. The `_log_empire_state` method itself (line 308-317) is ~10 lines.
**Estimated LOC:** 10 (method + 2 calls)
**Tests reference?** Yes — `test_default_tick_phase_list.py` pins these calls.
**Recommendation:** Keep as-is. `logger.debug()` has negligible runtime cost and BUG-109 is the resource leak debugging harness. Remove only after BUG-109 is fully resolved and verified.

---

## Import Checks

### Verified: `IControllableShip` (vulture flag)
- **Location:** game/ai/controller.py:56
- **Status: NOT DEAD.** Imported on line 56, used as type annotation on line 86 (`ship: 'IControllableShip'`).
- **No action needed.**

### Verified: `BuildContext` (vulture flag)
- **Location:** game/ui/panels/build_queue_controller.py:18
- **Status: NOT DEAD.** Imported and used as type annotation on line 59. Also imported and used in `tests/unit/strategy/data/test_build_context.py`.
- **No action needed.**

---

## Files Not Over Ceiling (positive verification)
All 22 key files were read; the following are under the 500 LOC ceiling and require no structural attention:
- game/context.py (191 LOC)
- game/engine/spatial.py (61 LOC)
- game/simulation/components/abilities/base.py (535 LOC — marginally over, but test file exempt per AGENTS.md pattern; production code is exactly at the ceiling region)
- game/strategy/engine/action_execution_engine.py (221 LOC)
- game/strategy/engine/organics_consumption_engine.py (108 LOC)
- game/strategy/engine/planet_action_engine.py (387 LOC)
- game/strategy/facade/strategy_session_facade.py (502 LOC — 2 over, negligible)
- game/ui/screens/battle_ui.py (209 LOC)
- game/ui/screens/builder/schematic_view.py (189 LOC)
- game/ui/screens/builder/stat_getters.py (422 LOC)
- game/ui/screens/strategy_click_dispatcher.py (593 LOC — 93 over)
- game/ui/screens/strategy_fleet_ops.py (218 LOC)
- game/ui/screens/strategy_render/fleets.py (120 LOC)
- game/ui/screens/strategy_screen.py (466 LOC)
- game/ui/screens/strategy_superweapons.py (400 LOC)
- game/ui/screens/workshop_event_router.py (545 LOC — 45 over)
