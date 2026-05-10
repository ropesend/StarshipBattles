# Review Report: 2026-02-01_general_full-codebase-health-check

## Metadata
- **Date:** 2026-02-01 18:30
- **Type:** General Review
- **Description:** Full Codebase Health Check
- **Agents Used:** 7

## Executive Summary
- **Total Findings:** 19
- **Critical:** 0 | **Major:** 9 | **Minor:** 9 | **Info:** 1
- **Overall Assessment:** Needs Improvement

## Priority Findings (Top 10)

### 1. MAJOR: UI/Simulation Coupling
**ID:** AR-01
**Agent:** Architecture
**Location:** `game/ui/`
**Effort:** Complex

**ID:** AR-01
**Location:** `game/ui/` -> `game/simulation/`
**Issue:** Heavy coupling between UI screens and Simulation internals (e.g. `BattleController`).
**Impact:** Makes it hard to run simulation headless (for testing or server).
**Recommendation:** Introduce a stricter Event Bus or ViewModel layer between UI and Sim.
**Effort:** Complex

---

### 2. MAJOR: God Class / Mega-File Pattern
**ID:** CQ-01
**Agent:** Code Quality
**Location:** `game/ui/screens/test_lab_screen.py:1-4703`
**Effort:** Complex

**ID:** CQ-01
**Location:** `game/ui/screens/test_lab_screen.py:1-4703`
**Issue:** File contains 4700+ lines of code, likely mixing UI, logic, and simulation test orchestration.
**Impact:** Extremely difficult to maintain, test, or refactor. High risk of regressions.
**Recommendation:** Decompose into smaller sub-components (e.g., specific test panels, logic handlers).
**Effort:** Complex

---

### 3. MAJOR: Excessive File Size in Simulation Tests
**ID:** CQ-02
**Agent:** Code Quality
**Location:** `simulation_tests/scenarios/*.py`
**Effort:** Medium

**ID:** CQ-02
**Location:** `simulation_tests/scenarios/*.py`
**Issue:** Scenario files (Beam, Propulsion, Resource) are exceptionally large (1500-2700 lines).
**Impact:** Tests become fragile monoliths; hard to read and debug failures.
**Recommendation:** Refactor scenarios into smaller, composable test cases or fixture-driven tests.
**Effort:** Medium

---

### 4. MAJOR: Builder UI Complexity
**ID:** CQ-03
**Agent:** Code Quality
**Location:** `game/ui/screens/builder/main.py:1-1047`
**Effort:** Medium

**ID:** CQ-03
**Location:** `game/ui/screens/builder/main.py:1-1047`
**Issue:** Ship Builder UI main file is over 1000 lines.
**Impact:** The Ship Builder is a core feature; complexity here slows down iteration and introduces UI bugs.
**Recommendation:** Extract widgets and state management into separate modules.
**Effort:** Medium

---

### 5. MAJOR: Uncleaned Deletion Markers
**ID:** DC-01
**Agent:** Dead Code
**Location:** `_marked_for_deletion_2026-01-28/`
**Effort:** Simple

**ID:** DC-01
**Location:** `_marked_for_deletion_2026-01-28/`
**Issue:** Directory containing 20+ files (some large) explicitly marked for deletion remains in codebase.
**Impact:** Bloats codebase, confuses grep/search results, might define duplicate classes/symbols.
**Recommendation:** Delete the directory and commit.
**Effort:** Simple

---

### 6. MAJOR: Swallowed Exceptions
**ID:** ERR-01
**Agent:** Error Handling
**Location:** `scripts/apply_resource_costs.py`
**Effort:** Simple

**ID:** ERR-01
**Location:** `scripts/apply_resource_costs.py`
**Issue:** `except: pass` usage.
**Impact:** Hides failures.
**Recommendation:** Log errors.
**Effort:** Simple

---

### 7. MAJOR: Dangerous Use of eval()
**ID:** SEC-01
**Agent:** Security
**Location:** `game/simulation/formula_system.py:120`
**Effort:** Medium

**ID:** SEC-01
**Location:** `game/simulation/formula_system.py:120`
**Issue:** Usage of `eval()` to calculate formulas.
**Impact:** Remote Code Execution (RCE) risk if formula strings can be influenced by external sources (e.g., downloaded mods, save files).
**Recommendation:** Replace `eval()` with a safe math parser library (e.g., `simpleeval`, `pyparsing`) or a strict AST whitelist.
**Effort:** Medium

