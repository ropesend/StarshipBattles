# Phase 2: Ring-Based Entry Vectors

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 2`

**Status:** Not Started
**Objective:** Implement a pure function that assigns entry vectors for any team count. TDD.

---

## Tasks

### Task 2.1: Write failing tests [Medium]
**File:** `tests/unit/simulation/combat/test_formation.py` (append — file exists)
**Tests:** `pytest tests/unit/simulation/combat/test_formation.py::test_resolve_team_entry_vectors -v`

- [ ] Test: `team_count=2, arena_radius=2000` returns EXACTLY the current west/east layout (backcompat)
- [ ] Test: `team_count=3, arena_radius=2000` returns 3 equally-spaced points at 120° intervals
- [ ] Test: `team_count=4, arena_radius=2000` returns 4 points at 90° intervals (N, E, S, W)
- [ ] Test: Each team's facing points inward (toward origin)
- [ ] Test: `team_count=1` raises ValueError
- [ ] Test: `team_count=0` raises ValueError
- [ ] Test: `team_count > 8` raises ValueError
- [ ] Run — all fail (function doesn't exist)

**Notes:**

### Task 2.2: Implement `resolve_team_entry_vectors` [Medium]
**File:** `game/simulation/combat/formation.py`
**Tests:** `pytest tests/unit/simulation/combat/test_formation.py -v`

- [ ] Add function per design.md sketch
- [ ] Preserve exact 2-team behavior (west origin facing east; east origin facing west)
- [ ] For N≥3: angle_step = 360 / N; team i at angle i*angle_step; facing = angle + 180 (inward)
- [ ] Raise ValueError for team_count < 2 or > 8
- [ ] Add docstring explaining the ring convention
- [ ] Run tests — pass

**Notes:**

### Task 2.3: Verify existing 2-team battles unchanged [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/ tests/integration/strategy/combat/ -n 12`

- [ ] All existing battle integration tests pass with no behavioral change
- [ ] In particular: `tests/integration/simulation/test_boundary_retreat.py` and 2-team Battle Setup tests produce identical ship positions as before
- [ ] If any diverge, confirm the divergence is intentional (likely: entry vectors flipped N/S vs. E/W) — if unintentional, fix

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status / plan.md as usual
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 2`
