# PROJ-393 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** Test-injection fallbacks + comment cleanups
**Batch summary:** 11 verified / 0 rejected / 3 uncertain (included) / 2 INFO (included) / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbol | Recommendation | Severity |
|---|---|---|---|---|
| LEG-02-002 | `game/run_loop.py:205` | Legacy `handle_input` branch for RESEARCH_TREE/GALAXY_TEST | migrate scenes to `IScene.handle_event` then delete | MINOR |
| LEG-02-003 | `game/strategy/engine/planet_action_engine.py:366` | `'PlanetaryShield'` hardcoded fallback | delete | MINOR |
| LEG-02-004 | `game/strategy/engine/commands/__init__.py:102, ~286, ~297` | `fleet_id: int  # Kept for backward compat` field on 3 commands | migrate_callers_then_delete | MINOR |
| LEG-02-013 | `build_queue_helpers.py:8`, `strategy_ui.py:25` | module-level `ResourceCatalog.from_json()` | replace with lazy init | MINOR |
| LEG-03-002 | `game/simulation/combat/formation.py:357` | comment-only legacy snap reference | delete (comment only) | MINOR |
| LEG-03-003 | `game/strategy/combat/spec_compiler.py:462` | comment-only EnvironmentalEffects reference | delete (comment only) | MINOR |
| LEG-03-004 | `game/strategy/validation/planet_order_validator.py:66-75` | activate `ability_name` fallback | migrate_callers_then_delete | MINOR |
| LEG-03-005 | `game/strategy/validation/planet_order_validator.py:113-125` | deactivate `ability_name` fallback | migrate_callers_then_delete | MINOR |
| LEG-03-006 | `game/ui/panels/build_queue_drag_handler.py:210-212` | test-fallback branch when callback None | migrate_callers_then_delete | MINOR |
| LEG-03-007 | `game/ui/screens/empire_build_queue_window.py:428-429` | test-fallback branch when facade None | migrate_callers_then_delete | MINOR |
| LEG-04-004 | `game/strategy/engine/order_handlers/transfer_branches.py:107-108` | Legacy/Default first-species fallback | delete (after fleet-cargo-species TODO resolved) | MINOR |

## Rejected

None for this bundle.

## Uncertain (resolved)

| ID | Symbol | Question | User decision |
|---|---|---|---|
| LEG-02-006 | `format_planet_info()` `view is None` branch (15 LOC) | Some callers still pass None (uncolonized planets + pre-PROJ-289 tests). Include or exclude? | **Include** — audit callers, migrate, delete branch |
| LEG-03-023 | 6 Combat Lab instance vars on `BattleScreen` (NOQA, tracked for PROJ-270 Phase 10) | PROJ-270 is archived. Reclaim now or wait? | **Include** — PROJ-270 archived, reclaim now |
| LEG-03-024 | `_LEGACY_PATTERN = re.compile(r"Comp_(\d+)\.\w+$")` in `sprites.py` | Whether dead depends on asset scan. Include or exclude? | **Include** — task starts with asset scan, deletes if no matches |

## INFO (resolved)

| ID | Symbol | User decision |
|---|---|---|
| LEG-02-005 | Historical `# legacy` comment in `save_game_service.py:68` | **Include** — clean up alongside the rest |
| LEG-02-017 | Stale `# PROJ-258` docstring tag at `context.py:13` | **Include** — PROJ-372 is current; update or remove |

## Out of Scope

| ID | Reason |
|---|---|
| LEG-02-001 (`Game.running` flag) | UNCERTAIN-excluded by user — test-bypass backdoor still needed. Recorded in shared [bundling_decisions.md](bundling_decisions.md). |

## Deferred During Implementation

### Phase 3, Task 3.2 (LEG-02-004) — `fleet_id: int  # Kept for backward compat` field
- **Reason:** The audit said "migrate callers to `entity_id`/`entity_type`, then delete `fleet_id`". There is no `entity_id` field on these DTOs to migrate to — only `fleet_id` (canonical, used by handlers) and `entity_type` (declared but unused by handlers). 20+ test sites + 1 production site use `fleet_id=` keyword.
- **Action taken:** Removed the misleading `# Kept for backward compat; use entity_id for new code` tag from `ClearOrdersCommand` (the only of the 3 commands that actually carried it). Updated docstring to explain real state and flag this as future work.
- **Action deferred:** Adding `entity_id` and migrating all callers is a real but separate scope-of-design refactor (likely a sibling of PROJ-238 follow-up).

### Phase 3, Task 3.3 (LEG-02-006) — `format_planet_info` `view=None` branch
- **Reason:** `PlanetSelectionWindow` (`game/ui/screens/planet_selection_window.py:195`) constructs a `PlanetReportPanel` without `view=`, so the panel's internal `format_planet_info` call goes through the legacy branch. PlanetSelectionWindow has no facade access in its `__init__` — only a `planets` list, manager, callbacks. Threading facade through requires touching the call sites (colonization workflow, strategy_event_router) and migrating tests; well beyond a "delete a fallback" cleanup.
- **Action deferred:** PROJ-289-style facade plumbing into PlanetSelectionWindow (and its construction chain). Audit also showed many tests pass `format_planet_info(mock_planet)` with no view — these would all need migration too.
- The branch is also defensively useful for any future caller that legitimately can't supply demographic data (e.g. galaxy-generation preview screens).

