# Phase 9: Documentation Rewrite

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 9`

**Status:** Not Started
**Objective:** Remove all "2-team assumption" caveats from docs. Document ring entry vectors + N-team invariants.

---

## Tasks

### Task 9.1: Rewrite `combat_simulation.md` §9 [Medium]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] Delete the "Multi-team Battle Limits (PROJ-272 Phase 9)" section (current §9) — it documents the old 2-team assumption
- [ ] Replace with "Multi-Team Battle Support" documenting:
  - Engine has always supported N teams
  - Compilers now emit N `TeamSpec`s
  - `_route_team_for_scope` returns `List[int]`; enemy-scope entries fan out
  - Ring entry vectors at 360/N intervals
  - Max 8 teams (UI cap)
  - `TeamEliminatedCondition` wins at ≤1 alive team (correct for any N)
  - Mid-battle reinforcement: new ship joins its specified team_id

**Notes:**

### Task 9.2: Rewrite conflict-resolution section in `strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [ ] Find the section describing `ConflictResolutionEngine` sequential 2-fleet decomposition
- [ ] Rewrite: 3+ empires in one sector produce a single N-team battle; no decomposition
- [ ] Update the `_NUM_TEAMS = 2` reference (around L800) — delete or update to "determined by state.sides"

**Notes:**

### Task 9.3: Update pattern catalog [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual review

- [ ] Review existing patterns for "2-team" phrasing; update to "N-team" as appropriate
- [ ] Consider adding a new pattern: "Scope-Driven Team Routing" — explains `_route_team_for_scope` returning `List[int]`

**Notes:**

### Task 9.4: Update memory [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** Manual

- [ ] Add bullet: "N-team combat supported end-to-end (PROJ-275); max 8 teams; ring entry vectors; sequential 2-fleet decomposition deleted"
- [ ] Remove any stale 2-team phrasing

**Notes:**

### Task 9.5: Final sweep [Simple]
**File:** Multiple — grep
**Tests:** N/A

- [ ] `grep -rn "2-team\|2 team\|two-team" docs/` — audit each remaining reference; update or delete
- [ ] `grep -rn "_NUM_TEAMS" docs/` — should be zero
- [ ] `grep -rn "sequential.*fleet.*decomposition\|N-choose-2" docs/` — should be zero
- [ ] `grep -rn "side_0\|side_1" docs/` — should refer only to archived/deleted items

**Notes:**

### Task 9.6: Full suite final check [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green
- [ ] Combat Lab suite: `python -m combat_lab.run_tests` — all passing

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md — mark project COMPLETE
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 9`
- [ ] User verification: manual 3-side Battle Setup + manual 3-empire strategy conflict
