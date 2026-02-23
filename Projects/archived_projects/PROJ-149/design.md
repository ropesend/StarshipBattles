# PROJ-149: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-14_031258_sweep_full-codebase-sweep](../../Reviews/results/2026-02-14_031258_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-14
- **Report:** [View Full Report](../../Reviews/results/2026-02-14_031258_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 241 total findings identified.
- **Critical:** 1
- **Major:** 13
- **Selected for remediation:** 59

## Selected Findings Summary

### CON-SIM-001: Inconsistent Return Convention for Not-F
- **Severity:** Critical
- **Location:** `game/simulation/services/battl`
- **Effort:** Medium

### CON-FND-004: Inconsistent Singleton Pattern Usage
- **Severity:** Major
- **Location:** `game/core/singleton.py`
- **Effort:** Medium

### CON-FND-005: Mixed Logging Patterns
- **Severity:** Major
- **Location:** `game/core/logger.py`
- **Effort:** Medium

### CON-SIM-003: Inconsistent Private Member Naming
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### CON-SIM-005: Mixed Docstring Styles
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### CON-SIM-006: Dual Patterns for Querying Components/Ab
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### CON-STR-001: Inconsistent Method Verb Prefixes for Lo
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### CON-STR-002: Mixed Return Type Patterns for Not-Found
- **Severity:** Major
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### CON-STR-003: Inconsistent Static Method vs Instance M
- **Severity:** Major
- **Location:** `game/strategy/validation/*.py`
- **Effort:** Medium

### CON-UI2-001: Inconsistent Dependency Injection Patter
- **Severity:** Major
- **Location:** `game/ui/services/`
- **Effort:** Medium

### CON-UI2-003: Inconsistent Type Hint Completeness
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-005: Two Singleton Patterns in Use
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py`
- **Effort:** Simple

### CON-UI1-002: Mixed UIConfig Usage vs Magic Numbers
- **Severity:** Major
- **Location:** `game/ui/screens/`
- **Effort:** Medium

### CON-UI1-005: Missing Type Hints on Key Public Methods
- **Severity:** Major
- **Location:** `game/ui/screens/battle_panels.`
- **Effort:** Medium

### CON-FND-008: Inconsistent Error Handling Return Patte
- **Severity:** Minor
- **Location:** `game/core/json_utils.py:33-97`
- **Effort:** Simple

### CON-FND-014: game/research/ - Data Class Serializatio
- **Severity:** Minor
- **Location:** `game/research/data/research_tr`
- **Effort:** Simple

### CON-SIM-002: Mixed Naming for Result/Error Types
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-SIM-004: Inconsistent Use of TYPE_CHECKING for Im
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-STR-004: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** Simple

### CON-UI2-002: Mixed Return Type Conventions for IO Ope
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### CON-UI2-004: Inconsistent Method Naming for Registry/
- **Severity:** Minor
- **Location:** `game/ui/services/`
- **Effort:** Simple

### CON-UI1-003: Inconsistent Method Verb Prefixes for Da
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Medium

### CON-UI1-004: Inconsistent Event Handler Naming
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Medium

### CON-UI1-006: Inconsistent Docstring Format
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-FND-001: Inconsistent Verb Prefix for Retrieval M
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py:50-140`
- **Effort:** Simple

### CON-FND-002: Mixed Boolean Naming Patterns
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Medium

### CON-FND-006: Inconsistent Docstring Format
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-007: Import Organization Variations
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-011: Singleton Pattern vs Dependency Injectio
- **Severity:** Minor
- **Location:** `game/ai/strategy_manager.py:20`
- **Effort:** Medium

### CON-FND-016: Camera Protocol Usage
- **Severity:** Minor
- **Location:** `game/research/ui/research_scen`
- **Effort:** Simple

### CON-SIM-007: Inconsistent Method Verb Prefixes
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-008: Inconsistent Parameter Naming for Ship R
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-009: Inconsistent Boolean Naming Patterns
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-SIM-010: Magic Numbers in Ship/Component Initiali
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Simple

### CON-SIM-011: Inconsistent Use of dataclass vs Manual
- **Severity:** Minor
- **Location:** `game/simulation/`
- **Effort:** Simple

### CON-SIM-012: Inconsistent Error Handling Strategy
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-SIM-013: Inconsistent Manager/Service/Helper Clas
- **Severity:** Minor
- **Location:** `game/simulation/`
- **Effort:** Medium

### CON-SIM-014: Inconsistent __init__.py Export Patterns
- **Severity:** Minor
- **Location:** `game/simulation/services/__ini`
- **Effort:** Simple

### CON-STR-005: Inconsistent Boolean Naming Prefixes
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet.py`
- **Effort:** Simple

### CON-STR-006: Inconsistent Docstring Format
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-STR-007: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `game/strategy/engine/command_h`
- **Effort:** Simple

### CON-STR-009: Inconsistent `__init__.py` Export Patter
- **Severity:** Minor
- **Location:** `game/strategy/*/`
- **Effort:** Simple

### CON-STR-011: Inconsistent Error Message Format
- **Severity:** Minor
- **Location:** `game/strategy/systems/save_gam`
- **Effort:** Simple

### CON-STR-012: Magic Numbers Not Extracted to Constants
- **Severity:** Minor
- **Location:** `game/strategy/formulas/habitab`
- **Effort:** Simple

### CON-UI2-006: Inconsistent Docstring Styles
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-007: Inconsistent Private Member Naming
- **Severity:** Minor
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### CON-UI2-008: Inconsistent Error Handling Patterns
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py`
- **Effort:** Simple

### CON-UI2-009: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-010: Magic Numbers in Renderer
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-UI2-011: Inconsistent Boolean Parameter Naming
- **Severity:** Minor
- **Location:** `game/ui/services/battle_factor`
- **Effort:** Simple

### CON-UI2-012: Inconsistent Method Prefix Verbs
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### CON-UI1-007: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-008: Mixed Boolean Naming Conventions
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Simple

### CON-UI1-009: Inconsistent Private Method Prefix Usage
- **Severity:** Minor
- **Location:** `game/ui/panels/`
- **Effort:** Simple

### CON-UI1-010: Inconsistent Window Class Inheritance
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Simple

### CON-UI1-011: Missing UIConfig Constants for Common Va
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Simple

### CON-UI1-012: Inconsistent Error Handling Granularity
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Simple

### CON-UI1-013: Inconsistent Logging Import Patterns
- **Severity:** Minor
- **Location:** `game/ui/screens/`
- **Effort:** Simple

### CON-UI1-014: Inconsistent kill() Method Implementatio
- **Severity:** Minor
- **Location:** `game/ui/panels/`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
