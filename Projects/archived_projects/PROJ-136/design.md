# PROJ-136: Design Document

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
- **Major:** 12
- **Selected for remediation:** 34

## Selected Findings Summary

### TCG-UI2-001: game_renderer.py Has No Test Coverage
- **Severity:** Critical
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### TCG-UI1-001: Builder Module Completely Untested
- **Severity:** Critical
- **Location:** `game/ui/screens/builder/`
- **Effort:** Complex

### TCG-FND-001: PhysicsBody Has Minimal Direct Unit Test
- **Severity:** Major
- **Location:** `game/engine/physics.py`
- **Effort:** Medium

### TCG-FND-002: Research UI Components Have No Pygame-In
- **Severity:** Major
- **Location:** `game/research/ui/research_cont`
- **Effort:** Complex

### TCG-UI1-002: Test Lab Module Minimal Coverage
- **Severity:** Major
- **Location:** `game/ui/screens/test_lab/`
- **Effort:** Medium

### TCG-UI1-003: Galaxy Test Module No Tests
- **Severity:** Major
- **Location:** `game/ui/screens/galaxy_test/`
- **Effort:** Simple

### TCG-UI1-004: Formation Module Missing Core Tests
- **Severity:** Major
- **Location:** `game/ui/screens/formation/`
- **Effort:** Simple

### TCG-FND-006: TargetEvaluator Rule Processing Missing
- **Severity:** Major
- **Location:** `game/ai/target_evaluator.py`
- **Effort:** Simple

### TCG-FND-007: AIControllerFactory Missing Error Path T
- **Severity:** Major
- **Location:** `game/ai/ai_factory.py`
- **Effort:** Simple

### TCG-UI2-002: ShipIOAdapter Has No Dedicated Tests
- **Severity:** Major
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Simple

### TCG-UI2-005: DesignLoaderAdapter Missing Error Path T
- **Severity:** Major
- **Location:** `game/ui/services/design_loader`
- **Effort:** Simple

### TCG-UI1-005: Panel Files Missing Tests
- **Severity:** Major
- **Location:** `game/ui/panels/`
- **Effort:** Medium

### TCG-UI1-007: Strategy Screen Complex Modules
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_*.py`
- **Effort:** Medium

### TCG-UI1-008: Workshop Data Components Untested
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_*.py`
- **Effort:** Medium

### TCG-UI2-003: UIConfig Has No Tests
- **Severity:** Minor
- **Location:** `game/ui/config.py`
- **Effort:** Simple

### TCG-UI2-006: BattleUIService Missing Tests for Edge C
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### TCG-UI2-007: ValidationService Missing Boundary Value
- **Severity:** Minor
- **Location:** `game/ui/services/validation_se`
- **Effort:** Simple

### TCG-UI1-006: BattlePanel Classes Undertested
- **Severity:** Minor
- **Location:** `game/ui/panels/battle_panels.p`
- **Effort:** Simple

### TCG-UI1-009: Fleet Report Components Undertested
- **Severity:** Minor
- **Location:** `game/ui/screens/fleet_*.py`
- **Effort:** Simple

### TCG-UI1-011: Planet List Components
- **Severity:** Minor
- **Location:** `game/ui/screens/planet_list_*.`
- **Effort:** Simple

### TCG-STR-019: Planet Population Model Edge Cases
- **Severity:** Minor
- **Location:** `game/strategy/data/planet.py:S`
- **Effort:** Simple

### TCG-STR-020: FleetDTO Build Validation
- **Severity:** Minor
- **Location:** `game/strategy/facade/dto/fleet`
- **Effort:** Simple

### TCG-UI2-008: SpriteManager Test Skips Production Dire
- **Severity:** Minor
- **Location:** `game/ui/renderer/sprites.py`
- **Effort:** Medium

### TCG-UI2-010: ShipThemeManager Tests Skip When Federat
- **Severity:** Minor
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Medium

### TCG-UI2-012: colors.py WHITE and BLACK Constants Not
- **Severity:** Minor
- **Location:** `game/ui/colors.py`
- **Effort:** Simple

### TCG-UI1-014: Column Manager
- **Severity:** Minor
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Simple

### TCG-UI1-017: Setup Screen Components
- **Severity:** Minor
- **Location:** `game/ui/screens/setup_*.py`
- **Effort:** Simple

### TCG-UI1-018: Empire Panel Window
- **Severity:** Minor
- **Location:** `game/ui/screens/empire_panel_w`
- **Effort:** Simple

### TCG-UI1-020: Design Selector Window
- **Severity:** Minor
- **Location:** `game/ui/screens/design_selecto`
- **Effort:** Simple

### TCG-UI2-009: InputMapper Missing Tests for Modifier C
- **Severity:** Info
- **Location:** `game/ui/services/input_mapper.`
- **Effort:** Simple

### TCG-UI2-011: ScreenshotManager capture() Region Clipp
- **Severity:** Info
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Simple

### TCG-UI2-014: test_atlas_fallback_logic Is Empty
- **Severity:** Info
- **Location:** `tests/unit/ui/test_sprites.py`
- **Effort:** Simple

### TCG-UI1-021: Test Quality - Bypass-Init Pattern Usage
- **Severity:** Info
- **Location:** `tests/unit/ui/screens/test_for`
- **Effort:** Medium

### TCG-UI1-022: Test Quality - Mock Heavy Tests
- **Severity:** Info
- **Location:** `tests/unit/ui/screens/test_for`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
