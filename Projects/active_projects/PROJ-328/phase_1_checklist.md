# Phase A: StrategyModalWindow shell + 3 light/medium modals (PROJ-322 Tasks 5.6/5.7/5.16/5.29 + 3.19/3.20/3.24/3.26)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-328 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Ready (PROJ-325 Phase 3 PoC merged 2026-05-04 — pattern proven on RaceSetupScreen with -55% helper LOC).

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

- [ ] Move the existing `bypass_init` guard from "first executable statement" to "AFTER cheap state setup, BEFORE `super().__init__`".
- [ ] Set `self._window_manager`, `self.ui_manager`, `self._window_init_bypassed = True` before returning. **Do NOT set `self.rect`** (pygame_gui descriptor issue — see Pattern-discovery finding 1).
- [ ] Verify all 23 existing `tests/unit/ui/screens/test_strategy_modal_window.py` tests still pass.
- [ ] Smoke-test all 4 subclasses still construct in production mode (default constructor, no `bypass_init`): `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_orders_window.py tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_build_queue_list_window.py -x` (should still all PASS — those tests use the existing `__new__` helper, not the new pattern yet).
- [ ] Commit as a focused single-file change.

**Notes:** [Filled during implementation]

---

### Task A.2: Refactor `BuildQueueListWindow` (PROJ-322 Tasks 5.29 + 3.19) [Medium]

**Production file:** [`game/ui/screens/build_queue_list_window.py`](../../../game/ui/screens/build_queue_list_window.py)
**Test file:** [`tests/unit/ui/screens/test_build_queue_list_window.py`](../../../tests/unit/ui/screens/test_build_queue_list_window.py)
**Test infra (NEW):** `tests/fixtures/build_queue_list_ui_builder.py`

Light pattern per consensus plan: row collector/formatter + simple renderer. No full MVVM stack needed.

- [ ] Read existing `BuildQueueListWindow.__init__` + `_build_list()`. Identify cheap state, delegates (if any — small modals may have no delegate layer), widget construction.
- [ ] Read existing `_make_build_queue_list_window` helper in test file. Note all attributes the helper assigns + all renderer-internal reach-throughs.
- [ ] Refactor `__init__` to two-stage shape (per refined headline pattern). For this small modal, "delegates" may collapse to a single `BuildQueueListRowCollector` or similar — match what's in production.
- [ ] Create `BuildQueueListUiBuilder` extracting widget-construction code from `_build_list()` and any inline construction in `__init__`.
- [ ] Create `NullBuildQueueListUiBuilder` + `MockBuildQueueListUiBuilder` in `tests/fixtures/build_queue_list_ui_builder.py`. MockBuilder reproduces every widget attribute the test helper assigned.
- [ ] Migrate test helper to direct construction.
- [ ] Verify all existing tests pass.
- [ ] Update PROJ-322 Task 5.29 + Task 3.19 annotations from `DEFERRED-OUT-OF-SCOPE` to `RESOLVED IN PROJ-328 Phase A Task A.2 (commit <SHA>)`.
- [ ] Record helper LOC delta in Notes.

**Notes:** [Filled during implementation. Document helper LOC before/after, test count, any pattern bends.]

---

### Task A.3: Refactor `OrdersWindow` (PROJ-322 Task 5.16 — Orders portion) [Medium]

**Production file:** [`game/ui/screens/orders_window.py`](../../../game/ui/screens/orders_window.py)
**Test file:** [`tests/unit/ui/screens/test_orders_window.py`](../../../tests/unit/ui/screens/test_orders_window.py) (verify path — may live in `test_sub_window_hotkeys.py`)
**Test infra (NEW):** `tests/fixtures/orders_ui_builder.py`

Light pattern per consensus plan: pure order-row description model + `OrdersListRenderer`. Full MVVM is ceremony for a 355-line modal.

- [ ] Same shape as Task A.2.
- [ ] Verify which tests the migration owns — Task 5.16 was a `test_sub_window_hotkeys.py` cluster covering 4 classes (Orders, BuildQueue, TransferDialog, BuildQueueList). Just do the Orders portion here.
- [ ] Update PROJ-322 Task 5.16 (Orders portion) annotation.

**Notes:** [Filled during implementation]

---

### Task A.4: Refactor `FleetReportWindow` (PROJ-322 Tasks 5.6 + 5.7 + 3.20) [Complex]

