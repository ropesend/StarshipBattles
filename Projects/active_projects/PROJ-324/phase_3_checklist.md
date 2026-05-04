# Phase 3: Migrate 14 unblocked PROJ-322 deferrals (test-side)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-324 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the 14 PROJ-322 deferrals unblocked by Phases 1-2 — 7 APC-001 cluster files + 5 Phase 3 boundary-patching tasks + Task 4.3 (already done in Phase 2) + Task 5.10/5.10a (workshop screen). Each migration replaces the `__new__` bypass-init pattern with `make_ui_widget` + `bypass_init` context manager, OR drives the test through the public boundary instead of patching private methods.

**Required reading before starting:**
- [`design.md`](design.md) — Implementation Pattern + Architecture sections
- PROJ-322 phase checklists for the deferred items — search for `**DEFERRED-OUT-OF-SCOPE` annotations to find original task scope:
  - [`Projects/active_projects/PROJ-322/phase_3_checklist.md`](Projects/active_projects/PROJ-322/phase_3_checklist.md) Tasks 3.19, 3.20, 3.21, 3.24, 3.26
  - [`Projects/active_projects/PROJ-322/phase_5_checklist.md`](Projects/active_projects/PROJ-322/phase_5_checklist.md) Tasks 5.6, 5.7, 5.10, 5.10a, 5.11, 5.12, 5.16, 5.29
- The original test-review at [`Reviews/results/2026-05-02_204633_test-review/`](Reviews/results/2026-05-02_204633_test-review/) for per-finding context if a deferred item's rationale is unclear

**Parallelism within Phase 3:** Each task is file-isolated. Tasks 3.X here may run concurrently with each other if multiple agents work the phase. **However:**
- Task 3.4 (race_setup_screen) has a known go/no-go check — see Decision D-005. Do not parallelize a Task 3.4 attempt with PROJ-325 Phase 3 RaceSetupScreen work.
- Tasks 3.5 + 3.7 + 3.8 (sub_window_hotkeys, build_queue_list_window, fleet_report_window_multi_select) reference subclasses of `StrategyModalWindow`. The `bypass_init` should already cover them transitively from Phase 1 Task 1.2; if any per-class guards are needed (Phase 1 Task 1.5 audit), those should land first.

**Cross-project parallelism:** Phase 3 may run in parallel with PROJ-326 entirely (file-disjoint). PROJ-325 Phase 3 (RaceSetupScreen decision) has overlap with Task 3.4 here; coordinate.

**Update upstream PROJ-322 annotations as you complete each task** (see Task 3.X "in PROJ-322 ... update annotation" subtasks). This keeps the audit trail intact.

---

## Tasks

### Task 3.1: Migrate `test_fleet_report_window.py` (PROJ-322 Task 5.6) [Medium]

