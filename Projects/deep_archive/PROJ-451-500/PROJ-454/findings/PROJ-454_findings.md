# PROJ-454 Findings (consolidated)

Source: `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`. All four findings (F-B-004, F-B-005, F-B-017, F-B-018) extracted verbatim below. File:line references **re-verified against current code on 2026-05-19** before this file was written.

---

## F-B-004 — `effect_ability_metadata.py` shim is still in place after PROJ-429 (decisions.md flagged the collapse as a follow-up)
- **Severity**: low
- **Category**: obsolete-code (intentional deferred-shim per PROJ-429 decisions.md row 2)
- **File**: `game/strategy/services/effect_ability_metadata.py:1-131`
- **Symbol**: module-level (`EffectAbilityMetadata`, `EFFECT_ABILITY_METADATA`, `find_metadata`, `is_known_effect_ability`, `all_owner_aware_scopes`)
- **Source refactor**: PROJ-429 (unified `AbilityMetadataRegistry`) — explicitly deferred
- **What survived**: The file's own header documents the deferral: "Collapsing this shim is intentionally OUT of scope for PROJ-429 (decisions.md row 2). The shim isolates the migration; a follow-up project will collapse it once all downstream callers are ready to migrate to the unified registry directly." Live consumers: `system_effects_collector.py:42-45` (`find_metadata`, `is_known_effect_ability`), `effect_ability_display.py:20` (`find_metadata`). Equivalent symbols already exist on `ability_metadata.py`.
- **Why it's a problem**: It's deferred dead-on-arrival code — 131 LOC of pure delegation. Every change to the underlying registry has to be mirrored across two surfaces. Forward-friction is real because callers can't tell which is "current".
- **Suggested action**: Sweep the two callers (`system_effects_collector.py`, `effect_ability_display.py`) to import directly from `ability_metadata.py`; delete `effect_ability_metadata.py`. Move the `_OWNER_AWARE_SCOPES` constant inline at its single use-site or to `ability_metadata.py`.
- **Effort**: small
- **Status as of 2026-05-19**: open. Verified the file still exists at 131 LOC with intact module docstring (lines 1-26 of the file).

### F-B-004 caller list (verified 2026-05-19)

```
game/strategy/services/effect_ability_display.py:20:from game.strategy.services.effect_ability_metadata import find_metadata
game/strategy/services/system_effects_collector.py:42:from game.strategy.services.effect_ability_metadata import (
tests/unit/strategy/services/test_effect_ability_metadata.py:4:from game.strategy.services.effect_ability_metadata import (
```

Three sites total: 2 production + 1 test.

---

## F-B-005 — `component_inspector.py` re-export shim survives PROJ-433 split
- **Severity**: low
- **Category**: obsolete-code (intentional re-export shim — but unbounded in time)
- **File**: `game/strategy/services/component_inspector.py:1-67`
- **Symbol**: module-level re-exports (16 symbols)
- **Source refactor**: PROJ-433 (file-split for 500-LOC ceiling)
- **What survived**: The full 67-line module is a re-export of names from `component_abilities` + `component_layers`. The header explicitly states "preserved as a thin re-export so the ~50 existing `from game.strategy.services.component_inspector import X` call sites across engines, UI, validators, and tests keep working unchanged."
- **Why it's a problem**: ~50 production + test imports still route through the shim rather than the canonical modules. Each round of new feature work that touches one of these callers is the natural moment to migrate the import — but the shim keeps the bypass alive indefinitely.
- **Suggested action**: One mechanical sweep — `from game.strategy.services.component_inspector import` → `from game.strategy.services.component_abilities import` (Surface A names) or `from game.strategy.services.component_layers import` (Surface B names). Then delete `component_inspector.py`.
- **Effort**: small (per the original scan; revised to **medium-large** here based on the 2026-05-19 caller count of ~68 sites — 52 imports + 16 patch targets).
- **Status as of 2026-05-19**: open. Verified 67 LOC of pure re-exports; 16 symbols split between two destination modules per the file header.

### F-B-005 symbol map (canonical)

Per `component_inspector.py:28-47` (the actual re-export block):

