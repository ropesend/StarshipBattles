# PROJ-446 Phase 4: UI LOC-ceiling extractions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-446 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 3 complete (several files drop under the ceiling after shim retirement; rescope before starting Phase 4)
**Objective:** Mechanical responsibility-based file splits for UI files still over 500 LOC after Phase 3, plus `game/core/exceptions.py` (544 LOC) split by domain. Several Phase-3 retirements naturally drop the LOC count of the offenders; this phase handles what's left.

**Cross-bucket file-ownership rule:** Only edit `game/ui/`, `game/core/`. Pure refactor — no behavior change.

**Source-of-truth findings:** [`findings/bucket_c_ui_core_tests_scan.md`](findings/bucket_c_ui_core_tests_scan.md) — F-C-027, F-C-028.

---

## Tasks

### Task 4.1: Pre-flight — re-measure LOC after Phase 3 [Simple, MANDATORY]
**Tests:** `wc -l game/ui/screens/*.py game/ui/screens/builder/*.py game/ui/panels/*.py game/core/exceptions.py`

- [ ] Run the LOC measurement command above
- [ ] Compare against the F-C-027 list of 12 files in plan.md
- [ ] Record which files Phase 3 already dropped under 500 LOC (these are removed from Phase 4 scope)
- [ ] Record the updated over-ceiling list in decisions.md

### Task 4.2: F-C-027 — Extract one responsibility from build_queue_screen.py (961 LOC, worst offender) [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py -v`

- [ ] Read build_queue_screen.py in full to identify a clean responsibility split. Candidates per the finding:
  - Yard population (loading available yards from the empire)
  - Queue selection (mouse/keyboard click handling)
  - Drag handling (drop pod / vehicle drag-and-drop into the queue)
- [ ] Pick the most cohesive of the three. Extract to `game/ui/screens/build_queue_<concern>.py`. Top-level `build_queue_screen.py` retains the screen class + delegates to the new module.
- [ ] Same pattern as the existing `build_queue_*` family split in the directory.
- [ ] Run targeted tests after the extraction; full sharded suite to verify no behavior regression.
- [ ] Verify build_queue_screen.py drops under 500 LOC (or document why not). If still over: extract a second responsibility.

### Task 4.3: F-C-027 — planet_list_window.py (862 LOC) [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py -v`

- [ ] Read in full; identify cohesive split candidates (filtering, sorting, rendering, selection?)
- [ ] Extract the cleanest one. Goal: under 500 LOC.
- [ ] Run tests.

### Task 4.4: F-C-027 — test_lab/screen.py (744 LOC) [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/ -v`

- [ ] Read in full; pick cohesive split.
- [ ] Extract. Goal: under 500 LOC.
- [ ] Run tests.

### Task 4.5: F-C-028 — Split game/core/exceptions.py [Small]
**File:** `game/core/exceptions.py:1` (544 LOC)
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Read existing exception hierarchy. Identify natural domain splits per the finding:
  - `exceptions_persistence.py` (save-load errors)
  - `exceptions_validation.py` (data-shape errors)
  - Possibly `exceptions_engine.py`, `exceptions_ui.py`
- [ ] Extract each domain group into a sibling module
- [ ] Keep top-level `game/core/exceptions.py` as a re-export shim (this is allowed per the convention "Preserve public API with a re-export shim only when many callers exist" — exception classes have many callers, so the shim is justified)
- [ ] Verify all imports from `game/core/exceptions import X` still resolve via the re-export
- [ ] Run targeted + sharded tests.

### Task 4.6 (conditional): F-C-027 — Continue with remaining files if time + LOC budget allows [Medium each]

If Tasks 4.2-4.4 left other files over the ceiling, prioritize:
- `new_game_setup_screen.py` (734 LOC, but Phase 3 Task 3.10 may have dropped this under 500)
- `empire_build_queue_window.py` (734)
- `event_log_window.py` (732)
- `panels/race_summary_panel.py` (732)
- `empire_panel_window.py` (724)
- `panels/build_queue_controller.py` (723)
- `panels/system_tree_panel.py` (711)
- `design_selector_window.py` (708)
- `strategy_detail_fmt.py` (707)

For each: read; identify split; extract; test. If a clean split isn't obvious, leave it and document in decisions.md as "next-touch" rule.

---

## Phase Completion Checklist

- [ ] Tasks 4.1-4.5 complete
- [ ] Top 3 worst offenders (build_queue_screen.py, planet_list_window.py, test_lab/screen.py) under 500 LOC OR explicitly deferred with rationale
- [ ] `game/core/exceptions.py` split with back-compat re-export shim in place
- [ ] Remaining over-ceiling UI files documented in decisions.md as "next-touch" rule
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-446 4` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 5
- [ ] No behavior changes detected (all UI screens render and operate identically)

## Notes

- Pure mechanical refactor phase. Extractions should be responsibility-based, not arbitrary line-count splits.
- If a file has no clean split: don't force one. Document the structural reason in decisions.md and defer.
- The `game/core/exceptions.py` shim is the only re-export shim being preserved by this project — exceptions are pervasive enough that breaking N callers is worse than keeping one shim.
