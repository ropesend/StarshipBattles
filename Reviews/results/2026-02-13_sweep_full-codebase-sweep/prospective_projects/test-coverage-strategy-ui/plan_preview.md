# Project Plan: Test Coverage - Strategy and UI

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Test Coverage - Strategy and UI
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 52 test coverage findings from the Strategy, UI-Screens, and UI-Framework layers. The primary goals are:

1. Add unit tests for uncovered strategy data modules
2. Add unit tests for UI panels and screens
3. Fix test quality issues (bypass-init, over-mocking)
4. Add critical integration tests for user flows

## Phases

### Phase 1: Critical Strategy Gaps

**Objective:** Add tests for critical strategy data modules.

**Tasks:**
- [ ] Add naming.py unit tests (TCG-STR-001)
- [ ] Add physics.py unit tests (TCG-STR-002)
- [ ] Add commands.py unit tests (TCG-STR-003)

**Estimated Effort:** 2-3 days

### Phase 2: Critical UI Gaps

**Objective:** Add tests for critical UI components.

**Tasks:**
- [ ] Add BattleStateViewer tests (TCG-UI1-001)
- [ ] Add TestLabValidationManager tests (TCG-UI1-002)
- [ ] Add UIConfig tests (TCG-UI2-001)

**Estimated Effort:** 3-4 days

### Phase 3: Strategy Engine Tests

**Objective:** Complete strategy engine test coverage.

**Tasks:**
- [ ] Add TurnEngine colonize validation tests (TCG-STR-004)
- [ ] Add FleetOrder serialization tests (TCG-STR-005)
- [ ] Add QuickstartBuilder tests (TCG-STR-006)
- [ ] Add StrategySessionFacade tests (TCG-STR-007)
- [ ] Add GameInitializer tests (TCG-STR-008)
- [ ] Add ShipStatsCalculator tests (TCG-STR-009)

**Estimated Effort:** 3-4 days

### Phase 4: UI Panel Tests

**Objective:** Add unit tests for UI panels.

**Tasks:**
- [ ] Add PlanetReportPanel tests (TCG-UI1-007)
- [ ] Add ShipDetailPanel tests (TCG-UI1-008)
- [ ] Add BaseGallery tests (TCG-UI1-009)
- [ ] Add DesignReportPanel tests (TCG-UI1-010)
- [ ] Add race panel tests (TCG-UI1-016)

**Estimated Effort:** 3-4 days

### Phase 5: Screen Module Tests

**Objective:** Add tests for UI screen modules.

**Tasks:**
- [ ] Add BuilderScreen tests (TCG-UI1-005)
- [ ] Add FormationEditor tests (TCG-UI1-006)
- [ ] Add builder submodule tests (TCG-UI1-011)
- [ ] Add test_lab submodule tests (TCG-UI1-012)
- [ ] Add formation submodule tests (TCG-UI1-014)
- [ ] Add workshop helper tests (TCG-UI1-015)

**Estimated Effort:** 4-5 days

### Phase 6: Test Quality and Integration

**Objective:** Fix test quality issues and add integration tests.

**Tasks:**
- [ ] Fix StrategyRenderer tests to test behavior (TCG-UI1-017)
- [ ] Fix DesignStatsPanel bypass-init pattern (TCG-UI1-018)
- [ ] Fix mock verification issues (TCG-UI1-022, TCG-UI1-023)
- [ ] Add battle UI flow integration test (TCG-UI1-026)
- [ ] Add strategy + build queue integration test (TCG-UI1-027)
- [ ] Add workshop + ship I/O roundtrip test (TCG-UI1-028)

**Estimated Effort:** 3-4 days

## Success Criteria

1. All CRITICAL test coverage gaps resolved
2. All MAJOR test coverage gaps resolved
3. Strategy data modules have comprehensive tests
4. All major UI panels have unit tests
5. At least 3 integration tests for user flows
6. Test baseline increases by 300+ tests

## Dependencies

- None (self-contained)

## Risks

- Complex UI screens may require significant test fixtures
- Integration tests may be time-consuming to set up
- Some tests may require refactoring for testability
