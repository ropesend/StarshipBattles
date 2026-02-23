# PROJ-150: Design Document

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
- **Major:** 9
- **Selected for remediation:** 27

## Selected Findings Summary

### LEG-UI2-001: BattleOrchestrator is Defined but Never
- **Severity:** Major
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Medium

### LEG-FND-002: Singleton Pattern Pervasive Despite DI P
- **Severity:** Major
- **Location:** `game/core/singleton.py`
- **Effort:** Complex

### LEG-FND-003: Defensive getattr Fallbacks in AI Module
- **Severity:** Major
- **Location:** `game/ai/controller.py:125-127,`
- **Effort:** Medium

### LEG-SIM-002: Unused BattleConfig.isolated Field
- **Severity:** Major
- **Location:** `game/simulation/battle_config.`
- **Effort:** Simple

### LEG-SIM-003: Unused validate_state Method in BattleSt
- **Severity:** Major
- **Location:** `game/simulation/managers/battl`
- **Effort:** Simple

### LEG-UI2-002: Defensive getattr Checks for Attributes
- **Severity:** Major
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI2-003: VehicleClassService Methods Appear Unuse
- **Severity:** Major
- **Location:** `game/ui/services/vehicle_class`
- **Effort:** Simple

### LEG-UI1-001: Legacy Single-Selection Fields Maintaine
- **Severity:** Major
- **Location:** `game/ui/screens/empire_build_q`
- **Effort:** Simple

### LEG-UI1-003: Fallback Pattern to Direct scene.ships A
- **Severity:** Major
- **Location:** `game/ui/panels/battle_panels.p`
- **Effort:** Medium

### LEG-FND-001: Unused Error Codes in error_codes.py
- **Severity:** Minor
- **Location:** `game/core/error_codes.py:82-10`
- **Effort:** Simple

### LEG-FND-004: Strategy Fallback Patterns in AI Documen
- **Severity:** Minor
- **Location:** `game/ai/__init__.py:38-48`
- **Effort:** Medium

### LEG-UI1-002: Unused Imports Across Multiple Files
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### LEG-FND-006: is_camera TypeGuard Never Used
- **Severity:** Minor
- **Location:** `game/core/protocols.py:577-579`
- **Effort:** Simple

### LEG-FND-007: Profiling Module Has Inconsistent API
- **Severity:** Minor
- **Location:** `game/core/profiling.py:63-64`
- **Effort:** Simple

### LEG-FND-008: Mock Detection Pattern in combat_utils
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py:44`
- **Effort:** Simple

### LEG-SIM-004: Unused Documentation Constants in physic
- **Severity:** Minor
- **Location:** `game/simulation/physics_consta`
- **Effort:** Simple

### LEG-SIM-005: Singleton Pattern in ComponentCacheManag
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Complex

### LEG-SIM-006: KNOWN_ISSUE Comment for Module Identity
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### LEG-SIM-008: Fallback Comments Suggesting Incomplete
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### LEG-UI2-004: ComponentService.is_modifier_allowed Dup
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Simple

### LEG-UI2-007: Inconsistent DI Patterns Across Services
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Simple

### LEG-UI1-004: Empty __init__ Method
- **Severity:** Minor
- **Location:** `game/ui/screens/race_asset_loa`
- **Effort:** Simple

### LEG-UI1-005: Disabled Feature Left as pass Statement
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/schema`
- **Effort:** Simple

### LEG-UI1-006: get_component_at Returns None Unconditio
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/schema`
- **Effort:** Simple

### LEG-UI1-007: Legacy Pattern Comment Without Active Co
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/stats_`
- **Effort:** Simple

### LEG-UI1-009: Formation File Format Comment Suggests R
- **Severity:** Minor
- **Location:** `game/ui/screens/formation_edit`
- **Effort:** Simple

### LEG-UI1-010: Fallback Mode in Build Queue Controller
- **Severity:** Minor
- **Location:** `game/ui/panels/build_queue_con`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