**Surface A — `game/strategy/services/component_abilities.py`** (12 symbols):
- `count_ability`
- `extract_abilities_from_component`
- `find_ship_with_ability`
- `get_ability_list`
- `get_component_abilities`
- `get_component_threshold`
- `get_component_type`
- `has_warp_capability`
- `iter_facility_ability_entries`
- `iterate_design_components`
- `list_ship_abilities`
- `ship_has_ability`

**Surface B — `game/strategy/services/component_layers.py`** (4 symbols):
- `count_damaged_components`
- `damaged_components_by_layer`
- `iter_components_by_layer`
- `lookup_design_max_hp`

### F-B-005 caller list — production (verified 2026-05-19)

```
game/strategy/data/build_queue_source.py:147,224         (get_component_abilities — Surface A)
game/strategy/data/fleet_capability_calculator.py:65,111,188,208,237,256   (ship_has_ability, count_ability, has_warp_capability, list_ship_abilities — Surface A)
game/strategy/data/planetary_facility.py:12              (get_component_abilities — Surface A)
game/strategy/data/ship_instance.py:635,654,663          (count_damaged_components, iter_components_by_layer, damaged_components_by_layer — Surface B)
game/strategy/engine/atmosphere_engine.py:15             (iter_facility_ability_entries — Surface A)
game/strategy/engine/consumable_management_engine.py:21,24    (get_component_abilities, get_ability_list — Surface A)
game/strategy/engine/harvesting_engine.py:27             (get_component_abilities — Surface A)
game/strategy/engine/planet_action_engine.py:311,325,339,388  (extract_abilities_from_component, iter_facility_ability_entries — Surface A)
game/strategy/engine/planet_energy_engine.py:28,88       (iter_facility_ability_entries, extract_abilities_from_component — Surface A)
game/strategy/engine/quality_engine.py:14                (iter_facility_ability_entries — Surface A)
game/strategy/engine/resupply_engine.py:23,27            (get_component_abilities, get_ability_list — Surface A)
game/strategy/engine/water_engine.py:14                  (iter_facility_ability_entries — Surface A)
game/strategy/services/ability_sources/facility.py:14    (extract_abilities_from_component — Surface A)
game/strategy/services/ability_sources/fleet.py:137      (extract_abilities_from_component — Surface A)
game/strategy/services/action_time_resolver.py:34,242    (multi-symbol — Surface A)
game/strategy/services/strategic_ability_scanner.py:14   (extract_abilities_from_component — Surface A)
game/strategy/validation/planet_order_validator.py:13    (get_component_abilities — Surface A)
game/strategy/validation/superweapon_validator.py:8      (multi-symbol — Surface A)
game/ui/screens/fleet_data_source.py:234,266             (has_warp_capability, ship_has_ability — Surface A)  *** UI: edit only the import, do NOT refactor behaviour ***
game/ui/screens/fleet_report_filters.py:12,186,313       (has_warp_capability, ship_has_ability — Surface A)  *** UI ***
game/ui/screens/planet_abilities_controller.py:112,142   (multi-symbol — Surface A)  *** UI ***
game/ui/screens/strategy_detail_fmt.py:405               (extract_abilities_from_component — Surface A)  *** UI ***
game/ui/screens/strategy_detail_formatter.py:305         (extract_abilities_from_component — Surface A)  *** UI ***
game/ui/screens/strategy_fleet_command_router.py:263     (extract_abilities_from_component — Surface A)  *** UI ***
```

24 production caller files (some with multiple call sites).

### F-B-005 caller list — tests (verified 2026-05-19)

```
tests/integration/test_design_load_warp_capability.py:30   (has_warp_capability — Surface A)
tests/unit/strategy/test_component_inspector.py:9          (multi-symbol — likely both surfaces; verify at task start)
tests/unit/strategy/test_fleet_capability_calculator.py:257,279,296,318   (4 × patch('game.strategy.services.component_inspector.has_warp_capability', ...))
tests/unit/strategy/services/test_component_inspector_layers.py            (Surface B tests; rename file when migrating)
tests/unit/strategy/services/test_component_inspector_surface.py:43,56,68  (Static drift gate; decide delete-or-refactor in Phase 2 Task 2.10)
tests/unit/ui/screens/test_fleet_data_source.py:296,301,456,469,486        (5 × patch(...))
tests/unit/ui/screens/test_fleet_report_filters.py:345,352,359,366,373,380,863,1079,1105,1155,1178   (11 × patch(...) — largest test-side caller)
tests/unit/ui/screens/test_strategy_fleet_command_router.py:415,458        (2 × patch(...))
```

