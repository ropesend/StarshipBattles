# Shard 10 — Test Coverage Audit Report

**Scope:** 38 production files, ~8326 LOC  
**Date:** 2026-05-04  
**Auditor:** OpenCode Discovery Agent

---

## Summary

| Metric | Count |
|---|---|
| Total files in shard | 38 |
| Fully covered (Tier 3) | 9 |
| Partially covered (Tier 1–2) | 12 |
| No dedicated tests (Tier 0 / untested Tier 2) | 17 |
| CRITICAL findings | 1 |
| MAJOR findings | 6 |
| MINOR findings | 8 |
| ADVISORY findings | 13 |

---

## CRITICAL — Tier 0 Non-UI Files

### game/core/profiling.py (Tier 0, 149 LOC)

**No dedicated unit test file.** A partial test exists at `tests/unit/core/test_profiling_edge_cases.py` but it only covers edge cases, not the core API.

| Symbol | Line | Status | Risk |
|---|---|---|---|
| `Profiler.__init__` | 43 | UNTESTED | Misses session_id generation, empty records |
| `Profiler.start()` | 55 | UNTESTED | Core enable flow |
| `Profiler.stop()` | 61 | UNTESTED | Core disable flow |
| `Profiler.toggle()` | 66 | UNTESTED | Flip transition |
| `Profiler.is_active()` | 74 | UNTESTED | Guard query |
| `Profiler.record()` | 77 | UNTESTED | Active/inactive branch both paths |
| `Profiler.save_history()` | 90 | UNTESTED | JSON persistence path |
| `Profiler.clear()` | 50 | UNTESTED | Test isolation helper |
| `profile_action` decorator | 116 | UNTESTED | Profiler None → fallthrough path |
| `profile_block` context manager | 136 | UNTESTED | Profiler None → yield path, finally-record path |
| `get_default_profiler()` | 20 | UNTESTED | Accessor |
| `set_default_profiler()` | 25 | UNTESTED | Accessor |

**Impact:** All profiling in the application depends on this module. Decorators and context managers silently no-op when profiler is None (which is untested). The `save_history()` JSON persistence path (lines 90-113) has no test coverage including the `filename is None` default, the `not self.records` early-return, the `load_json` fallback to `[]`, and the `save_json` failure branch.

**Recommendation:** Create `tests/unit/core/test_profiling.py` covering all 7 public methods + both convenience functions.

---

## MAJOR — Tier 1–2 with Significant Gaps

### 1. game/ai/combat_utils.py (Tier 2, 244 LOC)

**Test files:** `tests/unit/ai/test_combat_utils.py`, `tests/unit/ai/test_target_evaluator_edge_cases.py`

**Coverage matrix:** 8/9 symbols tested, 1 untested.

| Symbol | Line | Untested Reason |
|---|---|---|
| `get_capability_cache_key` | 73–87 | **No test references exist** in any test file. Three code paths: (1) `entity.id` exists, (2) `entity.id` missing but `name` exists, (3) neither exists → `None`. |

All other symbols (`is_vector2_like`, `get_entity_id`, `get_position`, `get_rotation`, `get_all_components`, `safe_distance`, `get_hp_percent`, `is_in_pdc_arc`) are tested. However, verify that boundary conditions for `safe_distance` (float('inf') return), `is_in_pdc_arc` (zero-length vector guard at line 226, non-IControllable ship path at line 219-222), and `get_hp_percent` (empty components → 1.0) are exercised.

### 2. game/services/llm/background.py (Tier 2, 332 LOC)

**Test files:** `tests/unit/services/llm/test_background.py`

This module contains a complex multi-threaded state machine with locking. Verify tests cover:

