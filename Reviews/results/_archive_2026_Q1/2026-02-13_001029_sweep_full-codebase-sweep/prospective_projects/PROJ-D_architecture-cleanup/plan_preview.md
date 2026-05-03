# PROJ-D: Architecture Cleanup - Layer Violations and Coupling

## Project Overview

**Goal:** Fix layer violations, standardize patterns (singleton vs DI), and establish consistent conventions.

**Context:** The codebase has accumulated architectural drift including layer violations, mixed patterns, and inconsistent conventions.

## Current State

- Research UI imports Camera from game.ui
- Simulation factory imports AI controller
- Mixed SingletonMeta and module-level globals
- Mixed logging patterns (custom Logger vs getLogger)
- Inconsistent return semantics (raise vs return default)

## Target State

- Clean layer boundaries with adapters/protocols
- Consistent DI pattern throughout
- Single logging pattern
- Documented return semantics convention

## Phases

### Phase 1: Layer Boundary Analysis
**Estimated Duration:** 2 days

#### 1.1 Map Cross-Layer Imports
- [ ] Document all imports from higher to lower layers
- [ ] Identify legitimate adapter patterns
- [ ] Identify violations requiring interfaces

#### 1.2 Design Interface Solutions
- [ ] Design Camera protocol for research layer
- [ ] Design AI provider interface for simulation
- [ ] Document adapter pattern usage

### Phase 2: Research Layer Fix
**Estimated Duration:** 2 days

#### 2.1 Camera Protocol
- [ ] Create `ICameraProtocol` in core or research layer
- [ ] Define required camera methods
- [ ] Update research_scene to use protocol

#### 2.2 Layer Relocation
- [ ] Evaluate if research UI belongs in game/ui
- [ ] If yes, move and update imports
- [ ] If no, ensure clean protocol boundary

### Phase 3: Simulation Layer Fix
**Estimated Duration:** 2 days

#### 3.1 AI Import Removal
- [ ] Analyze ai_factory usage
- [ ] Create AIProvider interface
- [ ] Inject AI dependencies rather than importing

#### 3.2 TYPE_CHECKING Cleanup
- [ ] Review TYPE_CHECKING imports for necessity
- [ ] Replace with protocols where appropriate
- [ ] Document legitimate forward references

### Phase 4: Pattern Consolidation
**Estimated Duration:** 3 days

#### 4.1 Singleton vs DI Decision
- [ ] Document decision: prefer DI
- [ ] Identify all singletons
- [ ] Create migration plan

#### 4.2 Singleton Migration
- [ ] Convert Logger to DI-friendly
- [ ] Convert ScreenshotManager to DI
- [ ] Convert vehicle_class_service to DI
- [ ] Document remaining intentional singletons

#### 4.3 Logging Pattern
- [ ] Choose: custom Logger or standard getLogger
- [ ] Migrate inconsistent usages
- [ ] Update CLAUDE.md with convention

### Phase 5: Return Semantics
**Estimated Duration:** 2 days

#### 5.1 Document Convention
- [ ] Define convention: Optional return vs raise
- [ ] Add to CLAUDE.md or project conventions
- [ ] Create `_required` method pattern

#### 5.2 Apply Convention
- [ ] Audit existing getters
- [ ] Add parallel methods where needed
- [ ] Update callers to match convention

## Validation

### During Development
- Run `pytest tests/ --testmon` after changes
- Verify no import cycles: `python -c "import game"`
- Check layer boundaries maintained

### Completion Criteria
- [ ] All Critical findings resolved (4/4)
- [ ] All Major findings resolved (9/9)
- [ ] No layer violations remain
- [ ] Consistent DI pattern
- [ ] Documented conventions
- [ ] Full test suite passes

## Notes

- INFO-level findings are documentation/monitoring only
- Prioritize Critical and Major findings
- Document architectural decisions in project docs
