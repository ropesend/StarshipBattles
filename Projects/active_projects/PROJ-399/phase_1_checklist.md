# Phase 1: Pre-existing failures + collection errors

**Status:** Complete (awaiting user verification)
**Objective:** Get the sharded suite to ZERO failures + ZERO collection errors.

---

## Tasks

### Task 1.1: Investigate `test_pathfinder_attached_after_init`
**File:** `tests/integration/strategy/test_save_round_trip_phase4.py` + `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/integration/strategy/test_save_round_trip_phase4.py -v`

- [x] Run the failing test, read the actual `AttributeError` trace.
- [x] Find where `Galaxy._intercept` was supposed to be set during init. (Likely deleted or renamed in earlier work.)
- [x] Decide: restore the attribute, rename the test to match the new attribute path, or delete the test if the assertion is obsolete.
- [x] Verify: focused test passes.

### Task 1.2: Reconcile `test_skill_does_not_claim_coverage_json_is_supported`
**File:** `.opencode/skills/ocode-testcoverage-audit/SKILL.md` + `tests/unit/tools/test_testcoverage_audit.py`
**Tests:** `pytest tests/unit/tools/test_testcoverage_audit.py -v`

- [x] Read the test — what was it asserting about the skill description?
- [x] User commit `e0e9dae08` removed the `"future extension point"` phrase from SKILL.md.
- [x] Decide: restore the phrase if it's load-bearing, OR update the test's substring expectation to match current SKILL.md content.
- [x] Verify: focused test passes.

### Task 1.3: Reconcile `test_scalene_workflow_files_are_documented`
**File:** `docs/README.md` + `tests/unit/tools/test_scalene_profiling_workflow.py`
**Tests:** `pytest tests/unit/tools/test_scalene_profiling_workflow.py -v`

- [x] Read the test — what link was it asserting?
- [x] User docs reorg `9642b50f2` likely moved the `[performance_profiling.md](guides/performance_profiling.md)` link.
- [x] Decide: restore the link in docs/README.md, OR update the test to look for the new docs path.
- [x] Verify: focused test passes.

### Task 1.4: Fix 4 pytest collection errors (basename collisions)
**File:** Various `tests/unit/{ui,workshop}/`
**Tests:** `pytest tests/unit/ui/ tests/unit/workshop/ --collect-only`

- [x] Identify the 4 colliding pairs (each `test_components.py`, `test_panel_factory.py`, `test_stat_getters.py`, `test_workshop_data_loader.py` exists in 2 different test directories without `__init__.py`).
- [x] Preferred fix: add `__init__.py` files to the affected directories so pytest treats them as packages (disambiguates without renaming).
- [x] Alternative: rename one of each pair to a unique name.
- [x] Verify: `--collect-only` returns 0 errors; full focused test path passes.

### Task 1.5: Final verification
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite returns ZERO failures + ZERO collection errors.
- [x] If new failures appear (introduced by another concurrent change), those go in a NEW remediation project, not this one.

---

## Phase Completion Checklist
- [x] All 5 items resolved
- [x] Sharded suite is clean
- [x] Update plan.md phase table row to `Complete`

_Source: stage-boundary sharded suite reports (PROJ-380..393 orchestration run)_
