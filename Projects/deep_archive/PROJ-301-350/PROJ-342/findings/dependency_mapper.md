# PROJ-342: Dependency Mapper Findings

**Date:** 2026-05-04  
**Scope:** Comprehensive sweep for callers of TestExecutionService, TestResultsService, TestLabUIController.handle_run_visual, and TestLabUIController.handle_run_headless that grep-based analysis might miss.

---

## Executive Summary

**PLAN VALIDATION: SAFE TO EXECUTE**

The plan to delete TestExecutionService, TestResultsService, and the two controller methods is safe. All production callers are confined to:
1. TestLabUIController itself (being deleted/refactored)
2. Two test files already listed in the plan for update/deletion
3. Docstrings and diagram documentation (stale, not live code)

**No dynamic dispatch, plugin registries, wildcard imports, or indirect references were discovered.** The plan can proceed without revision.

---

## Investigation Methodology

Investigated six categories per specification:

1. **Dynamic dispatch:** getattr(...), globals()['...'], importlib.import_module, pkgutil, plugin/registry patterns
2. **Wildcard imports:** rom combat_lab.services import * usage
3. **Indirect references:** Config files (JSON/YAML), event buses, string-based dispatchers, scene callbacks
4. **Test fixtures & conftest:** All test imports outside documented test files
5. **Docstring verification:** scenario_run_helper.py lines 4 and 68
6. **Archive & Tools:** _marked_for_deletion_*, Tools/, Projects/scripts/

---

## Findings by Category

### 1. Direct Imports: TestExecutionService / TestResultsService

**Status: All accounted for in plan**

| File | Import Type | Lines | Classification | Plan Status |
|------|-------------|-------|-----------------|-------------|
| combat_lab/services/__init__.py | Named export | 10, 12 | production-export | Delete with module |
| combat_lab/services/test_lab_controller.py | Import + instantiate | 11, 13, 41, 43 | production-call | Refactor controller; remove imports |
| 	ests/unit/combat_lab/services/test_test_execution_service.py | Test import | — | test | **Delete entire file (Phase 4)** |

**No other files import these services.**

---

### 2. Direct Calls: handle_run_visual / handle_run_headless

**Status: All accounted for in plan**

| File | Method Call | Context | Classification | Plan Status |
|------|-------------|---------|-----------------|-------------|
| 	ests/unit/combat_lab/services/test_controller_init_events.py:150 | controller.handle_run_visual() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_init_events.py:164 | controller.handle_run_visual() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_init_events.py:179 | controller.handle_run_visual() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_execution.py:36 | controller.handle_run_headless() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_execution.py:60 | controller.handle_run_headless() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_execution.py:74 | controller.handle_run_headless() | Unit test | test | Update test suite (Phase 4) |
| 	ests/unit/combat_lab/services/test_controller_execution.py:89 | controller.handle_run_headless() | Unit test | test | Update test suite (Phase 4) |

**No production callers found.** Current UI path routes through game/ui/screens/test_lab/screen.py and 	est_executor.py, not through controller methods (verified in plan r002 lines 17-18).

---

### 3. Dynamic Dispatch Investigation

**Status: No dynamic dispatch found**

#### 3a. getattr / importlib Patterns

- combat_lab/runner.py:36, 37, 160, 161 — getattr(ship, ...) for attribute access on ship objects; **unrelated to services**
- combat_lab/runner.py:292 — importlib.import_module(args.scenario) for loading scenario modules; **not service dispatch**
- combat_lab/runner.py:298 — getattr(module, attr_name) for discovering TestScenario subclasses; **not service dispatch**
- combat_lab/registry.py:212 — getattr(module, attr_name) for discovering TestScenario classes; **not service dispatch**

**Conclusion:** No reflection-based calls to TestExecutionService or TestResultsService.

#### 3b. globals() / __dict__ Access

**Status: No matches found** for service names in globals(), __dict__, or setattr patterns.

#### 3c. Plugin/Registry Patterns

**Status: No plugin/registry patterns found** for service dispatch.

- TestRegistry manages test scenario discovery, not service dispatch.
- UIStateService manages UI state, not service routing.
- No event bus, observer pattern, or callback registry subscriptions found.

---

### 4. Wildcard Imports

**Status: No wildcard imports found**

