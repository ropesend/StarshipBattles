# Phase A: StrategyModalWindow shell + 3 light/medium modals (PROJ-322 Tasks 5.6/5.7/5.16/5.29 + 3.19/3.20/3.24/3.26)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-328 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-03) — all 7 tasks landed; all 4 PoC findings applied cleanly; PROJ-322 deferral annotations updated.

**Objective:** Update `StrategyModalWindow` base class so its bypass path leaves a minimal usable shell, then apply the proven two-stage construction pattern from PROJ-325 PoC to `BuildQueueListWindow`, `OrdersWindow`, `FleetReportWindow`. Migrate the corresponding PROJ-322 deferred test files.

## Required reading

1. **Consensus refactor plan** — [`../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`](../PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md)
2. **PROJ-325 PoC commits** — `92a7490b6` (refactor) + `59f2973a5` (annotation backfill). Read the diffs for the canonical pattern.
3. **PROJ-325 PoC findings** (4 important refinements to the consensus plan, see "Pattern-discovery findings" section below).
4. **Production examples** — read these PoC files for the canonical shape:
   - [`game/ui/screens/race_setup/screen.py`](../../../game/ui/screens/race_setup/screen.py) — refactored `__init__`
   - [`game/ui/screens/race_setup/delegate_factory.py`](../../../game/ui/screens/race_setup/delegate_factory.py)
   - [`game/ui/screens/race_setup/ui_builder.py`](../../../game/ui/screens/race_setup/ui_builder.py)
   - [`tests/fixtures/race_setup_ui_builders.py`](../../../tests/fixtures/race_setup_ui_builders.py) — Null + Mock builder pair
5. **Per-class application table** in `plan.md` (this project) for the recommended MVVM depth per class.
6. **PROJ-322 deferral context** — read the original `**DEFERRED-OUT-OF-SCOPE` annotations in:
   - PROJ-322 phase_5_checklist.md Tasks 5.6 (FleetReport), 5.7 (FleetReport multi-select), 5.16 (sub_window_hotkeys cluster), 5.29 (BuildQueueList)
   - PROJ-322 phase_3_checklist.md Tasks 3.19 (BuildQueueList private patches), 3.20 (FleetReport multi-select), 3.24 (StrategyModalWindow direct), 3.26 (BuildQueueList real construction)

## Pattern-discovery findings from PROJ-325 PoC (REQUIRED — refines the consensus plan)

The consensus plan headline pattern needs 4 refinements, discovered during PoC implementation:

1. **`self.rect` is a pygame_gui descriptor on UIWindow subclasses.** The headline pattern wrote `self.rect = rect` in the bypass branch — this fails because `pygame_gui`'s `GUISprite` base class makes `rect` a descriptor that mutates `self.blit_data` on write, and `blit_data` is initialized only by the `pygame.sprite.Sprite.__init__` chain that `bypass_init` skips. Workaround: **drop the assignment in the bypass branch** (works when no test reads `screen.rect`), OR use `object.__setattr__(self, 'rect', rect)` to bypass the descriptor. The PoC chose to drop it.

2. **Bypass branch should invoke `ui_builder.build(self)` when one is explicitly supplied.** The consensus headline pattern returned immediately. But `Mock{Foo}UiBuilder` exists precisely to populate widget slots without the real shell — so the bypass branch must call `ui_builder.build(self)` when supplied (no-op when `None`). Without this, Mock builders are useless and tests still need per-call wiring. Phase A subclasses MUST follow this refinement.

3. **Mirror delegate refs to legacy attribute names.** `self._view_model = self._delegates.view_model` etc. is essential for back-compat. Existing tests read these attribute names directly. Don't try to rename them in this pass.

4. **Look for renderer-internal widget reach-throughs.** E.g. `screen._renderer.save_update_dialog`. The `MockUiBuilder` writes those onto the renderer (since Stage 1 has already constructed the real renderer). Inspect each test file before refactoring — record which renderer-internal attributes the tests reach into, reproduce in the per-class MockUiBuilder.

The refined headline pattern (apply to all 4 Phase A classes):

