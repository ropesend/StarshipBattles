# Review Report: 2026-02-27_211222_general_di-inconsistency-strategy

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (DI-focused)
- **Description:** Audit all `get_default_registry_provider()` usage to classify violations vs. legitimate entry-point usage
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 20
- **Critical:** 2 | **Major:** 2 | **Minor:** 7 | **Info:** 9
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 23
- **Confirmed:** 20 | **Downgraded:** 8 | **Rejected:** 3
- **Rejection Rate:** 13.0%
- **Findings Without Verdict:** 0

## Priority Findings (Top 10)

### 1. CRITICAL: `initialize_ship_data()` has no DI param
**ID:** DI-SIM-006
**Agent:** Validated
**Location:** `game/simulation/entities/ship_`
**Effort:** Simple

**Location:** `game/simulation/entities/ship_`

---

### 2. CRITICAL: `test_protocols_boundary.py` `simple_shi
**ID:** TI-005
**Agent:** Validated
**Location:** `tests/unit/core/test_protocols`
**Effort:** Simple

**Location:** `tests/unit/core/test_protocols`

---

### 3. MAJOR: `get_or_create_validator()` falls back t
**ID:** DI-SIM-001
**Agent:** Validated
**Location:** `game/simulation/entities/ship_`
**Effort:** Medium

**Location:** `game/simulation/entities/ship_`

---

### 4. MAJOR: `load_vehicle_classes()` falls back to g
**ID:** DI-SIM-002
**Agent:** Validated
**Location:** `game/simulation/entities/ship_`
**Effort:** Simple

**Location:** `game/simulation/entities/ship_`

---

### 5. MINOR: `load_components_data()` falls back to g
**ID:** DI-SIM-003
**Agent:** Validated
**Location:** `game/simulation/components/com`
**Effort:** Simple

**Location:** `game/simulation/components/com`

---

### 6. MINOR: `load_components()` uses global provider
**ID:** DI-SIM-004
**Agent:** Validated
**Location:** `game/simulation/components/com`
**Effort:** Medium

**Location:** `game/simulation/components/com`

---

### 7. MINOR: `load_modifiers()` uses global provider
**ID:** DI-SIM-005
**Agent:** Validated
**Location:** `game/simulation/components/com`
**Effort:** Medium

**Location:** `game/simulation/components/com`

---

### 8. MINOR: Simulation `isolated_registry` is class-
**ID:** TI-001
**Agent:** Validated
**Location:** `simulation_tests/conftest.py:7`
**Effort:** Medium

**Location:** `simulation_tests/conftest.py:7`

---

### 9. MINOR: `ship_stats.py` module docstring teaches
**ID:** DI-SIM-007
**Agent:** Validated
**Location:** `game/simulation/entities/ship_`
**Effort:** Simple

**Location:** `game/simulation/entities/ship_`

---

### 10. MINOR: `test_workshop_context_di.py` backward-c
**ID:** TI-006
**Agent:** Validated
**Location:** `tests/unit/builder/test_worksh`
**Effort:** Simple

**Location:** `tests/unit/builder/test_worksh`

---


## Findings by Severity

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-006 | `initialize_ship_data()` has no DI param | `game/simulation/entities/ship_` | Simple |
| TI-005 | `test_protocols_boundary.py` `simple_shi | `tests/unit/core/test_protocols` | Simple |

### Major (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-001 | `get_or_create_validator()` falls back t | `game/simulation/entities/ship_` | Medium |
| DI-SIM-002 | `load_vehicle_classes()` falls back to g | `game/simulation/entities/ship_` | Simple |

### Minor (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-003 | `load_components_data()` falls back to g | `game/simulation/components/com` | Simple |
| DI-SIM-004 | `load_components()` uses global provider | `game/simulation/components/com` | Medium |
| DI-SIM-005 | `load_modifiers()` uses global provider | `game/simulation/components/com` | Medium |
| TI-001 | Simulation `isolated_registry` is class- | `simulation_tests/conftest.py:7` | Medium |
| DI-SIM-007 | `ship_stats.py` module docstring teaches | `game/simulation/entities/ship_` | Simple |
| TI-006 | `test_workshop_context_di.py` backward-c | `tests/unit/builder/test_worksh` | Simple |
| TI-007 | `test_design_loader_adapter.py` line 80 | `tests/unit/ui/services/test_de` | Simple |

### Info (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TI-002 | `test_engine_physics.py` consumes global | `simulation_tests/tests/test_en` | Medium |
| TI-003 | `test_smoke.py` calls `get_default_regis | `simulation_tests/tests/test_sm` | Simple |
| TI-004 | `simulation_tests/scenarios/base.py` `_l | `simulation_tests/scenarios/bas` | Medium |
| TI-010 | `tests/integration/resource_system/conft | `tests/integration/resource_sys` | N |
| DI-SIM-009 | `game/core/__init__.py` re-exports `get_ | `game/core/__init__.py:73` | N |
| TI-011 | Root `conftest.py` provides robust singl | `conftest.py:10-117` | N |
| TI-012 | `test_registry_provider.py` legitimately | `tests/unit/core/test_registry_` | N |
| TI-013 | `test_component_service.py` demonstrates | `tests/unit/ui/services/test_co` | N |
| TI-014 | `test_registry_features.py` uses proper | `tests/unit/core/registry/test_` | N |


## Agent Reports

- [Architecture Report](findings/architecture_report.md)
- [Di Simulation Report](findings/di_simulation_report.md)
- [Di Strategy Report](findings/di_strategy_report.md)
- [Di Ui Report](findings/di_ui_report.md)
- [Test Isolation Report](findings/test_isolation_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 20 |
| Critical | 2 |
| Major | 2 |
| Minor | 7 |
| Info | 9 |
| Agents Used | 25 |

---
*Report generated: 2026-02-27 21:38*
