# PROJ-244 Completeness Audit Report
**Date:** 2026-04-10
**Auditor:** Completeness Auditor (automated)

## Summary

The project plan is largely well-structured for a mechanical rename refactor. However, the **plan is stale** -- the majority of production code changes described in Phase 1 have **already been completed** in the codebase. The plan text, line references, and checklist items describe a pre-rename state that no longer matches reality. Additionally, one file with old naming (`test_battle_determinism.py`) is missing from the plan entirely, and the fixtures README has a stale code example.

**Critical finding count:** 1 (stale plan)
**Moderate finding count:** 2 (missing file, stale README)
**Minor finding count:** 2 (cosmetic/process)

---

## Goal-to-Task Mapping

### Goal 1: Eliminate confusing `team1_ships` / `team2_ships` naming
**Tasks addressing this:** 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.1, 2.2
**Coverage:** Sufficient -- all known production and test fixture sites are covered.
**Gap:** `test_battle_determinism.py` is NOT covered (see Finding F-02).

### Goal 2: Standardize on 0-based naming
**Tasks addressing this:** Same as Goal 1 (rename tasks implement the 0-based convention).
**Coverage:** Sufficient.

### Goal 3: Update docstrings to remove "team1 = team 0" clarifications
**Tasks addressing this:** 1.2, 1.4, 1.5, 2.1, 2.3
**Coverage:** Sufficient -- all known docstring locations are included.

### Goal 4: No runtime behavior changes
**Tasks addressing this:** 1.1 (baseline), 1.10 (targeted suite), 2.4 (full suite + grep verification)
**Coverage:** Sufficient -- baseline and verification bookend the work.

**Verdict: All goals have corresponding tasks. No unaddressed goals.**

---

## Task-to-Goal Mapping

| Task | Serves Goal(s) | Orphaned? |
|------|----------------|-----------|
| 1.1 | Goal 4 | No |
| 1.2 | Goals 1, 2, 3 | No |
| 1.3 | Goals 1, 2 | No |
| 1.4 | Goals 1, 2, 3 | No |
| 1.5 | Goals 1, 2, 3 | No |
| 1.6 | Goals 1, 2 | No |
| 1.7 | Goals 1, 2 | No |
| 1.8 | Goals 1, 2 | No |
| 1.9 | Goals 1, 2 | No |
| 1.10 | Goal 4 | No |
| 2.1 | Goals 1, 2, 3 | No |
| 2.2 | Goals 1, 2 | No |
| 2.3 | Goals 1, 2, 3 | No |
| 2.4 | Goals 1, 2, 4 | No |

**Verdict: No orphaned tasks. All tasks trace to stated goals.**

---

## Findings

### F-01: Plan Describes Pre-Rename State But Code Is Already Renamed [CRITICAL]
**Category:** Scope Mismatch / Stale Plan
**Details:** The plan, initial analysis section, and phase 1 checklist describe the old naming (`team1_ships` meaning team 0, `team2_ships` meaning team 1) as the current state. However, inspecting the actual codebase reveals that **nearly all production code has already been renamed to 0-based naming**:

| File | Plan says (old naming) | Actual state |
|------|----------------------|--------------|
| `battle_engine.py` | `start(team1_ships, team2_ships)` | `start(team0_ships, team1_ships)` -- ALREADY DONE |
| `battle_service.py` | `team1_ships=self._team0_ships, team2_ships=self._team1_ships` | `team0_ships=self._team0_ships, team1_ships=self._team1_ships` -- ALREADY DONE |
| `battle_screen.py` | `start(team1_ships, team2_ships)` | `start(team0_ships, team1_ships)` -- ALREADY DONE |
| `battle_factories.py` | `create_manual_battle(team1_ships, team2_ships)` | `create_manual_battle(team0_ships, team1_ships)` -- ALREADY DONE |
| `app.py` | `start_battle(team1_ships, team2_ships)` | `start_battle(team0_ships, team1_ships)` -- ALREADY DONE |
| `battle_panels.py` | `team1_ships` for team 0, `team2_ships` for team 1 | `team0_ships` / `team1_ships` -- ALREADY DONE |
| `simulation_adapter.py` | `team1_ships` / `team2_ships` locals | `team0_ships` / `team1_ships` -- ALREADY DONE |
| `setup_screen.py` | `team1_ships, team2_ships` | `team0_ships, team1_ships` -- ALREADY DONE |
| `tests/fixtures/battle.py` | `team1_count`/`team2_count`, `Team1Ship`/`Team2Ship` | `team0_count`/`team1_count`, `Team0Ship`/`Team1Ship` -- ALREADY DONE |
| `test_service_integration.py` | `team1_count=2, team2_count=2` | `team0_count=2, team1_count=2` -- ALREADY DONE |
| `test_battle_screen_simulation.py` | docstring says "team1 and team2" | docstring says "team0 and team1" -- ALREADY DONE |

**All Phase 1 tasks (1.2-1.9) and Phase 2 tasks (2.1-2.3) appear to be complete in the codebase.** The checklist items are still marked "Not Started."

**Impact:** An implementer following this plan would waste significant time trying to apply changes that already exist, get confused by line numbers that don't match, or potentially introduce regressions by re-renaming already-correct code.

**Proposed Resolution:**
1. Mark all completed tasks as done in both checklists
2. Update the plan's "Current State" to reflect that production rename is complete
3. Update or remove the "Initial Analysis" section (line numbers and old-state descriptions are all wrong now)
4. The remaining work is: run Task 2.4 verification (grep + full test suite) to confirm completeness, and address F-02 below

---