**File:** [`tests/unit/ui/screens/test_fleet_report_window.py`](tests/unit/ui/screens/test_fleet_report_window.py)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`
**Production class:** [`game/ui/screens/fleet_report_window.py:32`](game/ui/screens/fleet_report_window.py#L32) (FleetReportWindow extends StrategyModalWindow → UIWindow)

- [ ] Read the existing test file. Identify the `__new__` bypass-init helper(s) and the test fixtures that depend on them.
- [ ] Replace the bypass-init helper with a fixture or context-manager call:
  ```python
  @pytest.fixture
  def fleet_report_window():
      with bypass_init(FleetReportWindow):
          window = make_ui_widget(
              FleetReportWindow,
              fleet=mock_fleet,
              empire=mock_empire,
              window_manager=Mock(),
              on_close_callback=Mock(),
              split_fleet_callback=Mock(),
          )
      yield window
  ```
- [ ] Update each test that consumed the bypass-init helper to use the new fixture.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py` passes.
- [ ] Verify LOC delta is negative (the bypass helper + manual attribute wiring should be larger than the new fixture).
- [ ] In PROJ-322 `phase_5_checklist.md` Task 5.6, update `**DEFERRED-OUT-OF-SCOPE` annotation to `**RESOLVED IN PROJ-324 Phase 3 Task 3.1 (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record LOC delta.]

---

### Task 3.2: Migrate `test_fleet_report_window_multi_select.py` (PROJ-322 Tasks 5.7 + 3.20) [Medium]

**File:** [`tests/unit/ui/screens/test_fleet_report_window_multi_select.py`](tests/unit/ui/screens/test_fleet_report_window_multi_select.py)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

This is a 2-in-1: APC-001 (`__new__` bypass-init) AND APC-003 (private-method patching of multi-select internals).

- [ ] Same APC-001 migration as Task 3.1 — `bypass_init` + `make_ui_widget`.
- [ ] For the APC-003 part: identify private-method patches (e.g., `patch.object(window, '_handle_multi_select_event')` or similar) and rewrite to drive the public `handle_event` surface with selection events instead.
- [ ] Verify: tests pass.
- [ ] Update PROJ-322 Task 5.7 + Task 3.20 annotations.

**Notes:** [Filled during implementation]

---

### Task 3.3: Migrate `test_workshop_screen.py` (PROJ-322 Task 5.10 + 5.10a) [Medium]

**File:** [`tests/unit/ui/screens/test_workshop_screen.py`](tests/unit/ui/screens/test_workshop_screen.py) (verify path)
**Integration alternative:** [`tests/integration/ui/workshop_screen/`](tests/integration/ui/workshop_screen/) (PROJ-322 manifest claims this exists)

- [ ] **First:** Check whether `tests/integration/ui/workshop_screen/` exists with adequate coverage (open/close, design list, save/load — this was the M-001 plan-review remediation acceptance criterion).
- [ ] **If integration tests are adequate:** Delete the unit file (mirror the `test_build_queue_screen.py` precedent). Update PROJ-322 Tasks 5.10 + 5.10a as `**RESOLVED via deletion in PROJ-324 Task 3.3**`.
- [ ] **If integration tests are missing or inadequate:** Migrate the unit tests via `bypass_init` + `make_ui_widget`.
- [ ] Verify: full suite passes for the workshop_screen surface.
- [ ] Update PROJ-322 annotations.

**Notes:** [Filled during implementation. Document the integration-coverage assessment.]

---

### Task 3.4: RaceSetupScreen migration GO/NO-GO decision + execution (PROJ-322 Tasks 5.11 + 2.17 + 3.21) [Complex]

**File:** [`tests/unit/ui/screens/test_race_setup_screen.py`](tests/unit/ui/screens/test_race_setup_screen.py) (1464 LOC, ~150 tests per OpenCode 322-review)
**Production class:** [`game/ui/screens/race_setup/screen.py:60`](game/ui/screens/race_setup/screen.py#L60) (6 declared params → 10+ collaborators + 8 lazy panels)

This is the high-risk task. See Decision D-005.

- [ ] Smoke-test: with `bypass_init(RaceSetupScreen)`, can the test factory construct an instance without errors?
- [ ] **GO criterion:** Construction succeeds AND test wiring (mocking the 10+ collaborators) is no worse than the existing bypass-init helper.
- [ ] **NO-GO criterion:** Construction works but test wiring is more complex than the existing bypass-init helper. In this case, stop work, update PROJ-322 Tasks 5.11/2.17/3.21 annotations to point at PROJ-325 Phase 3, and notify the user.
- [ ] **If GO:** Migrate. Replace bypass-init helper with `bypass_init` + `make_ui_widget`. Refactor fixtures.
- [ ] **If NO-GO:** Document the construction wiring requirements in this Notes section, the PROJ-322 task annotations, and PROJ-325 design.md (so PROJ-325 has a head start).
- [ ] Verify: tests pass under whichever path was taken.

**Notes:** [Filled during implementation. Document GO/NO-GO and rationale clearly.]

---

### Task 3.5: Migrate `test_new_game_setup_extended.py` (PROJ-322 Task 5.12) [Medium]

**File:** [`tests/unit/ui/screens/test_new_game_setup_extended.py`](tests/unit/ui/screens/test_new_game_setup_extended.py)
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py`

- [ ] APC-001 migration: `bypass_init` + `make_ui_widget`.
- [ ] Verify: tests pass.
- [ ] Update PROJ-322 Task 5.12 annotation.

