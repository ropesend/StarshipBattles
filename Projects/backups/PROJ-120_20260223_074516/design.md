# PROJ-120: Design Document

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
- **Critical:** 3
- **Major:** 7
- **Selected for remediation:** 18

## Selected Findings Summary

### TCG-SIM-001: Projectile Entity Has No Unit Tests
- **Severity:** Critical
- **Location:** `game/simulation/entities/proje`
- **Effort:** Medium

### TCG-SIM-002: ShipStatQuerier Has No Unit Tests
- **Severity:** Critical
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### TCG-SIM-003: ShipValidator Rules Have No Unit Tests
- **Severity:** Critical
- **Location:** `game/simulation/validation/shi`
- **Effort:** Complex

### TCG-SIM-004: BattleController Missing Edge Case Tests
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Medium

### TCG-SIM-005: DamageCalculator Armor Penetration Edge
- **Severity:** Major
- **Location:** `game/simulation/combat/damage_`
- **Effort:** Simple

### TCG-SIM-006: WeaponFiringSystem Missing Multishot Tes
- **Severity:** Major
- **Location:** `game/simulation/combat/weapon_`
- **Effort:** Medium

### TCG-SIM-007: TargetingSystem Missing AI Priority Test
- **Severity:** Major
- **Location:** `game/simulation/combat/targeti`
- **Effort:** Medium

### TCG-SIM-008: BattleEngine Tick Processing Incomplete
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Medium

### TCG-SIM-009: FormulaSystem Overflow/Underflow Not Tes
- **Severity:** Major
- **Location:** `game/simulation/formula_system`
- **Effort:** Simple

### TCG-SIM-010: Design System Serialization Roundtrip Ga
- **Severity:** Major
- **Location:** `game/simulation/designs.py`
- **Effort:** Medium

### TCG-SIM-011: AbilityAggregator Missing Concurrent Mod
- **Severity:** Minor
- **Location:** `game/simulation/entities/abili`
- **Effort:** Simple

### TCG-SIM-012: ShipCombatEngine Heat Management Not Tes
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-SIM-013: ShipFormation Missing Complex Formation
- **Severity:** Minor
- **Location:** `tests/unit/simulation/entities`
- **Effort:** Simple

### TCG-SIM-014: BattleStateSerializer Version Migration
- **Severity:** Minor
- **Location:** `tests/unit/simulation/test_bat`
- **Effort:** Simple

### TCG-SIM-015: PropulsionAbility Strategic Movement Not
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-016: ProjectileManager Missing Batch Update T
- **Severity:** Minor
- **Location:** `game/simulation/projectile_man`
- **Effort:** Simple

### TCG-SIM-017: Test Organization Inconsistency
- **Severity:** Info
- **Location:** `tests/unit/simulation/`
- **Effort:** N

### TCG-SIM-018: Simulation Integration Tests Sparse
- **Severity:** Info
- **Location:** `tests/integration/`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