### F-02: Missing File -- `test_battle_determinism.py` Still Uses Old Naming [MODERATE]
**Category:** Unaddressed Goal / Missing Task
**Details:** `tests/integration/fleet_combat/test_battle_determinism.py` contains:
- Line 16: `def _run_battle(team1_ships, team2_ships, ...)` -- old naming for local function params
- Line 20: `engine.start(team1_ships, team2_ships, seed=seed)` -- passes positionally (works but uses old variable names)
- Lines 35, 46: `team1 = [...]`, `team2 = [...]` -- old naming for local variables in `_make_teams()`

This file is NOT listed in the Key Files Reference, NOT in the In Scope / Out of Scope sections, and NOT addressed by any task. The plan's grep in Task 2.4 (`grep -r "team2_ships" game/ tests/`) WOULD catch this, but there is no task to actually fix it.

**Impact:** Task 2.4's grep verification will fail because `team2_ships` still appears in `tests/`. The plan has no task to fix it, creating a gap between the verification step and the actionable tasks.

**Proposed Resolution:** Add a new task (e.g., Task 2.2b or expand Task 2.2) to rename `_run_battle(team1_ships, team2_ships)` to `_run_battle(team0_ships, team1_ships)` and rename `team1`/`team2` locals in `_make_teams()` in `tests/integration/fleet_combat/test_battle_determinism.py`. Add this file to the Key Files Reference.

---

### F-03: Stale Code Example in `tests/fixtures/README.md` [MODERATE]
**Category:** Scope Mismatch
**Details:** Line 152 of `tests/fixtures/README.md` shows:
```python
engine = create_battle_engine_with_ships(team1_count=3, team2_count=2)
```
This uses the old `team1_count`/`team2_count` parameter names. The actual function signature is now `team0_count`/`team1_count`. This file is not mentioned in the plan at all.

**Impact:** Developers reading the fixtures README will get incorrect usage examples. Task 2.4's grep for `team2` would NOT catch this since it searches `game/` and `tests/` but not the README content specifically (though `tests/fixtures/README.md` is within the `tests/` search path, so `grep -r "team2_count" tests/` from Task 2.4's third bullet would actually catch the text `team2_count` here).

**Proposed Resolution:** Add a task or subtask to update the README example. This could be folded into Task 2.1 (same directory) or Task 2.4 (cleanup sweep).

---

### F-04: Phase 1 Line Number References Are All Wrong [MINOR]
**Category:** Stale Plan Data
**Details:** Phase 1 checklist references specific line numbers (e.g., "Line 223", "Line 259", "Line 275") that corresponded to the pre-rename state of the codebase. Since the rename has been applied, these line numbers may have shifted due to other changes, and the content at those lines no longer matches what the checklist describes. For example, the checklist says "Line 223: Rename parameter `team1_ships`" but line 240 in the current file already shows `team1_ships: List['Ship']` (the correctly-renamed team 1 parameter).

**Impact:** Low -- since the tasks are already done, nobody should need to follow these line references. But if the plan is left as-is, it creates confusion about project status.

**Proposed Resolution:** If tasks are marked done (per F-01 resolution), line number accuracy is moot. If the plan is kept for historical reference, add a note that line numbers reflect the pre-work state.

---

### F-05: Checklist Status Not Updated [MINOR]
**Category:** Process
**Details:** Both phase checklists show "Status: Not Started" and all checkboxes are unchecked, despite the work being complete in the codebase. The plan's "Current State" section says "Active Phase: Planning" and "Next Action: Begin Phase 1."

**Impact:** Any agent or developer picking up this project would not know the work is mostly done, leading to wasted effort or duplicate changes.

**Proposed Resolution:** Update checklist statuses to reflect reality. Mark completed items. Update the plan's Current State to indicate that production rename is complete and only verification (Task 2.4) remains.

---

## Phase Coherence Analysis

### Phase ordering: CORRECT
Phase 1 (production code) before Phase 2 (test fixtures + verification) is the right order. Dependencies are respected -- engine renamed before callers, callers before tests.

### Task ordering within phases: CORRECT
Tasks 1.2-1.9 follow dependency order: engine (1.2) -> service call site (1.3) -> screen (1.4) -> factory (1.5) -> app (1.6) -> local variables (1.7-1.9). Bookended by baseline (1.1) and verification (1.10).

### Complexity tags: CORRECT
All tasks are tagged [Simple], which is appropriate for a mechanical rename refactor. No task has hidden complexity.

### Test commands: CORRECT
Each task specifies reasonable, targeted test commands. The final verification uses the full sharded test suite.

---

## Scope Consistency Analysis

### In Scope vs Tasks: MATCH (with exceptions)
All In Scope items have corresponding tasks. The one exception is that `test_battle_determinism.py` should be In Scope but is not mentioned (F-02).

### Out of Scope vs Tasks: NO CONFLICTS
No task touches anything listed as Out of Scope. The exclusions (BattleResult fields, BattleService internal attributes, display labels, simulation_tests) are all correctly avoided.

### Key Files vs Tasks: MATCH
All 11 Key Files entries are referenced by at least one task. The gap is that `test_battle_determinism.py` should be a 12th Key File entry.

---

## Overall Assessment

The plan is **well-designed** in terms of goal coverage, task decomposition, phase ordering, and scope definition. The structural quality is high.

The **critical issue** is that the plan is stale -- the work described has already been done in the codebase, but the plan/checklists don't reflect this. One test file (`test_battle_determinism.py`) was missed and still has old naming. The fixtures README has a stale example.

### Recommended Actions (Priority Order)
1. **Update plan status** to reflect that Phase 1 and most of Phase 2 are complete (F-01, F-05)
2. **Add task for `test_battle_determinism.py`** rename (F-02) -- this is the only remaining code change
3. **Add subtask for `tests/fixtures/README.md`** example update (F-03)
4. **Run Task 2.4** verification to confirm everything is clean after fixing F-02 and F-03
