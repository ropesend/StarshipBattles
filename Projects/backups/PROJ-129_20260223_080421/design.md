# PROJ-129: Design Document

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
- **Critical:** 0
- **Major:** 3
- **Selected for remediation:** 20

## Selected Findings Summary

### LEG-STR-001: Legacy Behavior Branch in FleetOrderProc
- **Severity:** Major
- **Location:** `game/strategy/engine/fleet_ord`
- **Effort:** Medium

### LEG-STR-002: Backward Compatibility Comment in GameSe
- **Severity:** Major
- **Location:** `game/strategy/engine/game_sess`
- **Effort:** Medium

### LEG-STR-003: Legacy Items in ProductionEngine
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Medium

### LEG-FND-003: Raw Ship vs Adapter Access Pattern in Fo
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:276-400`
- **Effort:** Medium

### LEG-FND-004: Singleton Pattern Still in Use Despite D
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### LEG-FND-005: Unused AI_STATE_ERROR ErrorCode
- **Severity:** Minor
- **Location:** `game/core/error_codes.py:153`
- **Effort:** Simple

### LEG-SIM-006: Module Identity Drift Fallback in Abilit
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### LEG-SIM-007: Component Ability Index Fallback Pattern
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### LEG-STR-004: Backward Compatibility Comment in FleetN
- **Severity:** Minor
- **Location:** `game/strategy/services/fleet_n`
- **Effort:** Simple

### LEG-STR-005: Backward Compat Default in Planet.from_d
- **Severity:** Minor
- **Location:** `game/strategy/data/planet.py:3`
- **Effort:** Simple

### LEG-STR-006: Backward Compat Defaults in RaceConfig.f
- **Severity:** Minor
- **Location:** `game/strategy/data/race_config`
- **Effort:** N

### LEG-STR-007: Old Layer Format Detection in DesignMeta
- **Severity:** Minor
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### LEG-STR-008: Save Compatibility Field in DesignMetada
- **Severity:** Minor
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### LEG-UI2-003: Excessive getattr() with Defaults in bat
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI2-004: ModifierEditorPanel Marked as Legacy
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/modifi`
- **Effort:** Medium

### LEG-SIM-009: TechPresetLoader Only Used in Tests
- **Severity:** Info
- **Location:** `game/simulation/systems/tech_p`
- **Effort:** Unknown

### LEG-STR-009: Test Mock Compatibility in FleetOrderPro
- **Severity:** Info
- **Location:** `game/strategy/engine/fleet_ord`
- **Effort:** Simple

### LEG-STR-010: Intercept Function Accepts Both Fleet an
- **Severity:** Info
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** N

### LEG-UI2-005: Singleton Pattern Still in Use for Asset
- **Severity:** Info
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** N

### LEG-UI2-006: hasattr() Check in Camera for Defensive
- **Severity:** Info
- **Location:** `game/ui/renderer/camera.py:58`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
