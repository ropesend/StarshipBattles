# PROJ-126: Design Document

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
- **Critical:** 3
- **Major:** 13
- **Selected for remediation:** 29

## Selected Findings Summary

### ADR-SIM-001: AI Layer Imports in Simulation Factory
- **Severity:** Critical
- **Location:** `game/simulation/factories/ai_f`
- **Effort:** Medium

### ADR-UI1-001: Test Framework Coupling in Production UI
- **Severity:** Critical
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Medium

### ADR-UI1-002: Test Framework Import in Battle Screen
- **Severity:** Critical
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Simple

### ADR-SIM-002: TYPE_CHECKING Import of AI Controller
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### ADR-SIM-003: God Class - BattleController
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Complex

### ADR-SIM-004: God Class - Ship Entity
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Complex

### ADR-SIM-005: Documented Circular Import in Ship.add_c
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### ADR-UI2-002: God Class Potential in ShipThemeManager
- **Severity:** Major
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Medium

### ADR-UI1-003: God Class - TestLabScreen (1908 lines, 7
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### ADR-UI1-004: God Class - StrategyScreen (811 lines, 4
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Medium

### ADR-UI1-005: God Class - BuilderMain (1121 lines, 44
- **Severity:** Major
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Medium

### ADR-UI1-006: God Class - BuildQueueScreen (1098 lines
- **Severity:** Major
- **Location:** `game/ui/screens/build_queue_sc`
- **Effort:** Medium

### ADR-UI1-007: Circular Dependency Workarounds (Late Im
- **Severity:** Major
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Medium

### ADR-UI1-008: Private Attribute Access - StrategyEvent
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_event`
- **Effort:** Simple

### ADR-UI1-009: Private Attribute Access - WorkshopEvent
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_event`
- **Effort:** Simple

### ADR-UI1-010: Direct ViewModel State Mutation
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_scree`
- **Effort:** Simple

### ADR-FND-003: behaviors.py File Growing Large
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py`
- **Effort:** Simple

### ADR-SIM-006: Possible Circular Import Comment in ship
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### ADR-UI2-003: Lazy Import Pattern in ship_factory.py C
- **Severity:** Minor
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### ADR-UI1-011: Simulation Layer TYPE_CHECKING Imports
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### ADR-UI1-012: Planet Filter Cached Attributes
- **Severity:** Minor
- **Location:** `game/ui/screens/planet_list_fi`
- **Effort:** Simple

### ADR-UI1-013: Strategy Renderer Temporary Attributes
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_rende`
- **Effort:** Simple

### ADR-UI1-014: FleetCapabilityCalculator Private Method
- **Severity:** Minor
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Simple

### ADR-UI1-015: InputMapper Private Method Access
- **Severity:** Minor
- **Location:** `game/ui/screens/keybindings_sc`
- **Effort:** Simple

### ADR-SIM-007: Heavy Use of TYPE_CHECKING for Forward R
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### ADR-UI2-005: BattleOrchestrator Correctly Documents C
- **Severity:** Info
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** N

### ADR-UI1-016: Test Lab Executor Private Field Access
- **Severity:** Info
- **Location:** `game/ui/screens/test_lab/test_`
- **Effort:** Simple

### ADR-UI1-017: Deep Object Chain in StrategyUI
- **Severity:** Info
- **Location:** `game/ui/screens/strategy_ui.py`
- **Effort:** Simple

### ADR-UI1-018: Large Method Counts in UI Screens
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