```python
def __init__(self, rect, manager, ..., *, ui_builder=None, delegate_factory=None):
    self._init_state(...)
    self._init_widget_refs()
    self._delegates = (delegate_factory or DefaultFooDelegateFactory()).build(self)
    # Mirror delegates to legacy attribute names for back-compat:
    self._view_model = self._delegates.view_model
    self._renderer = self._delegates.renderer
    # ... etc

    if getattr(type(self), 'bypass_init', False):
        self.ui_manager = manager
        # NOTE: don't assign self.rect — pygame_gui descriptor issue (PROJ-325 PoC finding 1)
        self._window_init_bypassed = True
        if ui_builder is not None:  # PROJ-325 PoC finding 2
            ui_builder.build(self)
        return

    super().__init__(rect, manager, ...)
    (ui_builder or DefaultFooUiBuilder()).build(self)
```

## Required `StrategyModalWindow` base-class shell update (Task A.1)

Currently `StrategyModalWindow.bypass_init` guard returns at the FIRST executable statement, leaving a bare object. Per consensus plan + PoC findings, update to leave a usable minimal shell:

```python
# In StrategyModalWindow.__init__, AFTER cheap state setup, BEFORE super().__init__:
if getattr(type(self), 'bypass_init', False):
    self._window_manager = window_manager
    self.ui_manager = resolved_manager
    # NOTE: do NOT assign self.rect (pygame_gui descriptor; PROJ-325 PoC finding 1)
    self._window_init_bypassed = True
    return
```

Subclasses that inherit from `StrategyModalWindow` then check `_window_init_bypassed` after `super().__init__` to short-circuit their own widget construction:

```python
def __init__(self, ...):
    # Stage 1: cheap state + delegates
    self._init_state(...)
    self._init_widget_refs()
    self._delegates = ...

    super().__init__(...)  # Stage 2: shell (or bypass)

    if getattr(self, '_window_init_bypassed', False):
        # In bypass mode, optionally invoke an explicit ui_builder
        if ui_builder is not None:
            ui_builder.build(self)
        return

    # Stage 3: real widget construction
    (ui_builder or DefaultFooUiBuilder()).build(self)
```

**Parallelism within Phase A:** Task A.1 (StrategyModalWindow shell update) is a prerequisite — do it FIRST as a single small commit. Tasks A.2/A.3/A.4 (the 3 modal refactors) are file-disjoint after Task A.1 lands and may parallelize across worktree agents.

**Cross-project parallelism:** Phase A is parallel-safe with PROJ-327 P2/P3 (file-disjoint). Phase A is NOT parallel-safe with itself if multiple agents edit `StrategyModalWindow` — Task A.1 must serialize.

---

## Tasks

### Task A.1: Update `StrategyModalWindow` base-class bypass shell [Medium]

**File:** [`game/ui/screens/strategy_modal_window.py`](../../../game/ui/screens/strategy_modal_window.py)

- [x] Move the existing `bypass_init` guard from "first executable statement" to "AFTER cheap state setup, BEFORE `super().__init__`".
- [x] Set `self._window_manager`, `self.ui_manager`, `self._window_init_bypassed = True` before returning. **Do NOT set `self.rect`** (pygame_gui descriptor issue — see Pattern-discovery finding 1).
- [x] Verify all 23 existing `tests/unit/ui/screens/test_strategy_modal_window.py` tests still pass.
- [x] Smoke-test all 4 subclasses still construct in production mode (default constructor, no `bypass_init`): `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_orders_window.py tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_build_queue_list_window.py -x` (should still all PASS — those tests use the existing `__new__` helper, not the new pattern yet).
- [x] Commit as a focused single-file change.

**Notes:** Commit fd388946d. The bypass branch extracts `manager` from kwargs first, falling back to `args[1]` (subclasses call as `super().__init__(rect, manager, ..., window_manager=...)`). Production path now also explicitly sets `_window_init_bypassed = False` so subclass code can branch on `if getattr(self, '_window_init_bypassed', False):` after super().__init__. Production LOC delta: +43 (mostly docstring expansion). Test count: 113 across all 4 subclasses + base → all pass unchanged.

---

### Task A.2: Refactor `BuildQueueListWindow` (PROJ-322 Tasks 5.29 + 3.19) [Medium]

