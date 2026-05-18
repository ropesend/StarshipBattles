# Phase 2: Session / facade projection boundary cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 1 (canonical restoration path landed)
**Objective:** Narrow the named remaining `GameSession` mixed concerns (`save_path`, `human_player_ids`, derived `active_empire`/`enemy_empire`, lazy race-registry/config ownership, façade cache holder) into clearer separations between owned runtime state and derivable read projections — without redesigning the façade public API.

**Resolution (2026-05-18):** Phase 2 collapsed to a **documentation + invariant-pinning pass**. The blast-radius audit (60+ caller files across the four bare-attribute concerns) made a holder-extraction sweep poor ROI; the kickoff prompt's "don't expand into a façade API redesign" was binding. See `decisions.md` row dated 2026-05-18 for the full rationale.

---

## Tasks

### Task 2.1: Failing invariant test [Simple, TDD]
**Files:** `tests/unit/strategy/engine/test_game_session_projection_boundary.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_game_session_projection_boundary.py`

- [x] Write a failing AST/inspection-based test pinning the post-Phase-2 shape of `GameSession`. Initial intent was to assert holder extraction; revised after blast-radius audit to assert **categorical ownership documentation** (which is the actual Phase 2 narrowing). *(8 tests: 6 invariants on attribute categories + property contracts; 2 docstring contracts. Initially 6/8 passed and 2/8 failed — the two docstring tests for GameSession class docstring + FacadeSessionState perf-boundary marker.)*
- [x] Confirm tests fail before any production change.

### Task 2.2: Categorical documentation pass (in place; no holder/sweep) [Small]
**Files:** `game/strategy/engine/game_session.py`, `game/strategy/facade/slices/_facade_state.py`
**Tests:** Task 2.1 tests + `pytest tests/unit/strategy/test_game_session.py tests/unit/strategy/engine/session/`

- [x] Add a categorical class docstring to `GameSession` grouping every owned attribute by purpose (Owned domain state, Owned UI-rotation state, Owned UI configuration, Owned persistence metadata, Lazy-init owned services, Service-bag delegation). Explicitly notes that `active_empire`/`enemy_empire` are mutable UI-rotation state per BUG-125, NOT projections.
- [x] Add matching inline category comments in `_apply_bootstrap_state` so the same grouping is visible at the assignment site.
- [x] Update `FacadeSessionState` docstring to mark the per-turn cache as an **intentional performance boundary** (not compensation debt). Document that `invalidate_all` bounds freshness to one turn.
- [x] Run Task 2.1 tests: 8/8 green.
- [x] Run existing GameSession + session-bootstrap regression tests: 41/41 green.

### Task 2.3: Substrate-vs-sweep decision recorded [Small]
**Files:** `Projects/active_projects/PROJ-438/decisions.md`
**Tests:** None

- [x] Record the scope-collapse decision in `decisions.md` with blast-radius numbers and rationale (60+ caller files would have been a façade redesign in disguise; substrate `_apply_bootstrap_state` already exists from PROJ-423; future-projects note if a natural holder ever emerges).

### Task 2.4: Sweep + sharded suite [Small]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] No sweep required — the narrowing is in place, not extractive.
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 1 baseline)
- [x] Game still runnable / savable / loadable (no behavior changed — pure docstring + comment additions; preserved by 41 session regression tests)
- [x] Façade public API unchanged (no façade code changed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
- [x] `python Projects/scripts/validate_phase.py PROJ-438 2` passes
