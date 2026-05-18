# Phase 1: Triage `test_cargo_tracking.py`

**Status:** Not Started
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):** `tests/unit/strategy/data/test_cargo_tracking.py` + any production files implicated by real bugs

**Objective:** Triage the ~30 failures in `test_cargo_tracking.py` (PROJ-431-flagged baseline; current count from Phase 0 ledger). After PROJ-436 Phase 3's cargo manager API migration, many should now pass naturally. Classify each remaining failure: (a) now passing — done; (b) test assertion wrong against current contract — fix test; (c) test exposes a real bug — fix production code; (d) test obsolete — delete with rationale in `decisions.md`.

---

## Tasks (authored at phase start)

To be authored after Phase 0 baseline ledger is committed. Expected sub-phase shape:

- **1a** — re-run `pytest tests/unit/strategy/data/test_cargo_tracking.py -q --no-header` and capture the actual current failure list (the baseline may have changed across PROJ-436 Phases 3-7).
- **1b** through **1X** — one commit per cluster of related failures, RED→GREEN. Some clusters: (i) tests reading `ship.cargo_contents` directly that now hit the @property (post-Phase-3f) and need to read via `ship._cargo_mgr` instead; (ii) tests asserting cargo-type validation that now flow through `Container.accepts()` (post-Phase-7); (iii) obsolete tests pinning behavior that no longer exists.
- Final commit — verify `pytest tests/unit/strategy/data/test_cargo_tracking.py -q -n 4` is green.

---

## Phase Completion Checklist
- [ ] All test_cargo_tracking.py failures resolved or documented as deletions in `decisions.md`
- [ ] `pytest tests/unit/strategy/data/test_cargo_tracking.py -q -n 4` returns zero failures
- [ ] Sharded suite still green (no regression in visible tests)
- [ ] `plan.md` + `phase_state.json` updated
