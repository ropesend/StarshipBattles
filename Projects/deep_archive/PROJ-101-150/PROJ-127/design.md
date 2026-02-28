# PROJ-127: Design Document

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
- **Critical:** 0
- **Major:** 11
- **Selected for remediation:** 36

## Selected Findings Summary

### DUP-FND-001: Entity Position/State Access Patterns in
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:49-82`
- **Effort:** Medium

### DUP-SIM-001: Serialization to_dict/from_dict Pattern
- **Severity:** Major
- **Location:** `game/simulation/battle_state.p`
- **Effort:** Medium

### DUP-SIM-002: Resource Ability Classes Share Identical
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-SIM-003: Team Iteration Pattern Duplicated in Bat
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### DUP-STR-001: Build Queue Source Collection - Near-Ide
- **Severity:** Major
- **Location:** `game/strategy/data/build_queue`
- **Effort:** Simple

### DUP-STR-002: Facility Shipyard Detection - Duplicated
- **Severity:** Major
- **Location:** `game/strategy/data/build_queue`
- **Effort:** Simple

### DUP-STR-003: Mission Command Handler Duplication
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### DUP-STR-004: `to_dict` / `from_dict` Boilerplate Patt
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### DUP-STR-005: Fleet Resolution Pattern in Command Hand
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-006: ColonizeValidator Colony Pod Iteration P
- **Severity:** Major
- **Location:** `game/strategy/validation/colon`
- **Effort:** Simple

### DUP-STR-007: Component Layer Iteration Pattern - Repe
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-FND-004: Flee Direction Calculation
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:70-84`
- **Effort:** Simple

### DUP-FND-005: Tech Tree Validation Method Patterns
- **Severity:** Minor
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** Simple

### DUP-FND-006: Serialization to_dict/from_dict Patterns
- **Severity:** Minor
- **Location:** `game/research/data/research_tr`
- **Effort:** Complex

### DUP-SIM-004: Vector2 Conversion Pattern in Projectile
- **Severity:** Minor
- **Location:** `game/simulation/projectile_man`
- **Effort:** Simple

### DUP-SIM-005: get_ui_rows Color Mapping Pattern in Res
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-SIM-006: ship_id_map Pattern Repeated in RetreatM
- **Severity:** Minor
- **Location:** `game/simulation/managers/retre`
- **Effort:** Simple

### DUP-SIM-007: Validation Pattern in modifier_schema.py
- **Severity:** Minor
- **Location:** `game/simulation/components/mod`
- **Effort:** Medium

### DUP-STR-008: Gaussian Factor Calculation Pattern
- **Severity:** Minor
- **Location:** `game/strategy/formulas/habitab`
- **Effort:** Simple

### DUP-STR-009: Path Start Hex Determination Logic
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-010: Ship Ability Check Wrappers
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-STR-011: Resource Dictionary Accumulation Pattern
- **Severity:** Minor
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Simple

### DUP-STR-012: Fleet and Ship Delegation Pattern
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-UI2-004: Image Transform Operations Scattered Wit
- **Severity:** Minor
- **Location:** `game/ui/utils.py:66-94`
- **Effort:** Simple

### DUP-UI2-005: Validation Service Pattern Has Single-Pu
- **Severity:** Minor
- **Location:** `game/ui/services/validation_se`
- **Effort:** N

### DUP-UI2-006: Camera Coordinate Transform Duplication
- **Severity:** Minor
- **Location:** `game/ui/renderer/camera.py:116`
- **Effort:** Medium

### UNK-08: Population/Number Formatting Duplication
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-09: RaceThemeGallery Not Using BaseGallery
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-10: Window Kill/Cleanup Pattern Slightly Inc
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-11: Dropdown Recreation Utility
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### DUP-SIM-008: Natural Similarity in Dataclass State Cl
- **Severity:** Info
- **Location:** `game/simulation/battle_state.p`
- **Effort:** N

### DUP-STR-013: Validated Design Component Iteration
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-STR-014: Well-Consolidated Component Inspector
- **Severity:** Info
- **Location:** `game/strategy/services/compone`
- **Effort:** N

### DUP-UI2-007: Color Constants Could Be Centralized Fur
- **Severity:** Info
- **Location:** `game/ui/colors.py:7-45`
- **Effort:** N

### UNK-13: Ship Stats Renderer Already Extracted
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-14: Strategy Detail Formatters Properly Sepa
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Unknown


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
