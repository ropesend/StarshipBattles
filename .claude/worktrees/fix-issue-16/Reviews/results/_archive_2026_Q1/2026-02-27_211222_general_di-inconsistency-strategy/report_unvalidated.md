# Review Report: 2026-02-27_211222_general_di-inconsistency-strategy

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (DI-focused)
- **Description:** Audit all `get_default_registry_provider()` usage to classify violations vs. legitimate entry-point usage
- **Agents Used:** 2

## Executive Summary
- **Total Findings:** 23
- **Critical:** 2 | **Major:** 9 | **Minor:** 6 | **Info:** 6
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: `initialize_ship_data()` has no DI parameters and no registry forwarding
**ID:** DI-SIM-006
**Agent:** Di Simulation
**Location:** `game/simulation/entities/ship_loader.py:161-167`
**Effort:** Simple

**ID:** DI-SIM-006
**Location:** `game/simulation/entities/ship_loader.py:161-167`
**Issue:** `initialize_ship_data()` accepts only `base_path` and has no `registry_provider` parameter. It calls `load_vehicle_classes()` without forwarding any registry context. This is the top-level facade used by `app.py` and by **13+ test fixtures and test classes** to initialize the simulation layer. None of these can control which registries are populated.
**Impact:** This is the most widely-called initializa...

---

### 2. CRITICAL: `test_protocols_boundary.py` `simple_ship` fixture consumes global state for Ship creation
**ID:** TI-005
**Agent:** Test Isolation
**Location:** `tests/unit/core/test_protocols_boundary.py:23-44`
**Effort:** Simple

**ID:** TI-005
**Location:** `tests/unit/core/test_protocols_boundary.py:23-44`
**Issue:** The `simple_ship` fixture calls `get_default_registry_provider()` directly (line 28), constructs `GameRegistries` from it (lines 31-36), and passes it to `Ship()`. This fixture does NOT request `fresh_registries` or any other DI fixture. It relies entirely on the root conftest's `reset_game_state` autouse fixture to have hydrated the singleton before this fixture runs.

This is a **critical** issue because...

---

### 3. MAJOR: `get_or_create_validator()` falls back to global provider
**ID:** DI-SIM-001
**Agent:** Di Simulation
**Location:** `game/simulation/entities/ship_loader.py:20-47`
**Effort:** Medium

**ID:** DI-SIM-001
**Location:** `game/simulation/entities/ship_loader.py:20-47`
**Issue:** `get_or_create_validator()` accepts an optional `registry_provider` parameter but falls back to `get_default_registry_provider()` on line 37 when `None` is passed. This function is called from 6+ locations across the codebase (Ship.add_component, ShipValidatorHelper, VehicleDesignService, ValidationService), and NONE of them pass a `registry_provider` argument -- they all rely on the implicit fallback.
**...

---

### 4. MAJOR: `load_vehicle_classes()` falls back to global provider
**ID:** DI-SIM-002
**Agent:** Di Simulation
**Location:** `game/simulation/entities/ship_loader.py:117-158`
**Effort:** Simple

**ID:** DI-SIM-002
**Location:** `game/simulation/entities/ship_loader.py:117-158`
**Issue:** `load_vehicle_classes()` accepts optional `registry_provider` parameter (line 120) and falls back to `get_default_registry_provider()` on line 153 when `None`. This function mutates the global registry directly (clears and updates vehicle_classes dict from the provider).
**Impact:** The function's purpose is explicitly to "populate the global registry" (line 123-124), so global access is somewhat expect...

---

### 5. MAJOR: `load_components_data()` falls back to global provider
**ID:** DI-SIM-003
**Agent:** Di Simulation
**Location:** `game/simulation/components/component.py:483-555`
**Effort:** Simple

**ID:** DI-SIM-003
**Location:** `game/simulation/components/component.py:483-555`
**Issue:** `load_components_data()` accepts optional `registries` parameter (line 486) but falls back to constructing registries from `get_default_registry_provider()` on lines 514-520 when `None`. This is a "pure function" (per its docstring) that should not access global state.
**Impact:** The docstring claims this is a "pure function" but it violates that claim by accessing the global singleton. This is mislead...

---

### 6. MAJOR: `load_components()` uses global provider directly (no parameter)
**ID:** DI-SIM-004
**Agent:** Di Simulation
**Location:** `game/simulation/components/component.py:558-596`
**Effort:** Medium

**ID:** DI-SIM-004
**Location:** `game/simulation/components/component.py:558-596`
**Issue:** `load_components()` does NOT accept a `registry_provider` or `registries` parameter at all. It calls `get_default_registry_provider()` directly on line 569 (and constructs `GameRegistries` from it on lines 579-584). This is a wrapper function that populates the global registry.
**Impact:** This function is a composition-root-style loader, so global access is somewhat expected. However, it is called from...

---

### 7. MAJOR: `load_modifiers()` uses global provider directly (no parameter)
**ID:** DI-SIM-005
**Agent:** Di Simulation
**Location:** `game/simulation/components/component.py:657-685`
**Effort:** Medium

