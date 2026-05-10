# Project Proposal: Consistency Standardization

## Overview

This project addresses consistency violations across the codebase, including mixed naming patterns, inconsistent return conventions, varied docstring formats, and non-standard patterns. The focus is on establishing and enforcing consistent conventions.

## Rationale

The codebase has numerous consistency issues:
- Inconsistent return conventions for not-found cases (None vs raise vs Optional)
- Mixed singleton vs DI patterns
- Mixed logging patterns
- Inconsistent private member naming
- Mixed docstring formats
- Inconsistent method verb prefixes (get_ vs fetch_ vs load_)
- Magic numbers not extracted to constants

These inconsistencies create cognitive overhead and increase bug risk from unexpected behavior.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| CON-SIM-001 | Critical | Inconsistent Return Convention for Not-Found | game/simulation/services/ | Medium |
| CON-FND-004 | Major | Inconsistent Singleton Pattern Usage | game/core/singleton.py | Medium |
| CON-FND-005 | Major | Mixed Logging Patterns | game/core/logger.py | Medium |
| CON-SIM-003 | Major | Inconsistent Private Member Naming | game/simulation/ | Complex |
| CON-SIM-005 | Major | Mixed Docstring Styles | game/simulation/ | Complex |
| CON-SIM-006 | Major | Dual Patterns for Querying Components/Abilities | game/simulation/entities/ship.py | Medium |
| CON-STR-001 | Major | Inconsistent Method Verb Prefixes for Loading | game/strategy/ | Medium |
| CON-STR-002 | Major | Mixed Return Type Patterns for Not-Found | game/strategy/services/ | Medium |
| CON-STR-003 | Major | Inconsistent Static Method vs Instance Method | game/strategy/validation/ | Medium |
| CON-UI2-001 | Major | Inconsistent Dependency Injection Patterns | game/ui/services/ | Medium |
| CON-UI2-003 | Major | Inconsistent Type Hint Completeness | game/ui/ | Simple |
| CON-UI2-005 | Major | Two Singleton Patterns in Use | game/ui/renderer/sprites.py | Simple |
| CON-UI1-002 | Major | Mixed UIConfig Usage vs Magic Numbers | game/ui/screens/ | Medium |
| CON-UI1-005 | Major | Missing Type Hints on Key Public Methods | game/ui/screens/battle_panels.py | Medium |
| CON-FND-008 | Minor | Inconsistent Error Handling Return Patterns | game/core/json_utils.py | Simple |
| CON-SIM-002 | Minor | Mixed Naming for Result/Error Types | game/simulation/ | Medium |
| CON-SIM-004 | Minor | Inconsistent Use of TYPE_CHECKING | game/simulation/ | Simple |
| CON-STR-004 | Minor | Inconsistent Type Hint Coverage | game/strategy/data/ | Simple |
| CON-UI2-002 | Minor | Mixed Return Type Conventions for IO | game/ui/services/ | Medium |
| CON-UI2-004 | Minor | Inconsistent Method Naming for Registry | game/ui/services/ | Simple |
| CON-UI1-003 | Minor | Inconsistent Method Verb Prefixes | game/ui/screens/ | Medium |
| CON-UI1-004 | Minor | Inconsistent Event Handler Naming | game/ui/screens/ | Medium |
| CON-UI1-006 | Minor | Inconsistent Docstring Format | game/ui/ | Medium |
| CON-FND-001 | Minor | Inconsistent Verb Prefix for Retrieval Methods | game/ai/combat_utils.py | Simple |
| CON-FND-002 | Minor | Mixed Boolean Naming Patterns | game/ai/interfaces/ | Medium |
| CON-FND-006 | Minor | Inconsistent Docstring Format | game/core/ | Simple |
| CON-FND-007 | Minor | Import Organization Variations | game/ | Simple |
| CON-SIM-007 | Minor | Inconsistent Method Verb Prefixes | game/simulation/ | Simple |
| CON-SIM-008 | Minor | Inconsistent Parameter Naming for Ship References | game/simulation/ | Simple |
| CON-SIM-009 | Minor | Inconsistent Boolean Naming Patterns | game/simulation/ | Simple |
| CON-SIM-010 | Minor | Magic Numbers in Ship/Component Initialization | game/simulation/entities/ | Simple |
| CON-SIM-011 | Minor | Inconsistent Use of dataclass vs Manual | game/simulation/ | Simple |
| CON-SIM-012 | Minor | Inconsistent Error Handling Strategy | game/simulation/ | Medium |
| CON-SIM-013 | Minor | Inconsistent Manager/Service/Helper Class Suffixes | game/simulation/ | Medium |
| CON-SIM-014 | Minor | Inconsistent __init__.py Export Patterns | game/simulation/services/ | Simple |
| CON-STR-005 | Minor | Inconsistent Boolean Naming Prefixes | game/strategy/data/fleet.py | Simple |
| CON-STR-006 | Minor | Inconsistent Docstring Format | game/strategy/ | Medium |
| CON-STR-007 | Minor | Inconsistent Import Organization | game/strategy/engine/ | Simple |
| CON-STR-009 | Minor | Inconsistent __init__.py Export Patterns | game/strategy/ | Simple |
| CON-STR-011 | Minor | Inconsistent Error Message Format | game/strategy/systems/ | Simple |
| CON-STR-012 | Minor | Magic Numbers Not Extracted to Constants | game/strategy/formulas/ | Simple |
| CON-UI2-006 | Minor | Inconsistent Docstring Styles | game/ui/ | Simple |
| CON-UI2-007 | Minor | Inconsistent Private Member Naming | game/ui/services/ | Simple |
| CON-UI2-008 | Minor | Inconsistent Error Handling Patterns | game/ui/services/ship_io.py | Simple |
| CON-UI2-009 | Minor | Inconsistent Import Organization | game/ui/ | Simple |
| CON-UI2-010 | Minor | Magic Numbers in Renderer | game/ui/renderer/ | Simple |
| CON-UI2-011 | Minor | Inconsistent Boolean Parameter Naming | game/ui/services/ | Simple |
| CON-UI2-012 | Minor | Inconsistent Method Prefix Verbs | game/ui/assets/ | Simple |
| CON-UI1-007 | Minor | Inconsistent Import Organization | game/ui/screens/ | Simple |
| CON-UI1-008 | Minor | Mixed Boolean Naming Conventions | game/ui/screens/ | Simple |
| CON-UI1-009 | Minor | Inconsistent Private Method Prefix Usage | game/ui/panels/ | Simple |
| CON-UI1-010 | Minor | Inconsistent Window Class Inheritance | game/ui/screens/ | Simple |
| CON-UI1-011 | Minor | Missing UIConfig Constants for Common Values | game/ui/screens/ | Simple |
| CON-UI1-012 | Minor | Inconsistent Error Handling Granularity | game/ui/screens/ | Simple |
| CON-UI1-013 | Minor | Inconsistent Logging Import Patterns | game/ui/screens/ | Simple |
| CON-UI1-014 | Minor | Inconsistent kill() Method Implementation | game/ui/panels/ | Simple |
| CON-FND-011 | Minor | Singleton Pattern vs Dependency Injection | game/ai/strategy_manager.py | Medium |
| CON-FND-014 | Minor | Data Class Serialization Patterns | game/research/data/ | Simple |
| CON-FND-016 | Minor | Camera Protocol Usage | game/research/ui/ | Simple |

## Summary Statistics

- **Total Findings:** 59
- **Critical:** 1 | **Major:** 13 | **Minor:** 45
- **Estimated Effort:** Complex (large scope, many minor fixes)
- **Primary Location:** All layers - game/simulation/, game/strategy/, game/ui/

## Overlap with Active Projects

Potential overlap with:
- PROJ-146: 6_architecture_consistency (likely duplicate)
- PROJ-133: Consistency Standardization (likely duplicate)
- PROJ-128: codebase-consistency (likely duplicate)
- PROJ-125: PROJ-F_code-consistency (overlapping)

**Recommendation:** This is a large scope project. Consider phasing by layer or by issue type (naming, docstrings, return types).

## Success Criteria

1. Return type conventions documented and enforced for not-found cases
2. Method verb prefixes standardized (get_ vs load_ vs fetch_)
3. Boolean naming uses is_/has_/can_ prefixes consistently
4. Magic numbers extracted to named constants in UI
5. Docstring format standardized