**Notes:** [Filled during implementation]

---

### Task 3.6: Migrate `test_sub_window_hotkeys.py` (PROJ-322 Task 5.16) [Complex]

**File:** [`tests/unit/ui/screens/test_sub_window_hotkeys.py`](tests/unit/ui/screens/test_sub_window_hotkeys.py)
**Production classes targeted:** OrdersWindow ([`orders_window.py:36`](game/ui/screens/orders_window.py#L36)), BuildQueueScreen ([`build_queue_screen.py:38`](game/ui/screens/build_queue_screen.py#L38) — STANDALONE not UIWindow), TransferDialog ([`transfer_dialog.py:45`](game/ui/screens/transfer_dialog.py#L45)), BuildQueueListWindow ([`build_queue_list_window.py:18`](game/ui/screens/build_queue_list_window.py#L18))
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py`

Note BuildQueueScreen is NOT a UIWindow — it does not need `bypass_init`; standard `make_ui_widget(BuildQueueScreen, ...)` should already work.

- [ ] For each of the 4 target classes, audit the test for bypass-init usage.
- [ ] OrdersWindow + TransferDialog + BuildQueueListWindow: migrate via `bypass_init` + `make_ui_widget`.
- [ ] BuildQueueScreen: migrate via plain `make_ui_widget` (no bypass_init needed).
- [ ] Verify: tests pass.
- [ ] Update PROJ-322 Task 5.16 annotation.

**Notes:** [Filled during implementation]

---

### Task 3.7: Migrate `test_build_queue_list_window.py` (PROJ-322 Tasks 5.29 + 3.19) [Medium]

**File:** [`tests/unit/ui/screens/test_build_queue_list_window.py`](tests/unit/ui/screens/test_build_queue_list_window.py)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

2-in-1: APC-001 (`__new__` bypass-init) + APC-003 (`_build_list` private patch).

- [ ] APC-001 migration: `bypass_init` + `make_ui_widget`.
- [ ] APC-003: rewrite `_build_list` patches to drive public refresh/update method instead.
- [ ] Verify: tests pass.
- [ ] Update PROJ-322 Tasks 5.29 + 3.19 annotations.

**Notes:** [Filled during implementation]

---

### Task 3.8: Migrate `test_strategy_modal_window.py` (PROJ-322 Task 3.24) [Medium]

**File:** [`tests/unit/strategy/test_strategy_modal_window.py`](tests/unit/strategy/test_strategy_modal_window.py) (verify path)
**Tests:** `pytest tests/unit/strategy/ -k strategy_modal_window`

This is the UIWindow root-cause test file — testing `StrategyModalWindow` directly.

- [ ] APC-003 boundary patching: drive headless construction via `bypass_init(StrategyModalWindow)` + `make_ui_widget`.
- [ ] Verify: tests pass.
- [ ] Update PROJ-322 Task 3.24 annotation.

**Notes:** [Filled during implementation]

---

### Task 3.9: Walk PROJ-322 deferrals to confirm coverage [Simple]

**Files:** PROJ-322 phase checklists.

- [ ] For each `**DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):**` annotation in PROJ-322 Phase 3 + Phase 5 checklists, verify either:
  - It's annotated `**RESOLVED IN PROJ-324 ...**` by Tasks 3.1-3.8, OR
  - It's an explicit out-of-scope item (Task 3.14 virtual_table, Task 3.25 strategy_screen, Tasks 6.1/6.4 DUP/HLP, mutable-mock fixture rescopes Tasks 2.6/2.11/2.15/2.19/3.15) and is queued to PROJ-327, OR
  - It's a NO-GO from Task 3.4 (RaceSetupScreen) and is queued to PROJ-325.
- [ ] If any deferral is uncovered, document it in this task's Notes and surface to the user.
- [ ] Update PROJ-322 plan.md Continuation Guide to reflect the new state of deferrals.

**Notes:** [Filled during implementation. List any uncovered deferrals.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] All migrated test files pass: `pytest tests/unit/ui/ tests/unit/services/llm/ tests/unit/strategy/test_strategy_modal_window.py`
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] PROJ-322 phase checklist annotations updated for every closed deferral
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 4
