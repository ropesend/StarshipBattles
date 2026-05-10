# PROJ-144: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_223809_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 145 total findings identified.
- **Critical:** 0
- **Major:** 12
- **Selected for remediation:** 24

## Selected Findings Summary

### ADR-UI2-002: ShipIO module-level Tkinter initializati
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:20`
- **Effort:** Medium

### CON-UI2-005: Module-Level Side Effects in ship_io.py
- **Severity:** Major
- **Location:** `game/ui/services/ship_io.py:20`
- **Effort:** Medium

### LEG-FND-001: Excessive getattr() Fallbacks in AI Comb
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:44-212`
- **Effort:** Medium

### LEG-SIM-001: Module Identity Drift Fallback in Abilit
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### LEG-SIM-002: Singleton Pattern in Component Cache Man
- **Severity:** Major
- **Location:** `game/simulation/components/com`
- **Effort:** Complex

### LEG-SIM-003: Dead Fallback Code in BattleController._
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Simple

### LEG-STR-001: Backward Compatibility Fallback in GameS
- **Severity:** Major
- **Location:** `game/strategy/engine/game_sess`
- **Effort:** Medium

### LEG-STR-002: Legacy Behavior Comments in FleetOrderPr
- **Severity:** Major
- **Location:** `game/strategy/engine/fleet_ord`
- **Effort:** Medium

### LEG-STR-003: Backward Compatibility Default in Planet
- **Severity:** Major
- **Location:** `game/strategy/data/planet.py:3`
- **Effort:** Simple

### LEG-STR-004: Backward Compatibility in FleetNavigatio
- **Severity:** Major
- **Location:** `game/strategy/services/fleet_n`
- **Effort:** Medium

### LEG-STR-005: Legacy Production Items in ProductionEng
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Medium

### LEG-UI2-001: BattleOrchestrator Class Is Unused In Ga
- **Severity:** Major
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Simple

### LEG-FND-004: Defensive hasattr() Checks in AI Layer
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### LEG-FND-005: Unused Error Codes
- **Severity:** Minor
- **Location:** `game/core/error_codes.py:63-64`
- **Effort:** Simple

### LEG-SIM-009: Unused Parameter in _apply_results_to_fl
- **Severity:** Minor
- **Location:** `game/simulation/battle_control`
- **Effort:** Simple

### LEG-STR-006: Unused Import StarType in galaxy.py
- **Severity:** Minor
- **Location:** `game/strategy/data/galaxy.py:1`
- **Effort:** Simple

### LEG-STR-007: Reserved/Placeholder Field sprite_previe
- **Severity:** Minor
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### LEG-STR-009: Backward Compatibility Comment in game_c
- **Severity:** Minor
- **Location:** `game/strategy/engine/game_conf`
- **Effort:** Simple

### LEG-STR-010: Support for Old Layer Format in DesignMe
- **Severity:** Minor
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### LEG-UI2-003: WHITE and BLACK Color Constants Are Dead
- **Severity:** Minor
- **Location:** `game/ui/colors.py:7-8`
- **Effort:** Simple

### LEG-FND-007: Fallback Behaviors Are Intentional Desig
- **Severity:** Info
- **Location:** `game/ai/__init__.py:38-52`
- **Effort:** N

### LEG-SIM-010: Documented Technical Debt in ability_man
- **Severity:** Info
- **Location:** `game/simulation/components/abi`
- **Effort:** N

### LEG-STR-011: hasattr() Checks for Standard Attributes
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Medium

### LEG-UI2-005: Singleton Pattern Still Used in UI Layer
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
