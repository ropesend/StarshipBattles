# PROJ-146: Design Document

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
- **Major:** 9
- **Selected for remediation:** 35

## Selected Findings Summary

### ADR-SIM-001: Simulation Depends on game.engine (Physi
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### ADR-SIM-002: Simulation Depends on game.engine (Spati
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Medium

### ADR-SIM-003: Circular Import Risk - Ship and Modifier
- **Severity:** Major
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Medium

### ADR-STR-001: Strategy Layer Imports AI Layer (Permitt
- **Severity:** Major
- **Location:** `game/strategy/adapters/simulat`
- **Effort:** Simple

### ADR-STR-002: Galaxy Class Approaching God Class Terri
- **Severity:** Major
- **Location:** `game/strategy/data/galaxy.py:1`
- **Effort:** Complex

### ADR-UI2-001: ShipFactory uses pygame.math.Vector2 in
- **Severity:** Major
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### ADR-UI2-003: Camera class uses pygame.math.Vector2 in
- **Severity:** Major
- **Location:** `game/ui/renderer/camera.py:14,`
- **Effort:** Medium

### CON-STR-004: Inconsistent Constructor DI Pattern Appl
- **Severity:** Major
- **Location:** `game/strategy/engine/`
- **Effort:** Medium

### CON-STR-005: Mixed Static Methods and Instance Method
- **Severity:** Major
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### ADR-SIM-004: Circular Import Risk - ShipSerializer an
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### ADR-SIM-005: God Class Indicator - Ship Class (810 LO
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Complex

### ADR-SIM-006: God Class Indicator - Component Class (7
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Medium

### ADR-STR-003: Production Engine Approaching 500+ LOC
- **Severity:** Minor
- **Location:** `game/strategy/engine/productio`
- **Effort:** Medium

### ADR-STR-004: FleetOrderProcessor Approaching 500+ LOC
- **Severity:** Minor
- **Location:** `game/strategy/engine/fleet_ord`
- **Effort:** Medium

### ADR-UI2-006: Inconsistent use of Any type hints maski
- **Severity:** Minor
- **Location:** `game/ui/services/validation_se`
- **Effort:** Medium

### CON-FND-009: Inconsistent Use of `clear()` vs `reset(
- **Severity:** Minor
- **Location:** `game/core/registry.py:217-237`
- **Effort:** Simple

### CON-FND-011: Incomplete `__all__` Exports
- **Severity:** Minor
- **Location:** `game/core/constants.py:3-15`
- **Effort:** Simple

### CON-FND-013: Error Code Enum Incomplete Coverage
- **Severity:** Minor
- **Location:** `game/core/error_codes.py:52-15`
- **Effort:** Simple

### CON-SIM-009: Magic Numbers in Physics Calculations
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### CON-SIM-012: Component Type Checking via String vs is
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### ADR-FND-004: Core Layer Properly Isolates Strategy an
- **Severity:** Info
- **Location:** `game/core/constants.py:84`
- **Effort:** N

### ADR-SIM-007: TYPE_CHECKING Used Extensively for Layer
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### ADR-STR-005: Cross-Layer Imports via TYPE_CHECKING (G
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### ADR-UI2-007: DesignLoaderAdapter directly imports Sim
- **Severity:** Info
- **Location:** `game/ui/services/design_loader`
- **Effort:** Medium

### ADR-UI2-008: Screenshot manager uses hardcoded strate
- **Severity:** Info
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Complex

### CON-SIM-018: Singleton Pattern Usage
- **Severity:** Info
- **Location:** `game/simulation/components/com`
- **Effort:** Complex

### CON-SIM-019: Ability Registry as Module-Level Dict
- **Severity:** Info
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### CON-SIM-020: Late Import Comments
- **Severity:** Info
- **Location:** `game/simulation/entities/ship_`
- **Effort:** N

### CON-STR-014: Natural Variation in Method Signatures
- **Severity:** Info
- **Location:** `game/strategy/engine/`
- **Effort:** None

### CON-STR-015: Facade vs Direct Access Pattern Variatio
- **Severity:** Info
- **Location:** `game/strategy/facade/strategy_`
- **Effort:** None

### CON-STR-016: Delegate Pattern Consistency
- **Severity:** Info
- **Location:** `game/strategy/data/fleet.py`
- **Effort:** Simple

### CON-STR-017: Event System Consistency
- **Severity:** Info
- **Location:** `game/strategy/events/event_typ`
- **Effort:** None

### CON-STR-018: Interface Naming Convention
- **Severity:** Info
- **Location:** `game/strategy/interfaces/`
- **Effort:** None

### DUP-FND-008: Singleton Pattern Consistency
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### DUP-FND-009: Combat Utils Consolidation Success
- **Severity:** Info
- **Location:** `game/ai/combat_utils.py`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
