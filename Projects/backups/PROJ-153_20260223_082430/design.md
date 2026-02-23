# PROJ-153: Design Document

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
- **Critical:** 0
- **Major:** 3
- **Selected for remediation:** 11

## Selected Findings Summary

### TCG-UI1-004: InteractionController (drag-drop for shi
- **Severity:** Major
- **Location:** `game/ui/screens/builder/intera`
- **Effort:** Medium

### TCG-UI1-012: builder/ subpackage has no test files at
- **Severity:** Major
- **Location:** `game/ui/screens/builder/*.py`
- **Effort:** Complex

### TCG-UI1-013: test_lab/ subpackage has minimal direct
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/*.py`
- **Effort:** Medium

### TCG-UI2-005: ShipThemeManager Missing Tests for Concu
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Complex

### TCG-UI2-007: InputMapper Missing Tests for Numpad Key
- **Severity:** Minor
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### TCG-UI2-008: ScreenshotManager Missing Tests for Very
- **Severity:** Minor
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### TCG-UI2-009: ShipFactory Missing Tests for Invalid De
- **Severity:** Minor
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### TCG-UI1-017: DesignSelectorWindow tests don't cover r
- **Severity:** Minor
- **Location:** `tests/unit/ui/screens/test_des`
- **Effort:** Simple

### TCG-UI1-018: GalaxyTestScreen (galaxy_test/ subpackag
- **Severity:** Minor
- **Location:** `game/ui/screens/galaxy_test/*.`
- **Effort:** Simple

### TCG-UI1-021: workshop_event_router.py, workshop_data_
- **Severity:** Minor
- **Location:** `game/ui/screens/workshop_event`
- **Effort:** Simple

### TCG-UI1-022: setup_renderer.py has no tests (setup sc
- **Severity:** Minor
- **Location:** `game/ui/screens/setup_renderer`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
