# [PROJ-XXX] Test Coverage - Strategy Engine

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Add comprehensive test coverage for critical Strategy layer components including fleet navigation, production, combat resolution, and save/load systems.

### Problem Statement
Several critical Strategy engine components have inadequate test coverage:
- FleetNavigationService core methods are tested only indirectly
- Command handlers have partial coverage (3/8 handlers tested)
- Superweapon processor lacks error path validation
- Production engine tick edge cases untested
- Save/load round-trip integrity not verified

### Goals
1. Achieve direct test coverage for all critical navigation and command methods
2. Add error path and edge case tests for destructive operations
3. Verify save/load round-trip data integrity
4. Cover multi-party conflict resolution scenarios

### Success Criteria
- All critical and major findings have corresponding test files
- Test coverage for Strategy layer increases by 10%+
- No regressions in existing tests
- Edge cases documented in test names/docstrings

---

## Design Decisions

### DD-001: Test Organization
**Decision:** Create dedicated test files per production file for gaps
**Rationale:** Matches existing test structure, easier to locate tests
**Alternatives considered:** Single "gaps" test file (rejected - grows unwieldy)

### DD-002: Integration vs Unit Tests
**Decision:** Mix of unit tests (isolated) and integration tests (multi-component)
**Rationale:** Some findings require testing component interactions
**Alternatives considered:** Pure unit tests only (rejected - miss integration bugs)

---

## Phases

### Phase 1: Critical Navigation and Commands
**Target:** TCG-STR-001, TCG-STR-003
**Scope:** Fleet navigation and superweapon validation
**Tests Required:** 15-20 new test methods

- [ ] Create test_fleet_navigation_service.py with direct method tests
- [ ] Add compute_next_step() tests for all order types
- [ ] Add path recalculation condition tests
- [ ] Add superweapon validation failure tests
- [ ] Add cooldown enforcement tests

### Phase 2: Production and Economy
**Target:** TCG-STR-004, TCG-STR-007, TCG-STR-014
**Scope:** Production engine and economy calculations
**Tests Required:** 12-15 new test methods

- [ ] Add multiple completions same tick test
- [ ] Add resource exhaustion mid-queue test
- [ ] Add queue empty mid-tick test
- [ ] Add fleet and colony production interaction test
- [ ] Add empire economy integration tests
- [ ] Add partial resupply tests

### Phase 3: Combat and Conflict
**Target:** TCG-STR-008, TCG-FND-003
**Scope:** Conflict resolution and collision
**Tests Required:** 8-10 new test methods

- [ ] Add three-empire conflict test
- [ ] Add battle with retreat test
- [ ] Add post-battle fleet cleanup test
- [ ] Add collision system integration tests

### Phase 4: Save/Load and Initialization
**Target:** TCG-STR-012, TCG-STR-011, TCG-STR-009
**Scope:** Save/load integrity and game initialization
**Tests Required:** 10-12 new test methods

- [ ] Add save/load round-trip with fleet targets
- [ ] Add save/load component damage state test
- [ ] Add five-player distribution test
- [ ] Add order queueing behavior tests

### Phase 5: Data Classes and Utilities
**Target:** Remaining findings
**Scope:** Ship stats, pathfinding, fleet operations
**Tests Required:** 15-20 new test methods

- [ ] Add ship stats calculator edge case tests
- [ ] Add fleet capability tests with galaxy interaction
- [ ] Add pathfinding performance and edge case tests
- [ ] Add fleet merge preservation tests
- [ ] Add remaining minor finding tests

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tests require complex fixtures | Medium | Create reusable test fixtures |
| Integration tests slow down suite | Low | Use pytest marks for slow tests |
| Insufficient understanding of edge cases | Medium | Review code before writing tests |

---

## Notes

- Consider using pytest-xdist for parallel test execution
- Some tests may require mocking external dependencies (registry, file system)
- Integration tests should use test databases/fixtures, not production data
