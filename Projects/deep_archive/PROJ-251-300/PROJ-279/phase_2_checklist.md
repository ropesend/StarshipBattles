# Phase 2: Delete the monkey-patch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-279 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Delete the module-import-time monkey-patch at the bottom of `combat_lab/spec_compiler.py` that attaches `to_spec` to the `TestScenario` base class. After Phase 1 migrated every production call to `build_test_battle_spec(scenario)`, the patch has no callers — but its deletion REVEALS that 5 scenario subclasses had legitimately overridden `to_spec` for non-canonical layouts, requiring a small dispatch update.

---

## Tasks

### Task 2.1: Delete the monkey-patch [Simple]
**File:** `combat_lab/spec_compiler.py`
**Tests:** Targeted regression after deletion

- [x] Removed the `_to_spec` helper function and `TestScenario.to_spec = _to_spec` assignment (was lines 487-498)
- [x] Removed the section header comment block above the patch
- [x] Verified `__all__` block was unaffected

**Notes:** Clean deletion of ~13 lines including comment block. Pre-existing IDE hint about an unrelated unused `_` variable (line 72) is in a different function and was not introduced by this edit.

### Task 2.2: Restore polymorphic dispatch via subclass-override escape hatch [Medium]
**File:** `combat_lab/spec_compiler.py::build_test_battle_spec`
**Tests:** `python -m combat_lab.run_tests --fast`

After deleting the patch, the Combat Lab simulation suite revealed 5 scenarios that had defined their own `to_spec` overrides (in `tohit_attack_fleet_scenarios.py` × 3, `propulsion_scenarios.py` × 2). The previous code path was `production_caller.to_spec()` → polymorphic dispatch → subclass override OR (via patch) base→`build_test_battle_spec`. After Phase 1 migration, production calls `build_test_battle_spec(scenario)` directly, bypassing the subclass overrides.

- [x] Added MRO walk at the top of `build_test_battle_spec`: for each class between `type(scenario)` and `TestScenario`, check if it defines its own `to_spec` in `__dict__`; if yes, delegate to that override
- [x] Updated docstring to document the new dispatch order: (1) subclass override, (2) canonical template dispatch, (3) NotImplementedError
- [x] Updated NotImplementedError message to mention the `to_spec` override escape hatch
- [x] Verified Combat Lab simulation suite: 162 passed / 0 failed / 0 skipped (was failing on `FleetSensorSameGroupMax` etc. before this fix)

**Notes:** This preserves the user's "explicit composition" intent for the 95% case (5 canonical templates) while keeping the polymorphic-override capability that real custom scenarios depend on. The escape hatch is documented in the dispatch function's docstring.

### Task 2.3: Regression sweep [Simple]
**Tests:** PROJ-279 scope + Combat Lab simulation

- [x] `pytest tests/unit/combat_lab/ tests/unit/test_lab/ tests/unit/ui/`: 3626 passed
- [x] `python -m combat_lab.run_tests --fast`: 162 passed / 0 failed / 0 skipped

**Notes:** Pre-existing 78 failures in `tests/unit/strategy/data/` (`test_race_config.py`, `test_storm.py`, etc. — `TypeError: cannot unpack non-iterable ValidationResult object`) are unrelated to PROJ-279. They appear to be a different codebase-wide pre-existing baseline issue from the `test_galaxy_cleanup.py` failures noted earlier in PROJ-278.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] PROJ-279 scope: 3626 tests pass
- [x] Combat Lab simulation: 162 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (documentation)
