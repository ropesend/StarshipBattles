# PROJ-121: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 273 total findings identified.
- **Critical:** 2
- **Major:** 13
- **Selected for remediation:** 37

## Selected Findings Summary

### LEG-SIM-001: String-to-Enum Migration Support Code in
- **Severity:** Critical
- **Location:** `game/simulation/systems/battle`
- **Effort:** Medium

### LEG-UI1-001: Backward Compatibility Aliases in RacePo
- **Severity:** Critical
- **Location:** `game/ui/panels/race_portrait_g`
- **Effort:** Simple

### LEG-FND-001: Unused Exception Classes (AIException, T
- **Severity:** Major
- **Location:** `game/core/exceptions.py:216-23`
- **Effort:** Simple

### LEG-FND-002: Backward Compatibility Wrapper - load_re
- **Severity:** Major
- **Location:** `game/core/resources.py:101-114`
- **Effort:** Simple

### LEG-SIM-002: V1 Modifier Format Validation Code Still
- **Severity:** Major
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### LEG-SIM-003: Defensive hasattr Check for Always-Prese
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### LEG-SIM-004: retreat_status Attribute Accessed via ha
- **Severity:** Major
- **Location:** `game/simulation/managers/retre`
- **Effort:** Simple

### LEG-UI2-001: Dead Code - draw_hud and draw_bar Functi
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### LEG-UI2-002: Unused Method - create_ai_for_ship in Ba
- **Severity:** Major
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Simple

### LEG-UI2-003: Unused Method - capture_step in Screensh
- **Severity:** Major
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### LEG-UI1-002: Legacy BuilderScreen (builder/main.py) P
- **Severity:** Major
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Complex

### LEG-UI1-003: Legacy Tuple Format Support in Component
- **Severity:** Major
- **Location:** `game/ui/screens/builder/detail`
- **Effort:** Medium

### LEG-UI1-004: Legacy API Comment in FleetReportWindow
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_w`
- **Effort:** Simple

### LEG-UI1-005: Legacy Single-Selection Fields in Empire
- **Severity:** Major
- **Location:** `game/ui/screens/empire_build_q`
- **Effort:** Medium

### LEG-UI1-006: Fallback Mode in BuildQueueController
- **Severity:** Major
- **Location:** `game/ui/panels/build_queue_con`
- **Effort:** Medium

### LEG-FND-003: Backward Compatibility Comment in Valida
- **Severity:** Minor
- **Location:** `game/core/validation.py:100-10`
- **Effort:** Simple

### LEG-FND-004: Extensive getattr() with Defaults in AI
- **Severity:** Minor
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### LEG-FND-005: Raw Ship vs Adapter Access Pattern in Fo
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:276-400`
- **Effort:** Medium

### LEG-FND-006: DEBUG_SCREENSHOTS Hardcoded True
- **Severity:** Minor
- **Location:** `game/core/constants.py:41`
- **Effort:** Simple

### LEG-FND-007: Singleton Pattern Still in Use Despite D
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### LEG-SIM-005: Fallback Pattern Comment Suggesting Inco
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Simple

### LEG-SIM-006: Ability Manager Fallback for Module Iden
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### LEG-SIM-007: Component Fallback Delegation Pattern
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### LEG-SIM-008: Unused AbilityStatBinding.describe() Met
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### LEG-UI2-004: Duplicate Exception Handlers in ShipIO
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io.py:71`
- **Effort:** Simple

### LEG-UI2-005: Comment References "legacy behavior" in
- **Severity:** Minor
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Medium

### LEG-UI2-006: Basic Color Constants (BLUE, RED, GREEN)
- **Severity:** Minor
- **Location:** `game/ui/colors.py:9-11`
- **Effort:** Simple

### LEG-UI2-007: ShipIOAdapter vs ShipIO Direct Access
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### LEG-UI2-008: Excessive getattr() with Defaults in bat
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI1-007: Backward Compat Attribute Exposure in Ri
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/right_`
- **Effort:** Simple

### LEG-UI1-008: Backward Compatibility in WorkshopEventR
- **Severity:** Minor
- **Location:** `game/ui/screens/workshop_event`
- **Effort:** Simple

### LEG-UI1-009: Test Lab Screen Legacy Game Parameter
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Medium

### LEG-UI1-010: Compatibility Setter in BuilderStateMana
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/state_`
- **Effort:** Simple

### LEG-UI1-011: Deprecated Properties in StrategyScreen
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Complex

### LEG-UI2-009: Singleton Pattern Still in Use for Asset
- **Severity:** Info
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** N

### LEG-UI2-010: Anticipatory Code in _CONTEXT_OVERLAP
- **Severity:** Info
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### LEG-UI1-012: Legacy Keys Filtering in stats_config.py
- **Severity:** Info
- **Location:** `game/ui/screens/builder/stats_`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
