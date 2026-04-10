# PROJ-239: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-04-05_110710_general_strategy-layer-health](../../Reviews/results/2026-04-05_110710_general_strategy-layer-health/)
- **Type:** General Review
- **Date:** 2026-04-05
- **Report:** [View Full Report](../../Reviews/results/2026-04-05_110710_general_strategy-layer-health/report.md)

## Initial Analysis
Findings from review - 77 total findings identified.
- **Critical:** 2
- **Major:** 12
- **Selected for remediation:** 14

## Selected Findings Summary

### AR-001: AI Layer Import in Strategy Adapter (Lat
- **Severity:** Critical
- **Location:** `game/strategy/adapters/simulat`
- **Effort:** Medium

### ERR-001: No error handling around turn tick proce
- **Severity:** Critical
- **Location:** `game/strategy/engine/turn_engi`
- **Effort:** Medium

### AR-002: Widespread Facade Bypass -- UI Accesses
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Complex

### AR-003: data/ Subpackage Depends on engine/ (Upw
- **Severity:** Major
- **Location:** `game/strategy/data/build_queue`
- **Effort:** Simple

### AR-004: services/ Subpackage Depends on engine/
- **Severity:** Major
- **Location:** `game/strategy/services/cargo_t`
- **Effort:** Medium

### AR-005: 8 of 12 Sub-Engines Do Not Implement The
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Simple

### CQ-003: Duplicate Stabilizer Check Pattern in Su
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### CQ-004: Mock Object Hack in FleetNavigationServi
- **Severity:** Major
- **Location:** `game/strategy/services/fleet_n`
- **Effort:** Medium

### DC-003: Dead methods in planet_energy_engine.py
- **Severity:** Major
- **Location:** `game/strategy/engine/planet_en`
- **Effort:** Simple

### DC-004: Dead methods in AstrophysicsLoader (3 me
- **Severity:** Major
- **Location:** `game/strategy/generation/loade`
- **Effort:** Simple

### DC-005: Dead methods: Empire.remove_colony, Game
- **Severity:** Major
- **Location:** `game/strategy/data/empire.py:5`
- **Effort:** Simple

### DOCC-001: Orders system doc still uses FleetOrder
- **Severity:** Major
- **Location:** `docs/systems/orders_system.md`
- **Effort:** Simple

### DOCC-002: Orders system doc missing ACTIVATE_ABILI
- **Severity:** Major
- **Location:** `docs/systems/orders_system.md`
- **Effort:** Simple

### DOCC-003: Turn engine has undocumented post-loop p
- **Severity:** Major
- **Location:** `game/strategy/engine/turn_engi`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