| Area | Lines | Risk |
|---|---|---|
| `LLMBackgroundCall.cancel()` before start | 157–178 | PENDING→CANCELLED path; `_done_event.set()` called |
| `LLMBackgroundCall.wait()` API | 197–210 | PROJ-324 Phase 2 deterministic waiter |
| `_run()` outer finally decrements counter | 292–297 | `_in_flight_calls -= 1` always executes |
| `shutdown_all_calls()` timeout path | 305–325 | Worker alive after timeout |
| `LLMBackgroundCall.__init__` validation | 84–93 | None provider, empty messages |
| `LLMUnexpectedError` wrapping in `_run()` | 257–279 | Exception→ERROR path (PROJ-321..328 S1.1) |
| Global counter `_in_flight_calls >= MAX` guard | 133–143 | `LLMConfigError` raised |

### 3. game/strategy/services/race_resolver.py (Tier 2, 43 LOC)

**No dedicated test file found.** This module was extracted in PROJ-319 (DUP-X-01) to remove code duplication between `HappinessEngine` and `PopulationEngine`.

| Symbol | Line | Status |
|---|---|---|
| `resolve_race_config()` | 18–43 | UNTESTED. Four code paths: (1) registry returns config, (2) registry returns None + empire.race_config matches race_id, (3) empire.race_config matches race_id (no registry), (4) no match → None |

**Impact:** This function feeds into population growth and happiness calculations. A silent bug (returning the wrong race config) would produce incorrect growth/happiness values for multi-species colonies.

**Recommendation:** Create `tests/unit/strategy/services/test_race_resolver.py` covering all 4 paths + `race_registry is None` + `empire.race_config is None` cases.

### 4. game/ui/services/modifier_icon_service.py (Tier 2, 87 LOC)

**No dedicated test file found.**

| Symbol | Line | Status |
|---|---|---|
| `ModifierIconService.__init__` | 37 | UNTESTED |
| `ModifierIconService.get_icon()` | 48 | UNTESTED — cache hit, cache miss, filename not in map → fallback name, file not found, pygame load error, scale path (surface size != icon_size) |
| `ModifierIconService.clear_cache()` | 85 | UNTESTED |

### 5. game/strategy/engine/order_processor.py (Tier 2, 910 LOC)

**Test files exist:** `test_order_processor_instant.py`, `test_order_processor_colonize.py`, `test_order_processor_transfer.py`, `test_order_processor_fleet_merge.py`, `test_fleet_order_processor.py`, etc.

**Key gap verification required:**

| Area | Lines | Risk |
|---|---|---|
| `_deploy_drop_pod()` | 618–652 | Planet stockpile seeding from `initial_stockpile` |
| `_execute_fleet_transfer()` | 366–396 | Fleet-to-fleet transfer with cargo caps |
| `_load_pod_from_staging_yard()` | 532–585 | No-ship-capacity fallthrough, pod_name filter |
| `_unload_pod_to_staging_yard()` | 587–616 | Filter by pod name, capacity limits |
| `_elect_canonical_merges()` mutual pair logic | 823–883 | Three tie-breaking rules (most ships → smaller id) |
| `process_instant_orders()` cycle re-validation | 745–821 | Phase C absorbed-by-other-merge + target_absorbed paths |
| `_validate_tick_inputs()` | 734–743 | None orders list |

### 6. game/strategy/data/fleet.py (Tier 3, 615 LOC)

**No dedicated unit test file.** The Fleet data class is the centerpiece of the strategy layer. Tests exist indirectly through integration/strategy tests and UI tests, but no dedicated unit test exercises `Fleet.__init__`, `Fleet.to_dict()`, `Fleet.from_dict()`, `Fleet.merge_with()`, order lifecycle methods, or fleet hierarchy methods in isolation.

| Area | Lines | Risk |
|---|---|---|
| `Fleet.__init__` | 46–93 | All delegates instantiated |
| `Fleet.to_dict()` | 461–492 | Hierarchy serialization, fleet_policy edge |
| `Fleet.from_dict()` | 494–584 | PROJ-251 strict deserialization, corrupt ship data, PROJ-320 no-recalc decision |
| `Fleet.merge_with()` | 371–460 | PROJ-222 redirect pursuers, BUG-122 exclude self, FLEET_JOIN_CANCELLED fallback |
| `Fleet.clear_orders()` | 293–307 | Pursuer unregistration |
| `Fleet.remove_orders_by_type()` | 338–344 | Target unregistration |
| `Fleet.remove_orders_by_type_and_target()` | 346–369 | BUG-122 stale order cleanup |
| `resolve_order_references()` | 586–603 | Marker dict resolution |

