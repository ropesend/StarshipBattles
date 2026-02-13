# PROJ-116: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 0
- **Major:** 15
- **Selected for remediation:** 19

## Selected Findings Summary

### ADR-SIM-005: God class - battle_controller.py (848 li
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Large

### ADR-SIM-006: God class - ship.py (809 lines)
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Large

### ADR-SIM-007: God class - component.py (719 lines)
- **Severity:** Major
- **Location:** `game/simulation/components/com`
- **Effort:** Medium

### ADR-STR-003: ProductionEngine God Class (701 lines, 1
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Complex

### ADR-STR-004: Galaxy God Class (698 lines, 26 methods)
- **Severity:** Major
- **Location:** `game/strategy/data/galaxy.py:9`
- **Effort:** Complex

### ADR-STR-005: ShipInstance God Class (658 lines, 44 me
- **Severity:** Major
- **Location:** `game/strategy/data/ship_instan`
- **Effort:** Medium

### ADR-STR-006: Fleet God Class (353 lines, 41 methods)
- **Severity:** Major
- **Location:** `game/strategy/data/fleet.py:69`
- **Effort:** Medium

### ADR-UI1-003: TestLabScreen God Class (1877 lines, 75
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### ADR-UI1-004: BuilderScreen God Class (1042 lines, 44
- **Severity:** Major
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Medium

### ADR-UI1-005: FormationEditorScreen God Class (701 lin
- **Severity:** Major
- **Location:** `game/ui/screens/formation_edit`
- **Effort:** Medium

### ADR-UI1-006: StrategyScreen God Class (768 lines, 45
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Complex

### ADR-UI1-009: BattleScreen God Class (621 lines, 32 me
- **Severity:** Major
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Medium

### ADR-UI1-010: FleetReportWindow God Class (1075 lines,
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Medium

### ADR-UI1-011: BuildQueueScreen God Class (1057 lines,
- **Severity:** Major
- **Location:** `game/ui/screens/build_queue_sc`
- **Effort:** Medium

### ADR-UI1-012: EmpireBuildQueueWindow God Class (791 li
- **Severity:** Major
- **Location:** `game/ui/screens/empire_build_q`
- **Effort:** Medium

### ADR-UI1-020: WeaponsReportPanel File Size (1037 lines
- **Severity:** Info
- **Location:** `game/ui/screens/builder/weapon`
- **Effort:** Medium

### ADR-UI1-021: RaceSummaryPanel (671 lines, 25 methods)
- **Severity:** Info
- **Location:** `game/ui/panels/race_summary_pa`
- **Effort:** Simple

### ADR-UI1-022: WorkshopViewModel (551 lines, 36 methods
- **Severity:** Info
- **Location:** `game/ui/screens/workshop_viewm`
- **Effort:** Simple

### ADR-UI1-023: StrategyUI Thin Facade (357 lines, 38 me
- **Severity:** Info
- **Location:** `game/ui/screens/strategy_ui.py`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
