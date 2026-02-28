# PROJ-128: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 245 total findings identified.
- **Critical:** 1
- **Major:** 17
- **Selected for remediation:** 73

## Selected Findings Summary

### CON-SIM-001: ResourceRegistry Return Type Inconsisten
- **Severity:** Critical
- **Location:** `game/simulation/systems/resour`
- **Effort:** Simple

### CON-SIM-002: Duplicate Exception Handler in design_lo
- **Severity:** Major
- **Location:** `game/simulation/services/desig`
- **Effort:** Simple

### CON-SIM-003: Magic Numbers in Projectile Guidance Sys
- **Severity:** Major
- **Location:** `game/simulation/entities/proje`
- **Effort:** Simple

### CON-SIM-004: Singleton Fallback Pattern in Validation
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Complex

### CON-SIM-005: Inconsistent Parameter Naming - resource
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### CON-SIM-006: Type Hint Gaps in Physics and Combat Mod
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### CON-SIM-007: AIControllerFactory Uses Positional Para
- **Severity:** Major
- **Location:** `game/simulation/factories/ai_f`
- **Effort:** Simple

### CON-SIM-008: Magic Numbers in Targeting and Combat Sy
- **Severity:** Major
- **Location:** `game/simulation/combat/targeti`
- **Effort:** Simple

### CON-STR-001: Logging Pattern Inconsistency - Mixed Mo
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-STR-002: Protocol Interface Decorator Inconsisten
- **Severity:** Major
- **Location:** `game/strategy/engine/command_h`
- **Effort:** Simple

### CON-STR-003: Inconsistent Return Type for validate()
- **Severity:** Major
- **Location:** `game/strategy/data/race_config`
- **Effort:** Medium

### CON-STR-004: Inconsistent `from __future__ import ann
- **Severity:** Major
- **Location:** `game/strategy/`
- **Effort:** Medium

### CON-UI2-001: Inconsistent Dependency Injection Patter
- **Severity:** Major
- **Location:** `game/ui/services/*.py`
- **Effort:** Medium

