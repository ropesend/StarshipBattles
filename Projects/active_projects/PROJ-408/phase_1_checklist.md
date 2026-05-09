# Phase 1: Add direct unit coverage for C-01, C-02, C-04

**Status:** Not Started
**Objective:** Land 3 new direct unit tests covering the introspection/UI-only gaps in PROJ-381 and PROJ-397.

---

## Tasks

### Task 1.1: C-01 — Replace introspection-only `EmpireBuildQueueWindow` test [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`

- [ ] Read PROJ-397's existing F-05 test that verifies the constructor signature only via introspection.
- [ ] Read `game/ui/screens/empire_build_queue_window.py` to see the actual class — what dependencies does the constructor take, and what should a real instance be able to do?
- [ ] Write a new test (or augment the existing one) that:
  - Constructs `EmpireBuildQueueWindow` with realistic dependencies (use existing fixtures if any — check the module for facade/registry patterns).
  - Exercises at least one method that proves the threading is correct (e.g., a method that uses `self._facade.handle_command(...)`).
- [ ] If the introspection-only test was a `test_constructor_signature_*` pattern, **delete it** after the real-construction test lands — it's bug-shaped (asserts shape, not behavior).
- [ ] Run focused tests — pass.

**Notes:**

### Task 1.2: C-02 — Facade conversion `EnginePhaseError` → `TurnFailedError` [Medium]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py` (or wherever the facade is unit-tested — check; if no module exists, create one)
**Tests:** `pytest tests/unit/strategy/facade/ -v`

- [ ] Read `game/strategy/facade/strategy_session_facade.py:194-201` to understand the conversion path.
- [ ] Identify the facade method that catches `EnginePhaseError` and re-raises as `TurnFailedError` with context.
- [ ] Write a focused unit test that:
  - Patches the underlying engine call (or constructs a session with a stub engine) so it raises `EnginePhaseError`.
  - Asserts the facade method raises `TurnFailedError`.
  - Asserts the wrapped error carries the expected context (turn_number, save_path, etc. — see PROJ-381 Phase 3 verification).
- [ ] Run the test against current production — should PASS (the conversion exists; this is just adding test coverage that was missing).
- [ ] Run the broader facade test module to confirm no breakage.

**Notes:**

### Task 1.3: C-04 — `PlanetSelectionWindow` facade threading direct unit coverage [Medium]
**File:** `tests/unit/ui/screens/test_planet_selection_window.py` (or wherever — confirm via Glob)
**Tests:** `pytest tests/unit/ui/screens/ -k planet_selection -v`

- [ ] Read `PlanetSelectionWindow` to see the facade-threading the PROJ-397 review flagged.
- [ ] Find or create the test module.
- [ ] Write a unit test that:
  - Constructs `PlanetSelectionWindow` with a real (or stub) facade.
  - Calls a method that exercises facade threading (e.g., one that uses `self._facade` to fetch data or dispatch).
  - Asserts the facade is invoked with the expected arguments (use `unittest.mock.MagicMock` if needed).
- [ ] Run the test — pass.

**Notes:**

### Task 1.4: Run focused suites to confirm no breakage [Simple]
**Tests:**
- `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`
- `pytest tests/unit/strategy/facade/ -v`
- `pytest tests/unit/ui/screens/ -k planet_selection -v`

- [ ] All pass.

**Notes:**

### Task 1.5: Closeout
- [ ] Phase 1 status `Complete`
- [ ] Plan.md updated
- [ ] `Projects/projects_index.md` row for PROJ-408 set to `Complete`
- [ ] Validators PASS
- [ ] Commit (one or more): `PROJ-408 phase 1: add direct coverage for C-01/C-02/C-04`
- [ ] Verification report at `findings/verification_report.md`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] Focused suites pass
- [ ] `python Projects/scripts/validate_phase.py PROJ-408 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-408` PASSED