---

## MINOR — Partial Missing Branches & Untested Error Paths

### 7. game/core/resources.py (Tier 2, 178 LOC)

**Test files:** `tests/unit/core/test_resources.py`

| Area | Lines | Risk |
|---|---|---|
| `ResourceCatalog.from_json()` fallback paths | 90–105 | File-not-found, JSON decode error, permission error, OSError, TypeError, AttributeError — broad catch returns empty catalog |
| `_resolve_resource_path()` absolute path branch | 159–178 | `Path.exists(file_path)` when absolute is True |

### 8. game/simulation/combat/formation.py (Tier 2, 383 LOC)

**Test file:** `tests/unit/simulation/combat/test_formation.py`

| Area | Lines | Risk |
|---|---|---|
| `FormationShape.CUSTOM` with too-few positions (padding by repeat) | 141–146 | Pad with last entry |
| `FormationShape.CUSTOM` with empty custom_positions | 141–142 | Returns zeros |
| `FormationShape.SCREEN` with 1 ship | 178–192 | main = 1, screen_count = 0 |
| `FormationShape.CARRIER_PROTECTED` with 1 ship | 194–209 | carrier_count = 1, escort_count = 0 |
| `_compute_local_positions` unknown shape fallback | 211–212 | Line astern default |
| `resolve_default_for_task_force` empty ships | 277–281 | Returns LINE_ABREAST |
| `resolve_team_entry_vectors` team_count boundary (8) | 345–349 | ValueError for <2 and >8 |
| `resolve_team_entry_vectors` epsilon snap | 356–369 | Floating-point to zero clamping |

### 9. game/simulation/entities/ability_aggregator.py (Tier 2, 205 LOC)

**Test file:** `tests/unit/simulation/entities/test_ability_aggregator.py`

| Area | Lines | Risk |
|---|---|---|
| `calculate_ability_totals()` layer filtering when layer is not None | 128–130 | Skips raw dict processing, only processes instances |
| `calculate_ability_totals()` scope_filter with layer filter | 102–103 | Scope filtering branch |
| `_aggregate_ability_groups()` empty group_contributions | 47–48 | `continue` when no contributions |
| `get_ability_instances_by_class()` iterator | 176–203 | Utility for iterating abilities by class name |

### 10. game/ui/screens/planet_target_editor_base.py (Tier 1, 63 LOC)

**No dedicated test file found.**

| Symbol | Line | Status |
|---|---|---|
| `PlanetTargetEditor._button_handlers()` | 39 | Overridden by subclasses; base returns `{}` |
| `PlanetTargetEditor.process_event()` | 47 | Button dispatch loop + UI_WINDOW_CLOSE wiring |

**Impact:** This is a shared base for 4 planet target editors (Atmosphere, Gravity, Water, Radiation). Bugs in event routing affect all 4 editors.

### 11. game/ui/screens/builder/modifier_row.py (Tier 3 user-facing widget)

