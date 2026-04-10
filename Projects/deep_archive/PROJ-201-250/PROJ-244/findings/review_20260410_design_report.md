# PROJ-244 Design Pattern Analysis Report

**Date:** 2026-04-10
**Reviewer:** Design Pattern Analyst Agent
**Scope:** Verify PROJ-244's implementation approach against documented architecture, patterns, and conventions

---

## Executive Summary

PROJ-244 (Team Naming Standardization) has already been implemented in two commits (`d85718a2` partial, `abacb998` complete). The implementation was a pure rename refactor consistent with the project's documented conventions. However, the plan and checklists are now stale (still marked "Not Started"), and there are several residual inconsistencies the implementation missed. The design decisions (0-based naming, keep UI labels 1-based) are sound and align with the project's conventions.

---

## Findings

### FINDING-001: Plan and Checklists Are Stale -- Implementation Already Complete

**Plan Assumption:** Phase 1 and Phase 2 are both "Not Started" as of 2026-04-05.

**Current Reality:** Both phases were implemented on 2026-04-05 in commits `d85718a2` (engine, service, screen) and `abacb998` (factories, app, panels, adapter, setup screen, test fixtures). The plan's `plan.md` still says "Active Phase: Planning" and all checklist items remain unchecked.

**Impact:** Any agent picking up this project would waste time re-implementing already-completed work, or worse, could introduce conflicts. The plan's "Context for Next Agent" still says to begin Phase 1.

**Proposed Resolution:** Mark all checklist items as complete. Update plan.md status to reflect completion. Update the "Current State" section.

---

### FINDING-002: Missed File -- `test_battle_determinism.py` Still Uses Old Naming

**Plan Assumption:** The plan's scope section explicitly lists test files to update, but `test_battle_determinism.py` is NOT listed.

**Current Reality:** `tests/integration/fleet_combat/test_battle_determinism.py` still uses the old naming:
- Line 16: `def _run_battle(team1_ships, team2_ships, seed, max_ticks=500):`
- Line 20: `engine.start(team1_ships, team2_ships, seed=seed)`
- Lines 35-57: `_make_teams()` returns `team1, team2` (local vars with old 1-based naming)

While this works correctly because `engine.start()` uses positional args, it perpetuates the exact off-by-one naming confusion PROJ-244 was created to fix. The parameter `team1_ships` in `_run_battle()` receives ships with `team_id=0`.

**Impact:** Violates the project's stated goal: "All team1_ships references now correctly map to team_id == 1." This file was missed in both the plan's scope analysis and the implementation.

**Proposed Resolution:** Rename `team1_ships` to `team0_ships`, `team2_ships` to `team1_ships` in `_run_battle()`. Rename `team1`/`team2` to `team0`/`team1` in `_make_teams()` and its callers. Add to Phase 2 checklist.

---

### FINDING-003: Missed File -- `docs/systems/combat_simulation.md` Uses Old Naming

**Plan Assumption:** The plan's verification checklist says "No documentation updates needed (this is an internal naming change, not an architecture change)."

**Current Reality:** `docs/systems/combat_simulation.md` line 32-33 shows:
```
controller.add_ships(team1_ships, team_id=0)
controller.add_ships(team2_ships, team_id=1)
```

This is the exact off-by-one pattern PROJ-244 eliminates. Per Rule 2 (Documentation -- CHECK Before, UPDATE After), documentation that contains code examples showing the old naming should be updated.

**Impact:** A developer reading the docs would see the old naming convention and propagate it. Contradicts the project's code-documentation consistency contract from CLAUDE.md.

**Proposed Resolution:** Update the code example to use `team0_ships`/`team1_ships` or use the current factory-based approach.

---

### FINDING-004: Missed File -- `tests/fixtures/README.md` Uses Old Naming

**Plan Assumption:** Not mentioned in plan scope.

**Current Reality:** `tests/fixtures/README.md` line 152 shows:
```
engine = create_battle_engine_with_ships(team1_count=3, team2_count=2)
```

