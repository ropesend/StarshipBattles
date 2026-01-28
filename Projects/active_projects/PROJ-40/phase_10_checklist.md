# Phase 10: Test Infrastructure

**Status:** Not Started
**Estimated Effort:** 5-7 hours
**Priority:** Medium

## Overview
Address issues in test organization, fixtures, and framework consistency across `tests/` directory.

---

## Tasks

### 10.1 Consolidate Duplicate Test Scripts (NEW-TEST-001)
**Location:** `tests/unit/` and `tests/unit/performance/`
**Effort:** Simple

- [ ] Remove duplicate `profile_simulation.py` (keep one version)
- [ ] Consolidate `repro_shield.py`, `repro_energy_stats.py`, `reproduce_scaling.py`
- [ ] Move all reproduction scripts to `tests/repro/` or `tests/utils/`
- [ ] Update any scripts that reference moved files
- [ ] Run: `pytest tests/unit/ -v`

---

### 10.2 Move Non-Test Scripts (NEW-TEST-002)
**Location:** `tests/unit/` (17+ utility scripts)
**Effort:** Simple

- [ ] Create `tests/utils/` directory
- [ ] Move reproduction scripts: `repro_*.py`, `reproduce_*.py`
- [ ] Move profiling scripts: `profile_simulation.py`, `stress_test.py`
- [ ] Move data generation: `generate_test_data.py`
- [ ] Rename with `_` prefix or move to avoid pytest collection
- [ ] Run: `pytest tests/ --collect-only` to verify

---

### 10.3 Refactor Tests to Use Public APIs (NEW-TEST-003)
**Location:** `tests/unit/entities/test_ship.py`, `tests/unit/systems/`, `tests/unit/refactor/`
**Effort:** Medium (partial in this phase)

- [ ] Audit tests for internal implementation references
- [ ] Identify tests referencing deprecated `allowed_layers`
- [ ] Update to use public API methods
- [ ] Document which tests are intentionally testing internals
- [ ] Run: `pytest tests/unit/ -v`

---

### 10.4 Consolidate Shared Test Helpers (NEW-INT-003)
**Location:** Multiple integration test files
**Effort:** Simple

- [ ] Move `make_mock_ship_instance()` to `tests/conftest.py`
- [ ] Remove duplicates from:
  - `test_gameplay_loop.py:32-44`
  - `test_colonization.py:30-42`
  - `test_save_load.py:29-41`
- [ ] Update all imports
- [ ] Run: `pytest tests/integration/ -v`

---

### 10.5 Fix Colonization Test Fragility (NEW-INT-001)
**Location:** `tests/integration/test_colonization.py:103-505`
**Effort:** Medium

- [ ] Create deterministic galaxy fixtures
- [ ] Seed randomness with fixed values
- [ ] Create pre-configured test galaxies with required planet types
- [ ] Remove conditional `pytest.skip()` calls
- [ ] Run: `pytest tests/integration/test_colonization.py -v`

---

### 10.6 Fix Formation Test File Dependencies (NEW-INT-002)
**Location:** `tests/integration/test_formation_flight.py:26,29`, `test_formation_attack.py:27,31`
**Effort:** Simple

- [ ] Add file existence checks before loading
- [ ] Use pytest fixtures to provide test data
- [ ] Create test data files in `tests/data/` if needed
- [ ] Run: `pytest tests/integration/test_formation*.py -v`

---

### 10.7 Consolidate Test Directories (NEW-TEST-005)
**Location:** Multiple underutilized directories
**Effort:** Simple

- [ ] Review `tests/unit/components/` (1 file)
- [ ] Review `tests/unit/data/` (0 files)
- [ ] Review `tests/unit/engine/` (1 file)
- [ ] Review `tests/unit/validation/` (1 file)
- [ ] Either add tests or remove/merge directories
- [ ] Run: `pytest tests/ --collect-only`

---

### 10.8 Convert unittest to pytest (NEW-TEST-006)
**Location:** 9 files using unittest
**Effort:** Medium

- [ ] Convert `repro_shield.py` to pytest style
- [ ] Convert `repro_energy_stats.py` to pytest style
- [ ] Convert `reproduce_scaling.py` to pytest style
- [ ] Convert `test_modifier_logic.py` to pytest style
- [ ] Convert `test_builder_refactor.py` to pytest style
- [ ] Convert `verify_themes.py` to pytest style
- [ ] Run: `pytest tests/ -v`