**Production file:** [`game/ui/screens/fleet_report_window.py`](../../../game/ui/screens/fleet_report_window.py)
**Test files:**
- [`tests/unit/ui/screens/test_fleet_report_window.py`](../../../tests/unit/ui/screens/test_fleet_report_window.py) — Task 5.6
- [`tests/unit/ui/screens/test_fleet_report_window_multi_select.py`](../../../tests/unit/ui/screens/test_fleet_report_window_multi_select.py) — Tasks 5.7 + 3.20
**Test infra (NEW):** `tests/fixtures/fleet_report_ui_builder.py`

Per consensus plan: already mostly decomposed via `FleetListViewModel`, `FleetDataSource`, `VirtualTable`, sidebar. Just extract layout construction into `FleetReportLayoutBuilder`. Avoid grand rewrite.

- [ ] Read `FleetReportWindow.__init__` carefully — identify which collaborators already exist and which need extraction.
- [ ] Apply the refined two-stage pattern minimally: extract layout-construction into `FleetReportLayoutBuilder`; keep existing `FleetListViewModel`/`FleetDataSource`/`VirtualTable`/sidebar plumbing intact.
- [ ] Both test files migrate to direct construction. The multi-select file (Task 3.20) may have additional private-method patches to clean up — drive through the public boundary instead per APC-003 guidance in the consensus plan.
- [ ] Update PROJ-322 Tasks 5.6, 5.7, 3.20 annotations.

**Notes:** [Filled during implementation]

---

### Task A.5: Migrate `tests/unit/strategy/test_strategy_modal_window.py` (PROJ-322 Task 3.24) [Medium]

**File:** [`tests/unit/ui/screens/test_strategy_modal_window.py`](../../../tests/unit/ui/screens/test_strategy_modal_window.py) (verify path — may live elsewhere)

This is the test file that exercises `StrategyModalWindow` directly (not via subclass). After Task A.1, the bypass shell leaves a minimal usable instance — these tests should now be migratable to direct construction.

- [ ] Audit existing test patterns in the file.
- [ ] Where private-method patches exist, rewrite to drive the public boundary (APC-003 cleanup per consensus plan).
- [ ] Update PROJ-322 Task 3.24 annotation.

**Notes:** [Filled during implementation]

---

### Task A.6: Sub-window hotkeys cluster — sweep remaining (PROJ-322 Task 5.16 — non-Orders portion) [Medium]

**File:** [`tests/unit/ui/screens/test_sub_window_hotkeys.py`](../../../tests/unit/ui/screens/test_sub_window_hotkeys.py)

Task 5.16 covered 4 classes — Orders (handled in Task A.3), BuildQueueScreen (NOT a UIWindow, not Phase A scope), TransferDialog (deferred to Phase C), BuildQueueListWindow (handled in Task A.2). Sweep the remaining hotkey-cluster tests for any outstanding `__new__` bypass usage.

- [ ] If TransferDialog hotkey tests can be migrated WITHOUT the deep refactor (Phase C scope), do so. Otherwise leave for Phase C.
- [ ] Update PROJ-322 Task 5.16 final disposition.

**Notes:** [Filled during implementation]

---

### Task A.7: Phase completion verification + handoff [Simple]

- [ ] All Task A.X tests pass: `pytest tests/unit/ui/screens/ -x -q`.
- [ ] Sharded test suite passes (run from main repo root, NOT worktree — known `\a` bug): `cd c:/Developer/StarshipBattles && python Tools/test_sharded/test_sharded.py`.
- [ ] All 4 Phase A production class refactors landed. Per-class LOC delta documented.
- [ ] Test-helper LOC reduction documented per migrated test file.
- [ ] PROJ-322 deferral annotations updated for: 5.6, 5.7, 5.16, 5.29 + 3.19, 3.20, 3.24, (3.26 if applicable).
- [ ] Update `plan.md` Quick Status Phase A → Complete.
- [ ] Update `plan.md` Current State to point to Phase B (or note that B+C may run in parallel if desired).
- [ ] Signal PROJ-328 Phase B + Phase C are unblocked.

**Notes:** [Filled during implementation. Cumulative LOC delta + test pass count.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] All migrated test files pass
- [ ] PROJ-322 annotations updated (8 task IDs)
- [ ] Sharded test suite passes from main repo root
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase B