### CON-UI2-004: Return Type Inconsistency for Failure Ca
- **Severity:** Major
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### CON-UI1-001: Inconsistent Constructor Parameter Order
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### CON-UI1-002: Incomplete God Class Decomposition (test
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### CON-UI1-003: Direct Singleton Access Instead of Depen
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI1-004: Mixed Event Handler Naming (handle_event
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-007: Inconsistent Docstring Format - Google S
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-FND-008: Boolean Property Naming - is_alive() vs
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### CON-FND-009: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/core/logger.py:27-41`
- **Effort:** Simple

### CON-FND-010: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `game/ai/controller.py:51-66`
- **Effort:** Simple

### CON-FND-011: Magic Numbers in AI Layer
- **Severity:** Minor
- **Location:** `game/ai/controller.py:445`
- **Effort:** Simple

### CON-FND-012: Inconsistent Error Handling - Broad Exce
- **Severity:** Minor
- **Location:** `game/ai/controller.py:217-223`
- **Effort:** Simple

### CON-FND-013: Inconsistent `__all__` Export Patterns
- **Severity:** Minor
- **Location:** `game/core/constants.py:1-15`
- **Effort:** Simple

### CON-FND-014: Redundant Protocol Definition
- **Severity:** Minor
- **Location:** `game/core/validation.py:23-60`
- **Effort:** Simple

### CON-SIM-009: Abbreviated Parameter Names in solve_lea
- **Severity:** Minor
- **Location:** `game/simulation/combat/targeti`
- **Effort:** Simple

### CON-SIM-010: Mixed Logging Initialization Patterns
- **Severity:** Minor
- **Location:** `game/simulation/services/regis`
- **Effort:** Simple

### CON-SIM-011: STAT_BINDINGS Type Hint Inconsistency
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### CON-SIM-012: sync_data() Inconsistent Implementation
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### CON-SIM-013: Inconsistent Method Verb Conventions
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### CON-SIM-014: Missing Exports in services/__init__.py
- **Severity:** Minor
- **Location:** `game/simulation/services/__ini`
- **Effort:** Simple

### CON-SIM-015: ability_aggregator.py Naming Convention
- **Severity:** Minor
- **Location:** `game/simulation/entities/abili`
- **Effort:** Simple

### CON-SIM-016: PROJ Comment Format Inconsistency
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-STR-005: Method Naming Inconsistency - lookup_ vs
- **Severity:** Minor
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Simple

### CON-STR-006: Missing Type Hints on Public API Methods
- **Severity:** Minor
- **Location:** `game/strategy/data/naming.py:6`
- **Effort:** Simple

### CON-STR-007: Missing Docstrings in stars.py Methods
- **Severity:** Minor
- **Location:** `game/strategy/data/stars.py`
- **Effort:** Simple

### CON-STR-008: Missing `__all__` Export in Package `__i
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-STR-009: Inconsistent Engine Constructor DI Patte
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-STR-010: Duplicate MAINTENANCE_RATE Constant
- **Severity:** Minor
- **Location:** `game/strategy/engine/maintenan`
- **Effort:** Simple

### CON-UI2-006: Inconsistent Type Hint Usage for Ship Pa
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Simple

### CON-UI2-007: Docstring Format Inconsistency
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI2-008: Boolean Parameter Naming Without Prefix
- **Severity:** Minor
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### CON-UI2-009: Constants Defined at Module Level vs Cla
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### CON-UI2-010: Mixed Logging Patterns
- **Severity:** Minor
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### CON-UI2-011: Import Organization Inconsistencies
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### CON-UI2-012: Inconsistent Use of Optional vs Default
- **Severity:** Minor
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### CON-UI2-013: Thread Safety Documentation Inconsistenc
- **Severity:** Minor
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Medium

### CON-UI2-014: User Story Comment in Production Code
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-UI1-005: Inconsistent Event Handler Return Type A
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI1-006: Mixed Screen/Scene Class Naming Suffix
- **Severity:** Minor
- **Location:** `game/ui/screens/menu_scene.py`
- **Effort:** Simple

### CON-UI1-007: Inconsistent UI Manager Attribute Names
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-UI1-008: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/compon`
- **Effort:** Medium

### CON-UI1-009: Inconsistent Future Annotations Usage
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-010: Inconsistent Event Handler Return Values
- **Severity:** Minor
- **Location:** `BattlePanel.handle_click()`
- **Effort:** Medium

### CON-UI1-011: Two Initialization Method Naming Convent
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-012: Missing Module Docstrings
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/compon`
- **Effort:** Simple

### CON-UI1-013: Inconsistent Panel Base Class Usage
- **Severity:** Minor
- **Location:** `game/ui/panels/`
- **Effort:** Simple

### CON-UI1-014: Mixed Responsibility in test_lab Subdire
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### CON-FND-016: ResourceType is a Class, Not an Enum
- **Severity:** Info
- **Location:** `game/core/constants.py:83-92`
- **Effort:** Simple

### CON-FND-017: TechNode/TechTree Separate from Core Reg
- **Severity:** Info
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** N

### CON-FND-018: Research Layer Has Direct pygame Import
- **Severity:** Info
- **Location:** `game/research/ui/research_scen`
- **Effort:** Complex

### CON-SIM-017: ResourceRegistry Class Name Deviation
- **Severity:** Info
- **Location:** `game/simulation/systems/resour`
- **Effort:** Simple

### CON-SIM-018: Excellent Pattern Adherence - Facade/Del
- **Severity:** Info
- **Location:** `game/simulation/entities/ship_`
- **Effort:** N

### CON-STR-011: Well-Established Consistent Patterns
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### CON-STR-012: Consistent Class Naming Suffixes
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### CON-UI2-015: Protocol Definition Location
- **Severity:** Info
- **Location:** `game/ui/interfaces/battle_ui.p`
- **Effort:** N

### CON-UI2-016: __init__.py Export Patterns
- **Severity:** Info
- **Location:** `game/ui/__init__.py`
- **Effort:** N

### CON-UI1-015: Good Pattern Adoption - Facade/Delegate
- **Severity:** Info
- **Location:** `strategy_ui.py`
- **Effort:** N

### CON-UI1-016: Consistent Callback Naming Pattern
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### CON-UI1-017: Good Class Naming Suffix Consistency
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### CON-UI1-018: Well-Organized builder/ Module Structure
- **Severity:** Info
- **Location:** `game/ui/screens/builder/`
- **Effort:** N

### CON-UI1-019: Consistent Logging Pattern
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
