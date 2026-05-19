# PROJ-446 Phase 3: UI back-compat shim cluster retirement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-446 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 1 (test infra settled) + Phase 2 (static guards + protocol narrowing in place)
**Objective:** Retire 9 back-compat property/method shim clusters on UI screens that survived previous controller/view-model MVVM splits. Same recipe per cluster: find test/peer reads → migrate to canonical source → delete property block. Several files drop under the 500-LOC ceiling as a side effect.

**Cross-bucket file-ownership rule:** Only edit `game/ui/` and tests under `tests/unit/ui/`. **STRUCTURAL JOINT-PHASE handoff:** F-C-020 (shared fixture `tests/fixtures/strategy_entities.py`) is OUT of this phase — it ships in PROJ-444 Phase 3 as a stacked dependency with the wrapper retirement.

**Source-of-truth findings:** [`findings/bucket_c_ui_core_tests_scan.md`](findings/bucket_c_ui_core_tests_scan.md) — F-C-001, F-C-002, F-C-003, F-C-004, F-C-005, F-C-006, F-C-007, F-C-008, F-C-009, F-C-010, F-C-011, F-C-012, F-C-015 (+ DI-2026-05-18-004), F-C-029 (+ DI-2026-05-18-002).

---

## Tasks (ordered smallest-first to build momentum)

### Task 3.1: F-C-005 — Delete draw_grid free function [Simple]
**File:** `game/ui/screens/strategy_render/grid.py:104` (delete); 2 test files (migrate)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/strategy_render/test_grid_and_storms.py -v`

- [ ] Find the 2 test sites calling `draw_grid(r, screen)` (per the finding) — `tests/unit/ui/screens/test_strategy_renderer.py` and `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py`
- [ ] Migrate each test to instantiate `GridLayer` and call its `.draw` method
- [ ] **GREEN**: Delete the module-level `draw_grid` function from `grid.py:104`
- [ ] Run targeted tests; all pass.

### Task 3.2: F-C-006 — Audit build_context legacy kwarg [Small — wider blast radius than initially scoped]
**File:** `game/ui/screens/build_queue_screen.py:84-90`
**Tests (multiple files):**
- `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v` (the actual screen test file — uses `_lifecycle` suffix)
- `pytest tests/unit/ui/panels/test_build_queue_controller.py -v`
- `pytest tests/integration/ui/build_queue_screen/ -v`

- [ ] Run `rg -n "build_context=" game/ tests/` (PowerShell-friendly). Codex 2026-05-18 verified the caller set includes:
  - `game/ui/screens/strategy_build_queue_manager.py` (production caller — in scope: PROJ-446 owns ui/)
  - `tests/unit/ui/panels/test_build_queue_controller.py`
  - `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
  - `tests/integration/ui/build_queue_screen/*.py`
  - Plus the `build_queue_screen.py` consumer itself
- [ ] **Scope note**: This task's caller sweep spills slightly beyond `tests/unit/ui/`. All hits are still in `game/ui/` (production) or `tests/{unit,integration}/ui/` (PROJ-446-owned tests), so no cross-bucket conflict — but the task's blast radius is wider than the canonical "tests/unit/ui only" file-ownership rule suggests. Stay alert.
- [ ] For each caller using `build_context=`: rename to `initial_yard=` per the new kwarg name
- [ ] **GREEN**: Drop the `build_context` parameter from `BuildQueueScreen.__init__`; remove the `effective_initial_yard = initial_yard if initial_yard is not None else build_context` line
- [ ] Run targeted tests for ALL three test paths listed above; full sharded suite to be safe.

