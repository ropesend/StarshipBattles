# test_framework/ Dependency Analyzer Report

## Summary
- Total files in test_framework: 17 Python files
- Total lines of code: ~2,100+
- Files actively imported by game code: 4 consumer files
- Files with zero external consumers: ~10 (internal helpers, legacy scenarios)
- Migration feasibility: **HARD** — unique UI functionality, not simply replaceable
- **Assessment: test_framework is NOT dead code — it is actively used by Combat Lab UI**

---

## Findings

### Major: test_framework is NOT Orphaned — Active Combat Lab Dependency

**ID:** TF-001
**Location:** `test_framework/` (17 files, ~2,100 lines)
**Issue:** Prior review flagged test_framework as "orphaned" but it is actively used by Combat Lab UI
**Impact:** Deleting test_framework would break the Combat Lab UI entirely
**Recommendation:** Keep test_framework as-is; it serves a unique interactive purpose distinct from simulation_tests
**Effort:** N/A (no action needed)

---

## File-by-File Analysis

### Core Files
| File | Lines | Imports By | Status |
|------|-------|-----------|--------|
| __init__.py | 19 | Re-exports | Active |
| registry.py | 493 | test_lab/screen.py | Active |
| runner.py | 249 | test_lab/test_executor.py, battle_screen.py | Active |
| test_history.py | 315 | test_lab/screen.py | Active |
| battle_state_capture.py | 295 | test_lab/test_executor.py | Active |
| scenario.py | 137 | simulation_tests (via inheritance) | Active |

### Service Layer (test_framework/services/)
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| __init__.py | 22 | Re-exports | Active |
| test_lab_controller.py | ~100 | TestLabUIController orchestrating UI | Active |
| test_execution_service.py | ~100 | Scenario execution for UI | Active |
| metadata_management_service.py | ~150 | Metadata validation | Active |
| test_results_service.py | ~130 | Wraps TestHistory for UI | Active |
| ui_state_service.py | ~150 | Combat Lab state management | Active |
| scenario_data_service.py | ~150 | Ship/component data loading | Active |

### Legacy Scenarios (test_framework/scenarios/)
| File | Lines | Status |
|------|-------|--------|
| simple_duel.py | 67 | Could migrate to simulation_tests |
| engine_performance.py | ~80 | Could migrate to simulation_tests |
| gun_accuracy_test.py | ~80 | Could migrate to simulation_tests |
| range_test.py | ~80 | Could migrate to simulation_tests |

---

## Consumer Analysis

### Consumer 1: game/ui/screens/test_lab/screen.py
- **Imports:** TestRegistry, TestHistory, TestLabUIController, load_battle_state_json
- **Usage Pattern:** Deep — initializes registry and history at startup, passes to controller
- **Coupling:** Deep
- **Migration Effort:** Complex

### Consumer 2: game/ui/screens/test_lab/test_executor.py
- **Imports:** TestRunner, BattleStateCapture
- **Usage Pattern:** Medium — instantiates runner for execution, captures battle states
- **Coupling:** Medium
- **Migration Effort:** Medium

### Consumer 3: game/ui/screens/battle_screen.py (line 456)
- **Imports:** TestRunner (lazy import)
- **Usage Pattern:** Shallow — optional logging only, wrapped in try/except
- **Coupling:** Shallow
- **Migration Effort:** Trivial

### Consumer 4: simulation_tests/scenarios/base.py
- **Imports:** CombatScenario from test_framework
- **Usage Pattern:** Inheritance — TestScenario extends CombatScenario
- **Coupling:** Medium — foundational base class
- **Migration Effort:** Medium (could move CombatScenario to simulation_tests)

---

## Comparison: test_framework vs simulation_tests

| Functionality | test_framework | simulation_tests | Assessment |
|---|---|---|---|
| Scenario Base Class | CombatScenario | TestScenario (extends it) | Superset in sim_tests |
| Metadata System | None | TestMetadata (dataclass) | sim_tests only |
| Scenario Registry | TestRegistry (discovery) | None (pytest collects) | Unique to test_framework |
| Test Runner | TestRunner (UI execution) | pytest runner | Different purposes |
| Battle State Capture | BattleStateCapture | None | Unique to test_framework |
| Test History | TestHistory + TestRunRecord | None | Unique to test_framework |
| Validation | None | ValidationRule, Validator | sim_tests only |
| UI Services | 6 service classes | None | Unique to test_framework |

---

## Migration Feasibility Report

### Can Replace (straightforward):
- Legacy scenarios (simple_duel, etc.) → migrate to simulation_tests/scenarios/

### Needs New Code (moderate effort):
- TestHistory persistence → would need rebuilding in UI layer
- BattleStateCapture → would need JSON serialization in UI
- TestRunner → could be simplified into a UI-specific executor

### Unique Functionality (cannot simply delete):
- TestLabUIController + 5 service classes — orchestrate Combat Lab UI
- UIStateService — manages category selection, test selection, seed modes
- MetadataManagementService — validation integration for UI
- TestResultsService — history + registry integration for UI

### Recommendation
**Option A: Keep test_framework (RECOMMENDED)**
- Cost: Low maintenance (isolated to Combat Lab UI)
- Benefit: Fully featured Combat Lab
- Risk: Low — only Combat Lab uses it

**Option B: Minimal Cleanup**
- Keep test_framework core
- Move legacy scenarios to simulation_tests/
- Clean up any unused internal code

**Option C: Full Migration (NOT RECOMMENDED)**
- Cost: HIGH — significant refactoring of Combat Lab UI
- Would need to rebuild all 6 service classes
- Risk: High complexity for minimal benefit

---

## Top 5 Priority Issues

1. **TF-001** — test_framework is NOT dead code — active Combat Lab dependency (no action needed)
2. Legacy scenarios could be migrated to simulation_tests (low priority, optional)
3. CombatScenario base class could be extracted to a shared location (optional)
4. simulation_tests depends on test_framework via CombatScenario inheritance (acceptable coupling)
5. pytest tests do NOT import test_framework (clean separation confirmed)
