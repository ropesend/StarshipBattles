# PROJ-148: Design Document

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
- **Major:** 12
- **Selected for remediation:** 27

## Selected Findings Summary

### DUP-UI1-001: Duplicate ColumnManager Classes
- **Severity:** Critical
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Medium

### DUP-FND-001: Strategy Data Loading Duplication
- **Severity:** Major
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### DUP-SIM-001: Ability Pattern Boilerplate Duplication
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### DUP-SIM-002: Formula Evaluation Pattern Duplication
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-SIM-003: Resource Type Handling Duplication
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### DUP-SIM-004: Validation Pattern Repetition in Loaders
- **Severity:** Major
- **Location:** `game/simulation/components/com`
- **Effort:** Medium

### DUP-STR-001: Component Ability Extraction Pattern Rep
- **Severity:** Major
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Medium

### DUP-STR-002: Layer Iteration Pattern Duplicated in 7+
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-UI2-010: Registry Provider Access Pattern Duplica
- **Severity:** Major
- **Location:** `game/ui/services/component_ser`
- **Effort:** Medium

### DUP-UI2-012: Singleton Manager Pattern Duplication
- **Severity:** Major
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Medium

### DUP-UI1-003: Duplicate HP Color Calculation Logic
- **Severity:** Major
- **Location:** `game/ui/panels/ship_stats_rend`
- **Effort:** Simple

### DUP-UI1-004: Duplicate Number Magnitude Formatting
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-UI1-005: RaceThemeGallery Does Not Extend BaseGal
- **Severity:** Major
- **Location:** `game/ui/panels/race_theme_gall`
- **Effort:** Medium

### DUP-FND-002: Singleton Clear Pattern Repetition
- **Severity:** Minor
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Medium

### DUP-STR-003: Maintenance Cost Calculation Has Near-Du
- **Severity:** Minor
- **Location:** `game/strategy/engine/maintenan`
- **Effort:** Medium

### DUP-UI2-011: Service Adapter Boilerplate Pattern
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### DUP-UI1-002: Duplicate draw_stat_bar Implementations
- **Severity:** Minor
- **Location:** `game/ui/panels/battle_panels.p`
- **Effort:** Simple

### DUP-SIM-005: Target Validation Pattern Duplication
- **Severity:** Minor
- **Location:** `game/simulation/combat/targeti`
- **Effort:** Simple

### DUP-SIM-007: UI Row Generation Pattern
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### DUP-SIM-008: Physics Constants Duplication
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### DUP-STR-004: Distance Calculation From Center Repeate
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-005: Density Primitive Gaussian Falloff Patte
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-006: Fleet-Like Object Creation for Pathfindi
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-UI2-015: Image Loading Exception Handling Pattern
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### DUP-UI2-016: Empty __init__.py Files
- **Severity:** Minor
- **Location:** `game/ui/renderer/__init__.py`
- **Effort:** Simple

### DUP-UI1-006: Duplicate Portrait Loading Logic
- **Severity:** Minor
- **Location:** `game/ui/screens/design_image_h`
- **Effort:** Simple

### DUP-UI1-008: Filter/Sort Pattern Duplication
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