Plus the original `tests/unit/strategy/test_component_inspector.py` (a unit-test file targeting the shim's exports directly).

Approximate test-side total: 8-10 files with multiple call sites each → 25-30 individual patch/import lines.

### F-B-005 caller-discovery commands (canonical scaffolding per project brief)

```bash
# All live callers — production + tests:
git grep -nE "from game\.strategy\.services\.component_inspector import|game\.strategy\.services\.component_inspector\." game/ tests/

# Patch-target sites (need careful migration to the canonical module path):
git grep -n "game.strategy.services.component_inspector\." tests/

# Per-symbol discovery (run after Phase 2 Task 2.1 to confirm individual surface assignment):
for sym in get_component_abilities extract_abilities_from_component get_component_type \
           get_component_threshold iterate_design_components iter_facility_ability_entries \
           ship_has_ability find_ship_with_ability count_ability list_ship_abilities \
           get_ability_list has_warp_capability iter_components_by_layer \
           damaged_components_by_layer count_damaged_components lookup_design_max_hp; do
  echo "=== $sym ==="
  git grep -n "$sym" game/ tests/ | grep -v "component_inspector\|component_abilities\|component_layers"
done
```

---

## F-B-017 — `OrderProcessor` facade still reshapes `OrderExecutionResult` back into pre-PROJ-368 legacy typed result dataclasses
- **Severity**: medium
- **Category**: obsolete-code (facade-side legacy result reshape blocking the Protocol unification from completing)
- **File**: `game/strategy/engine/order_handlers/base.py:36-56`, `game/strategy/engine/order_processor.py:97-143` (verified 2026-05-19)
- **Symbol**: `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` + the legacy result types `JoinFleetResult` / `ColonizeResult` / `TransferResult`
- **Source refactor**: PROJ-368 (facade), PROJ-438 Phase 6 (unified `execute_for_issuer` — but the `execute_action_order` facade reshape was left as-is)
- **What survived**: The concrete handler signatures themselves are NOT mismatched — `JoinFleetHandler.execute_action_order` at `join_fleet.py:50-57`, `ColonizeHandler.execute_action_order` at `colonize.py:45-52`, and `TransferHandler.execute_action_order` at `transfer.py:64-71` all already accept the full 5-kwarg shape with defaults (verified by Codex consult 2026-05-18). What DOES survive is the facade-side reshape: `OrderProcessor.process_join_fleet/process_colonize/process_transfer` still wrap `OrderExecutionResult` back into `JoinFleetResult` / `ColonizeResult` / `TransferResult` for legacy callers, and `OrderExecutionResult` at `base.py:36-56` still carries the five per-handler "legacy fields" (`merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`) explicitly to support that reshape.
- **Why it's a problem**: The Protocol unification is half-finished at the facade boundary. The handlers are already on the unified contract, but the facade still hand-rebuilds the pre-PROJ-368 typed dataclasses for external callers. Same survival pattern PROJ-438 Phase 6 cleaned up for `execute_for_issuer` is still present here for `execute_action_order` callers.
- **Suggested action**: Audit characterization callers (per the PROJ-333 comment at `order_processor.py:14-19`); migrate them to read `OrderExecutionResult` directly; then drop `JoinFleetResult` / `ColonizeResult` / `TransferResult` and the `process_join_fleet` / `process_colonize` / `process_transfer` facade methods. F-B-018 follows naturally once this lands.
- **Effort**: medium
- **Status as of 2026-05-19**: open. Verified the three facade methods still present at order_processor.py:97-143 + the three dataclasses at :39-58.

### F-B-017 caller list (verified 2026-05-19)

Production sites — **zero**. The `process_*` facade methods are only consumed by tests today.

Test sites:
```
tests/integration/colonization/test_explicit_orders.py:65,91,105            (process_transfer — 3 sites)
tests/integration/colonization/test_planet_specific_colonization.py:286,380,390,473,484,520,550   (process_colonize — 7 sites)
tests/integration/strategy/test_fleet_registration_lifecycle.py:212         (process_join_fleet — 1 site)
tests/unit/strategy/engine/test_colonize_population.py:22 (import), 180, 211   (process_colonize + ColonizeResult import)
tests/unit/strategy/engine/test_transfer_order.py:15 (import) + any process_transfer sites in the file
tests/unit/strategy/engine/test_order_processor_colonize.py:102 (docstring)  (the no-order edge case)
tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py:33,37,53-54   (facade docstring — review)
```

12-15 test call sites across 7 files.

### F-B-017 caller-discovery command

```bash
git grep -nE "process_join_fleet|process_colonize|process_transfer\b" game/ tests/
git grep -nE "JoinFleetResult|ColonizeResult|TransferResult" game/ tests/
```

---

## F-B-018 — `OrderExecutionResult` carries 5 "legacy field" attributes documented as facade-reshape compensation
- **Severity**: low
- **Category**: obsolete-code (follow-on cleanup blocked by F-B-017)
- **File**: `game/strategy/engine/order_handlers/base.py:46-55` (verified 2026-05-19)
- **Symbol**: `OrderExecutionResult` (fields `merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred`)
- **Source refactor**: PROJ-368
- **What survived**: Five per-handler "extras" on a unified result type so the facade can re-cast to legacy types. Inline comments explicitly label them: `# JoinFleet legacy field`, `# Colonize legacy field`, `# Transfer legacy field`.
- **Why it's a problem**: Couples the shared result type to specific handler outputs; new handlers can't follow the pattern cleanly. Untangle is blocked by F-B-017 — but worth tracking separately because it can ship in the same PR.
- **Suggested action**: Once F-B-017 is resolved, drop the "legacy field" framing in the comments / docstring (the 5 fields become live on the unified result, not legacy). If any field is unused by any handler post-F-B-017 (verify with grep), delete that field.
- **Effort**: tiny (after F-B-017)
- **Status as of 2026-05-19**: open. Verified all 5 fields + the inline comments at base.py:50-55.

---

## Out-of-scope clarifications (not closed by this project)

- **F-B-001 / F-B-002 / F-B-014 / F-B-019 / F-B-020 / F-B-022** — closed by archived PROJ-445 Phases 1-2; not in PROJ-454 scope.
- **F-B-003** — partial close in archived PROJ-445 Phase 2; remaining `ship._cargo_mgr` private-slot migration deferred to a future ShipInstance delegator project.
- **F-B-006 / F-B-007 / F-B-008 / F-B-009 / F-B-010 / F-B-011 / F-B-012 / F-B-015 / F-B-016 / F-B-021** — owned by PROJ-453 (annotation polish + dead skips + stale docstrings). Do NOT touch in PROJ-454.
- **F-B-013** — joint-phase staging-yard substrate work; deferred until typed-staging-yard project lands.
- **`SuperweaponResult`** — mentioned in `OrderExecutionResult`'s docstring at base.py:42-45 alongside the three legacy result types. SuperweaponOrderProcessor uses a separate facade and is out of PROJ-454's scope.
- **DI-2026-05-18-001 ActionExecutionEngine half** — owned by PROJ-455.
- **DI-2026-05-18-003 / -004 / -005** — owned by PROJ-452.

---

## UI behaviour preservation (Phase 2 critical discipline)

When migrating `component_inspector` imports in the 6 UI files listed under "F-B-005 caller list — production" (UI section), the rule is:

> **Edit only the import statement; do NOT refactor UI behaviour.**

Even when the surrounding UI code is obviously stale — old comments, dead branches, MVVM split residue — those are not in PROJ-454's territory. They're tracked by a separate Codex r4 redesign job (#8 — "UI shim retirement sweep"). If you spot UI residue while doing the Phase 2 import migration, log it via `/claude-di-log` and keep going.

The 6 UI files affected:
- `game/ui/screens/fleet_data_source.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/ui/screens/planet_abilities_controller.py`
- `game/ui/screens/strategy_detail_fmt.py`
- `game/ui/screens/strategy_detail_formatter.py`
- `game/ui/screens/strategy_fleet_command_router.py`

Per-file: 1-3 import-line edits. Run the file's existing tests after each touch; do not modify any other line in the file.