**ID:** DI-SIM-005
**Location:** `game/simulation/components/component.py:657-685`
**Issue:** `load_modifiers()` does NOT accept a `registry_provider` or `registries` parameter. It calls `get_default_registry_provider().get_modifiers()` directly on line 668. Like `load_components()`, this is a registry-population function with no DI escape hatch.
**Impact:** Same as DI-SIM-004. Called from `app.py` (composition root, acceptable), `registry_loader.py:93`, and `workshop_data_loader.py:129` (not co...

---

### 8. MAJOR: Simulation `isolated_registry` is class-scoped, enabling intra-class state bleed
**ID:** TI-001
**Agent:** Test Isolation
**Location:** `simulation_tests/conftest.py:75-111`
**Effort:** Medium

**ID:** TI-001
**Location:** `simulation_tests/conftest.py:75-111`
**Issue:** The `isolated_registry` fixture is scoped to `class`, meaning all test methods within a class share the same registry state. If one test method mutates the registry (e.g., adds components, modifies data), subsequent test methods in that class will see those mutations.
**Impact:** Tests within the same class are not isolated from each other. A test that adds or modifies registry data will affect all subsequent tests in ...

---

### 9. MAJOR: `test_engine_physics.py` consumes global state via `get_default_registry_provider()` in test helper
**ID:** TI-002
**Agent:** Test Isolation
**Location:** `simulation_tests/tests/test_engine_physics.py:28-41`
**Effort:** Medium

**ID:** TI-002
**Location:** `simulation_tests/tests/test_engine_physics.py:28-41`
**Issue:** The `_load_ship` helper method calls `get_default_registry_provider()` directly to get registry data. While the class has `autouse=True` on the `setup` fixture which references `isolated_registry`, the `_load_ship` method reads from the singleton, creating a tight implicit coupling. If the `isolated_registry` fixture ever fails to populate the singleton (or if a test is run in isolation without the fixt...

---

### 10. MAJOR: `test_smoke.py` calls `get_default_registry_provider()` multiple times without explicit DI
**ID:** TI-003
**Agent:** Test Isolation
**Location:** `simulation_tests/tests/test_smoke.py:21-58`
**Effort:** Simple

**ID:** TI-003
**Location:** `simulation_tests/tests/test_smoke.py:21-58`
**Issue:** All three test methods (`test_vehicle_classes_loaded`, `test_components_loaded`, `test_ship_creation`) call `get_default_registry_provider()` directly in test body code. The class relies on `isolated_registry` (autouse) to populate the singleton. This is the same pattern as TI-002 but across three separate test methods, each independently reading global state.
**Impact:** Same as TI-002 -- implicit coupling to s...

---


## Findings by Severity

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-006 | `initialize_ship_data()` has no DI param | `game/simulation/entities/ship_` | Simple |
| TI-005 | `test_protocols_boundary.py` `simple_shi | `tests/unit/core/test_protocols` | Simple |

### Major (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-001 | `get_or_create_validator()` falls back t | `game/simulation/entities/ship_` | Medium |
| DI-SIM-002 | `load_vehicle_classes()` falls back to g | `game/simulation/entities/ship_` | Simple |
| DI-SIM-003 | `load_components_data()` falls back to g | `game/simulation/components/com` | Simple |
| DI-SIM-004 | `load_components()` uses global provider | `game/simulation/components/com` | Medium |
| DI-SIM-005 | `load_modifiers()` uses global provider  | `game/simulation/components/com` | Medium |
| TI-001 | Simulation `isolated_registry` is class- | `simulation_tests/conftest.py:7` | Medium |
| TI-002 | `test_engine_physics.py` consumes global | `simulation_tests/tests/test_en` | Medium |
| TI-003 | `test_smoke.py` calls `get_default_regis | `simulation_tests/tests/test_sm` | Simple |
| TI-004 | `simulation_tests/scenarios/base.py` `_l | `simulation_tests/scenarios/bas` | Medium |

### Minor (6)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-007 | `ship_stats.py` module docstring teaches | `game/simulation/entities/ship_` | Simple |
| TI-006 | `test_workshop_context_di.py` backward-c | `tests/unit/builder/test_worksh` | Simple |
| TI-007 | `test_design_loader_adapter.py` line 80  | `tests/unit/ui/services/test_de` | Simple |
| TI-008 | `tests/unit/strategy/conftest.py` `reset | `tests/unit/strategy/conftest.p` | Simple |
| TI-009 | `tests/unit/strategy/conftest.py` `mock_ | `tests/unit/strategy/conftest.p` | N |
| TI-010 | `tests/integration/resource_system/conft | `tests/integration/resource_sys` | N |

### Info (6)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DI-SIM-008 | `get_default_registry_provider()` defini | `game/core/registry.py:364-378` | N |
| DI-SIM-009 | `game/core/__init__.py` re-exports `get_ | `game/core/__init__.py:73` | N |
| TI-011 | Root `conftest.py` provides robust singl | `conftest.py:10-117` | N |
| TI-012 | `test_registry_provider.py` legitimately | `tests/unit/core/test_registry_` | N |
| TI-013 | `test_component_service.py` demonstrates | `tests/unit/ui/services/test_co` | N |
| TI-014 | `test_registry_features.py` uses proper  | `tests/unit/core/registry/test_` | N |


## Agent Reports

- [Architecture Report](findings/architecture_report.md)
- [Di Simulation Report](findings/di_simulation_report.md)
- [Di Strategy Report](findings/di_strategy_report.md)
- [Di Ui Report](findings/di_ui_report.md)
- [Test Isolation Report](findings/test_isolation_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 23 |
| Critical | 2 |
| Major | 9 |
| Minor | 6 |
| Info | 6 |
| Agents Used | 2 |

---
*Report generated: 2026-02-27 21:29*
