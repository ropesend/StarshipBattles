# Phase 10: Final Verification — Zero Shims Remain

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 10`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final sweep confirming zero singleton shims remain in production or test code. Update documentation and regression tests.

---

## Tasks

### Task 10.1: Grep verification — zero shim usage [Simple]

- [ ] `grep -rn "\.instance()" game/ --include="*.py"` — zero results (excluding singleton.py docstring)
- [ ] `grep -rn "\.instance()" tests/ conftest.py --include="*.py"` — zero results
- [ ] `grep -rn "\.reset()" game/ --include="*.py"` — zero singleton reset calls (exclude unrelated .reset() like cache_clear)
- [ ] `grep -rn "\.reset()" tests/ --include="*.py" | grep -E "Manager|Profiler|Service|Settings"` — zero results
- [ ] `grep -rn "metaclass=SingletonMeta" game/ --include="*.py"` — zero results
- [ ] `grep -rn "from game.core.singleton import" game/ --include="*.py"` — zero results

---

### Task 10.2: Update regression test for singleton counts [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`

- [ ] Read the file — it contains tests counting `RegistryManager.instance()` occurrences
- [ ] Update expected counts to 0 (or remove the counting tests since shims no longer exist)
- [ ] Run: `pytest tests/regression/test_deprecated_code_removed.py -x -q`

---

### Task 10.3: Update documentation [Simple]
**File:** `docs/02_PATTERNS.md`

- [ ] Update ApplicationContext section to note shims have been fully removed
- [ ] Remove any remaining references to `.instance()` as a valid access pattern
- [ ] Verify CLAUDE.md still accurate

---

### Task 10.4: Full test suite [Simple]

- [ ] `python Tools/test_sharded/test_sharded.py` — 14783+ pass, 0 failures
- [ ] `python -m combat_lab.run_tests --fast` — all pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero `.instance()` anywhere in codebase (production + tests)
- [ ] Zero `.reset()` on former singletons anywhere in codebase
- [ ] Zero `SingletonMeta` imports in production code
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete — All shims removed"
