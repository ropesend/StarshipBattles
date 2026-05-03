# Plan: Architecture Layer Violations

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Fix architecture layer violations and document god class refactoring paths.

## Current State

- Strategy layer imports from AI layer (violates documented architecture)
- Multiple god classes exceed 1000 lines
- Several circular import workarounds exist
- Presentation logic has leaked into strategy layer

## Target State

- Layer dependencies follow documented architecture
- God classes have refactoring plans documented
- Circular import workarounds are documented with ADRs
- Critical layer violation (Strategy->AI) is fixed

## Phases

### Phase 1: Fix Critical Layer Violation
**Files to modify:**
- `game/strategy/adapters/simulation_adapter.py`

**Changes:**
- Remove direct import of AIControllerFactory
- Accept AIControllerFactory as parameter to SimulationBattleResolver
- Update BattleController to inject AI factory

### Phase 2: Document God Classes
**Files to analyze:**
- `game/ui/screens/test_lab/screen.py` (1906 lines)
- `game/ui/screens/fleet_report_window.py` (1093 lines)
- `game/ui/screens/build_queue_screen.py` (1084 lines)
- `game/ui/screens/builder/weapons_panel.py` (1037 lines)

**Deliverable:**
- Architecture Decision Record documenting:
  - Why each class is large
  - Proposed decomposition strategy
  - Priority for refactoring

### Phase 3: Fix Research UI Layer Violation
**Files to modify:**
- `game/research/ui/research_scene.py`

**Changes:**
- Use protocol instead of direct camera import
- Or move to proper UI layer

### Phase 4: Document Circular Import Patterns
**Files to document:**
- `game/strategy/data/galaxy.py` (late import)
- `game/strategy/data/ship_display_formatter.py` (presentation in strategy)
- Various files with "INTENTIONAL LATE IMPORT" comments

**Deliverable:**
- ADR documenting intentional late import patterns
- Recommendation for future restructuring

### Phase 5: Minor Cleanup
**Files to fix:**
- `game/ui/services/ship_io.py` (direct simulation import)
- `game/ui/renderer/camera.py` (pygame.math usage)
- Various near-god classes (add TODO comments)

## Checklist

### Phase 1: Critical Fix
- [ ] Modify SimulationBattleResolver to accept AI factory
- [ ] Update all callers to provide AI factory
- [ ] Remove direct AIControllerFactory import
- [ ] Update tests
- [ ] Verify layer diagram compliance

### Phase 2: God Class Documentation
- [ ] Analyze TestLabScreen responsibilities
- [ ] Analyze fleet_report_window responsibilities
- [ ] Analyze build_queue_screen responsibilities
- [ ] Analyze weapons_panel responsibilities
- [ ] Create ADR with decomposition strategies
- [ ] Add inline TODO comments with ADR reference

### Phase 3: Research UI
- [ ] Define camera protocol in core
- [ ] Update research_scene to use protocol
- [ ] Verify no pygame imports in research/

### Phase 4: Late Import ADR
- [ ] Inventory all late import locations
- [ ] Document rationale for each
- [ ] Create ADR with pattern guidelines
- [ ] Update ARCHITECTURE.md if needed

### Phase 5: Minor Cleanup
- [ ] Fix ship_io.py imports
- [ ] Document camera pygame usage
- [ ] Add TODO comments to near-god classes

## Dependencies

- None - can run independently

## Risks

- God class refactoring may be deferred to future projects
- Some layer violations may be intentional and documented
