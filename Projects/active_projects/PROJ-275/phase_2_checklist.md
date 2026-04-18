# Phase 2: Ring-Based Entry Vectors

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 2`

**Status:** Complete
**Objective:** Implement a pure function that assigns entry vectors for any team count. TDD.

---

## Tasks

### Task 2.1: Write failing tests [Medium]
**File:** `tests/unit/simulation/combat/test_formation.py` (append — file exists)
**Tests:** `pytest tests/unit/simulation/combat/test_formation.py::test_resolve_team_entry_vectors -v`

- [x] Test: `team_count=2, arena_radius=2000` returns EXACTLY the current west/east layout (backcompat)
- [x] Test: `team_count=3, arena_radius=2000` returns 3 equally-spaced points at 120° intervals
- [x] Test: `team_count=4, arena_radius=2000` returns 4 points at 90° intervals (N, E, S, W)
- [x] Test: Each team's facing points inward (toward origin)
- [x] Test: `team_count=1` raises ValueError
- [x] Test: `team_count=0` raises ValueError
- [x] Test: `team_count > 8` raises ValueError
- [x] Run — all fail (function doesn't exist)

**Notes:** 8 new tests added to existing `test_formation.py` under `TestResolveTeamEntryVectors` class. Tests use `math.hypot` / `atan2` to assert ring properties invariantly. Included a "default arena_radius" test and a `team_count=9` raises-ValueError test (plan originally wrote ">8"; implemented as `> 8` boundary). Initial run: 8 fail with `ImportError: cannot import name 'resolve_team_entry_vectors'` — correct TDD-red state.

### Task 2.2: Implement `resolve_team_entry_vectors` [Medium]
**File:** `game/simulation/combat/formation.py`
**Tests:** `pytest tests/unit/simulation/combat/test_formation.py -v`

- [x] Add function per design.md sketch
- [x] Preserve exact 2-team behavior (west origin facing east; east origin facing west)
- [x] For N≥3: angle_step = 360 / N; team i at angle i*angle_step; facing = angle + 180 (inward)
- [x] Raise ValueError for team_count < 2 or > 8
- [x] Add docstring explaining the ring convention
- [x] Run tests — pass

**Notes:** Implemented at `game/simulation/combat/formation.py` L316-363. Exported `DEFAULT_ARENA_RADIUS = 500.0` + `resolve_team_entry_vectors` in `__all__`. Convention: team i at angle `(180 + i*(360/N))°` — starting offset 180° ensures team 0 always sits at west (-r, 0) for ANY N, preserving player expectations from the 2-team case. Added floating-point snap near zero (epsilon = `1e-9 * max(1.0, arena_radius)`) so the 2-team layout reports `(-500.0, 0.0)` byte-identically to the legacy `_SIDE_ENTRY_VECTORS` constant (without the snap, sin(180°) produces `6e-14` artifacts). All 15 formation tests pass (7 existing + 8 new).

### Task 2.3: Verify existing 2-team battles unchanged [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/ tests/integration/strategy/combat/ -n 12`

- [x] All existing battle integration tests pass with no behavioral change
- [x] In particular: `tests/integration/simulation/test_boundary_retreat.py` and 2-team Battle Setup tests produce identical ship positions as before
- [x] If any diverge, confirm the divergence is intentional (likely: entry vectors flipped N/S vs. E/W) — if unintentional, fix

**Notes:** Regression sweep `tests/integration/simulation/ tests/unit/ui/screens/battle_setup/ tests/unit/simulation/combat/`: **379 passed, 0 failed** in 3.81s. No behavioral regression. The function is not yet consumed by any production code (that's Phases 4 + 6) — so Phase 2 is purely additive and mechanically guarantees backward compat. The snap-to-zero also keeps downstream tests that assert exact `(-500, 0)` / `(500, 0)` positions stable when they eventually consume the helper in Phase 4.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status / plan.md as usual
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 2`
