# Phase 2: Triage `test_mutator_boundary_ast_guard.py`

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` + any `game/strategy/data/` files implicated by guard violations

**Objective:** Triage the ~9 AST static-guard failures (`test_mutator_boundary[Fleet|Planet|Empire|ShipInstance]` etc.) in `test_mutator_boundary_ast_guard.py`. These guards check that strategy entity mutation flows through the mutator-protocol path documented in `docs/01_ARCHITECTURE.md` §"Protocols And Boundary Contracts." They have drifted relative to post-PROJ-422..436 entity surfaces.

For each guard failure:
1. Is the guard checking a still-valid invariant? If yes, fix the implicated code or test to satisfy it (real architecture violation).
2. If the invariant no longer applies (e.g., post-Phase-3 ShipInstance has the `@property`-over-private-field pattern that the original guard didn't anticipate), rewrite the guard.

---

## Tasks (authored at phase start)

To be authored after Phase 1 completes. Expected per-failure shape:
- Re-run failing test, capture error output.
- Read the implicated production file and confirm whether the AST violation is real architectural drift or test-side drift.
- Commit the appropriate fix with a rationale-bearing decisions.md entry.

---

## Phase Completion Checklist
- [ ] `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py -q -n 4` returns zero failures
- [ ] Sharded suite still green
- [ ] Any rewritten guards documented in `decisions.md`
- [ ] `plan.md` + `phase_state.json` updated
