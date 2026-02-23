# PROJ-134: Design Document

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
- **Critical:** 0
- **Major:** 8
- **Selected for remediation:** 33

## Selected Findings Summary

### LEG-SIM-001: Empty Factory Module (Dead Package)
- **Severity:** Major
- **Location:** `game/simulation/factories/__in`
- **Effort:** Simple

### LEG-SIM-002: Incomplete Migration - StrategyBattleMod
- **Severity:** Major
- **Location:** `game/simulation/combat/battle_`
- **Effort:** Medium

### LEG-SIM-004: Hasattr Checks for ability_instances on
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### LEG-UI2-001: Global Registry Fallback Pattern in Ship
- **Severity:** Major
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Medium

### LEG-UI2-002: Global Registry Fallback Pattern in Comp
- **Severity:** Major
- **Location:** `game/ui/services/component_ser`
- **Effort:** Medium

### LEG-UI1-001: Legacy Single-Selection Fields in Empire
- **Severity:** Major
- **Location:** `game/ui/screens/empire_build_q`
- **Effort:** Medium

### LEG-UI1-002: Backward Compatibility Property in TestL
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Simple

### LEG-UI1-003: Legacy API Method in FleetReportWindow
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Medium

### LEG-FND-002: Extensive getattr() Defensive Patterns S
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py:63-181`
- **Effort:** Complex

### LEG-SIM-003: Defensive getattr/hasattr Usage on Core
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### LEG-FND-003: Singleton Pattern Still Used Extensively
- **Severity:** Minor
- **Location:** `game/core/singleton.py`
- **Effort:** Complex

### LEG-FND-004: hasattr() Checks for Mock Detection in P
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py:43-47`
- **Effort:** Simple

### LEG-FND-005: Fallback Behavior Documented Extensively
- **Severity:** Minor
- **Location:** `game/ai/__init__.py:34-52`
- **Effort:** Medium

### LEG-FND-006: Commented Strategy Hints in Controller C
- **Severity:** Minor
- **Location:** `game/ai/controller.py:346`
- **Effort:** Simple

### LEG-SIM-005: V1 Modifier Format Check Still Present
- **Severity:** Minor
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### LEG-SIM-006: Projectile Type String Conversion Patter
- **Severity:** Minor
- **Location:** `game/simulation/entities/proje`
- **Effort:** Simple

### LEG-SIM-007: Legacy Comment References (PROJ-106 Lega
- **Severity:** Minor
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### LEG-SIM-008: Stale Docstring Reference to Legacy Beha
- **Severity:** Minor
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### LEG-UI2-003: Unused Protocol Import (IBattleUI)
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### LEG-UI2-005: Global Registry Fallback in DesignLoader
- **Severity:** Minor
- **Location:** `game/ui/services/design_loader`
- **Effort:** Simple

### LEG-UI2-006: Defensive getattr Patterns for Missing A
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI2-007: hasattr Checks for Potentially Missing A
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI1-004: Comments Referencing "Legacy Dispatch" i
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_input`
- **Effort:** Simple

### LEG-UI1-005: Pass Statements in Stub Methods
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/ship_`
- **Effort:** Simple

### LEG-UI1-008: Fallback Chains in Workshop Context
- **Severity:** Minor
- **Location:** `game/ui/screens/workshop_conte`
- **Effort:** Simple

### LEG-UI1-009: PROJ-40 Migration Comments Still Present
- **Severity:** Minor
- **Location:** `game/ui/screens/fleet_report_f`
- **Effort:** Simple

### LEG-FND-007: Potential Dead Parameters in navigate_to
- **Severity:** Info
- **Location:** `game/ai/controller.py:434`
- **Effort:** Simple

### LEG-UI2-004: Unused Method get_ships_folder in ShipIO
- **Severity:** Info
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Simple

### LEG-UI1-006: Extensive hasattr() Checks for Optional
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### LEG-UI1-007: Singleton Instance Access Pattern
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### LEG-UI1-010: getattr() Defensive Patterns
- **Severity:** Info
- **Location:** `game/ui/screens/empire_panel_w`
- **Effort:** Medium

### LEG-UI1-011: Dual-Path Ship/DTO Support in BattlePane
- **Severity:** Info
- **Location:** `game/ui/panels/battle_panels.p`
- **Effort:** Deferred

### LEG-UI1-012: Build Queue Fallback Mode
- **Severity:** Info
- **Location:** `game/ui/panels/build_queue_con`
- **Effort:** None


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
