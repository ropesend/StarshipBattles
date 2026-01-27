# PROJ-26: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-01-27_update_naming-inconsistencies](../../Reviews/results/2026-01-27_update_naming-inconsistencies/)
- **Type:** Update Review
- **Date:** 2026-01-27
- **Report:** [View Full Report](../../Reviews/results/2026-01-27_update_naming-inconsistencies/report.md)

## Initial Analysis
Findings from review - 15 total findings identified.
- **Critical:** 1
- **Major:** 6
- **Selected for remediation:** 7

## Selected Findings Summary

### NC-03: ShipBuilderService shim
- **Severity:** Major
- **Location:** `ship_builder_service.py` deleted`
- **Effort:** 

### NC-02: Builder vs Workshop terminology
- **Severity:** Major
- **Location:** `Workshop files created, builder_* files remain`
- **Effort:** 

### NC-05: Battle vs Combat distinction
- **Severity:** Major
- **Location:** `Exists but not documented`
- **Effort:** 

### NC-02: Workshop imports from Builder directory
- **Severity:** Major
- **Location:** ``
- **Effort:** Reg-03

### NC-01: Duplicate BattleScene not removed
- **Severity:** Critical
- **Location:** `**Details:** See [regression_report.md](findings/regression_report.md)

---

## New Issues Found (6)`
- **Effort:** Id

### NEW-03: Duplicate InputHandler class
- **Severity:** Major
- **Location:** `input_handler.py` (2 files)`
- **Effort:** 

### NEW-05: Duplicate Ability classes
- **Severity:** Major
- **Location:** `abilities.py` + `abilities/*.py`
- **Effort:** 


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
