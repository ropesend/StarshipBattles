# Phase 1: Audit & migrate all `scenario.to_spec()` callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-279 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Find every caller of `scenario.to_spec()` (production + tests + dynamic `getattr` lookups) and replace with explicit `build_test_battle_spec(scenario, registries)` calls. Do not delete the monkey-patch yet — Phase 2 does that, after Phase 1 verifies all callers migrated.

---

## Audit Findings (Task 1.1, completed)

**Production callers (4):**
- `combat_lab/services/scenario_run_helper.py:58` — `spec = scenario.to_spec(registries=None)` in `run_scenario_via_run_battle`
- `combat_lab/services/test_execution_service.py:72` — `spec = scenario.to_spec(registries=None)` in visual UI execution path
- `game/ui/screens/test_lab/screen.py:420` — `spec = scenario.to_spec(registries=None)` in `_switch_to_battle`
- `combat_lab/scenarios/templates.py:1069` — `return self.to_spec(registries=None)` in `ComparisonScenario.build_variant_spec()`

**Test callers (1):**
- `tests/unit/combat_lab/test_spec_compiler.py:169` — `test_test_scenario_to_spec_delegates_to_compiler` (tested the patch's behavior; deleted as redundant since the patch itself is being removed)

**Dynamic lookups (`getattr` / `hasattr`):** ZERO production hits.

**Documentation/comment-only mentions:** Multiple (in docstrings, archived project files); not flagged for migration.

---

## Tasks

### Task 1.1: Audit all callers [Simple]
**File:** Audit findings recorded above
**Tests:** N/A (research task)

- [x] Grep for `\.to_spec\(` across the entire repo (production + tests)
- [x] Grep for `getattr.*to_spec` to catch dynamic lookups (zero hits)
- [x] Grep for `hasattr.*to_spec` to catch capability checks (zero hits)
- [x] Document each hit with file:line, caller type (prod/test), and intended replacement
- [x] Confirm zero callers in non-Combat Lab code (1 hit in `game/ui/screens/test_lab/screen.py` is the visual UI integration; no other game-layer callers)

**Notes:** 4 production + 1 test caller. The production hits are all clean call sites. The single test caller's purpose was meta — verifying the monkey-patch worked — so it's deleted in Task 1.3 rather than migrated.

### Task 1.2: Migrate production callers [Medium]
**File:** 4 files modified
**Tests:** `pytest tests/unit/combat_lab/ tests/unit/test_lab/ tests/unit/ui/`

- [x] `combat_lab/services/scenario_run_helper.py` — added `from combat_lab.spec_compiler import build_test_battle_spec`; replaced call site with PROJ-279 comment
- [x] `combat_lab/services/test_execution_service.py` — added local import inside the method (matches surrounding lazy-import pattern); replaced call site
- [x] `game/ui/screens/test_lab/screen.py` — added local import inside `_switch_to_battle`; replaced call site
- [x] `combat_lab/scenarios/templates.py` — `ComparisonScenario.build_variant_spec()` migrated; the call was internal (`self.to_spec`) but still flowed through the monkey-patched method, so updated to explicit call
- [x] Run targeted tests — initially saw 27 mock-related failures (covered in Task 1.3 fix below)
- [x] Verify behavior unchanged once mock fixture patched: all 3626 tests pass

**Notes:** All 4 production callers migrated to explicit composition. The migration revealed that 27 mock-based tests in `tests/unit/combat_lab/services/` and `tests/unit/test_lab/` relied on the production code calling `mock_scenario.to_spec()` to inject a controlled spec. Task 1.3 below adds an autouse fixture that bridges the gap.

### Task 1.3: Migrate test callers + add fixture bridge [Medium]
**Files:** `tests/unit/combat_lab/test_spec_compiler.py`, `tests/fixtures/test_scenarios.py`, `tests/unit/combat_lab/services/conftest.py`, `tests/unit/test_lab/conftest.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/ tests/unit/test_lab/ tests/unit/ui/`

- [x] **Deleted** `test_test_scenario_to_spec_delegates_to_compiler` (and its section header) from `test_spec_compiler.py` — its purpose was verifying the patch we're removing, so migrating to `build_test_battle_spec` would make it tautological
- [x] **Added helper** `patch_spec_compiler_to_delegate_to_mock_scenario()` in `tests/fixtures/test_scenarios.py` — returns a `mock.patch` context manager that patches `combat_lab.spec_compiler.build_test_battle_spec` with a `side_effect` that calls `scenario.to_spec(registries)`. Preserves every existing assertion like `mock_scenario.to_spec.assert_called_once()` without rewriting tests
- [x] **Added autouse fixture** `_proj279_patch_spec_compiler` to `tests/unit/combat_lab/services/conftest.py` (existing conftest)
- [x] **Created** `tests/unit/test_lab/conftest.py` with the same autouse fixture (no conftest existed there before)
- [x] All 3626 tests in PROJ-279 scope pass

**Notes:** The fixture-bridge approach was chosen over rewriting all 27 tests because the tests' Mock setups (`mock_scenario.to_spec.return_value = empty_spec`) are still semantically correct — they just need the production call to route through them. The `side_effect` pattern preserves every existing assertion verbatim.

### Task 1.4: Verify no dynamic callers remain [Simple]
**File:** N/A (verification)
**Tests:** Grep + targeted regression sweep

- [x] Re-grep `\.to_spec\(`, `getattr.*to_spec`, `hasattr.*to_spec` — only docstring breadcrumbs and archived project files remain
- [x] Targeted regression: `pytest tests/unit/combat_lab/ tests/unit/test_lab/ tests/unit/ui/` returns 3626 passed
- [x] Combat Lab simulation suite: 162 passed / 0 failed / 0 skipped

**Notes:** Skipped the full sharded suite at this point — Phase 2 will run the full suite after the monkey-patch deletion, which is the more meaningful checkpoint.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Caller audit recorded in this checklist
- [x] PROJ-279 scope tests pass (3626)
- [x] Combat Lab simulation suite passes (162)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (delete the monkey-patch)
