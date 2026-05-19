# PROJ-454 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 — F-B-004: retire `effect_ability_metadata.py`

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/effect_ability_metadata.py` | Production (delete) | Delete the 131-LOC shim. |
| `game/strategy/services/effect_ability_display.py` | Production (modified) | Line 20: migrate `from game.strategy.services.effect_ability_metadata import find_metadata` → `from game.strategy.services.ability_metadata import find_metadata` (verify the symbol exists on `ability_metadata.py`; if it's renamed, follow the canonical name). |
| `game/strategy/services/system_effects_collector.py` | Production (modified) | Lines 42-45: migrate the multi-symbol import (`find_metadata`, `is_known_effect_ability`) from `effect_ability_metadata` → `ability_metadata`. |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/services/test_effect_ability_metadata.py` | Test (delete or rewrite) | Delete outright if `ability_metadata.py` has equivalent coverage. Otherwise rewrite against `ability_metadata.py` and rename to `test_ability_metadata_effects.py` (or similar). Decision in Phase 1 Task 1.3. |

---

## Phase 2 — F-B-005: retire `component_inspector.py`

### Production files (delete)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/component_inspector.py` | Production (delete) | Delete the 67-LOC re-export shim. |

### Production callers — strategy/data (5 files)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/build_queue_source.py` | Production (modified) | Lines 147, 224: migrate `get_component_abilities` → `component_abilities` |
| `game/strategy/data/fleet_capability_calculator.py` | Production (modified) | Lines 65, 111, 188, 208, 237, 256: migrate `ship_has_ability` / `count_ability` / `has_warp_capability` / `list_ship_abilities` → `component_abilities` |
| `game/strategy/data/planetary_facility.py` | Production (modified) | Line 12: migrate `get_component_abilities` → `component_abilities` |
| `game/strategy/data/ship_instance.py` | Production (modified) | Lines 635, 654, 663: migrate `count_damaged_components` / `iter_components_by_layer` / `damaged_components_by_layer` → `component_layers` |

### Production callers — strategy/engine (8 files)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/atmosphere_engine.py` | Production (modified) | Line 15: `iter_facility_ability_entries` → `component_abilities` |
| `game/strategy/engine/consumable_management_engine.py` | Production (modified) | Lines 21, 24: `get_component_abilities` / `get_ability_list` → `component_abilities` |
| `game/strategy/engine/harvesting_engine.py` | Production (modified) | Line 27: `get_component_abilities` → `component_abilities` |
| `game/strategy/engine/planet_action_engine.py` | Production (modified) | Lines 311, 325, 339, 388: `extract_abilities_from_component` / `iter_facility_ability_entries` → `component_abilities` |
| `game/strategy/engine/planet_energy_engine.py` | Production (modified) | Lines 28, 88: `iter_facility_ability_entries` / `extract_abilities_from_component` → `component_abilities` |
| `game/strategy/engine/quality_engine.py` | Production (modified) | Line 14: `iter_facility_ability_entries` → `component_abilities` |
| `game/strategy/engine/resupply_engine.py` | Production (modified) | Lines 23, 27: `get_component_abilities` / `get_ability_list` → `component_abilities` |
| `game/strategy/engine/water_engine.py` | Production (modified) | Line 14: `iter_facility_ability_entries` → `component_abilities` |

### Production callers — strategy/services and strategy/validation (5 files)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/ability_sources/facility.py` | Production (modified) | Line 14: `extract_abilities_from_component` → `component_abilities` |
| `game/strategy/services/ability_sources/fleet.py` | Production (modified) | Line 137: `extract_abilities_from_component` → `component_abilities` |
| `game/strategy/services/action_time_resolver.py` | Production (modified) | Lines 34, 242: multi-symbol imports → `component_abilities` |
| `game/strategy/services/strategic_ability_scanner.py` | Production (modified) | Line 14: `extract_abilities_from_component` → `component_abilities` |
| `game/strategy/validation/planet_order_validator.py` | Production (modified) | Line 13: `get_component_abilities` → `component_abilities` |
| `game/strategy/validation/superweapon_validator.py` | Production (modified) | Line 8: multi-symbol import → `component_abilities` |