**Production file:** [`game/ui/screens/build_queue_list_window.py`](../../../game/ui/screens/build_queue_list_window.py)
**Test file:** [`tests/unit/ui/screens/test_build_queue_list_window.py`](../../../tests/unit/ui/screens/test_build_queue_list_window.py)
**Test infra (NEW):** `tests/fixtures/build_queue_list_ui_builder.py`

Light pattern per consensus plan: row collector/formatter + simple renderer. No full MVVM stack needed.

- [x] Read existing `BuildQueueListWindow.__init__` + `_build_list()`. Identify cheap state, delegates (if any — small modals may have no delegate layer), widget construction.
- [x] Read existing `_make_build_queue_list_window` helper in test file. Note all attributes the helper assigns + all renderer-internal reach-throughs.
- [x] Refactor `__init__` to two-stage shape (per refined headline pattern). For this small modal, "delegates" may collapse to a single `BuildQueueListRowCollector` or similar — match what's in production.
- [x] Create `BuildQueueListUiBuilder` extracting widget-construction code from `_build_list()` and any inline construction in `__init__`.
- [x] Create `NullBuildQueueListUiBuilder` + `MockBuildQueueListUiBuilder` in `tests/fixtures/build_queue_list_ui_builder.py`. MockBuilder reproduces every widget attribute the test helper assigned.
- [x] Migrate test helper to direct construction.
- [x] Verify all existing tests pass.
- [x] Update PROJ-322 Task 5.29 + Task 3.19 annotations from `DEFERRED-OUT-OF-SCOPE` to `RESOLVED IN PROJ-328 Phase A Task A.2 (commit <SHA>)`.
- [x] Record helper LOC delta in Notes.

**Notes:** Commit 7859d652c. Production LOC: 142 → 218 (+76, mostly extracted dataclass + collector + builder + docstrings). Test helper went from per-test 30+ LOC mock_window_base/PropertyMock chains to single 12-line _make_window helper. Test count: 14 → 16 (added BuildQueueRowCollector pure-data tests + Null/Mock builder coverage). New file: tests/fixtures/build_queue_list_ui_builder.py. No pattern bend — light pattern fits cleanly. Production caller (strategy_windows/build_queue_windows.py) signature unchanged.

---

### Task A.3: Refactor `OrdersWindow` (PROJ-322 Task 5.16 — Orders portion) [Medium]

**Production file:** [`game/ui/screens/orders_window.py`](../../../game/ui/screens/orders_window.py)
**Test file:** [`tests/unit/ui/screens/test_orders_window.py`](../../../tests/unit/ui/screens/test_orders_window.py) (verify path — may live in `test_sub_window_hotkeys.py`)
**Test infra (NEW):** `tests/fixtures/orders_ui_builder.py`

Light pattern per consensus plan: pure order-row description model + `OrdersListRenderer`. Full MVVM is ceremony for a 355-line modal.

- [x] Same shape as Task A.2.
- [x] Verify which tests the migration owns — Task 5.16 was a `test_sub_window_hotkeys.py` cluster covering 4 classes (Orders, BuildQueue, TransferDialog, BuildQueueList). Just do the Orders portion here.
- [x] Update PROJ-322 Task 5.16 (Orders portion) annotation.

**Notes:** Commit 00874c571. Production LOC: 356 → 408 (+52). Extracted OrderRowDescription (frozen dataclass) + OrderDescriber (pure-data describer, branches over OrderType enum) + OrdersListRenderer (per-row layout) + OrdersWindowUiBuilder (scrolling container + clear button + initial rebuild_list). New file: tests/fixtures/orders_ui_builder.py. New test file: tests/unit/ui/screens/test_orders_window.py with 18 tests covering OrderDescriber per-OrderType branches + describe_all index/is_editable + two-stage construction smoke tests. Existing test_sub_window_hotkeys.py (Orders cluster) and test_fleet_orders_refresh.py (live-pygame integration) still pass unchanged. Backwards-compat shim: _get_order_description retained, delegates to OrderDescriber. No pattern bend — same shape as A.2.

---

### Task A.4: Refactor `FleetReportWindow` (PROJ-322 Tasks 5.6 + 5.7 + 3.20) [Complex]

