# PROJ-123: Design Document

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
- **Critical:** 4
- **Major:** 9
- **Selected for remediation:** 24

## Selected Findings Summary

### ADR-FND-001: Research UI Layer Imports Concrete Camer
- **Severity:** Critical
- **Location:** `game/research/ui/research_scen`
- **Effort:** Medium

### ADR-SIM-001: AI Layer Imports in Simulation Factory
- **Severity:** Critical
- **Location:** `game/simulation/factories/ai_f`
- **Effort:** Medium

### CON-FND-001: Inconsistent Singleton Pattern Usage - S
- **Severity:** Critical
- **Location:** `game/core/registry.py:79-120`
- **Effort:** Medium

### CON-UI2-001: Inconsistent DI Pattern - Some Services
- **Severity:** Critical
- **Location:** `game/ui/services/vehicle_class`
- **Effort:** Medium

### ADR-FND-002: protocols.py is Approaching God Class Te
- **Severity:** Major
- **Location:** `game/core/protocols.py`
- **Effort:** Medium

### ADR-SIM-002: TYPE_CHECKING Import of AI Controller
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### ADR-STR-001: Simulation Layer Coupling via Direct Imp
- **Severity:** Major
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### ADR-STR-002: Simulation Adapter Has Top-Level Simulat
- **Severity:** Major
- **Location:** `game/strategy/adapters/simulat`
- **Effort:** Simple

### ADR-UI2-001: pygame.math.Vector2 Usage in game_render
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-FND-002: Inconsistent Logging Pattern - Logger Si
- **Severity:** Major
- **Location:** `game/core/logger.py`
- **Effort:** Medium

### CON-FND-003: Mixed Return Semantics for Not-Found Cas
- **Severity:** Major
- **Location:** `game/core/registry.py:98-120`
- **Effort:** Simple

### CON-UI2-002: Singleton vs Dependency Injection Patter
- **Severity:** Major
- **Location:** `game/ui/services/screenshot_ma`
- **Effort:** Complex

### PP-006: Direct Singleton Access in Some Files
- **Severity:** Major
- **Location:** `game/ui/screens/race_setup_scr`
- **Effort:** Medium

### ADR-FND-003: behaviors.py File Growing Large
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py`
- **Effort:** Simple

### ADR-SIM-005: Possible Circular Import Workaround
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### ADR-STR-004: TYPE_CHECKING Block Indicates Tight Coup
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_battl`
- **Effort:** Simple

### ADR-STR-005: Late Import Pattern Inconsistency
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Simple

### ADR-STR-006: Potential Circular Dependency Risk in Fl
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_battl`
- **Effort:** Simple

### ADR-UI2-003: Lazy Import Pattern in ship_factory.py C
- **Severity:** Minor
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### ADR-UI2-004: TYPE_CHECKING Import for GameRegistries
- **Severity:** Minor
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### ADR-SIM-006: Heavy Use of TYPE_CHECKING for Forward R
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### ADR-STR-007: Well-Architected Adapter Pattern in Plac
- **Severity:** Info
- **Location:** `game/strategy/adapters/simulat`
- **Effort:** N

### ADR-UI2-005: BattleOrchestrator Correctly Documents C
- **Severity:** Info
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** N

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
