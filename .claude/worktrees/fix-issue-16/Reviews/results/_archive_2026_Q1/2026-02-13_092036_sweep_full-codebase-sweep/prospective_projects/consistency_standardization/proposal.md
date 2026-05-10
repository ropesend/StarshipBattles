# Prospective Project: Consistency Standardization

## Overview
This project addresses consistency violations across the codebase including inconsistent naming conventions, mixed patterns for similar operations, missing type hints, inconsistent error handling, and varying code organization. Standardizing these patterns will improve code readability, reduce cognitive load, and make the codebase more maintainable.

## Grouping Rationale
These findings all relate to consistency issues across the codebase:
1. **Naming conventions** - Inconsistent method names, parameter names, boolean prefixes
2. **Pattern usage** - Mixed DI patterns, initialization patterns, return conventions
3. **Documentation** - Inconsistent docstrings, missing type hints
4. **Organization** - Mixed import styles, export patterns, module structure
5. **Shared fix strategy** - Establish standards and apply consistently

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 52 total (0 Critical, 16 Major, 24 Minor, 12 Info)

## Suggested Execution Order
**Should be done SIXTH (or parallel)** - Consistency fixes are lower priority than architecture, test coverage, and legacy cleanup. Can be done in parallel with other projects as a continuous improvement effort.

## Findings

### Major (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-STR-001 | Inconsistent Error Handling Return Types | `game/strategy/validation/` | Medium |
| CON-FND-001 | Inconsistent Logging Pattern - Direct logging | `game/ai/combat_utils.py:14` | Simple |
| CON-FND-002 | Mixed os.path.join and Path-style path construction | `game/core/paths.py:53-99` | Medium |
| CON-SIM-001 | Mixed return conventions for "not found" | `game/simulation/systems/resource_system.py` | Medium |
| CON-SIM-005 | Facade pattern inconsistently applied | `game/simulation/entities/ship.py` | Medium |
| CON-STR-002 | Mixed Engine Initialization Patterns | `game/strategy/engine/` | Medium |
| CON-STR-005 | Inconsistent Use of TYPE_CHECKING Pattern | `game/strategy/data/pathfinding.py` | Simple |
| CON-UI2-001 | Inconsistent DI Pattern Between Services | `game/ui/services/` | Medium |
| CON-UI2-003 | Singleton Classes Missing Type Hints | `game/ui/renderer/sprites.py:26` | Simple |
| CON-UI2-004 | Inconsistent Docstring Presence and Format | Unknown | Medium |
| CON-UI2-005 | Static Methods vs Instance Methods Inconsistency | `game/ui/services/ship_io.py:41` | Medium |
| CON-UI1-002 | Inconsistent Method Naming for Update Operations | `game/ui/panels/` | Medium |
| CON-UI1-005 | Inconsistent Event Handler Return Types | `game/ui/screens/` | Complex |
| CON-UI1-006 | Inconsistent Panel Cleanup Methods | `game/ui/panels/` | Medium |
| DUP-STR-004 | Duplicated Ability Lookup in Validators | Strategy layer | Simple |
| DUP-STR-005 | Duplicated Superweapon Ship Removal Pattern | Strategy layer | Simple |

### Minor (24)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-SIM-003 | Inconsistent use of is_ vs has_ boolean naming | `game/simulation/components/` | Simple |
| CON-SIM-004 | Parameter ordering inconsistency for ship_id | `game/simulation/combat/targeting_system.py` | Simple |
| CON-STR-003 | Inconsistent Docstring Formats | Unknown | Complex |
| CON-STR-004 | Mixed Method Verb Prefixes for Similar Operations | Unknown | Simple |
| CON-UI2-002 | Mixed Parameter Naming for Registry Injection | `game/ui/services/` | Simple |
| CON-UI1-001 | Inconsistent Class Naming Suffixes | Unknown | Medium |
| CON-FND-007 | Inconsistent Parameter Naming - node_id vs tech_id | `game/research/data/tech_tree.py` | Simple |
| CON-FND-009 | Magic Numbers in Research UI - Layout Constants | `game/research/ui/research_scene.py` | Simple |
| CON-FND-010 | Inconsistent Type Hints - Any vs Specific | `game/engine/collision.py:50-54` | Medium |
| CON-SIM-006 | Inconsistent private member naming | `game/simulation/entities/ship.py` | Medium |
| CON-SIM-007 | Logger initialization patterns vary | `game/simulation/components/` | Simple |
| CON-SIM-008 | Inconsistent exception handling patterns | `game/simulation/services/design_service.py` | Medium |
| CON-SIM-009 | Ability class naming suffix inconsistency | `game/simulation/components/abilities/` | Medium |
| CON-SIM-012 | Inconsistent type hints for callable parameters | `game/simulation/managers/retreat_manager.py` | Simple |
| CON-SIM-017 | Duplicate code between ability recalculation | `game/simulation/components/abilities/` | Medium |
| CON-STR-006 | Inconsistent Parameter Naming for Registry | `game/strategy/validation/superweapon_validator.py` | Simple |
| CON-STR-007 | Inconsistent Boolean Property Naming | `game/strategy/data/fleet.py` | Simple |
| CON-STR-008 | Dual Implementation of Same Logic | `game/strategy/engine/harvesting_engine.py` | Simple |
| CON-STR-009 | Inconsistent __init__.py Export Patterns | `game/strategy/__init__.py` | Simple |
| CON-STR-011 | Missing Type Hints on Return Types | `game/strategy/data/pathfinding.py` | Simple |
| CON-UI2-009 | Magic Numbers in Rendering Code | `game/ui/renderer/game_renderer.py` | Simple |
| CON-UI2-012 | Module-Level Side Effects | `game/ui/services/ship_io.py:20` | Medium |
| CON-UI1-003 | Inconsistent Boolean Parameter Naming | Unknown | Simple |
| CON-UI1-004 | Mixed Callback Naming Patterns | Unknown | Simple |

