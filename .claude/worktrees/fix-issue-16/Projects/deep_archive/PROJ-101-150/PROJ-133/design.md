# PROJ-133: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_092036_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_092036_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_092036_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 221 total findings identified.
- **Critical:** 0
- **Major:** 16
- **Selected for remediation:** 59

## Selected Findings Summary

### CON-STR-001: Inconsistent Error Handling Return Types
- **Severity:** Major
- **Location:** `game/strategy/validation/colon`
- **Effort:** Medium

### CON-FND-001: Inconsistent Logging Pattern - Direct lo
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:14`
- **Effort:** Simple

### CON-FND-002: Mixed os.path.join and Path-style path c
- **Severity:** Major
- **Location:** `game/core/paths.py:53-99`
- **Effort:** Medium

### CON-SIM-001: Mixed return conventions for "not found"
- **Severity:** Major
- **Location:** `game/simulation/systems/resour`
- **Effort:** Medium

### CON-SIM-005: Facade pattern inconsistently applied in
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### CON-STR-002: Mixed Engine Initialization Patterns
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Medium

### CON-STR-005: Inconsistent Use of TYPE_CHECKING Patter
- **Severity:** Major
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** Simple

### CON-UI2-001: Inconsistent DI Pattern Between Services
- **Severity:** Major
- **Location:** `game/ui/services/`
- **Effort:** Medium

### CON-UI2-003: Singleton Classes Missing Type Hints on
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py:26`
- **Effort:** Simple

### CON-UI2-004: Inconsistent Docstring Presence and Form
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI2-005: Static Methods vs Instance Methods Incon
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:41`
- **Effort:** Medium

### CON-UI1-002: Inconsistent Method Naming for Update Op
- **Severity:** Major
- **Location:** `game/ui/panels/`
- **Effort:** Medium

### CON-UI1-005: Inconsistent Event Handler Return Types
- **Severity:** Major
- **Location:** `game/ui/screens/`
- **Effort:** Complex

### CON-UI1-006: Inconsistent Panel Cleanup Methods
- **Severity:** Major
- **Location:** `game/ui/panels/`
- **Effort:** Medium

### DUP-STR-004: Duplicated Ability Lookup in Validators
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-005: Duplicated Superweapon Ship Removal Patt
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-003: Inconsistent use of is_ vs has_ boolean
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### CON-SIM-004: Parameter ordering inconsistency for shi
- **Severity:** Minor
- **Location:** `game/simulation/combat/targeti`
- **Effort:** Simple

### CON-STR-003: Inconsistent Docstring Formats
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### CON-STR-004: Mixed Method Verb Prefixes for Similar O
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-002: Mixed Parameter Naming for Registry Inje
- **Severity:** Minor
- **Location:** `game/ui/services/`
- **Effort:** Simple

### CON-UI1-001: Inconsistent Class Naming Suffixes
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-FND-007: Inconsistent Parameter Naming - node_id
- **Severity:** Minor
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** Simple

### CON-FND-009: Magic Numbers in Research UI - Layout Co
- **Severity:** Minor
- **Location:** `game/research/ui/research_scen`
- **Effort:** Simple

### CON-FND-010: Inconsistent Type Hints - Any vs Specifi
- **Severity:** Minor
- **Location:** `game/engine/collision.py:50-54`
- **Effort:** Medium

### CON-SIM-006: Inconsistent private member naming with
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### CON-SIM-007: Logger initialization patterns vary
- **Severity:** Minor
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### CON-SIM-008: Inconsistent exception handling patterns
- **Severity:** Minor
- **Location:** `game/simulation/services/desig`
- **Effort:** Medium

### CON-SIM-009: Ability class naming suffix inconsistenc
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### CON-SIM-012: Inconsistent type hints for callable par
- **Severity:** Minor
- **Location:** `game/simulation/managers/retre`
- **Effort:** Simple

### CON-SIM-017: Duplicate code between ability recalcula
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### CON-STR-006: Inconsistent Parameter Naming for Regist
- **Severity:** Minor
- **Location:** `game/strategy/validation/super`
- **Effort:** Simple

### CON-STR-007: Inconsistent Boolean Property Naming
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet.py`
- **Effort:** Simple

### CON-STR-008: Dual Implementation of Same Logic
- **Severity:** Minor
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Simple

### CON-STR-009: Inconsistent __init__.py Export Patterns
- **Severity:** Minor
- **Location:** `game/strategy/__init__.py`
- **Effort:** Simple

### CON-STR-011: Missing Type Hints on Return Types
- **Severity:** Minor
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** Simple

### CON-UI2-009: Magic Numbers in Rendering Code
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-UI2-012: Module-Level Side Effects
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:20`
- **Effort:** Medium

### CON-UI1-003: Inconsistent Boolean Parameter Naming
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-004: Mixed Callback Naming Patterns
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-007: Inconsistent Exception Handling Patterns
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-008: Missing Type Hints on Public Methods
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI1-009: Inconsistent Docstring Presence
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI1-012: Mixed Parameter Ordering Conventions
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-013: Direct Asset Loading Bypassing Service P
- **Severity:** Minor
- **Location:** `game/ui/panels/design_report_p`
- **Effort:** Simple

### CON-UI1-017: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-018: Screen Protocol Compliance Varies
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-FND-006: Inconsistent Method Verb Prefixes for Ac
- **Severity:** Info
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** N

### CON-FND-011: Inconsistent __all__ Export Patterns
- **Severity:** Info
- **Location:** `game/core/singleton.py:22`
- **Effort:** Simple

### CON-SIM-011: Method naming verb inconsistency for ret
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-013: Inconsistent use of dataclasses vs regul
- **Severity:** Info
- **Location:** `game/simulation/managers/retre`
- **Effort:** Simple

### CON-STR-010: Inconsistent Comment Style for Project R
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-007: Inconsistent Error Handling - Return vs
- **Severity:** Info
- **Location:** `game/ui/services/ship_io.py`
- **Effort:** Simple

### CON-UI2-010: Inconsistent Use of Optional Type Annota
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-013: Optional vs Union[X, None] Usage
- **Severity:** Info
- **Location:** `game/core/protocols.py:24-31`
- **Effort:** N

### CON-SIM-014: Import organization varies slightly
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-015: Some __init__.py files export different
- **Severity:** Info
- **Location:** `game/simulation/__init__.py`
- **Effort:** Simple

### CON-STR-012: Magic Numbers in Pathfinding
- **Severity:** Info
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** Simple

### CON-STR-014: Event System Enums vs String Constants
- **Severity:** Info
- **Location:** `game/strategy/events/event_typ`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