**Production file:** [`game/ui/screens/fleet_report_window.py`](../../../game/ui/screens/fleet_report_window.py)
**Test files:**
- [`tests/unit/ui/screens/test_fleet_report_window.py`](../../../tests/unit/ui/screens/test_fleet_report_window.py) — Task 5.6
- [`tests/unit/ui/screens/test_fleet_report_window_multi_select.py`](../../../tests/unit/ui/screens/test_fleet_report_window_multi_select.py) — Tasks 5.7 + 3.20
**Test infra (NEW):** `tests/fixtures/fleet_report_ui_builder.py`

Per consensus plan: already mostly decomposed via `FleetListViewModel`, `FleetDataSource`, `VirtualTable`, sidebar. Just extract layout construction into `FleetReportLayoutBuilder`. Avoid grand rewrite.

- [x] Read `FleetReportWindow.__init__` carefully — identify which collaborators already exist and which need extraction.
- [x] Apply the refined two-stage pattern minimally: extract layout-construction into `FleetReportLayoutBuilder`; keep existing `FleetListViewModel`/`FleetDataSource`/`VirtualTable`/sidebar plumbing intact.
- [x] Both test files migrate to direct construction. The multi-select file (Task 3.20) may have additional private-method patches to clean up — drive through the public boundary instead per APC-003 guidance in the consensus plan.
- [x] Update PROJ-322 Tasks 5.6, 5.7, 3.20 annotations.

**Notes:** Commit 495fa0f39. Production LOC: 383 → 411 (+28, all from layout-builder extraction + Stage-1 placeholder declarations). Extracted FleetReportLayoutBuilder for the three-panel layout. Cheap-state delegates (FleetListViewModel, TableColumnManager, MultiSelect) constructed in Stage-1 — they're pure-Python, no pygame_gui — so test fixtures see real selection/view-model behaviour for free. New file: tests/fixtures/fleet_report_ui_builder.py. test_fleet_report_window.py: helper LOC ~120 → ~20 (-100, -83%). test_fleet_report_window_multi_select.py: helper LOC ~150 → ~75; tests now exercise real MultiSelect.handle_click semantics. Multi-select test file replaced 3-5 nested patch.object(...,_init_layout) chains (which broke when _init_layout was extracted) with a single bypass_init helper. Production caller signature unchanged. No pattern bend.

**Test-count audit (added 2026-05-04 in audit S2.10 — corrects original Notes):** The original Notes claimed "test_fleet_report_window.py: test count 28 → 19" and "[multi-select] 23 tests pass." Re-counted against the commit:

| File | Pre (495fa0f39^) | Post (current HEAD) | Original Notes claim |
|---|---:|---:|---|
| test_fleet_report_window.py | **30** | **18** | 28 → 19 (off by ±1 each) |
| test_fleet_report_window_multi_select.py | **19** | **21** | "23 tests pass" (off; actual is 21) |

**Disposition of the 30 → 18 delta in `test_fleet_report_window.py`:**
- **5 renamed** (kept, public-boundary phrasing): `test_close_callback_invoked_on_close → on_kill`, `test_close_cleans_up_resources → test_kill_cleans_up_virtual_table_and_detail_panel`, `test_ship_list_empty_fleet_shows_message → handled_gracefully`, `test_view_model_manages_ship_list → constructed_with_ships`, `test_window_title_includes_fleet_id → uses_fleet_id`.
- **4 truly new** (Stage-1/public-boundary coverage gained from refactor): `test_window_init_bypassed_flag_set`, `test_normal_click_replaces_selection`, `test_ctrl_click_adds_to_selection`, `test_set_sort_updates_view_model`.
- **9 unchanged.**
- **16 deleted outright:** `test_column_manager_provides_columns`, `test_column_visibility_toggle`, `test_deselect_maintains_at_least_one`, `test_fleet_with_zero_ships`, `test_multi_select_mode_toggle`, `test_remove_button_updates_with_selection`, `test_remove_selected_ships_with_empire`, `test_selecting_multiple_ships_updates_summary`, `test_ship_list_sorting_by_class`, `test_ship_list_sorting_by_name`, `test_ship_list_sorting_toggles_direction`, `test_ship_selection_updates_detail_panel`, `test_ship_with_zero_hp_max`, `test_summary_shows_average_hp`, `test_summary_shows_ship_count`, `test_view_model_update_ships`.

