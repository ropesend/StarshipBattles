# PROJ-147: Design Document

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
- **Major:** 11
- **Selected for remediation:** 19

## Selected Findings Summary

### ADR-STR-001: Strategy Layer Imports from AI Layer
- **Severity:** Critical
- **Location:** `game/strategy/adapters/simulat`
- **Effort:** Medium

### ADR-FND-001: Research UI imports game.ui.renderer.cam
- **Severity:** Major
- **Location:** `game/research/ui/research_scen`
- **Effort:** Medium

### ADR-SIM-001: Ship Class is Approaching God Class Terr
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Simple

### ADR-SIM-002: Intentional Late Imports for Circular De
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### ADR-STR-002: ShipDisplayFormatter in Strategy Layer (
- **Severity:** Major
- **Location:** `game/strategy/data/ship_displa`
- **Effort:** Medium

### ADR-STR-003: Circular Import Workaround in Galaxy
- **Severity:** Major
- **Location:** `game/strategy/data/galaxy.py:4`
- **Effort:** Medium

### ADR-UI2-001: ShipIO Direct Import of Simulation Entit
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:20`
- **Effort:** Medium

### ADR-UI2-002: Camera Uses pygame.math.Vector2 Instead
- **Severity:** Major
- **Location:** `game/ui/renderer/camera.py:14,`
- **Effort:** Simple

### ADR-UI1-001: God Class - TestLabScreen (1906 lines)
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### ADR-UI1-002: God Class - fleet_report_window.py (1093
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Medium

### ADR-UI1-003: God Class - build_queue_screen.py (1084
- **Severity:** Major
- **Location:** `game/ui/screens/build_queue_sc`
- **Effort:** Medium

### ADR-UI1-004: God Class - weapons_panel.py (1037 lines
- **Severity:** Major
- **Location:** `game/ui/screens/builder/weapon`
- **Effort:** Medium

### ADR-FND-002: Research UI subpackage uses pygame direc
- **Severity:** Minor
- **Location:** `game/research/ui/research_cont`
- **Effort:** Medium

### ADR-SIM-003: Component Module Contains Multiple Conce
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### ADR-STR-004: Intentional Late Imports - Documented bu
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### ADR-STR-005: RGB Color Tuples in Game Config
- **Severity:** Minor
- **Location:** `game/strategy/engine/game_conf`
- **Effort:** Simple

### ADR-UI2-003: Game Renderer Inline Import of ShipTheme
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### ADR-UI1-005: Near-God Classes (500-1000 lines)
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### ADR-UI1-006: Inconsistent Cross-Layer Import Document
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
