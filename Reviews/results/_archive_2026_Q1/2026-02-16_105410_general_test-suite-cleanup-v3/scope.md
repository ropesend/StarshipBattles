# Review Scope: Test Suite Cleanup v3

## Metadata
- **Date:** 2026-02-16 10:54
- **Type:** General Review
- **Description:** test-suite-cleanup-v3 (third attempt - previous two failed due to context/agent issues)

## Scope Definition

### Target
Full test suite: `tests/` directory (~949 files, ~235K lines)
Focus: `tests/unit/` (640 files, 197K lines) + `tests/integration/` (90 files, 24K lines)

### Priorities
Find unnecessary, broken, redundant, or obsolete tests that are candidates for removal or significant modification.

### Categories of Problem Tests
1. **Dead code tests** - Testing classes/methods/modules that no longer exist
2. **Duplicate tests** - Same behavior tested in multiple places
3. **Over-mocked tests** - So heavily mocked they validate nothing real
4. **Trivially obvious tests** - Testing Python builtins or trivial getters/setters
5. **Abandoned regression tests** - For fixed bugs now covered by proper unit tests
6. **Obsolete integration tests** - Testing old workflows that changed
7. **Skipped/xfail tests** - Abandoned and never revisited
8. **Scaffold/repro tests** - Never meant to be permanent

### Exclusions
- `tests/simulation_tests/` (separate simulation test framework)
- `__pycache__` directories
- `__init__.py` files

## Agent Configuration
**Confirmed Agent Count:** 8
**Agent Type:** general-purpose (can write files)
**Batch Strategy:** 2 batches of 4

### Selected Agents
| Agent | Territory | Files | Lines | Status |
|-------|-----------|-------|-------|--------|
| 1 - UI Tests | `tests/unit/ui/` | 137 | 48K | Pending |
| 2 - Strategy Tests | `tests/unit/strategy/` | 154 | 48K | Pending |
| 3 - Simulation Tests | `tests/unit/simulation/` | 77 | 38K | Pending |
| 4 - Core+Entities+Data | `tests/unit/core/`, `entities/`, `data/` | 95 | 19K | Pending |
| 5 - AI+Research+Combat | `tests/unit/ai/`, `research/`, `combat/` | 62 | 18K | Pending |
| 6 - Refactor+Builder+Systems+Engine | Multiple dirs | 69 | 13K | Pending |
| 7 - Remaining+Integration | Small unit dirs + integration | ~120 | 30K | Pending |
| 8 - Cross-cutting | Duplicate/overlap across all dirs | all | scan | Pending |

## Confidence Levels
- **HIGH** - Almost certainly removable (dead code tests, exact duplicates, repro scripts)
- **MEDIUM** - Likely removable but needs verification (over-mocked, trivial, probably superseded)
- **LOW** - Possibly removable, needs careful review (partial duplicates, may test subtle edge cases)