### Task 3.3: F-C-007 — Retire RaceSetupScreen._description_controller shim [Simple]
**File:** `game/ui/screens/race_setup/screen.py:277-285`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py -v`

- [ ] Find callers of `screen._description_controller` (search both production and test code)
- [ ] Migrate each to `screen._controller.description_controller` (reads) / `screen._controller.attach_description_controller(...)` (writes)
- [ ] **GREEN**: Delete the @property + @setter pair at lines 277-285
- [ ] Run targeted tests.

### Task 3.4: F-C-010 — Retire OrdersWindow._get_order_description shim [Simple]
**File:** `game/ui/screens/orders_window.py:464-475`
**Tests:** `pytest tests/unit/ui/screens/test_orders_window.py -v`

- [ ] Find callers of `screen._get_order_description(order)` (mostly tests)
- [ ] Migrate each to instantiate `OrderDescriber` and call directly
- [ ] **GREEN**: Delete the shim method
- [ ] Run targeted tests.

### Task 3.5: F-C-012 — Retire EventLogWindow empire_name=None fallback [Simple]
**File:** `game/ui/screens/event_log_window.py:113-116`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py -v`

- [ ] Audit test constructors of `EventLogWindow(...)` — add explicit `empire_name="<some name>"` to each
- [ ] **GREEN**: Change the parameter signature: `empire_name: str` (no `= None` default). Drop the None branch in the title rendering at lines 113-116.
- [ ] Run targeted tests.

### Task 3.6: F-C-001 — Retire BattleSetupState.side_0 / side_1 shim [Small]
**File:** `game/ui/screens/battle_setup_state.py:172` (property block 178-192); plus 2 production files + 5 tests
**Tests:** `pytest tests/unit/ui/screens/ -k battle_setup -v`

