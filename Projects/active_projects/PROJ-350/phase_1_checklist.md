# Phase 1: Regression Test + Registry Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-350 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (awaiting user verification)
**Objective:** Replace the bespoke `spec_from_file_location` loader in `combat_lab/registry.py` with `importlib.import_module`, locked in by a regression test that fails on current main.

---

## Tasks

### Task 1.1: Write failing regression test [Simple]
**File:** `tests/unit/combat_lab/test_registry_class_identity.py` (new)
**Tests:** `pytest tests/unit/combat_lab/test_registry_class_identity.py -v`

- [x] Import `combat_lab.spec_compiler` first (forces template-class identity into compiler globals)
- [x] Import `ComparisonScenario` from `combat_lab.scenarios.templates` and capture as `compiler_template_cls` (same module the compiler imported)
- [x] Reset and instantiate `TestRegistry`
- [x] Fetch a registered ComparisonScenario subclass (use `TOHIT-ATK-001` — `SensorIncreasesAccuracyScenario`)
- [x] Instantiate it
- [x] Assert `isinstance(inst, compiler_template_cls)` is True
- [x] Assert `build_test_battle_spec(inst, registries=None)` does not raise
- [x] Run on current main — verify the test FAILS with `NotImplementedError` and the isinstance assertion

**Notes:** Test must be in a fresh-process state so prior imports don't mask the bug.

---

### Task 1.2: Apply registry fix [Simple]
**File:** `combat_lab/registry.py`
**Tests:** `pytest tests/unit/combat_lab/test_registry_class_identity.py -v`

- [x] Replace lines 197-208 (the `spec_from_file_location` block) with `module = importlib.import_module(module_name)`
- [x] Drop now-unused imports (`importlib.util`, possibly `sys` if no other usage remains)
- [x] Verify file imports still parse and lint clean
- [x] Re-run regression test — must now PASS

**Notes:** Diff target:
```diff
- spec = importlib.util.spec_from_file_location(module_name, file_path)
- if spec is None or spec.loader is None:
-     logger.warning(f"Could not load spec for {file_path}")
-     continue
- module = importlib.util.module_from_spec(spec)
- sys.modules[module_name] = module
- spec.loader.exec_module(module)
+ module = importlib.import_module(module_name)
```

---

### Task 1.3: Targeted Combat Lab verification [Simple]
**Tests:** `python -m combat_lab.run_tests TOHIT-ATK-001 --no-history`

- [x] Reproduce the original crash path: run TOHIT-ATK-001 (the scenario the user crashed on) headless
- [x] Verify no `NotImplementedError`
- [x] Run `python -m combat_lab.run_tests --fast` — verify all non-`-HT` Combat Lab scenarios pass

**Notes:** This validates the original user-facing crash is gone, not just the unit test.

---

### Task 1.4: Full regression sweep [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite
- [x] Baseline: 15405 passed (per memory MEMORY.md "Recently Archived 2026-04-27")
- [x] No regressions; new regression test included in count
- [x] If any failure surfaces, diagnose root cause — do NOT skip or weaken tests

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to closure / awaiting user verification