### Phase 3, Task 3.5 (LEG-03-023) — `BattleScreen` Combat Lab instance vars
- **Reason:** Vars are not stale; they are actively used by production code, not just legacy back-compat.
- **Evidence:**
  - `headless_mode`: read by `game/run_loop.py:216`, `battle_screen.py:302` (gates the entire headless update path), `battle_screen.py:157` (set from `controller.config.headless`).
  - `test_completed`: read+written by `game/ui/screens/test_lab/screen.py:337,348,360` and `battle_screen.py` test-completion bookkeeping.
  - `test_tick_count`: read by `test_lab/screen.py:346` for results recording.
  - `test_mode`, `test_scenario`: read by `battle_screen.py:490` `is_battle_over` test-mode shortcut.
- The `# NOQA: legacy-retained` comment misled the audit; PROJ-270's archive doesn't mean these are dead, just that *the cleanup is unscheduled*. The real refactor (route Combat Lab visual mode through a non-attribute-stuffing mechanism) is non-trivial and out of PROJ-393's scope.
- Recommendation: file a follow-up project (`PROJ-39x: Combat Lab BattleScreen attribute reclaim`) that designs the proper extraction, with full test_lab integration coverage. PROJ-393 only handles "true legacy" code; this one is "in-flight without a clear owner."

## Stage-Boundary Regressions (Closeout Followup)

The orchestrator's stage-boundary sharded run after PROJ-393's closeout
commit caught 3 test regressions that the phase-scoped focused tests in
the original execution missed. All 3 were caused by the production
fallback removals; in each case the test still exercised the deleted
fallback path via implicit defaults.

| Test | Failure cause | Fix |
|---|---|---|
| `tests/unit/strategy/engine/test_transfer_order.py::TestOrderProcessorTransfer::test_process_transfer_load_passengers_from_colony` | Called passenger LOAD without `species_id`, hit the deleted Legacy/Default first-species fallback (LEG-04-004), got `amount_transferred=0`. | Added `species_id='human'` to the order params (matches the planet's single SpeciesPopulation race_id). |
| `tests/unit/strategy/engine/test_transfer_order.py::TestOrderProcessorTransfer::test_transfer_partial_amount` | Same root cause as above. | Same fix — explicit `species_id='human'`. |
| `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py::test_mouse_motion_pops_from_queue_source` | Asserted `len(construction_queue) == 1` after drag-pickup, but the deleted in-place `construction_queue.pop(idx)` fallback (LEG-03-006) means the canonical path now relies on the injected `on_remove_from_queue` callback to actually mutate the queue. The fixture's `MagicMock()` callback was a no-op. | Reworked the fixture to inject a closure that pops from `single_queue_source.construction_queue`, simulating production's command-dispatch semantics. |

### Lesson — test-side audit gap

The Phase 2/3 checklists called for grepping `tests/` for the affected
constructor or function before deleting the production fallback. That
audit ran successfully for the build_queue_drag_handler and
empire_build_queue_window cases, but missed two failure shapes:

1. `test_drag_handler_multi_queue.py` already passed `on_remove_from_queue=MagicMock()` (added during the original Phase 2 fix), so it appeared migrated — but the `MagicMock` no-op left the assertion `len(queue) == 1` unsatisfiable. The right migration was to inject a real list-mutator, not just a Mock.
2. `test_transfer_order.py` exercises `OrderProcessor` end-to-end with real planet/fleet builders, and the order params dict simply omitted `species_id` rather than naming it. A `species_id` text grep didn't surface this site, and the phase-scoped focused tests (`pytest -k "transfer_branches or transfer_handler"`) didn't reach this integration-shaped path.

The phase-scoped focused tests passed because they target the
unit-level handler/branch files, not the broader order-processor
integration tests. The stage-boundary sharded suite was the right
safety net here. **Future audit step:** when deleting a production
fallback that supplies an implicit default, also grep test fixtures
for params dicts / Mock injection sites that omit the now-required
field.

## Implementation Notes

### Phase 1, Task 1.1 (LEG-02-017) — `PROJ-258` references in `game/context.py`
- Docstring tag at original line 13 (`PROJ-258: Initial implementation as wrapper around existing singletons.`) was the stale-state comment the user wanted cleaned up. **Deleted.**
- Two other `PROJ-258` references remain and are intentionally preserved:
  - Line ~41: docstring inside `get_default_planet_habitability_service` saying "modders may override … (PROJ-258 pattern)" — documents the architectural pattern name; not stale.
  - Line ~162: comment at the start of the `set_default_*` block in `create_production` describing why all module-level references are set in lockstep — current implementation context.
- The checklist's literal grep verification (`grep -rn "PROJ-258" game/context.py" returns zero hits`) is too aggressive. The intent was the stale docstring tag, which is gone.
