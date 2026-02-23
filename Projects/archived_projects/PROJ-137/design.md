# PROJ-137: Design Document

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
- **Critical:** 1
- **Major:** 10
- **Selected for remediation:** 19

## Selected Findings Summary

### DUP-UI1-001: Number Formatting with K/M Suffixes Dupl
- **Severity:** Critical
- **Location:** `game/ui/panels/planet_report_p`
- **Effort:** Simple

### CON-UI1-010: Duplicate ColumnManager Classes
- **Severity:** Major
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Medium

### DUP-FND-003: Distance Calculation Pattern Repetition
- **Severity:** Major
- **Location:** `game/ai/controller.py:197-201`
- **Effort:** Medium

### DUP-STR-001: Duplicated Facility Component Iteration
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-STR-002: Duplicated Command Handler Pattern
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-STR-003: Duplicated Resource Cost Calculation
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### DUP-UI2-001: Tkinter Root Initialization Duplicated
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:20`
- **Effort:** Medium

### DUP-UI2-003: Image Bounding Box + Scale Logic Duplica
- **Severity:** Major
- **Location:** `game/ui/utils.py:116-162`
- **Effort:** Simple

### DUP-UI1-002: Virtual Scrolling List Pattern Repeated
- **Severity:** Major
- **Location:** `game/ui/screens/planet_list_wi`
- **Effort:** Medium

### DUP-UI1-003: Filter Toggle Button Pattern Duplicated
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Medium

### DUP-UI1-005: Sidebar Filter Section Building Pattern
- **Severity:** Major
- **Location:** `game/ui/screens/empire_build_q`
- **Effort:** Medium

### DUP-FND-001: IControllable Protocol Duplicates IShip
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Medium

### DUP-FND-002: ResearchTracker and ResearchControlPanel
- **Severity:** Minor
- **Location:** `game/research/data/research_tr`
- **Effort:** Simple

### DUP-UI2-002: Registry Provider Lazy Resolution Patter
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Medium

### DUP-UI1-004: Placeholder Surface Creation
- **Severity:** Minor
- **Location:** `game/ui/panels/build_queue_por`
- **Effort:** Simple

### DUP-FND-006: Flee Direction Calculation
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:70-85`
- **Effort:** Simple

### DUP-UI1-007: Column Visibility Toggle Handling
- **Severity:** Minor
- **Location:** `game/ui/screens/planet_list_wi`
- **Effort:** Simple

### DUP-UI2-004: Singleton Manager Boilerplate
- **Severity:** Info
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### DUP-UI2-006: Clipboard Copy Implementation
- **Severity:** Info
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
