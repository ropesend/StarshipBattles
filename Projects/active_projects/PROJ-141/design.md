# PROJ-141: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_223809_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 145 total findings identified.
- **Critical:** 3
- **Major:** 4
- **Selected for remediation:** 18

## Selected Findings Summary

### CON-UI2-001: Inconsistent Dependency Injection Patter
- **Severity:** Critical
- **Location:** `game/ui/services/`
- **Effort:** Medium

### DUP-UI2-001: Tkinter Root Initialization Duplicated A
- **Severity:** Critical
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-UI1-001: Screenshot Toast Notification Pattern Du
- **Severity:** Critical
- **Location:** `game/ui/screens/planet_list_wi`
- **Effort:** Simple

### DUP-UI2-002: Battle Factory Functions Follow Identica
- **Severity:** Major
- **Location:** `game/ui/services/battle_factor`
- **Effort:** Medium

### DUP-UI2-004: BattleUIService Repeated Null-Check Patt
- **Severity:** Major
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### DUP-UI1-003: Filter State Management Pattern Repeated
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_f`
- **Effort:** Medium

### DUP-UI1-004: Compact Number Formatting Logic Isolated
- **Severity:** Major
- **Location:** `game/ui/panels/planet_report_p`
- **Effort:** Simple

### CON-UI2-007: Inconsistent Type Hint Coverage
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:42`
- **Effort:** Simple

### CON-UI2-008: Inconsistent Error Logging Patterns
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:72`
- **Effort:** Simple

### CON-UI2-010: Boolean Parameter Naming Inconsistency
- **Severity:** Minor
- **Location:** `game/ui/services/battle_factor`
- **Effort:** Simple

### CON-UI2-011: Inconsistent Import Organization
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:1-`
- **Effort:** Simple

### CON-UI2-012: Magic Numbers in Rendering Code
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### DUP-UI2-006: Ship Cloning Logic in create_hypothetica
- **Severity:** Minor
- **Location:** `game/ui/services/battle_factor`
- **Effort:** Simple

### DUP-UI1-005: RaceThemeGallery Not Using BaseGallery
- **Severity:** Minor
- **Location:** `game/ui/panels/race_theme_gall`
- **Effort:** Simple

### CON-UI2-013: Inconsistent __all__ Export Patterns
- **Severity:** Info
- **Location:** `game/ui/__init__.py`
- **Effort:** Simple

### DUP-UI2-008: Adapter Classes Follow Consistent Patter
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### DUP-UI1-009: Well-Refactored Gallery System
- **Severity:** Info
- **Location:** `game/ui/panels/base_gallery.py`
- **Effort:** N

### DUP-UI1-010: DesignStatsPanel Successful Extraction
- **Severity:** Info
- **Location:** `game/ui/panels/design_stats_pa`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