**No unit test file found.** This is a complex interactive widget (355 LOC) with:
- 3 control types (linear, linear_stepped, facing_selector)
- Slider, text entry, step buttons, preset buttons
- Mandatory modifier lock (can't toggle off)
- Smart snap-to-floor/ceil with MinMaxBounds

### 12. game/ui/utils/resource_display.py (Tier 2, 58 LOC)

**No test file found.**

| Symbol | Line | Untested |
|---|---|---|
| `get_resource_abbreviation()` | 36–43 | Unknown resource falls back to `res[:3].title()` |
| `get_displayed_resource_ids()` | 46–58 | Catalog load from JSON, group ordering |

### 13. game/strategy/events/event_types.py (Tier 2, 38 LOC)

**No test file.** This is purely enum definitions (EventType, EventCategory). Tests would be checking enum values exist as expected — low priority for a constants-only file.

### 14. game/strategy/engine/organics_consumption_engine.py (Tier 3, 108 LOC)

**Test file:** `tests/unit/strategy/engine/test_organics_consumption_engine.py`

| Area | Lines | Risk |
|---|---|---|
| `_process_colony()` with empty populations | 92 | No populations on a colony |
| `_process_colony()` where `needed <= 0` (zero pop or zero allocation) | 101–103 | Writes `1.0` ratio |
| `economy_config.population_consumption` is empty dict | 98 | No resources to consume |
| `_validate_tick_inputs()` None colony in list | 64–73 | ValidationException raised |

---

## TIER 3 — Verified (Appears Covered)

These files have dedicated tests with good coverage per the coverage matrix. Verified by spot-checking test files:

| File | LOC | Test File(s) | Verification |
|---|---:|---|
| `game/core/component_state.py` | 102 | `test_component_state.py` | **VERIFIED.** 13 tests covering ComponentState, ComponentInstanceView, to_dict/from_dict roundtrip, is_damaged, default fields, integer coercion, missing optional fields, frozen immutability, equality. |
| `game/core/state_machine.py` | 146 | `test_state_machine.py` | **VERIFIED.** 16 tests covering init, transitions, guards (passing/failing/missing), on_enter/on_exit callbacks with ordering, push/pop stack (LIFO, empty stack, push validation, pop validation). |
| `game/core/exceptions.py` | 437 | `test_exceptions.py` | **Appears covered.** Exception hierarchy with 26 classes, all instantiable with message+code+context. |
| `game/core/resources.py` | 178 | `test_resources.py` | **Appears covered.** ResourceCatalog CRUD, ResourceDefinition, from_json, from_data, path resolution. |
| `game/simulation/entities/ability_aggregator.py` | 205 | `test_ability_aggregator.py` | **Appears covered.** Two-phase aggregation, marker abilities, layer/scope filtering. |
| `game/strategy/data/race_config.py` | 372 | `test_race_config.py` | **Appears covered.** Validation checks, to_dict/from_dict, save/load, PROJ-283 preferences. |
| `game/strategy/generation/star_image_registry.py` | 111 | `test_star_image_registry.py` | **Appears covered.** Manifest loading, random image selection, type mapping. |
| `game/ui/screens/strategy_colonization.py` | 276 | `test_strategy_colonization.py` | **Appears covered.** Colonization workflow logic. |
| `game/ui/screens/strategy_screen_assets.py` | 88 | `test_strategy_screen_assets.py` | **Appears covered.** Asset loading helpers. |

---

## File Coverage Verification Table

| File | LOC | Tier | Dedicated Test? | Status | Findings |
|---|---|---|---|---|---|
| `game/ai/combat_utils.py` | 244 | 2 | Yes | PARTIAL | 1 untested symbol (get_capability_cache_key) |
| `game/core/component_state.py` | 102 | 2 | Yes | VERIFIED | Complete coverage |
| `game/core/exceptions.py` | 437 | 3 | Yes | VERIFIED | 26 exception classes |
| `game/core/profiling.py` | 149 | 0 | Partial | CRITICAL GAP | No dedicated unit test |
| `game/core/resources.py` | 178 | 2 | Yes | MAJOR GAP | Error fallback paths untested |
| `game/core/state_machine.py` | 146 | 2 | Yes | VERIFIED | Complete coverage |
| `game/services/llm/background.py` | 332 | 2 | Yes | MAJOR GAP | Complex concurrency; verify all paths |
| `game/simulation/combat/formation.py` | 383 | 2 | Yes | MINOR | Edge shapes + CUSTOM padding untested |
| `game/simulation/components/abilities/ui_colors.py` | 84 | 2 | No | ADVISORY | Constants-only, no logic to test |
| `game/simulation/entities/ability_aggregator.py` | 205 | 2 | Yes | VERIFIED | Appears well covered |
| `game/strategy/data/fleet.py` | 615 | 3 | No | MAJOR GAP | No dedicated unit test; indirect only |
| `game/strategy/data/planet_naming.py` | 78 | 0 | Yes | ADVISORY | Constants/procedural naming |
| `game/strategy/data/race_config.py` | 372 | 2 | Yes | VERIFIED | Appears well covered |
| `game/strategy/engine/order_processor.py` | 910 | 2 | Yes | PARTIAL | Multiple test files, but sub-methods need verification |
| `game/strategy/engine/organics_consumption_engine.py` | 108 | 3 | Yes | PARTIAL | Zero-pop, zero-allocation, empty dict edges |
| `game/strategy/engine/quality_engine.py` | 99 | 0 | Yes | MINOR | Has tests but verify line 62-75 (list vs dict abilities) |
| `game/strategy/events/event_types.py` | 38 | 2 | No | ADVISORY | Enums only, no logic |
| `game/strategy/generation/density/primitives/density_primitive.py` | 45 | 2 | No | ADVISORY | Protocol + clamp helper only |
| `game/strategy/generation/density/primitives/ring.py` | 63 | 0 | Yes | ADVISORY | Has tests |
| `game/strategy/generation/star_image_registry.py` | 111 | 0 | Yes | ADVISORY | Has tests |
| `game/strategy/interfaces/engines.py` | 714 | 2 | No | ADVISORY | Abstract interfaces, tested via implementations |
| `game/strategy/services/race_resolver.py` | 43 | 2 | No | MAJOR GAP | No dedicated test |
| `game/ui/filters/__init__.py` | 4 | 0 | No | ADVISORY | Re-exports only |
| `game/ui/panels/race_theme_gallery.py` | 191 | 2 | Yes | ADVISORY | UI panel, has tests |
| `game/ui/screens/battle_setup/panels/center_panel.py` | 299 | 2 | No | ADVISORY | UI rendering, no dedicated test |
| `game/ui/screens/builder/modifier_row.py` | 355 | 3 | No | MAJOR GAP | Complex widget, no test |
| `game/ui/screens/planet_target_editor_base.py` | 63 | 1 | No | MINOR | Shared base for 4 editors, no test |
| `game/ui/screens/strategy_colonization.py` | 276 | 3 | Yes | VERIFIED | Has tests |
| `game/ui/screens/strategy_screen_assets.py` | 88 | 0 | Yes | ADVISORY | Has tests |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | 94 | 0 | No | ADVISORY | UI dialog, no test |
| `game/ui/screens/test_lab/details/__init__.py` | 17 | 0 | No | ADVISORY | Re-exports only |
| `game/ui/screens/test_lab/renderer/header_panel.py` | 152 | 2 | No | ADVISORY | UI rendering, no dedicated test |
| `game/ui/screens/test_lab/test_run_details.py` | 12 | 2 | No | ADVISORY | Shim re-export, no logic |
| `game/ui/screens/workshop_event_router.py` | 545 | 2 | No | MINOR | Event routing, no test, >300 LOC |
| `game/ui/screens/workshop_viewmodel_ship_ops.py` | 330 | 2 | No | MINOR | Ship CRUD operations, no test |
| `game/ui/services/battle_ui_service.py` | 299 | 2 | Yes | ADVISORY | Has tests |
| `game/ui/services/modifier_icon_service.py` | 87 | 2 | No | MAJOR GAP | No tests |
| `game/ui/utils/resource_display.py` | 58 | 2 | No | MINOR | No tests |

---

## Context Usage Estimate

| Phase | Operations |
|---|---|
| Production files read | 38 files (~8326 LOC) |
| Test files searched | ~40 glob patterns across all domains |
| Test files verified (spot-check) | 4 files fully read, ~15 identified |
| Coverage matrix consulted | 1 file (filtered to shard entries) |
| Architecture docs read | 3 files (01_ARCHITECTURE.md, 02_PATTERNS.md, 03_CONVENTIONS.md) |
| **Estimated context tokens** | ~180K |