### Info (12)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-FND-006 | Inconsistent Method Verb Prefixes for Actions | `game/ai/interfaces/controllable.py` | N |
| CON-FND-011 | Inconsistent __all__ Export Patterns | `game/core/singleton.py:22` | Simple |
| CON-FND-013 | Optional vs Union[X, None] Usage | `game/core/protocols.py:24-31` | N |
| CON-SIM-011 | Method naming verb inconsistency for retrieval | Unknown | Simple |
| CON-SIM-013 | Inconsistent use of dataclasses vs regular classes | `game/simulation/managers/retreat_manager.py` | Simple |
| CON-SIM-014 | Import organization varies slightly | Unknown | Simple |
| CON-SIM-015 | Some __init__.py files export different patterns | `game/simulation/__init__.py` | Simple |
| CON-STR-010 | Inconsistent Comment Style for Project References | Unknown | Simple |
| CON-STR-012 | Magic Numbers in Pathfinding | `game/strategy/data/pathfinding.py` | Simple |
| CON-STR-014 | Event System Enums vs String Constants | `game/strategy/events/event_types.py` | Simple |
| CON-UI2-007 | Inconsistent Error Handling - Return vs Exception | `game/ui/services/ship_io.py` | Simple |
| CON-UI2-010 | Inconsistent Use of Optional Type Annotations | Unknown | Simple |

## Affected Files

### Foundation/Core
- `game/core/paths.py`
- `game/core/singleton.py`
- `game/core/protocols.py`
- `game/ai/combat_utils.py`
- `game/ai/interfaces/controllable.py`
- `game/research/data/tech_tree.py`
- `game/research/ui/research_scene.py`
- `game/engine/collision.py`

### Simulation
- `game/simulation/entities/ship.py`
- `game/simulation/systems/resource_system.py`
- `game/simulation/components/*.py`
- `game/simulation/services/design_service.py`
- `game/simulation/managers/retreat_manager.py`
- `game/simulation/combat/targeting_system.py`

### Strategy
- `game/strategy/validation/*.py`
- `game/strategy/engine/*.py`
- `game/strategy/data/fleet.py`
- `game/strategy/data/pathfinding.py`
- `game/strategy/events/event_types.py`
- `game/strategy/__init__.py`

### UI
- `game/ui/services/*.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`
- `game/ui/panels/*.py`
- `game/ui/screens/*.py`

## Effort Estimate
- **Simple tasks:** 33
- **Medium tasks:** 16
- **Complex tasks:** 3
- **Overall scope:** Medium-Large (but low priority items)

## Overlap with Existing Projects
- **PROJ-128 (codebase-consistency)** - Direct overlap
- **PROJ-125 (PROJ-F_code-consistency)** - Direct overlap

## Suggested Phases

### Phase 1: Naming Conventions (3-4 days)
Establish and apply consistent naming:
1. Boolean properties: is_/has_ prefixes
2. Method verbs: get_/fetch_/retrieve_ standardization
3. Parameter naming: registry, component, ship_id consistency
4. Class naming suffixes: Screen/Window, Panel, Manager

### Phase 2: Return Type Consistency (2-3 days)
Standardize return patterns:
1. CON-STR-001: Error handling return types (Result objects vs exceptions)
2. CON-SIM-001: "Not found" returns (None vs empty vs exception)
3. CON-UI1-005: Event handler return types

### Phase 3: Type Hints and Documentation (3-4 days)
Add missing type hints and standardize docstrings:
1. CON-STR-011, CON-FND-010: Add missing type hints
2. CON-UI2-003: Add type hints to singleton classes
3. CON-STR-003, CON-UI2-004: Standardize docstring format

### Phase 4: Pattern Standardization (3-4 days)
Apply consistent patterns:
1. CON-UI2-001: Standardize DI pattern in services
2. CON-STR-002: Standardize engine initialization
3. CON-FND-002: Standardize path construction (pathlib)
4. CON-SIM-005: Apply facade pattern consistently

### Phase 5: Code Organization (2-3 days)
Standardize organization:
1. CON-STR-009, CON-SIM-015: Standardize __init__.py exports
2. CON-SIM-014: Standardize import organization
3. CON-FND-009, CON-UI2-009, CON-STR-012: Extract magic numbers to constants
4. CON-UI2-012: Remove module-level side effects
