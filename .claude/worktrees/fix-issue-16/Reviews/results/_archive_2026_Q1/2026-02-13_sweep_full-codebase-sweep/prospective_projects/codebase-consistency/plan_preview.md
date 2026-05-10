# Project Plan: Codebase Consistency

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Codebase Consistency
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 73 consistency violation findings from the codebase sweep. The primary goals are:

1. Standardize API return types and parameter naming
2. Extract magic numbers to named constants
3. Unify logging and DI patterns
4. Complete type hint coverage
5. Standardize documentation format

## Phases

### Phase 1: API Consistency

**Objective:** Fix inconsistent return types and parameter patterns.

**Tasks:**
- [ ] Fix ResourceRegistry return type consistency (CON-SIM-001)
- [ ] Standardize validate() return types (CON-STR-003)
- [ ] Standardize failure return types in ship_io_adapter (CON-UI2-004)
- [ ] Standardize parameter naming in abilities (CON-SIM-005)

**Estimated Effort:** 2-3 days

### Phase 2: Magic Numbers

**Objective:** Extract magic numbers to named constants.

**Tasks:**
- [ ] Extract projectile guidance constants (CON-SIM-003)
- [ ] Extract targeting system constants (CON-SIM-008)
- [ ] Extract AI layer constants (CON-FND-011)

**Estimated Effort:** 1-2 days

### Phase 3: Pattern Unification

**Objective:** Establish consistent patterns across the codebase.

**Tasks:**
- [ ] Unify logging initialization patterns (CON-STR-001, CON-SIM-010, CON-UI2-010)
- [ ] Unify dependency injection in UI services (CON-UI2-001)
- [ ] Replace direct singleton access with DI (CON-UI1-003)
- [ ] Standardize event handler naming (CON-UI1-004)

**Estimated Effort:** 3-4 days

### Phase 4: Type Hints and Documentation

**Objective:** Complete type hint coverage and standardize documentation.

**Tasks:**
- [ ] Add type hints to physics/combat modules (CON-SIM-006)
- [ ] Complete type hint coverage in core modules (CON-FND-009)
- [ ] Standardize docstring format to Google style (CON-FND-007, CON-UI2-007)
- [ ] Add missing module docstrings (CON-UI1-012)

**Estimated Effort:** 2-3 days

### Phase 5: Cleanup

**Objective:** Address remaining minor consistency issues.

**Tasks:**
- [ ] Standardize `__all__` exports (CON-FND-013, CON-STR-008)
- [ ] Standardize future annotations usage (CON-STR-004, CON-UI1-009)
- [ ] Clean up import organization (CON-FND-010, CON-UI2-011)

**Estimated Effort:** 1-2 days

## Success Criteria

1. All CRITICAL and MAJOR consistency issues resolved
2. Magic numbers extracted to named constants
3. Consistent logging pattern across all modules
4. Type hint coverage above 90% for public APIs
5. All docstrings follow Google style format

## Dependencies

- None (self-contained)

## Risks

- Some naming changes may require broad refactoring
- Pattern unification may affect existing tests
