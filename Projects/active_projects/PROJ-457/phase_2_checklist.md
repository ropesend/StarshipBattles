# PROJ-457 Phase 2: Same recipe for `planet_list_window.py` (862 → under 500)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 0 (LOC re-measured); Phase 1 not a hard prerequisite — write scopes are disjoint.
**Review Mode:** standard
**Objective:** Drop `game/ui/screens/planet_list_window.py` from 862 LOC (or post-PROJ-456 re-measured value) to under the 500-LOC ceiling. Same recipe as Phase 1.

**Source-of-truth finding:** F-C-027 entry in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md).

**Existing file structure (verified 2026-05-19 by reading lines 1-60):**
- The file already imports from sibling modules `planet_list_controller`, `planet_list_filters`, `planet_list_filter_manager`, `planet_list_sidebar`, `planet_list_presets`, `planet_data_source`, `planet_report_panel` — so the extract-by-responsibility pattern has clear precedent.
- Candidate clusters:
  - **Formatting helpers** (`_format_population` at line 57 + other private formatters) → `planet_list_formatting.py`.
  - **Sidebar build orchestration** (around `build_sidebar` import on line 49) — may be ready for an internal-orchestration extraction.
  - **PresetManager wiring + capture/apply state lifecycle** (lines around 46) → `planet_list_state_lifecycle.py`.

---

## Tasks

### Task 2.1: Read the file + identify candidate responsibilities [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** none — read-only audit.

- [ ] Read `planet_list_window.py` end-to-end.
- [ ] Identify cohesive responsibility clusters: formatting helpers, sidebar build, preset lifecycle, filter-state hookup, etc.
- [ ] List each candidate with estimated LOC out and API surface in.
- [ ] Pick the best ratio. Record in `decisions.md`.

### Task 2.2: Create the sibling module [Medium]
**File:** `game/ui/screens/planet_list_<responsibility>.py` (new)
**Tests:** `tests/unit/ui/screens/test_planet_list_<responsibility>.py` (new)

- [ ] Create the new sibling module per the Phase 1 recipe.
- [ ] Move the chosen cluster.
- [ ] Expose a narrow API.

### Task 2.3: Rewire `planet_list_window.py` [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window*.py tests/unit/ui/screens/planet_list/ -q`

- [ ] Import the new module's API.
- [ ] Replace calls to old methods with new API calls.
- [ ] Delete the old methods + state fields.
- [ ] Run targeted tests.

### Task 2.4: Migrate test reads to the new module's API [Medium]
**Files:** existing planet-list test files + new dedicated test file for the extracted module.

- [ ] For each test that was reading the extracted internals, migrate to the new API.
- [ ] Add new behavior-locking tests for the extracted module.
- [ ] Run each test file individually.

### Task 2.5: Verify LOC + sharded green [Simple]

- [ ] (PowerShell-safe) `(Get-Content game/ui/screens/planet_list_window.py | Measure-Object -Line).Lines` returns < 500.
- [ ] (PowerShell-safe) `(Get-Content game/ui/screens/planet_list_<responsibility>.py | Measure-Object -Line).Lines` returns < 500.
- [ ] Run sharded suite green.
- [ ] Run targeted tests.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] F-C-027 status updated in `findings/PROJ-457_findings.md` — `planet_list_window.py` row flipped to `Status: resolved`.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-457 2` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 3.
- [ ] Commit message: `PROJ-457 Phase 2: extract <responsibility> from planet_list_window.py (862 -> <FINAL> LOC; F-C-027 partial close)`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
