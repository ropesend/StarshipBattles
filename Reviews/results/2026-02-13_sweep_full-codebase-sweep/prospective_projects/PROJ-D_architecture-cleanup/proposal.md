# Project Proposal: Architecture Cleanup - Layer Violations and Coupling

## Summary

**Project ID:** PROJ-D (Prospective)
**Theme:** Architecture Drift - Layer Violations and Coupling
**Priority:** Medium
**Estimated Effort:** Medium
**Findings Count:** 24

## Problem Statement

The codebase has accumulated architectural drift in the form of:
- **Layer violations**: UI importing from simulation directly, strategy importing concrete types
- **Tight coupling**: Late imports to avoid circular dependencies
- **Pattern inconsistencies**: Mixed singleton and DI patterns

These issues make the codebase harder to maintain and test in isolation.

## Scope

### Layer Violation Categories

1. **Research UI Layer Violations**: Research UI imports Camera directly from game.ui
2. **AI Layer in Simulation**: Simulation factory imports AI controller
3. **Strategy-Simulation Coupling**: Strategy services import simulation types directly
4. **UI-Simulation Coupling**: UI panels import simulation layer types

### Coupling Issues

- Late imports to avoid circular dependencies
- Mixed DI and singleton patterns
- Inconsistent error return semantics

## Findings Included

| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| ADR-FND-001 | Critical | Research UI Layer Imports Concrete Camera | Medium |
| ADR-SIM-001 | Critical | AI Layer Imports in Simulation Factory | Medium |
| ADR-FND-002 | Major | protocols.py Approaching God Class | Medium |
| ADR-SIM-002 | Major | TYPE_CHECKING Import of AI Controller | Simple |
| ADR-STR-001 | Major | Simulation Layer Coupling via Direct Import | Medium |
| ADR-STR-002 | Major | Simulation Adapter Has Top-Level Imports | Simple |
| ADR-UI2-001 | Major | pygame.math.Vector2 Usage in game_renderer | Simple |
| CON-FND-001 | Critical | Inconsistent Singleton Pattern Usage | Medium |
| CON-UI2-001 | Critical | Inconsistent DI Pattern - Some Services | Medium |
| CON-FND-002 | Major | Inconsistent Logging Pattern | Medium |
| CON-FND-003 | Major | Mixed Return Semantics for Not-Found | Simple |
| CON-UI2-002 | Major | Singleton vs DI Pattern Conflict | Complex |
| PP-006 | Major | Direct Singleton Access in Some Files | Medium |
| ADR-FND-003 | Minor | behaviors.py File Growing Large | Simple |
| ADR-SIM-005 | Minor | Possible Circular Import Workaround | Simple |
| ADR-STR-004 | Minor | TYPE_CHECKING Block Indicates Coupling | Simple |
| ADR-STR-005 | Minor | Late Import Pattern Inconsistency | Simple |
| ADR-STR-006 | Minor | Circular Dependency Risk in fleet_battle | Simple |
| ADR-UI2-003 | Minor | Lazy Import in ship_factory | Simple |
| ADR-UI2-004 | Minor | TYPE_CHECKING for GameRegistries | Simple |
| ADR-SIM-006 | Info | Heavy Use of TYPE_CHECKING | N/A |
| ADR-STR-007 | Info | Well-Architected Adapter Pattern | N/A |
| ADR-UI2-005 | Info | BattleOrchestrator Documents Coupling | N/A |
| ADR-UI1-018 | Info | Large Method Counts (Monitoring) | N/A |

## Overlap Analysis

No direct overlap with existing projects. This project focuses on architectural boundaries rather than code cleanup.

## Success Criteria

1. Research UI does not import from game.ui directly
2. Simulation layer has no AI imports
3. Consistent DI pattern across all services
4. No late imports needed for circular dependency avoidance
5. Consistent return semantics documented and enforced

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking layer boundaries may require interface changes | Design interfaces carefully upfront |
| DI migration may require extensive changes | Phase rollout, starting with new services |
| Return semantics change may break callers | Add parallel methods first, then migrate |

## Recommended Phases

### Phase 1: Layer Boundary Analysis (Days 1-2)
- Map all cross-layer imports
- Identify legitimate adapter patterns
- Design interface solutions for violations

### Phase 2: Research Layer Fix (Days 3-4)
- Create Camera protocol/interface
- Move research UI to proper layer location
- Remove direct pygame imports from research

### Phase 3: Simulation Layer Fix (Days 5-6)
- Remove AI imports from simulation factory
- Create AIProvider interface if needed
- Use dependency injection for AI needs

### Phase 4: Pattern Consolidation (Days 7-9)
- Choose singleton vs DI pattern
- Migrate remaining singletons to DI
- Document chosen pattern in CLAUDE.md

### Phase 5: Return Semantics (Days 10-11)
- Document return semantics convention
- Add parallel `_required` methods where needed
- Migrate callers to consistent pattern

## Dependencies

- Should run after PROJ-B (Legacy Eradication) to avoid working on deprecated code
- May benefit from PROJ-C (God Class Decomposition) running first