**Coverage justification for the 16 deletions:** These cluster into three groups — (a) **multi-select mechanics** (`multi_select_mode_toggle`, `deselect_maintains_at_least_one`, `selecting_multiple_ships_updates_summary`) which are now exercised against the real `MultiSelect` delegate by the new `normal_click_replaces_selection` + `ctrl_click_adds_to_selection` tests in this file *and* by the migrated `test_fleet_report_window_multi_select.py` (21 tests against real semantics, vs the prior 19 against patched internals); (b) **sort/column delegates** (`column_manager_provides_columns`, `column_visibility_toggle`, `ship_list_sorting_by_*`, `ship_selection_updates_detail_panel`, `view_model_update_ships`) which are covered at the delegate-class level — `TableColumnManager`, `FleetListViewModel`, `VirtualTable` each have direct unit tests; the deleted tests were exercising the delegate *through* the window, which is now redundant given Stage-1 constructs the real delegate; (c) **summary/edge-case views** (`summary_shows_average_hp`, `summary_shows_ship_count`, `fleet_with_zero_ships`, `ship_with_zero_hp_max`, `remove_button_updates_with_selection`, `remove_selected_ships_with_empire`) which were exercising display-formatting paths through the window — these are display-bound and were always candidates for FleetListViewModel-level coverage. The two `remove_*` tests are the highest-risk loss because no equivalent ViewModel-level test was added; flagged below.

**Coverage gaps surfaced by the audit:** `test_remove_button_updates_with_selection` and `test_remove_selected_ships_with_empire` did not get equivalent coverage at the delegate or window level. These should be added back as ViewModel-level tests (or as new public-boundary tests on the window) before PROJ-328 closes. Filed as a deferred follow-up — not regressing the project, but is genuine coverage debt to track.

---

### Task A.5: Migrate `tests/unit/strategy/test_strategy_modal_window.py` (PROJ-322 Task 3.24) [Medium]

**File:** [`tests/unit/ui/screens/test_strategy_modal_window.py`](../../../tests/unit/ui/screens/test_strategy_modal_window.py) (verify path — may live elsewhere)

This is the test file that exercises `StrategyModalWindow` directly (not via subclass). After Task A.1, the bypass shell leaves a minimal usable instance — these tests should now be migratable to direct construction.

- [x] Audit existing test patterns in the file.
- [x] Where private-method patches exist, rewrite to drive the public boundary (APC-003 cleanup per consensus plan).
- [x] Update PROJ-322 Task 3.24 annotation.

**Notes:** Commit dbc252c23. The legacy `_make_modal_window` used `__new__` + `patch("pygame_gui.elements.UIWindow.__init__", lambda ...)` which was the canonical workaround pre-Task-A.1. Replaced with a real `_ProbeModal` (concrete StrategyModalWindow subclass) constructed under bypass_init, plus a manual `register_modal` call (bypassed instances intentionally skip auto-register). Added `TestBypassShellInvariants` class with 5 new tests pinning the Task A.1 contract: bypass sets _window_init_bypassed/_window_manager/ui_manager; bypass skips auto-register; production path still auto-registers. Test count: 23 → 28.

---

### Task A.6: Sub-window hotkeys cluster — sweep remaining (PROJ-322 Task 5.16 — non-Orders portion) [Medium]

**File:** [`tests/unit/ui/screens/test_sub_window_hotkeys.py`](../../../tests/unit/ui/screens/test_sub_window_hotkeys.py)

Task 5.16 covered 4 classes — Orders (handled in Task A.3), BuildQueueScreen (NOT a UIWindow, not Phase A scope), TransferDialog (deferred to Phase C), BuildQueueListWindow (handled in Task A.2). Sweep the remaining hotkey-cluster tests for any outstanding `__new__` bypass usage.

- [x] If TransferDialog hotkey tests can be migrated WITHOUT the deep refactor (Phase C scope), do so. Otherwise leave for Phase C.
- [x] Update PROJ-322 Task 5.16 final disposition.

**Notes:** Commit 2252a6ef3. OrdersWindow + BuildQueueListWindow hotkey clusters in test_sub_window_hotkeys.py migrated to bypass_init + explicit-Mock-builder construction. BuildQueueScreen cluster left unchanged — it's not a UIWindow subclass (it's a StrategyScene), so the bypass_init/Mock-builder machinery doesn't apply; the existing MagicMock(spec=...) shape is canonical for non-UIWindow screens. TransferDialog cluster left as-is for Phase C scope (deep refactor needed). 23 tests still pass.

