# PROJ-11: Architecture Layer Separation

## Overview
**Status:** Planning
**Created:** 2026-01-24
**Source:** Review 2026-01-24_general_full-codebase-maintainability

This project addresses the critical layered architecture violations identified in the code review. The goal is to establish clean boundaries between Simulation, Strategy, and UI layers.

## Goals
1. Remove pygame dependency from simulation layer
2. Remove UI imports from strategy layer
3. Remove bidirectional dependencies between simulation and strategy
4. Establish clear interface contracts between layers
5. Enable headless execution of simulation and strategy layers

## Scope

### In Scope
- AR-001: Simulation imports pygame
- AR-002: Strategy imports UI components (has_warp_capability)
- AR-005: Pygame in persistence layer
- AR-006: Bidirectional simulation-strategy dependency
- AR-007: Circular import workarounds
- STRAT-002: UI layer coupling in Fleet
- STRAT-004: Cross-layer coupling to simulation
- UI-001: Direct simulation coupling (partial - interface definition)

### Out of Scope
- God class decomposition (PROJ-12)
- UI architectural patterns (PROJ-13)
- Error handling (PROJ-10)

## Success Criteria
- [ ] Simulation layer has zero pygame imports
- [ ] Strategy layer has zero UI layer imports
- [ ] No circular import workarounds needed
- [ ] Simulation can run in headless mode (no display)
- [ ] Strategy can run without UI (for testing/server use)
- [ ] All tests pass after changes

## Phases

### Phase 1: Core Math Abstraction
Create `game/core/math.py` with Vector2 class to replace pygame.math.Vector2.

### Phase 2: Simulation Layer Cleanup
Remove pygame imports from all simulation files.

### Phase 3: Strategy-UI Separation
Move has_warp_capability and similar functions to strategy services.

### Phase 4: Interface Contracts
Define explicit interfaces between layers.

## Dependencies
- Should complete PROJ-10 first (error handling will help debug any issues)

## Risks
- **Medium:** Vector2 replacement may have subtle behavioral differences
- **Mitigation:** Comprehensive testing of physics and collision
- **Medium:** Breaking changes to save file format
- **Mitigation:** Migration path for existing saves

## Related Documents
- [Design Document](design.md)
- [Decisions Log](decisions.md)
- [Phase 1 Checklist](phase_1_checklist.md)
- [Phase 2 Checklist](phase_2_checklist.md)
- [Phase 3 Checklist](phase_3_checklist.md)
- [Phase 4 Checklist](phase_4_checklist.md)
- [Source Review - Architecture](../../Reviews/results/2026-01-24_general_full-codebase-maintainability/findings/architecture_report.md)
- [Source Review - Strategy](../../Reviews/results/2026-01-24_general_full-codebase-maintainability/findings/strategy_specialist_report.md)
