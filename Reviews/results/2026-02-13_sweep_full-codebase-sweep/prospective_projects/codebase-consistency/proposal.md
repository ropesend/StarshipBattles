# Project Proposal: Codebase Consistency

## Overview

**Project ID:** PROJ-B_codebase-consistency
**Theme:** Consistency Violations (CON)
**Total Findings:** 73
**Severity Breakdown:** Critical: 1 | Major: 14 | Minor: 41 | Info: 17

## Problem Statement

The codebase exhibits various consistency issues that make it harder to maintain and understand. These include:

1. **Naming inconsistencies** - Mixed naming conventions for methods, parameters, and classes
2. **Type hint gaps** - Inconsistent type annotation coverage
3. **Pattern deviations** - Different approaches to similar problems (logging, DI, validation)
4. **Documentation gaps** - Missing docstrings and inconsistent formats
5. **API inconsistencies** - Different return types for similar operations

While individually minor, these issues collectively increase cognitive load and make the codebase harder to navigate.

## Scope

### In Scope
- All CON (Consistency Violations) findings from all shards
- Naming standardization
- Type hint completion
- Pattern unification
- Documentation improvements

### Out of Scope
- Test coverage (separate project)
- Architecture violations (separate project)
- Code duplication (separate project)

## Findings Summary

### Critical (1)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-SIM-001 | ResourceRegistry Return Type Inconsistency | `game/simulation/systems/resource_manager.py` | Simple |

### Major (14)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-SIM-002 | Duplicate Exception Handler in design_loader | `game/simulation/services/design_loader.py` | Simple |
| CON-SIM-003 | Magic Numbers in Projectile Guidance System | `game/simulation/entities/projectile.py` | Simple |
| CON-SIM-004 | Singleton Fallback Pattern in Validation | `game/simulation/entities/ship_validation.py` | Complex |
| CON-SIM-005 | Inconsistent Parameter Naming - resource | `game/simulation/components/abilities/` | Simple |
| CON-SIM-006 | Type Hint Gaps in Physics and Combat Modules | `game/simulation/entities/ship_physics.py` | Medium |
| CON-SIM-007 | AIControllerFactory Uses Positional Parameters | `game/simulation/factories/ai_factory.py` | Simple |
| CON-SIM-008 | Magic Numbers in Targeting and Combat Systems | `game/simulation/combat/targeting.py` | Simple |
| CON-STR-001 | Logging Pattern Inconsistency - Mixed Modules | Multiple files | Simple |
| CON-STR-002 | Protocol Interface Decorator Inconsistency | `game/strategy/engine/command_handler.py` | Simple |
| CON-STR-003 | Inconsistent Return Type for validate() | `game/strategy/data/race_config.py` | Medium |
| CON-STR-004 | Inconsistent future annotations Usage | `game/strategy/` | Medium |
| CON-UI2-001 | Inconsistent Dependency Injection Pattern | `game/ui/services/*.py` | Medium |
| CON-UI2-004 | Return Type Inconsistency for Failure Cases | `game/ui/services/ship_io_adapter.py` | Medium |
| CON-UI1-001 | Inconsistent Constructor Parameter Order | Multiple files | Complex |
| CON-UI1-002 | Incomplete God Class Decomposition (test_lab) | `game/ui/screens/test_lab/screen.py` | Complex |
| CON-UI1-003 | Direct Singleton Access Instead of DI | Multiple files | Medium |
| CON-UI1-004 | Mixed Event Handler Naming | Multiple files | Simple |

### Minor (41)

Includes findings related to:
- Docstring format inconsistencies (CON-FND-007, CON-UI2-007)
- Boolean property naming (CON-FND-008)
- Type hint coverage gaps (CON-FND-009, CON-SIM-011, CON-UI1-008)
- Import organization (CON-FND-010, CON-UI2-011)
- Magic numbers (CON-FND-011)
- Error handling patterns (CON-FND-012)
- `__all__` export patterns (CON-FND-013, CON-STR-008)
- Method naming conventions (CON-SIM-013, CON-STR-005)
- Logging initialization patterns (CON-SIM-010, CON-UI2-010)
- And 26 additional minor consistency issues

### Info (17)

Positive findings noting good patterns already in place:
- ResourceType class design (CON-FND-016)
- Facade/Delegate pattern adherence (CON-SIM-018, CON-UI1-015)
- Consistent patterns (CON-STR-011, CON-STR-012)
- Protocol definitions (CON-UI2-015)
- And 11 additional info-level observations

## Effort Estimate

- **Simple tasks:** 35 findings
- **Medium tasks:** 16 findings
- **Complex tasks:** 5 findings
- **N/A (info/good patterns):** 17 findings

**Estimated Duration:** 2-3 sprints

## Recommended Phases

### Phase 1: API Consistency (Critical/Major)
1. CON-SIM-001 - Fix ResourceRegistry return type consistency
2. CON-STR-003 - Standardize validate() return types
3. CON-UI2-004 - Standardize failure return types

### Phase 2: Magic Numbers (Simple)
4. CON-SIM-003 - Extract projectile guidance constants
5. CON-SIM-008 - Extract targeting constants
6. CON-FND-011 - Extract AI layer constants

### Phase 3: Naming Standardization (Simple/Medium)
7. CON-SIM-005 - Standardize parameter naming
8. CON-SIM-013 - Standardize method verb conventions
9. CON-UI1-004 - Standardize event handler naming
10. CON-STR-005 - Standardize method naming

### Phase 4: Pattern Unification (Medium)
11. CON-STR-001 - Unify logging patterns
12. CON-UI2-001 - Unify DI patterns in UI services
13. CON-UI1-003 - Replace singleton access with DI

### Phase 5: Type Hints and Documentation (Simple)
14. CON-SIM-006 - Add type hints to physics/combat
15. CON-FND-009, CON-UI1-008 - Complete type hint coverage
16. CON-FND-007, CON-UI2-007 - Standardize docstring format

## Potential Overlaps

Per `overlap_check.md`:
- **PROJ-125 (PROJ-F_code-consistency)** - Status: Planning - Direct overlap with Consistency Violations

**Recommendation:** This proposal may duplicate PROJ-125. Review existing project scope and either merge or identify non-overlapping findings.

## Success Criteria

1. All CRITICAL consistency issues resolved
2. All MAJOR consistency issues resolved
3. Magic numbers extracted to named constants
4. Consistent naming patterns across similar APIs
5. Type hint coverage above 90% for public APIs
6. Consistent docstring format (Google style)