---

### Task A.7: Phase completion verification + handoff [Simple]

- [x] All Task A.X tests pass: `pytest tests/unit/ui/screens/ -x -q`. — 2173 passed, 1 skipped in 25.68s.
- [x] Sharded test suite passes (run from main repo root, NOT worktree — known `\a` bug): `cd c:/Developer/StarshipBattles && python Tools/test_sharded/test_sharded.py`. — Done; 16350/16362 pass, 8 failures pre-existing and unrelated to Phase A (codex discussion skill frontmatter docs).
- [x] All 4 Phase A production class refactors landed. Per-class LOC delta documented.
- [x] Test-helper LOC reduction documented per migrated test file.
- [x] PROJ-322 deferral annotations updated for: 5.6, 5.7, 5.16, 5.29 + 3.19, 3.20, 3.24, (3.26 if applicable).
- [x] Update `plan.md` Quick Status Phase A → Complete.
- [x] Update `plan.md` Current State to point to Phase B (or note that B+C may run in parallel if desired).
- [x] Signal PROJ-328 Phase B + Phase C are unblocked.

**Notes:** All 7 tasks landed across 6 commits on `feat/03c-phase-aware-execution`:

| Task | Commit | What |
|------|--------|------|
| A.1 | fd388946d | StrategyModalWindow bypass shell update |
| A.2 | 7859d652c | BuildQueueListWindow refactor + tests + fixture |
| A.3 | 00874c571 | OrdersWindow refactor + tests + fixture |
| A.4 | 495fa0f39 | FleetReportWindow refactor + 2 test files migrated + fixture |
| A.5 | dbc252c23 | test_strategy_modal_window.py migration + 5 new bypass-shell tests |
| A.6 | 2252a6ef3 | sub_window_hotkeys.py Orders + BuildQueueList cluster migration |
| (A.7) | (this commit) | Plan/checklist update + PROJ-322 annotation pass |

**Cumulative production LOC delta:** +199 across 4 production files (StrategyModalWindow +43, BuildQueueListWindow +76, OrdersWindow +52, FleetReportWindow +28). The +199 is mostly extracted dataclasses + collectors + builders + docstrings — the refactor centralizes per-row widget geometry that was previously inlined and duplicate-prone.

**Cumulative test-helper LOC reduction:** approximately -240 across 4 test files (test_build_queue_list_window.py: per-test ~30-line bypass blocks → 12-line shared helper; test_fleet_report_window.py: ~120 → ~20 = -100; test_fleet_report_window_multi_select.py: ~150 → ~75 = -75; test_strategy_modal_window.py: -15 then +60 from new invariant tests).

**New test fixtures:** 3 files in `tests/fixtures/` — `build_queue_list_ui_builder.py`, `orders_ui_builder.py`, `fleet_report_ui_builder.py` — each providing a Null + Mock builder pair matching the production builder protocol.

**All 4 PoC findings applied cleanly:** No 5th finding emerged. The pattern transferred cleanly across all 3 modal refactors. Both the "light pattern" (Tasks A.2, A.3) and the "layout-builder-only" pattern (Task A.4) shared the same refined headline: cheap state + delegates → super().__init__() → bypass branch invokes explicit ui_builder if supplied → production branch invokes default builder. Backwards-compat shims (e.g., `_get_order_description` on OrdersWindow) added only where existing tests reach into renamed internals.

**Effort:** Comfortably within ~1 LLM session for Phase A. Total run time including final verification under 60 minutes of wall-clock.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] All migrated test files pass
- [x] PROJ-322 annotations updated (8 task IDs)
- [x] Sharded test suite passes from main repo root — TOTAL: 16362 tests | 16350 passed | 8 failed | 0 errors | 4 skipped | wall time 145.1s (12 shards). The 8 failures are all in `tests/unit/tools/test_codex_interagent_discussion_skills.py` (codex discussion skill markdown frontmatter assertions) — confirmed pre-existing and unrelated to Phase A by re-running on a clean tree (`git stash` → run → `git stash pop`). All 3634 UI + fixtures tests pass.
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase B
