# PROJ-145: Design Document

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
- **Critical:** 1
- **Major:** 12
- **Selected for remediation:** 21

## Selected Findings Summary

### DUP-STR-001: Duplicate Component Ability Extraction P
- **Severity:** Critical
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Medium

### CON-FND-001: Inconsistent Singleton Pattern Usage
- **Severity:** Major
- **Location:** `game/core/registry.py:379-397`
- **Effort:** Medium

### CON-SIM-003: Mixed Docstring Formats
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### CON-SIM-005: Ability Class Naming Inconsistency
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Complex

### DUP-FND-001: Singleton Clear Pattern Duplication
- **Severity:** Major
- **Location:** `game/core/profiling.py:39-42`
- **Effort:** Medium

### DUP-FND-003: JSON Loading with Fallback Pattern
- **Severity:** Major
- **Location:** `game/core/resources.py:54-98`
- **Effort:** Simple

### DUP-SIM-001: Ability `__init__` Pattern Duplication A
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-SIM-002: Repeated `sync_data` Pattern Across Prop
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-SIM-003: Repeated `recalculate` Pattern for Singl
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### DUP-SIM-004: `to_dict` / `from_dict` Serialization Pa
- **Severity:** Major
- **Location:** `game/simulation/battle_state.p`
- **Effort:** Medium

### DUP-STR-003: Duplicated Star Generation Logic
- **Severity:** Major
- **Location:** `game/strategy/data/stars.py:37`
- **Effort:** Medium

### DUP-STR-004: Ship Spawning Duplication in ProductionE
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Simple

### DUP-STR-005: Duplicated Complex Spawning Logic
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Simple

### DUP-SIM-008: WeaponAbility Formula Handling Pattern
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### DUP-STR-006: Resource Consumption Loop Pattern
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_resou`
- **Effort:** Simple

### DUP-STR-007: has_resources/consume Pattern in FleetRe
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_resou`
- **Effort:** Simple

### DUP-STR-010: Layer Iteration Pattern
- **Severity:** Minor
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Simple

### DUP-SIM-011: Consistent Use of Helper Class Pattern
- **Severity:** Info
- **Location:** `game/simulation/components/mod`
- **Effort:** N

### DUP-SIM-012: Well-Factored Combat Subsystems
- **Severity:** Info
- **Location:** `game/simulation/combat/targeti`
- **Effort:** N

### DUP-STR-011: Similar DTO from_X Factory Methods
- **Severity:** Info
- **Location:** `game/strategy/facade/dto/fleet`
- **Effort:** N

### DUP-STR-012: NavigationState Pattern
- **Severity:** Info
- **Location:** `game/strategy/services/fleet_n`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