---

### 10.9 Fix Hardcoded Test Paths (NEW-TEST-007)
**Location:** Multiple test files
**Effort:** Simple

- [ ] Update `profile_simulation.py` to use pathlib
- [ ] Update `stress_test.py` to remove sys.path manipulation
- [ ] Update `generate_test_data.py` path handling
- [ ] Use conftest.py for path management
- [ ] Run: `pytest tests/ -v`

---

### 10.10 Audit Phase-Referenced Tests (NEW-TEST-008)
**Location:** `tests/unit/refactor/`, `tests/unit/entities/test_ship.py`
**Effort:** Medium

- [ ] List all tests with "Phase" references
- [ ] Determine if phases are still relevant
- [ ] Update or remove obsolete phase tests
- [ ] Document current phase status
- [ ] Run: `pytest tests/unit/refactor/ -v`

---

### 10.11 Review Fixture Tests (NEW-TEST-009)
**Location:** `tests/unit/fixtures/`
**Effort:** Simple

- [ ] Evaluate if fixture tests add value
- [ ] Review `test_ship_fixtures.py`
- [ ] Review `test_component_fixtures.py`
- [ ] Review `test_battle_fixtures.py`
- [ ] Remove or document purpose
- [ ] Run: `pytest tests/unit/fixtures/ -v`

---

### 10.12 Establish Test Organization Guidelines (NEW-TEST-010)
**Location:** Documentation
**Effort:** Simple

- [ ] Create `tests/README.md` with organization guidelines
- [ ] Document directory structure
- [ ] Document naming conventions
- [ ] Document when to use unit vs integration tests
- [ ] Reference in CONTRIBUTING.md if exists

---

### 10.13 Fix Fixture Dependencies (NEW-INT-004)
**Location:** `tests/integration/test_ai_strategy.py:49`
**Effort:** Simple

- [ ] Review `loaded_registry` fixture dependencies
- [ ] Verify `global_ship_data` is available
- [ ] Add explicit scope definition
- [ ] Run: `pytest tests/integration/test_ai_strategy.py -v`

---

### 10.14 Add Formation Test Assertions (NEW-INT-005)
**Location:** `tests/integration/test_formation_attack.py:141-145`
**Effort:** Simple

- [ ] Add meaningful assertions for formation behavior
- [ ] Add threshold for max deviation
- [ ] Assert formation stabilizes within expected frames
- [ ] Run: `pytest tests/integration/test_formation_attack.py -v`

---

### 10.15 Fix Design ID Dependencies (NEW-INT-006)
**Location:** `tests/integration/test_complex_workflow.py:149-161`
**Effort:** Simple

- [ ] Add validation for design existence
- [ ] Use constants for design IDs
- [ ] Add helpful error message if design missing
- [ ] Run: `pytest tests/integration/test_complex_workflow.py -v`

---

### 10.16 Remove Orphaned Test Class (NEW-INT-007)
**Location:** `tests/integration/test_formation_flight.py:89-125`
**Effort:** Simple

- [ ] Review `CheckpointBehavior` class usage
- [ ] Either integrate into test assertions or remove
- [ ] Run: `pytest tests/integration/test_formation_flight.py -v`

---

### 10.17 Fix Design Library Synchronization (NEW-INT-008)
**Location:** `tests/integration/test_complex_workflow.py:23-88`
**Effort:** Simple

- [ ] Use parameterized fixtures for empire_id
- [ ] Verify ID synchronization between library and fixture
- [ ] Run: `pytest tests/integration/test_complex_workflow.py -v`

---

### 10.18 Optimize Session-Scoped Validation (NEW-INT-009)
**Location:** `simulation_tests/conftest.py:34-62`
**Effort:** Simple

- [ ] Use lazy validation pattern
- [ ] Or scope validation to simulation tests only
- [ ] Measure startup time impact
- [ ] Run: `pytest simulation_tests/ -v`

---

## Verification

- [ ] Run all tests: `pytest`
- [ ] Verify test collection: `pytest --collect-only`
- [ ] Check for test warnings: `pytest -W default`

---

## Notes
- Many tasks in this phase are independent and can be done in any order
- Task 10.5 (colonization fragility) has highest impact on test reliability
- Consider running coverage analysis after this phase
