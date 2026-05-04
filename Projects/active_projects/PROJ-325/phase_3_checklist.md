# Phase 3: RaceSetupScreen testable construction (CONDITIONAL)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-325 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

> **⚠️ PHASE 3 IS BLOCKED until PROJ-324 Phase 3 Task 3.4 reports its GO/NO-GO outcome.**
> Do NOT begin work in this phase until that signal lands. Check
> [`Projects/active_projects/PROJ-324/phase_3_checklist.md`](Projects/active_projects/PROJ-324/phase_3_checklist.md)
> Task 3.4 Notes section for the outcome.

**Status:** Blocked (awaits PROJ-324 Phase 3 Task 3.4 outcome)
**Objective:** Resolve RaceSetupScreen testable construction. Scope depends on PROJ-324's RaceSetupScreen migration probe outcome:
- **GO path:** mechanical migration via `bypass_init` + `make_ui_widget`. Closes PROJ-322 Tasks 5.11 + 2.17 + 3.21. ~1 session LLM-paced.
- **NO-GO path:** production-side refactor — extract panel construction to a `PanelRegistry` protocol passed in via `__init__`. ~1-2 sessions LLM-paced. If estimate balloons past 3 sessions, stop and notify the user (Decision D-006).

**Required reading:**
- [`design.md`](design.md) — Phase 3 GO/NO-GO criteria + NO-GO refactor approach
- [`Projects/active_projects/PROJ-324/phase_3_checklist.md`](Projects/active_projects/PROJ-324/phase_3_checklist.md) — Task 3.4 Notes for the outcome
- [`game/ui/screens/race_setup/screen.py`](game/ui/screens/race_setup/screen.py) — full file before any edit
- [`tests/unit/ui/screens/test_race_setup_screen.py`](tests/unit/ui/screens/test_race_setup_screen.py) — full file before any edit

**Parallelism:** **NOT parallel-safe with PROJ-324 Phase 3 Task 3.4** (same files). Must wait for PROJ-324 to either roll back its probe (NO-GO) or land it (GO). May run in parallel with PROJ-326 entirely.

---

## Branch decision Task

### Task 3.0: Read PROJ-324 Phase 3 Task 3.4 outcome [Simple]

- [ ] Open [`Projects/active_projects/PROJ-324/phase_3_checklist.md`](Projects/active_projects/PROJ-324/phase_3_checklist.md), Task 3.4 Notes section.
- [ ] Determine outcome: GO or NO-GO.
- [ ] If GO: proceed to GO Path Tasks (3.1G..3.3G). Skip NO-GO tasks.
- [ ] If NO-GO: proceed to NO-GO Path Tasks (3.1N..3.5N). Skip GO tasks.
- [ ] Document the determination in this task's Notes.

**Notes:** [Filled when PROJ-324 outcome read]

---

## GO Path Tasks (only if PROJ-324 reports GO)

### Task 3.1G: Migrate `test_race_setup_screen.py` (PROJ-322 Tasks 5.11 + 2.17 + 3.21) [Medium]

