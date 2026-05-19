# PROJ-457 Phase 3: Same recipe for `test_lab/screen.py` (744 → under 500)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 0 (LOC re-measured); Phase 1 and 2 not hard prerequisites — write scopes are disjoint.
**Review Mode:** standard
**Objective:** Drop `game/ui/screens/test_lab/screen.py` from 744 LOC (or post-PROJ-456 re-measured value) to under the 500-LOC ceiling. Same recipe as Phase 1.

**Source-of-truth finding:** F-C-027 entry in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md).

**File context (verified 2026-05-19):**
- Docstring at lines 1-13 explicitly says "Target: keep the class under 300 lines — delegate logic to ViewModel / Renderer / InputHandler / Controller. FleetBattleSetupScreen is the sibling exemplar." The 744 LOC reality is 2.5x the stated target.
- Existing decomposition: `viewmodel`, `renderer`, `input_handler`, `panel_manager`, `test_executor`, `data_extractor`, `JSONPopup` dialog. The screen orchestrates these; further extraction has clear precedent.
- Candidate clusters:
  - **Scenario loading / discovery** (interaction with `TestRegistry` from `combat_lab.registry`).
  - **Test history coordination** (interaction with `TestHistory` from `combat_lab.test_history`).
  - **Theme + font setup** (around the `theme` import on line 27).
  - **Top-level state machine / orchestration glue** that ties the collaborators together.

---

## Tasks

### Task 3.1: Read the file + identify candidate responsibilities [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** none — read-only audit.

- [ ] Read `test_lab/screen.py` end-to-end.
- [ ] Identify cohesive responsibility clusters per the existing decomposition exemplar.
- [ ] Pick the cluster with the best ratio.
- [ ] Record choice in `decisions.md`.

### Task 3.2: Create the sibling module [Medium]
**File:** `game/ui/screens/test_lab/<responsibility>.py` (new)
**Tests:** `tests/unit/ui/screens/test_lab/test_<responsibility>.py` (new)

- [ ] Create the new sibling module per the Phase 1 recipe.
- [ ] Move the chosen cluster.
- [ ] Expose a narrow API.

### Task 3.3: Rewire `test_lab/screen.py` [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/ -q`

- [ ] Import the new module's API.
- [ ] Replace calls to old methods with new API calls.
- [ ] Delete the old methods + state fields.
- [ ] Run targeted tests.

### Task 3.4: Migrate test reads to the new module's API [Medium]
**Files:** existing test_lab test files + new dedicated test file.

- [ ] For each test that was reading the extracted internals, migrate to the new API.
- [ ] Add new behavior-locking tests for the extracted module.
- [ ] Run each test file individually.

### Task 3.5: Verify LOC + sharded green [Simple]

- [ ] (PowerShell-safe) `(Get-Content game/ui/screens/test_lab/screen.py | Measure-Object -Line).Lines` returns < 500.
- [ ] (PowerShell-safe) `(Get-Content game/ui/screens/test_lab/<responsibility>.py | Measure-Object -Line).Lines` returns < 500.
- [ ] Run sharded suite green.
- [ ] Run combat_lab targeted tests: `pytest tests/unit/combat_lab/ -q` (in case the extraction touched that path).
- [ ] Run combat lab integration: `python -m combat_lab.run_tests` to confirm the Combat Lab runtime path still works.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] F-C-027 status updated in `findings/PROJ-457_findings.md` — `test_lab/screen.py` row flipped to `Status: resolved`.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-457 3` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 4.
- [ ] Commit message: `PROJ-457 Phase 3: extract <responsibility> from test_lab/screen.py (744 -> <FINAL> LOC; F-C-027 partial close)`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
