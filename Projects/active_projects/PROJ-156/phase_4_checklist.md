# Phase 4: Directory Cleanup & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (depends on Phase 3 completion)
**Objective:** Clean up emptied directories and run final verification. Confirm no regressions.
**Priority:** Normal

---

## Tasks

### Task 4.1: Clean up controllable_interface directory [Simple]
**Path:** `tests/unit/ai/controllable_interface/`

After Phase 1 (deleted `test_interface_definition.py`) and Phase 3 Task 3.4 (will delete `test_adapter_basics.py` + `test_adapter_methods.py`):

- [ ] List remaining files in `tests/unit/ai/controllable_interface/`
- [ ] If only `conftest.py` and/or `__init__.py` remain, delete the entire directory
- [ ] If test files remain, document which ones and leave directory alone

**Notes:** Currently contains: `__init__.py`, `conftest.py`, `test_adapter_basics.py`, `test_adapter_methods.py`. After Phase 3 Task 3.4, only `__init__.py` and `conftest.py` should remain — delete the entire directory.

### Task 4.2: Verify target_evaluator directory [Simple]
**Path:** `tests/unit/ai/target_evaluator/`

After Phase 3 Tasks 3.5 and 3.6 (will delete `test_evaluation_integration.py` and `test_evaluation_rules.py`):

- [ ] List remaining files in `tests/unit/ai/target_evaluator/`
- [ ] Verify `test_capabilities_cache.py` still exists and passes
- [ ] Verify conftest.py fixtures are still needed by remaining file(s)
- [ ] If conftest.py has fixtures ONLY used by deleted files, clean up unused fixtures
- [ ] Specifically check: `target_with_hp` fixture appears unused — remove if confirmed

**Notes:** Currently contains: `__init__.py`, `conftest.py`, `test_capabilities_cache.py`, `test_evaluation_integration.py`, `test_evaluation_rules.py`. After Phase 3, only `__init__.py`, `conftest.py`, and `test_capabilities_cache.py` should remain. The `target_with_hp` fixture in conftest.py was identified as unused during code review — verify and remove.

### Task 4.3: Final full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run complete test suite
- [ ] Verify: no new failures beyond pre-existing ones (~143 per PROJ-157 audit)
- [ ] Record final passed count and compare to post-PROJ-157 baseline (~12,185)
- [ ] Summary: total lines removed, total test methods removed, unique tests preserved

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No orphaned directories remain
- [ ] Final test count recorded
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