### Production callers — UI (6 files) — **edit only the import statement; do NOT refactor UI behaviour**

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/fleet_data_source.py` | Production (modified) | Lines 234, 266: migrate `has_warp_capability` / `ship_has_ability` → `component_abilities`. UI behaviour stays as-is. |
| `game/ui/screens/fleet_report_filters.py` | Production (modified) | Lines 12, 186, 313: migrate `has_warp_capability` / `ship_has_ability` → `component_abilities`. UI behaviour stays as-is. |
| `game/ui/screens/planet_abilities_controller.py` | Production (modified) | Lines 112, 142: multi-symbol imports → `component_abilities`. UI behaviour stays as-is. |
| `game/ui/screens/strategy_detail_fmt.py` | Production (modified) | Line 405: `extract_abilities_from_component` → `component_abilities`. UI behaviour stays as-is. |
| `game/ui/screens/strategy_detail_formatter.py` | Production (modified) | Line 305: `extract_abilities_from_component` → `component_abilities`. UI behaviour stays as-is. |
| `game/ui/screens/strategy_fleet_command_router.py` | Production (modified) | Line 263: `extract_abilities_from_component` → `component_abilities`. UI behaviour stays as-is. |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/services/test_component_inspector_surface.py` | Test (delete or refactor) | Static drift gate against the shim. Decision in Phase 2 Task 2.10: delete (shim is gone) OR refactor into a guard against re-emergence of the shim (mirroring `test_no_design_library_class.py` / `test_no_resource_types_constant.py`). |
| `tests/unit/strategy/test_component_inspector.py` | Test (modified or migrated) | Line 9: multi-symbol import → `component_abilities` / `component_layers`. Rename file to match the destination module(s) if convenient. |
| `tests/unit/strategy/test_fleet_capability_calculator.py` | Test (modified) | Lines 257, 279, 296, 318: `patch('game.strategy.services.component_inspector.has_warp_capability', ...)` → `patch('game.strategy.services.component_abilities.has_warp_capability', ...)`. |
| `tests/unit/ui/screens/test_fleet_data_source.py` | Test (modified) | Lines 296, 301, 456, 469, 486: 5 `patch(...)` targets need repointing to `component_abilities`. |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test (modified) | Lines 345, 352, 359, 366, 373, 380, 863, 1079, 1105, 1155, 1178: **11 `patch(...)` targets** need repointing. Largest test-side migration in the project. |
| `tests/unit/ui/screens/test_strategy_fleet_command_router.py` | Test (modified) | Lines 415, 458: 2 `patch(...)` targets → `component_abilities`. |
| `tests/integration/test_design_load_warp_capability.py` | Test (modified) | Line 30: `has_warp_capability` import → `component_abilities`. |

---

## Phase 3 — F-B-017: unwind `OrderProcessor.process_*` facade reshape

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/order_processor.py` | Production (modified) | Delete lines 39-58 (the three dataclasses `JoinFleetResult` / `ColonizeResult` / `TransferResult`) AND lines 97-143 (the three `process_join_fleet` / `process_colonize` / `process_transfer` facade methods). Update the module docstring at lines 1-20 to remove the legacy-types narration. |

### Test caller files (migrate to read `OrderExecutionResult` directly)

**Inventory corrected by codex audit 2026-05-19: 68 call sites across 12 test files (original audit cited ~15 sites / 7 files — undercount of more than 4×).**

| File | Type | Notes |
|------|------|-------|
| `tests/integration/colonization/test_explicit_orders.py` | Test (modified) | **3 call sites** — lines 65, 91, 105: replace `processor.process_transfer(...)` with `processor.get_handler(OrderType.TRANSFER).execute_action_order(...)`. Read `result.success` / `result.amount_transferred` / `result.message` directly from the `OrderExecutionResult`. |
| `tests/integration/colonization/test_planet_specific_colonization.py` | Test (modified) | **7 call sites** — lines 286, 380, 390, 473, 484, 520, 550: replace `processor.process_colonize(...)` calls with the handler-direct path. |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | Test (modified) | **1 call site** — line 212: replace `processor.process_join_fleet(...)` call with the handler-direct path. |
| `tests/unit/strategy/engine/test_colonize_population.py` | Test (modified) | **6 call sites + 1 import** — line 22: drop `ColonizeResult` import (the dataclass is gone); lines 180, 211, 245, 280, 310, 341: replace `processor.process_colonize(...)` with handler-direct calls (count corrected from 2 to 6 by codex audit 2026-05-19). |
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | Test (modified) | **3 call sites** — lines 97, 106, 115: added by codex audit 2026-05-19; was missing from the original inventory. Migrate each `processor.process_transfer(...)` per the standard recipe. |
| `tests/unit/strategy/engine/test_order_processor_colonize.py` | Test (modified) | **7 call sites + 2 docstring/comment refs** — lines 105, 124, 157, 181, 213, 245, 283: migrate each `proc.process_colonize(...)` (count corrected by codex audit 2026-05-19). Lines 102, 304 docstring/comment: update narration. |
| `tests/unit/strategy/engine/test_order_processor_instant.py` | Test (modified) | **2 call sites** — lines 247, 268: added by codex audit 2026-05-19. Migrate `proc.process_join_fleet(...)` calls; update narration at lines 8, 234, 238, 254. |
| `tests/unit/strategy/engine/test_order_processor_transfer.py` | Test (modified) | **10 call sites** — lines 74, 112, 131, 169, 201, 231, 268, 302, 332, 369: added by codex audit 2026-05-19; was missing from the original inventory. **Second-largest single-file migration in Phase 3.** |
| `tests/unit/strategy/engine/test_process_colonize_validation.py` | Test (modified) | **6 call sites** — lines 201, 234, 271, 307, 386, 420: added by codex audit 2026-05-19; was missing from the original inventory. Update file docstring (lines 2-6) and section docstrings (176, 320). Consider rename to `test_colonize_handler_validation.py`. |
| `tests/unit/strategy/engine/test_transfer_order.py` | Test (modified) | **7 call sites + 1 import** — line 15: drop `TransferResult` import; migrate all 7 `process_transfer` call sites at lines 196, 230, 262, 293, 327, 372, 414. (Line 103 is a docstring narration, not a call.) |
| `tests/unit/strategy/test_engine_event_emission.py` | Test (modified) | **5 call sites** — lines 496, 528, 592, 991, 1047: added by codex audit 2026-05-19; was missing from the original inventory. Migrate each `processor.process_colonize(...)`. (Line 478 is a docstring narration, not a call.) |
| `tests/unit/strategy/test_fleet_order_processor.py` | Test (modified) | **11 call sites — LARGEST single-file migration in Phase 3** — lines 82, 102, 116, 129, 196, 224, 245, 269, 520, 549, 577: added by codex audit 2026-05-19; was missing from the original inventory. Mixes `process_join_fleet` (4 sites) and `process_colonize` (7 sites). |
| `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` | Test (review) | Lines 33, 37, 53-54: docstring mentions the facade methods; either update the test to assert the unified-result path, or delete if obsolete. Phase 3 Task 3.9 decides. |

---

## Phase 4 — F-B-018: refresh `OrderExecutionResult` legacy-field framing

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/order_handlers/base.py` | Production (modified) | Lines 46-55: drop the `# JoinFleet legacy field` / `# Colonize legacy field` / `# Transfer legacy field` inline comments. Update the class docstring at lines 36-45 to remove the legacy-typed-result narration; describe the current unified contract. If any of the 5 fields are now demonstrably unused post-Phase-3 (verify with grep), delete those fields and add a `decisions.md` row explaining what was kept and why. |

