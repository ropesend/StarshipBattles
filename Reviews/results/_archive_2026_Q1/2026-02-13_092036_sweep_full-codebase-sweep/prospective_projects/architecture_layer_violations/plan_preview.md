# [PROJ-XXX] Architecture Layer Violations

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Fix critical and major architecture violations where lower layers incorrectly depend on higher layers, and decompose god classes that have grown beyond maintainable sizes.

### Problem Statement
The codebase has accumulated layer violations and god classes that undermine the architecture's maintainability:
- Simulation layer imports AI layer (should be reversed)
- Research module imports from UI layer (should use protocols)
- Multiple classes exceed 500-800 lines with too many responsibilities

### Goals
1. Restore proper layer dependency direction (Core <- Simulation <- Strategy/AI <- UI)
2. Use protocols and dependency injection instead of direct imports across layers
3. Decompose god classes into focused, single-responsibility components

### Success Criteria
- No simulation -> AI imports (verify via static analysis)
- No lower layer -> higher layer imports (except through protocols)
- No classes exceeding 600 lines
- All existing tests pass
- Code coverage maintained or improved

---

## Design Decisions

### DD-001: Layer Violation Fix Strategy
**Decision:** Use protocols and dependency injection, not facade layers
**Rationale:** Protocols allow type-safe cross-layer communication without runtime coupling
**Alternatives considered:** Facade pattern (rejected - adds complexity)

### DD-002: God Class Decomposition Approach
**Decision:** Extract to helper classes, not inheritance
**Rationale:** Composition is more flexible and avoids inheritance hierarchies
**Alternatives considered:** Mixin classes (rejected - harder to test)

---

## Phases

### Phase 1: Critical Layer Violations
**Target:** ADR-FND-001, ADR-SIM-001
**Scope:** Fix the two critical layer violations
**Tests Required:** Integration tests for DI patterns

- [ ] ADR-FND-001: Extract ICamera protocol usage in ResearchScene
- [ ] ADR-SIM-001: Move battle factory functions to game/engine layer
- [ ] Verify no simulation -> AI runtime imports

### Phase 2: Simulation/Strategy Layer Fixes
**Target:** ADR-SIM-002, ADR-STR-005, ADR-UI2-001
**Scope:** Fix TYPE_CHECKING and cross-layer imports
**Tests Required:** Existing tests should pass

- [ ] ADR-SIM-002: Use IAIController protocol instead of AIController concrete type
- [ ] ADR-STR-005: Abstract ship stats interface for strategy layer
- [ ] ADR-UI2-001: Fix ship_io.py simulation layer import

### Phase 3: God Class Decomposition - Core
**Target:** ADR-SIM-003, ADR-SIM-004, ADR-STR-001, ADR-STR-002
**Scope:** Decompose the largest god classes
**Tests Required:** Unit tests for extracted classes

- [ ] ADR-SIM-003: Continue Ship decomposition (target: <600 lines)
- [ ] ADR-SIM-004: Extract BattleController state management
- [ ] ADR-STR-001: Decompose Galaxy class
- [ ] ADR-STR-002: Decompose ProductionEngine

### Phase 4: UI God Classes
**Target:** ADR-UI1-001 through ADR-UI1-007
**Scope:** Decompose UI god classes and fix encapsulation
**Tests Required:** UI component tests

- [ ] ADR-UI1-001: Decompose TestLabScreen
- [ ] ADR-UI1-002: Decompose FleetReportWindow
- [ ] ADR-UI1-003, ADR-UI1-004: Decompose queue and strategy screens
- [ ] Fix private access violations (multiple findings)

### Phase 5: Protocol and Interface Cleanup
**Target:** ADR-FND-002, ADR-FND-003, circular deps
**Scope:** Split large interfaces and protocols
**Tests Required:** Protocol compliance tests

- [ ] ADR-FND-002: Split IControllable into role-specific interfaces
- [ ] ADR-FND-003: Split protocols.py into domain modules
- [ ] Address circular dependency workarounds

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing functionality | High | Run full test suite after each phase |
| Merge conflicts with parallel work | Medium | Coordinate with other active projects |
| Test coverage gaps in decomposed code | Medium | Add unit tests for extracted classes |

---

## Notes

- This project overlaps with PROJ-126 (architecture-layer-fixes) and PROJ-123 (architecture-cleanup)
- Consider merging with or superseding those projects
- God class decomposition should follow existing patterns (e.g., Ship -> ShipCombatEngine)
