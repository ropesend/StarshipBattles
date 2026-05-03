# Prospective Projects Summary

## Sweep Source
- **Review:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Total Findings:** 221 (7 Critical, 70 Major, 99 Minor, 45 Info)
- **Findings Assigned to Projects:** 182 / 221
- **Unassigned Findings:** 39 (see coverage analysis below)

## Proposed Projects

| # | Project | Findings | Critical | Major | Minor | Info | Scope | Execution Order |
|---|---------|----------|----------|-------|-------|------|-------|-----------------|
| 1 | Architecture Layer Violations | 24 | 2 | 15 | 7 | 0 | Large | 1st - Foundation |
| 2 | Test Coverage - Strategy Engine | 20 | 2 | 13 | 5 | 0 | Medium | 2nd |
| 3 | Test Coverage - UI Components | 34 | 2 | 12 | 12 | 8 | Large | 3rd |
| 4 | UI Pattern Consolidation | 19 | 1 | 9 | 7 | 2 | Medium | 4th |
| 5 | Legacy Code Cleanup | 33 | 0 | 10 | 16 | 7 | Medium-Large | 5th |
| 6 | Consistency Standardization | 52 | 0 | 16 | 24 | 12 | Medium-Large | 6th (parallel) |

**Totals:** 182 findings assigned across 6 projects

## Execution Order Recommendation

1. **Architecture Layer Violations** (First)
   - Establishes clean layer boundaries that all other work depends on
   - Fixes critical simulation -> AI imports and research -> UI imports
   - Decomposes god classes for better testability
   - Rationale: Clean architecture enables easier testing and refactoring

2. **Test Coverage - Strategy Engine** (Second)
   - Adds safety net for critical game mechanics
   - Covers fleet navigation, production, save/load - core systems
   - Benefits from stable architecture from project 1
   - Rationale: Strategy layer tests validate game logic correctness

3. **Test Coverage - UI Components** (Third)
   - Covers completely untested modules (Builder, Galaxy Test)
   - Benefits from stable lower layers and strategy tests
   - Large scope but modular - can be phased
   - Rationale: UI tests validate user experience

4. **UI Pattern Consolidation** (Fourth)
   - Refactoring work that benefits from comprehensive test coverage
   - Extracts reusable components from duplicated patterns
   - Improves maintainability for future UI work
   - Rationale: Safe refactoring requires tests

5. **Legacy Code Cleanup** (Fifth)
   - Removes dead code, completes migrations, removes defensive patterns
   - Benefits from test coverage to validate deletions are safe
   - Reduces confusion and maintenance burden
   - Rationale: Cleanup is safest after tests exist

6. **Consistency Standardization** (Sixth, or parallel)
   - Lower priority polish work
   - Can be done incrementally alongside other projects
   - Improves readability and reduces cognitive load
   - Rationale: Style improvements don't block other work

## Coverage Analysis

**Findings covered:** 182/221 (82.4%)

### Intentionally Excluded Findings (39 findings)

#### UNK (Unknown) Findings - 9 findings
These findings have Unknown location/effort and represent observations rather than actionable issues:
- UNK-01 through UNK-08: Pattern observations, intentional designs, or informational notes
- Should be reviewed and either filed properly or closed as "not an issue"

#### Duplicate Strategy Findings Already in UI Pattern Consolidation - 6 findings
These were counted in the Consistency project but overlap with DUP findings:
- DUP-STR-006, DUP-STR-007, DUP-STR-008: Minor Strategy duplication (already in UI Pattern Consolidation scope)

#### Positive/Informational Findings - 5 findings
These are positive observations, not issues to fix:
- TCG-STR-021, TCG-STR-022: Good coverage examples (informational)
- CON-UI1-014, CON-UI1-015, CON-UI1-016: Good practices (informational)
- DUP-UI1-009: Already consolidated (informational)

#### Test Quality Findings - 7 findings
These relate to test quality rather than production code:
- TCG-FND-013: Test organization
- TCG-FND-014: Visual test recommendations
- TCG-UI1-023, TCG-UI1-024: Test organization/integration gaps
- Already included in Test Coverage - UI project

#### Architectural Info-Level Findings - 6 findings
Low-priority observations that don't require action:
- ADR-FND-004, ADR-SIM-006: Layer documentation (Info)
- ADR-UI1-013, ADR-UI1-014: TYPE_CHECKING usage (N effort)
- ADR-UI2-002: TYPE_CHECKING in services (Info)

#### Remaining Minor/Info Findings - 6 findings
Very low priority items:
- DUP-FND-005: Serialization pattern (N effort - intentional)
- DUP-FND-008: Already imported utility (Info)
- TCG-FND-008, TCG-FND-009, TCG-FND-011, TCG-FND-012: Minor test gaps

## Overlap Notes

### Significant Overlaps with Existing Projects

| Proposed Project | Existing Project(s) | Recommendation |
|------------------|---------------------|----------------|
| Architecture Layer Violations | PROJ-126, PROJ-123 | **Supersede** - these existing projects should be reviewed and merged or closed |
| Test Coverage - Strategy Engine | PROJ-131, PROJ-130, PROJ-119, PROJ-118 | **Coordinate** - align scope with existing projects |
| Test Coverage - UI Components | PROJ-131, PROJ-124, PROJ-105 | **Coordinate** - especially with visual regression testing |
| UI Pattern Consolidation | PROJ-127 | **Supersede** - this existing project should be merged |
| Legacy Code Cleanup | PROJ-129, PROJ-121, PROJ-58 | **Supersede** - these existing projects should be merged |
| Consistency Standardization | PROJ-128, PROJ-125 | **Supersede** - these existing projects should be merged |

### Recommended Actions for Existing Projects

1. **Close as superseded:** PROJ-126, PROJ-127, PROJ-128, PROJ-129, PROJ-125
2. **Review and coordinate:** PROJ-131, PROJ-130, PROJ-119, PROJ-118, PROJ-124
3. **Consider merging:** PROJ-121 (legacy), PROJ-58 (backward compatibility)
4. **Keep separate:** PROJ-105 (visual regression testing - different approach)
5. **Review status:** PROJ-123 (architecture cleanup) - may overlap with Phase 3-4 of Architecture project

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Projects Proposed | 6 |
| Total Findings Covered | 182 |
| Coverage Percentage | 82.4% |
| Critical Findings Covered | 7/7 (100%) |
| Major Findings Covered | 60/70 (85.7%) |
| Estimated Total Effort | 12-16 weeks (sequential) |
| Recommended Parallelism | Projects 5 & 6 can run parallel after Project 4 |

---

*Generated: 2026-02-13*
*Source Sweep: 2026-02-13_092036_sweep_full-codebase-sweep*