- [ ] Find callers: 2 production (`battle_setup_state.py` itself + `battle_setup/controller.py`) + 5 tests per the finding
- [ ] Migrate each `state.side_0` → `state.sides[0]` (or `state.get_side(team_id=0)` if there's a canonical accessor)
- [ ] **GREEN**: Delete the `side_0` / `side_1` property pair at lines 172, 178-192
- [ ] Run targeted tests.

### Task 3.7: F-C-002 — Add intentional-broad-catch marker on transfer_dialog._on_confirm [Simple]
**File:** `game/ui/screens/transfer_dialog.py:412`

- [ ] Read the existing `except Exception:` at line 412 + the body comment "Catastrophic dispatch failure — close the modal..."
- [ ] **GREEN**: Add `# Intentional broad catch: catastrophic dispatch failure must not leave modal in inconsistent state` on the same line or immediately above. Match the convention used elsewhere in `game/ui/`.
- [ ] No test change.

### Task 3.8: F-C-003 + F-C-011 + F-C-029 + DI-2026-05-18-002 — Joint transfer_dialog shim retirement [Medium]
**Files:**
- `game/ui/screens/transfer_dialog.py:279-286` (F-C-003 — 3 method shims)
- `game/ui/screens/transfer_dialog.py:58-66` (F-C-011 — sentinel + layout constant re-exports)
- `tests/unit/ui/screens/test_transfer_dialog.py:74-75` + `test_transfer_dialog_enhanced.py:49` + `test_transfer_dialog_characterization.py` (70+ refs) (F-C-029)
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog*.py -v`

- [ ] This is the biggest cluster in Phase 3. Closes both DI-2026-05-18-002 and the F-C trio.
- [ ] **GREEN — test migration**: Mechanical sweep across `test_transfer_dialog*.py`:
  - `dialog._row_data` → `dialog.view_model.row_data`
  - `dialog._current_source` → `dialog.view_model.current_source`
  - `dialog._current_target` → `dialog.view_model.current_target`
  - `dialog._filter_empty` → `dialog.view_model.filter_empty`
  - `dialog.available_sources` → `dialog.view_model.available_sources`
  - `dialog.available_targets` → `dialog.view_model.available_targets`
  - `dialog.pending_transfers` → `dialog.view_model.pending_transfers`
- [ ] **GREEN — delete method shims**: Remove `_extract_dropdown_value`, `_format_pending`, `_discover_pod_designs` at transfer_dialog.py:279-286
- [ ] **GREEN — move sentinels/layout constants**: Move `_MAX_SENTINEL` and the layout constants at transfer_dialog.py:58-66 to `TransferGridRenderer` or `TransferViewModel` (their owning module). Update the 1-2 importers. Delete the class-level re-exports.
- [ ] Verify `transfer_dialog.py` is now under 500 LOC (was 523; F-C-029 expected to drop ~23 LOC + the F-C-003/F-C-011 cleanup adds more headroom)
- [ ] Run targeted tests.
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-002 as `resolved`.

### Task 3.9: F-C-004 — Retire StrategyRenderer 6 cache-attr shims [Simple]
**File:** `game/ui/screens/strategy_renderer.py:107-130`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`

- [ ] Find tests reading `_bg_image`, `_bg_scaled`, `_bg_scaled_size`, `_bg_brightness`, `_hex_outline_cache`, `_hex_outline_cache_turn` directly on the renderer
- [ ] Migrate each to read through the layer objects (`renderer._background._bg_image`, `renderer._hex_outlines._cache`, etc.) — better, audit whether the test should poke private cache state at all. If it shouldn't, replace with a public assertion.
- [ ] **GREEN**: Delete the 6 @property shims at lines 107-130
- [ ] Run targeted tests.

### Task 3.10: F-C-008 — Retire NewGameSetupScreen 6 VM property shims [Small]
**File:** `game/ui/screens/new_game_setup_screen.py:272-321`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_screen.py -v`

- [ ] Find callers of `screen.player_count`, `screen.galaxy_type`, `screen.system_count`, `screen.player_races`, `screen.active_race_modal`, `screen.race_modal_player_index` (production + tests)
- [ ] Migrate each to `screen._view_model.<name>`
- [ ] **GREEN**: Delete the 6 @property + @setter pairs at lines 272-321
- [ ] Verify `new_game_setup_screen.py` (was 734) drops; record new LOC in decisions.md
- [ ] Run targeted tests.

### Task 3.11: F-C-009 — Retire BattleSetupScreen 11 VM/controller shims [Small]
**File:** `game/ui/screens/battle_setup/screen.py:93-205`
**Tests:** `pytest tests/unit/ui/screens/ -k battle_setup -v`

- [ ] Find callers of the 11 shims (5 VM at 93-143, 6 controller at 145-205 per the finding) — read the finding for the exact names
- [ ] Migrate VM shims to `screen.view_model.<name>`; controller shims to `screen.controller.<name>`
- [ ] **GREEN**: Delete the property block(s)
- [ ] Verify `battle_setup/screen.py` (was 559) drops under 500 LOC; record in decisions.md
- [ ] Run targeted tests.

### Task 3.12: F-C-015 + DI-2026-05-18-004 — stat_rows_dynamic LABEL_ABBREV closure [Simple]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py:177-181, 251-254`
**Tests:** `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -v`

- [ ] This is the label-side companion of the already-logged DI-2026-05-18-004 (IDs side). Single PR closes both halves.
- [ ] Drop the two `LABEL_ABBREV` hardcoded dicts at lines 177-181 and 251-254
- [ ] **GREEN**: Add a helper `_label_for(resource_id: str) -> str` that wraps `ResourceCatalog.from_json().get(resource_id).name`. Call it from both label sites.
- [ ] **RED-then-GREEN**: Add a test that adds a new (test-only) resource definition to the catalog and confirms its label surfaces correctly in both rows.
- [ ] Run targeted tests.
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-004 as `resolved`.

---

## Phase Completion Checklist

- [ ] All 12 task groups complete
- [ ] All 9 UI shim clusters retired
- [ ] `transfer_dialog.py` under 500 LOC
- [ ] `new_game_setup_screen.py` and `battle_setup/screen.py` LOC reductions recorded in decisions.md
- [ ] DI-2026-05-18-002 + DI-2026-05-18-004 marked `resolved` in `discovered_issues/log.jsonl`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-446 3` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 4
- [ ] No new entries in `discovered_issues/log.jsonl` unless genuine out-of-scope discoveries

## Notes

- Phase 3 is the largest PROJ-446 phase by task count. Pace yourself; run targeted tests after EACH task (not just at the end).
- Several files naturally drop under the 500-LOC ceiling after shim retirement; record the wins in decisions.md so Phase 4 (UI LOC extractions) can adjust scope.
- Coordination with PROJ-444 Phase 3 (wrapper retirement / F-C-020): If you happen to start Phase 3 before PROJ-444 Phase 3 begins, do NOT touch `tests/fixtures/strategy_entities.py`. That file ships as part of the joint-phase work.