---

### 8. MAJOR: Bare Exception in Resource Scripts
**ID:** SEC-02
**Agent:** Security
**Location:** `scripts/apply_resource_costs.py:96`
**Effort:** Simple

**ID:** SEC-02
**Location:** `scripts/apply_resource_costs.py:96`
**Issue:** `except: pass` swallows all errors, including SystemExit and KeyboardInterrupt.
**Impact:** Scripts may fail silently, leaving data in inconsistent states or hiding critical bugs.
**Recommendation:** Catch specific exceptions (`Exception` or specific types) and log the error.
**Effort:** Simple

---

### 9. MAJOR: Mixed Testing Strategies
**ID:** TC-01
**Agent:** Test Coverage
**Location:** `simulation_tests/`
**Effort:** Complex

**ID:** TC-01
**Location:** `simulation_tests/` vs `tests/unit/`
**Issue:** Co-existence of massive scenario scripts and granular unit tests.
**Impact:** Split brain in testing. High maintenance cost for the scenario scripts which seem to duplicate logic.
**Recommendation:** Consolidate testing strategy. Prefer unit tests for logic and small integration tests for flows.
**Effort:** Complex

---

### 10. MINOR: God Object Config
**ID:** AR-02
**Agent:** Architecture
**Location:** `game/app.py`
**Effort:** Medium

**ID:** AR-02
**Location:** `game/app.py`
**Issue:** `app.py` often becomes a dumping ground for initialization logic.
**Impact:** Startup logic is brittle.
**Recommendation:** Extract `AppConfig` and `ServiceLocator` patterns.
**Effort:** Medium

### Top 5 Priority Issues
1. Decouple UI from Simulation (AR-01)

---


## Findings by Severity

### Major (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-01 | UI/Simulation Coupling | `game/ui/` | Complex |
| CQ-01 | God Class / Mega-File Pattern | `game/ui/screens/test_lab_scree` | Complex |
| CQ-02 | Excessive File Size in Simulation Tests | `simulation_tests/scenarios/*.p` | Medium |
| CQ-03 | Builder UI Complexity | `game/ui/screens/builder/main.p` | Medium |
| DC-01 | Uncleaned Deletion Markers | `_marked_for_deletion_2026-01-2` | Simple |
| ERR-01 | Swallowed Exceptions | `scripts/apply_resource_costs.p` | Simple |
| SEC-01 | Dangerous Use of eval() | `game/simulation/formula_system` | Medium |
| SEC-02 | Bare Exception in Resource Scripts | `scripts/apply_resource_costs.p` | Simple |
| TC-01 | Mixed Testing Strategies | `simulation_tests/` | Complex |

### Minor (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-02 | God Object Config | `game/app.py` | Medium |
| CQ-04 | Large Battle Controller | `game/simulation/battle_control` | Medium |
| CQ-05 | Ship Entity Complexity | `game/simulation/entities/ship.` | Medium |
| DC-02 | Commented Out Code | `game/simulation/battle_state.p` | Simple |
| DOC-01 | Missing Docstrings in Complex Logic | `game/simulation/systems/battle` | Medium |
| ERR-02 | Console Printing | `Unknown` | Medium |
| SEC-03 | Sandbox Reliance | `game/simulation/components/mod` | Medium |
| TC-02 | Test Lab Screen Reliance | `game/ui/screens/test_lab_scree` | Complex |
| TC-03 | Pytest Cache Pollution | `__pycache__` | Simple |

### Info (1)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-06 | High Component Count | `General` | Simple |


## Agent Reports

- [Architecture Report](findings/architecture_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Dead Code Report](findings/dead_code_report.md)
- [Documentation Report](findings/documentation_report.md)
- [Error Handling Report](findings/error_handling_report.md)
- [Security Report](findings/security_report.md)
- [Test Coverage Report](findings/test_coverage_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 19 |
| Critical | 0 |
| Major | 9 |
| Minor | 9 |
| Info | 1 |
| Agents Used | 7 |

---
*Report generated: 2026-02-01 18:34*
