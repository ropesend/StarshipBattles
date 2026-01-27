# PROJ-22: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-01-27_general_legacy-cleanup-verification](../../Reviews/results/2026-01-27_general_legacy-cleanup-verification/)
- **Type:** General Review - Legacy Cleanup Verification
- **Date:** 2026-01-27
- **Report:** [View Full Report](../../Reviews/results/2026-01-27_general_legacy-cleanup-verification/report.md)

## Initial Analysis
Findings from review - 21 total findings identified.
- **Critical:** 6
- **Major:** 7
- **Selected for remediation:** 13

## Selected Findings Summary

### DC-01: Marked_For_Deletion folder (103 files, 45MB)
- **Severity:** Major
- **Location:** `Root`
- **Effort:** Simple

### AR-01: Dead physics mixin (102 lines)
- **Severity:** Critical
- **Location:** `entities/mixins/physics.py`
- **Effort:** Simple

### AR-02: Dead combat mixin (437 lines)
- **Severity:** Critical
- **Location:** `entities/mixins/combat.py`
- **Effort:** Simple

### LPA-01: ShipControllableAdapter blocks migration
- **Severity:** Critical
- **Location:** `controllable.py`
- **Effort:** Complex

### LPA-02: ship_theme.py shim (0 users)
- **Severity:** Major
- **Location:** `ship_theme.py`
- **Effort:** Simple

### LPA-03: SHIP_CLASSES alias (1 user)
- **Severity:** Major
- **Location:** `ship.py`
- **Effort:** Simple

### LDF-01: Module-level side effect
- **Severity:** Critical
- **Location:** `system.py`
- **Effort:** Medium

### LDF-02: GameSession legacy params
- **Severity:** Critical
- **Location:** `game_session.py`
- **Effort:** Complex

### LDF-03: CrewCapacity fallback (3x)
- **Severity:** Major
- **Location:** `stats_config.py`
- **Effort:** Medium

### LDF-04: Design metadata dual format
- **Severity:** Major
- **Location:** `design_metadata.py`
- **Effort:** Simple

### MSA-01: ValidationResult import chain
- **Severity:** Critical
- **Location:** `ship.py`
- **Effort:** Simple

### MSA-02: Dead validation re-export
- **Severity:** Major
- **Location:** `validation/__init__.py`
- **Effort:** Simple

### MSA-03: Inconsistent import pattern
- **Severity:** Major
- **Location:** `vehicle_design_service.py`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