Grep for rom combat_lab.services import * across entire repo: **0 matches**

All imports are explicit via __all__ in __init__.py.

---

### 5. Configuration Files & String-Based Dispatch

**Status: No config-driven dispatch found**

- **JSON/YAML files scanned:** 100+ files in combat_lab/data/; **0 service references**
- **Event bus patterns:** grep for event.*subscribe, egister.*callback, scene.*callback; **0 matches**
- **No string-based dispatchers** mentioning TestExecutionService, TestResultsService, or controller methods

---

### 6. Docstring-Only References

**Status: Both documented in scenario_run_helper.py are docstrings only, no live calls**

| File | Lines | Content | Classification |
|------|-------|---------|-----------------|
| combat_lab/services/scenario_run_helper.py | 3-5 | Docstring mentioning historical extraction | docstring |
| combat_lab/services/scenario_run_helper.py | 68 | Comment describing what TestExecutionService previously did | docstring |

The actual materializer setup happens in TestRunner.__init__(), which persists after deletion.

---

### 7. Test Fixtures & conftest.py

**Status: All fixtures accounted for**

- 	ests/unit/combat_lab/services/conftest.py — No direct service imports; fixture re-exports only
- 	ests/unit/test_lab/conftest.py — No service imports; spec-compiler patch only

---

### 8. Archive & Tools Sweep

**Status: No live references**

- _marked_for_deletion_2026-05-29/ — Historical archives only
- Tools/ — Visual tools and managers; **0 service references**
- Projects/scripts/ — Project utilities; **0 service references**

---

### 9. Documentation-Only Diagrams

**Status: All stale; require update in Phase 5**

| File | Lines | Content |
|------|-------|---------|
| combat_lab/COMBAT_LAB_DOCUMENTATION.md | 73-75 | Service list in architecture diagram |
| combat_lab/COMBAT_LAB_DOCUMENTATION.md | 222, 226, 259 | Flow diagram showing handle_run_* and TestResultsService |

These are ASCII diagrams in docstrings. No code execution depends on these strings.

---

## Summary Table: All References Found

### Production Calls (All in methods being deleted)

| Reference | File | Lines | Status |
|-----------|------|-------|--------|
| TestExecutionService() instantiation | combat_lab/services/test_lab_controller.py | 41 | **Deleted with refactor** |
| self.test_execution.run_visual(...) | combat_lab/services/test_lab_controller.py | 102-106 | **Deleted with method** |
| self.test_execution.run_headless(...) | combat_lab/services/test_lab_controller.py | 137-140 | **Deleted with method** |
| TestResultsService(...) instantiation | combat_lab/services/test_lab_controller.py | 43 | **Deleted with refactor** |
| self.test_results.add_run(...) | combat_lab/services/test_lab_controller.py | 150 | **Deleted with method** |

### Test References (All in files marked for update/deletion)

| Reference | File | Status |
|-----------|------|--------|
| TestLabUIController init/mocking | 	ests/unit/combat_lab/services/test_test_execution_service.py | **Delete entire file (Phase 4)** |
| controller.handle_run_visual() calls | 	ests/unit/combat_lab/services/test_controller_init_events.py | **Update test classes (Phase 4)** |
| controller.handle_run_headless() calls | 	ests/unit/combat_lab/services/test_controller_execution.py | **Update test classes (Phase 4)** |

### Docstrings/Comments (No Code Execution)

| Reference | File | Status |
|-----------|------|--------|
| scenario_run_helper.py docstring/comment | Lines 3-5, 68 | **Update docstring (Phase 5)** |
| COMBAT_LAB_DOCUMENTATION.md diagrams | Lines 73-75, 222, 226, 259 | **Update diagrams (Phase 5)** |

---

## Plan Revision Assessment

**NO REVISION REQUIRED**

All investigation criteria met:
- ✓ No dynamic dispatch found
- ✓ No wildcard imports
- ✓ No config-based dispatch
- ✓ scenario_run_helper.py references are docstrings only (no live calls)
- ✓ All test imports are in files already marked for update/deletion
- ✓ No references in Tools/, Projects/scripts/, or archives

**Plan is safe to execute as-is.**

---

## Artifacts

- This report: Projects/active_projects/PROJ-342/findings/dependency_mapper.md

Investigation complete. Recommendation: **Proceed with Phase 1.**