The actual function signature was already renamed to `team0_count`/`team1_count` (verified in `tests/fixtures/battle.py`), making this documentation example incorrect and misleading.

**Impact:** Low severity but still a documentation inconsistency. Developers copying this example would get a TypeError.

**Proposed Resolution:** Update the example to use `team0_count=3, team1_count=2`.

---

### FINDING-005: Design Decisions Are Sound and Consistent

**Plan Assumption:** Use 0-based naming (`team0_ships`, `team1_ships`) matching `team_id` values (0, 1). Keep UI display labels as "TEAM 1" / "TEAM 2".

**Current Reality:** This decision is consistent with:
- **03_CONVENTIONS.md**: No explicit team naming convention exists, but the general principle of matching variable names to their semantic meaning is a standard Python convention.
- **02_PATTERNS.md**: No pattern conflicts. The rename doesn't change any interfaces or protocols.
- **01_ARCHITECTURE.md**: Layer boundaries are respected. The rename correctly follows dependency order (engine first, then callers).
- **ICombatant protocol** (`core/protocols.py`): Uses `team_id: int` which is 0-based. Having variables named `team0_ships` match `team_id=0` is the correct alignment.

**Impact:** None. The decisions are well-reasoned.

**Proposed Resolution:** None needed.

---

### FINDING-006: Phase Structure Is Appropriate

**Plan Assumption:** Two phases: (1) production code, (2) test fixtures + verification.

**Current Reality:** The 2-phase structure is appropriate for a mechanical rename. The dependency-order approach within Phase 1 (engine -> callers -> locals) was correctly followed in the implementation (commit `d85718a2` did engine/service/screen, commit `abacb998` did everything else).

**Impact:** None. The phasing was sensible.

**Proposed Resolution:** None needed.

---

### FINDING-007: No New Patterns or Abstractions Relevant Since Plan Creation

**Plan Assumption:** Plan was written 2026-04-05. Implementation was also done 2026-04-05.

**Current Reality:** Several commits have landed since (PROJ-259 state machine, fleet aura manager, ship decomposition), but none introduce patterns that would affect a team naming rename. The `BattleController` / `create_started_battle_controller()` factory pattern (which the plan correctly identified as already using 0-based naming) remains unchanged.

**Impact:** None.

**Proposed Resolution:** None needed.

---

### FINDING-008: `setup_screen.py` Has Residual Naming Inconsistency

**Plan Assumption:** The plan notes `self.team1` and `self.team2` are "UI data lists, not being renamed."

**Current Reality:** `setup_screen.py` line 102-103:
```python
team0_ships = load_ships_from_entries(self.team1, team_id=0, ...)
team1_ships = load_ships_from_entries(self.team2, team_id=1, ...)
```

Here `self.team1` (1-based UI list) feeds into `team0_ships` (0-based code variable). This is the exact pattern the plan decided to keep -- UI attributes (`self.team1`, `self.team2`) stay 1-based because they represent "Team 1" and "Team 2" display concepts.

**Impact:** This is a deliberate decision documented in the plan. The conversion from 1-based UI naming to 0-based code naming happens at this boundary, which is the correct place for it.

**Proposed Resolution:** None needed. The decision is documented and intentional. A comment explaining the 1-to-0 mapping at this boundary would improve clarity but is not required.

---

## Summary of Required Actions

| Priority | Finding | Action Required |
|----------|---------|----------------|
| High | FINDING-001 | Update plan.md, phase checklists to reflect completed state |
| Medium | FINDING-002 | Rename old naming in `test_battle_determinism.py` |
| Medium | FINDING-003 | Update code example in `docs/systems/combat_simulation.md` |
| Low | FINDING-004 | Update example in `tests/fixtures/README.md` |

## Conclusion

The design approach is consistent with the documented architecture, patterns, and conventions. The 0-based naming decision aligns with `ICombatant.team_id` semantics and eliminates a genuine source of confusion. The implementation was executed correctly for the files it touched. However, three files were missed (one test file, two documentation files), and the project tracking documents are stale. These are minor cleanup items, not design concerns.
