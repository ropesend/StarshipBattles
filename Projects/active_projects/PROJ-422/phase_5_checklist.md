# Phase 5: Clean review

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):** none (review-only phase)
**Objective:** Final inspection — confirm the diff shape matches the TD plan, leaves have no copy/paste residue, and the package surface is exactly 18 ABCs.

---

## Tasks

### Task 5.1: Confirm diff shape matches the TD plan [Simple]
**Tests:** `git status --short` and `git diff --stat main`

- [ ] Exactly **1 deletion**: `game/strategy/interfaces/engines.py` (778 LOC removed).
- [ ] Exactly **10 additions** under `game/strategy/interfaces/engines/`: `__init__.py` + 9 leaf modules.
- [ ] Exactly **1 rewrite**: `game/strategy/interfaces/__init__.py`.
- [ ] Exactly **1 new test**: `tests/unit/strategy/interfaces/test_engines_package_layout.py`.
- [ ] **0 concrete engine files** modified under `game/strategy/engine/`.
- [ ] **0 pre-existing test files** modified.
- [ ] **1-2 doc files** touched (per Phase 4).
- [ ] Net production code: roughly -778 + ~860 ≈ +80 LOC (the cost of 10 module headers + an explicit `__init__.py`).

**Notes:** [Filled during implementation]

### Task 5.2: Inspect each leaf module for residue [Medium]
**Files:** all 9 leaves under `game/strategy/interfaces/engines/`
**Tests:** manual inspection + `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q`

For each leaf module, confirm:

- [ ] No copy/paste duplicates of an ABC class.
- [ ] No orphan TYPE_CHECKING imports (a TYPE_CHECKING block should only import symbols referenced by the ABCs in that leaf).
- [ ] Docstrings preserved byte-identically from the original monolith — no editorial tightening, no PROJ-tag drops.
- [ ] `from __future__ import annotations` present at the top.
- [ ] `__all__` matches the layout table verbatim.
- [ ] Leaf LOC is well under 200 (max expected: `logistics.py` at ~140).

**Notes:** [Filled during implementation]

### Task 5.3: Confirm `engines/__init__.py` surface [Simple]
**File:** `game/strategy/interfaces/engines/__init__.py`
**Tests:** `python -c "from game.strategy.interfaces import engines; assert len(engines.__all__) == 18; print(sorted(engines.__all__))"`

- [ ] `engines.__all__` lists exactly 18 names.
- [ ] Every name in `__all__` is actually importable from the package root.
- [ ] No name in `__all__` is missing from an explicit import block.
- [ ] No name is imported but missing from `__all__`.

**Notes:** [Filled during implementation. Per TD plan §"Per-Phase Success Criteria" — Phase 5 (cleanup) closes the project.]

### Task 5.4: Final acceptance-criteria sweep [Simple]
**Reference:** [plan.md](plan.md) §"Verification" — the TD plan's acceptance criteria.

- [ ] `engines.py` replaced by package layout without changing public symbols. ✓
- [ ] Package-root imports work for all existing consumers. ✓ (validated by Phase 3 test runs)
- [ ] No concrete engine modules required logic changes. ✓ (confirmed in 5.1)
- [ ] New structural layout test present and passing. ✓
- [ ] Focused interface/import regression coverage green. ✓
- [ ] Full sharded baseline green. ✓ (re-confirm with one more run if anything was touched in Phase 4)
- [ ] Docs no longer describe `engines.py` as a single file. ✓

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Diff shape matches the TD plan exactly
- [ ] All 6 layout-test assertions green
- [ ] All 7 acceptance-criteria items satisfied
- [ ] `python Projects/scripts/validate_phase.py PROJ-422 5` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `All phases complete; ready for user verification`
- [ ] Project ready for archive via `/claude-proj-archive`