### Test files

| File | Type | Notes |
|------|------|-------|
| (none expected) | | Phase 4 is a documentation-only refresh unless Phase 3 surfaced a field that's dead. |

---

## Cross-bucket conflicts to watch

| File | Other projects touching | Resolution |
|------|------------------------|------------|
| `game/strategy/engine/order_processor.py` | **PROJ-453 Task 1.2** (annotate `__init__`) | Sites are disjoint within the file. If PROJ-453 lands first (preferred per Codex r4 redesign), the diff is cleaner. If PROJ-454 Phase 3 lands first, PROJ-453's `__init__` annotation rebases trivially. |
| `game/strategy/engine/order_handlers/base.py` | None | No conflict. |
| `game/strategy/services/effect_ability_metadata.py` | None — exclusive PROJ-454 target | No conflict. |
| `game/strategy/services/component_inspector.py` | None — exclusive PROJ-454 target | No conflict. |
| UI files in Phase 2 (`fleet_data_source.py`, `fleet_report_filters.py`, etc.) | None — PROJ-454 touches only import statements; UI shim retirement (Codex r4 job #8) is a future project | No conflict expected, but **strict discipline required**: don't touch UI behaviour. |

## File count summary

- **Phase 1**: 4 production files touched (1 delete, 2 modified, 1 test delete-or-rewrite)
- **Phase 2**: 1 production file deleted, ~24 production files modified (import lines only), ~7 test files modified (multiple patch-target repoints each), 1 static-guard test deleted or refactored. **Site count corrected by codex audit 2026-05-19: ~68 references = 52 `from ... import` + 16 `patch(...)` targets, across ~31 distinct files (up from `~45 sites` in original estimate).**
- **Phase 3**: 1 production file modified (large delete), **12 test files modified (up from `~7` in original estimate)** = **68 call sites total** (codex audit 2026-05-19 corrected from `~15 sites / 7 files`).
- **Phase 4**: 1 production file modified (small)

- **Total production LOC delta:** ≈-300 LOC (two shim deletes + facade method delete + dataclass deletes; ~50 net additions from import-line repoints)
- **Total test LOC delta:** ≈-100 LOC (deleted test files) + ≈+50 LOC from patch-target repoints
