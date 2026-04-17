# Phase 8: End-to-End Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 8`

**Status:** Not Started
**Objective:** Three integration suites, one per entry point. 3-team and 4-team coverage.

---

## Tasks

### Task 8.1: Extend `test_three_team_battle.py` [Medium]
**File:** `tests/integration/simulation/test_three_team_battle.py`
**Tests:** `pytest tests/integration/simulation/test_three_team_battle.py -v`

- [ ] Add: entry vectors for 3 teams are ring-spaced (120° apart)
- [ ] Add: `TeamEliminatedCondition` fires when teams 1 and 2 are dead, team 0 alive → winner=0
- [ ] Add: `TeamEliminatedCondition` fires when all teams have ships → battle continues
- [ ] Add: mid-battle reinforcement added to team 1 correctly assigned (per `add_ship_mid_battle`)
- [ ] Add: `FleetAuraManager` correctly composes bonuses across 3 teams
- [ ] All existing tests pass
- [ ] Run — pass

**Notes:**

### Task 8.2: Create `test_four_team_battle.py` [Medium]
**File:** `tests/integration/simulation/test_four_team_battle.py` (NEW)
**Tests:** `pytest tests/integration/simulation/test_four_team_battle.py -v`

- [ ] Test: 4-team battle runs to completion
- [ ] Test: entry vectors at N/E/S/W positions
- [ ] Test: enemy-scope modifier on team 0 fans to teams 1, 2, 3 (3 entries)
- [ ] Test: `TeamEliminatedCondition` with 3 dead teams
- [ ] Test: AI targeting correctly prioritizes nearest enemy across any team
- [ ] Run — pass

**Notes:**

### Task 8.3: Create `test_three_empire_battle.py` [Medium]
**File:** `tests/integration/strategy/test_three_empire_battle.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_three_empire_battle.py -v`

- [ ] Covered by Phase 7.1 — extend if needed
- [ ] Test: 3 empires at same sector → single 3-team battle
- [ ] Test: each empire's `FleetCombatModifiers` applied to its team
- [ ] Test: `apply_outcome_to_fleets` updates ALL 3 empires' fleets correctly
- [ ] Test: destroyed fleets pruned from their empires
- [ ] Run — pass

**Notes:**

### Task 8.4: Create `test_battle_setup_three_sides.py` [Medium]
**File:** `tests/integration/ui/test_battle_setup_three_sides.py` (NEW)
**Tests:** `pytest tests/integration/ui/test_battle_setup_three_sides.py -v`

- [ ] Test: 3-sided `BattleSetupState` → `build_manual_battle_spec` → 3-team `BattleSpec` → `run_battle` → 3-team `BattleOutcome`
- [ ] Test: enemy-scope complex on side 0 fans to sides 1 and 2 (observable via `ModifierStack` inspection)
- [ ] Test: entry vectors match the ring layout
- [ ] Test: `BattleResultsScreen.extract_battle_results(outcome)` handles 3 teams (display fields populated for all 3)
- [ ] Run — pass

**Notes:**

### Task 8.5: Telemetry overhead regression [Simple]
**File:** N/A
**Tests:** `pytest tests/performance/test_telemetry_overhead.py -v`

- [ ] 2-team baseline unchanged
- [ ] 3-team and 4-team overhead measured and documented
- [ ] If significant regression (>20%), add findings to `findings/perf_n_team.md` and revisit

**Notes:**

### Task 8.6: Full suite final [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full pytest suite green
- [ ] No existing test regressions
- [ ] Baseline expanded (14727 + new tests)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 8`
