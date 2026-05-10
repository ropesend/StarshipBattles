# PROJ-132: Design Document

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
- **Critical:** 2
- **Major:** 10
- **Selected for remediation:** 24

## Selected Findings Summary

### ADR-FND-001: Research UI layer imports from game.ui
- **Severity:** Critical
- **Location:** `game/research/ui/research_scen`
- **Effort:** Medium

### ADR-SIM-001: Simulation imports AI layer in factory f
- **Severity:** Critical
- **Location:** `game/simulation/battle_control`
- **Effort:** Medium

### ADR-STR-001: Galaxy Class Exceeds Size Threshold (God
- **Severity:** Major
- **Location:** `game/strategy/data/galaxy.py:1`
- **Effort:** Medium

### ADR-STR-002: ProductionEngine Exceeds Size Threshold
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Medium

### ADR-UI2-001: Direct Simulation Layer Import in ship_i
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:16`
- **Effort:** Medium

### ADR-UI1-001: TestLabScreen God Class
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### ADR-UI1-002: FleetReportWindow God Class
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Medium

### ADR-UI1-003: BuildQueueScreen Large Class
- **Severity:** Major
- **Location:** `game/ui/screens/build_queue_sc`
- **Effort:** Medium

### ADR-UI1-004: StrategyScreen Large Class
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Medium

### ADR-UI1-005: Private Facade Access in Dialogs
- **Severity:** Major
- **Location:** `game/ui/screens/cargo_quick_di`
- **Effort:** Simple

### ADR-UI1-006: Private Method Access in BattleUI
- **Severity:** Major
- **Location:** `game/ui/screens/battle_ui.py:9`
- **Effort:** Simple

### ADR-UI1-007: StrategyInputHandler Excessive Scene Cou
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_input`
- **Effort:** Medium

### ADR-FND-002: IControllable interface exceeds god clas
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Complex

### ADR-SIM-002: TYPE_CHECKING import from AI layer
- **Severity:** Minor
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### ADR-FND-003: protocols.py exceeds 500 lines
- **Severity:** Minor
- **Location:** `game/core/protocols.py:1-547`
- **Effort:** Simple

### ADR-SIM-005: Late import pattern for circular depende
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Complex

### ADR-STR-003: Circular Import Workaround in galaxy.py
- **Severity:** Minor
- **Location:** `game/strategy/data/galaxy.py:3`
- **Effort:** Simple

### ADR-STR-004: ShipInstance Cross-Layer Late Imports
- **Severity:** Minor
- **Location:** `game/strategy/data/ship_instan`
- **Effort:** Complex

### ADR-STR-005: ShipStatsCalculator Imports from Simulat
- **Severity:** Minor
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### ADR-UI1-008: Deep Attribute Chains (Law of Demeter)
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Simple

### ADR-UI1-009: Panel Accessing Internal Cache
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/valid`
- **Effort:** Simple

### ADR-UI1-011: Workshop Data Reloader Private Attribute
- **Severity:** Minor
- **Location:** `game/ui/screens/workshop_data_`
- **Effort:** Simple

### ADR-UI1-012: Strategy Event Router Accesses Scene Pri
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_event`
- **Effort:** Simple

### ADR-SIM-007: Component.py approaching god class thres
- **Severity:** Info
- **Location:** `game/simulation/components/com`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