**File:** [`tests/unit/ui/screens/test_race_setup_screen.py`](tests/unit/ui/screens/test_race_setup_screen.py)
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [ ] Replace `__new__` bypass-init helper with `bypass_init(RaceSetupScreen)` + `make_ui_widget` fixture pattern (same approach as PROJ-324 Phase 3 Task 3.1).
- [ ] Migrate fixtures across the ~150 tests.
- [ ] Verify: tests pass.
- [ ] Verify LOC delta is negative (the bypass helper + manual collaborator wiring should be larger than the new fixture). If LOC delta is positive, that may signal NO-GO was actually correct — re-evaluate.
- [ ] Update PROJ-322 phase_5_checklist.md Task 5.11, phase_2_checklist.md Task 2.17, phase_3_checklist.md Task 3.21: change deferral annotations to `**RESOLVED IN PROJ-325 Phase 3 Task 3.1G (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record LOC delta + test count.]

---

### Task 3.2G: Audit RaceSetupScreen sibling tests [Simple]

- [ ] Look for related test files: `find tests/unit/ui/screens/race_setup/ -name 'test_*.py'`.
- [ ] For each file, check whether it uses bypass-init helpers or relies on RaceSetupScreen construction. Migrate to the new pattern if so.

**Notes:** [Filled during implementation]

---

### Task 3.3G: Final verification (GO path) [Simple]

- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] No new bypass-init helpers introduced anywhere

---

## NO-GO Path Tasks (only if PROJ-324 reports NO-GO)

### Task 3.1N: Define `PanelRegistry` protocol [Medium]

**File:** [`game/ui/screens/race_setup/panel_registry.py`](game/ui/screens/race_setup/panel_registry.py) (NEW)
**Tests:** Smoke test in `tests/unit/ui/screens/race_setup/test_panel_registry.py` (NEW)

- [ ] Read [`game/ui/screens/race_setup/screen.py:104-166`](game/ui/screens/race_setup/screen.py#L104-L166) to understand the 8 panel constructions currently inline in `_create_ui()`.
- [ ] Define a `PanelRegistry` Protocol with one method per panel: `make_summary_panel(...)`, `make_identity_panel(...)`, `make_environment_panel(...)`, `make_aptitudes_panel(...)`, `make_description_panel(...)`, `make_flag_gallery(...)`, `make_portrait_gallery(...)`, `make_theme_gallery(...)`. Match the existing inline construction signatures.
- [ ] Define a default `RaceSetupPanelFactory` class that implements the protocol with the existing construction logic moved verbatim.
- [ ] Add smoke test that `RaceSetupPanelFactory().make_summary_panel(...)` returns the expected object.

**Notes:** [Filled during implementation]

---

### Task 3.2N: Wire PanelRegistry into RaceSetupScreen `__init__` [Medium]

**File:** [`game/ui/screens/race_setup/screen.py`](game/ui/screens/race_setup/screen.py)
**Tests:** Existing `tests/unit/ui/screens/race_setup/` tests (will be updated in Task 3.4N)

- [ ] Add `panel_registry: PanelRegistry | None = None` to `__init__` signature.
- [ ] In `__init__`, after the existing `bypass_init` guard (added by PROJ-324), default `self._panel_registry = panel_registry or RaceSetupPanelFactory()`.
- [ ] In `_create_ui()`, replace inline panel constructions with `self._panel_registry.make_<panel>(...)` calls.
- [ ] Verify: production behavior unchanged. Run the entire `tests/unit/ui/screens/race_setup/` suite — should still pass against the default factory.

**Notes:** [Filled during implementation]

---

### Task 3.3N: Add `MockPanelRegistry` test fixture [Simple]

**File:** [`tests/fixtures/race_setup_panel_registry.py`](tests/fixtures/race_setup_panel_registry.py) (NEW)
**Tests:** Smoke test.

- [ ] Implement `MockPanelRegistry` that returns Mock objects for every panel-creation method.
- [ ] Add a smoke test that confirms it's a valid `PanelRegistry` (duck-type check).

**Notes:** [Filled during implementation]

---

### Task 3.4N: Migrate `test_race_setup_screen.py` to inject MockPanelRegistry [Complex]

**File:** [`tests/unit/ui/screens/test_race_setup_screen.py`](tests/unit/ui/screens/test_race_setup_screen.py)
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [ ] Replace bypass-init helper with construction via `make_ui_widget` + injected `MockPanelRegistry`. The `bypass_init` flag is no longer required for the panel-related code paths.
- [ ] Update fixtures: tests now construct via:
  ```python
  @pytest.fixture
  def race_setup_screen():
      return make_ui_widget(
          RaceSetupScreen,
          rect=pygame.Rect(0, 0, 800, 600),
          manager=Mock(),
          on_complete_callback=Mock(),
          on_cancel_callback=Mock(),
          panel_registry=MockPanelRegistry(),
      )
  ```
- [ ] Verify all ~150 tests pass.
- [ ] Verify LOC delta — should be measurably negative.
- [ ] Update PROJ-322 phase_5_checklist.md Task 5.11, phase_2_checklist.md Task 2.17, phase_3_checklist.md Task 3.21: change deferral annotations to `**RESOLVED IN PROJ-325 Phase 3 Tasks 3.1N-3.4N (commit <SHA>)**`.

**Notes:** [Filled during implementation]

---

### Task 3.5N: Final verification (NO-GO path) [Simple]

- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] Production behavior unchanged — load the actual race-setup screen in-game (manual smoke test).
- [ ] Document the new `PanelRegistry` pattern in [`docs/02_PATTERNS.md`](docs/02_PATTERNS.md) as a sub-pattern under the panel/registry pattern (Pattern X — find appropriate slot).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done (whichever path was taken):

- [ ] All task checkboxes above are checked (only the path taken)
- [ ] Sharded test suite passes
- [ ] PROJ-322 Tasks 5.11 + 2.17 + 3.21 annotations updated
- [ ] If NO-GO path: `PanelRegistry` documented in `docs/02_PATTERNS.md`
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "All phases Complete"
- [ ] Update `plan.md` Verification section checkboxes
