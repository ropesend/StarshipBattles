# PROJ-48: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Baseline Test Suite:**
- 5244 passed, 5 failed (pre-existing), 3 skipped
- 28,166 warnings (mostly deprecation warnings)
- ~40 seconds full suite runtime

**Key Metrics:**
- 379 total test files
- 13 conftest.py files
- 50 test files over 500 LOC
- 4 critical monoliths over 1000 LOC
- 2 disabled integration tests
- Test-to-code ratio: 1.58x (99,262 test LOC vs 62,724 production LOC)

## Swarm Findings Summary

### Architecture

**Test Organization:** Hybrid approach with layer-based (unit/integration) and feature-based organization.

**Key Inconsistencies:**
1. **Builder Location Mismatch:** `game/ui/screens/builder/` -> `tests/unit/builder/` (doesn't mirror source)
2. **Simulation Fragmentation:** Combat/simulation split across 4 directories
3. **Strategy Duplication:** Both `tests/unit/strategy/` and `tests/strategy/` exist
4. **UI Test Duplication:** Both `tests/unit/ui/` and `tests/ui/` exist

**Fixture Architecture (Excellent):**
- Well-documented `tests/fixtures/` module
- Factory + fixture pattern (`create_test_ship()` + `basic_ship` fixture)
- SessionRegistryCache for expensive data loading
- Deep-copy returns to prevent test pollution

### Dependency Map

**Conftest Hierarchy (13 files):**
```
conftest.py (root)
├── reset_game_state [autouse] - Hydration + cleanup
├── enforce_headless [autouse] - Pygame setup

tests/conftest.py
├── reset_singletons [autouse] - Post-test cleanup
├── session_registries [session] - DI registries
├── fresh_registries [function] - Mutable copies
├── minimal_registries [function] - Empty for unit tests

tests/unit/*/conftest.py (11 files)
└── Module-specific fixtures and setup
```

**Critical Dependencies:**
- `reset_game_state` + `reset_singletons` run for ALL 419 test files
- Session fixtures (`session_registries`, `global_ship_data`) run once per xdist worker (4 times total with `-n 4`)
- Module conftest imports from `tests/fixtures/common`, `tests/fixtures/ships`, `tests/fixtures/paths`

### Key Patterns to Reuse

- **Session Caching:** `tests/infrastructure/session_cache.py` - Thread-safe singleton cache
- **Fixture Factory Pattern:** `tests/fixtures/battle.py` - `create_battle_engine()` + `@pytest.fixture`
- **Strong Assertions:** `tests/unit/refactor/test_weapon_ability_bindings.py` - `pytest.approx`, context messages
- **Test Organization:** `tests/unit/builder/test_builder_validation.py` - Class-based with autouse setup

### Dependencies & Risks

1. **Dual Registry Cleanup (CRITICAL):** Two competing autouse fixtures (`reset_game_state`, `reset_singletons`) - must consolidate
2. **SessionRegistryCache Mutation:** Despite deep_copy, tests modify registry data - need immutability enforcement
3. **Xdist Session Fixture Multiplication:** Session-scoped fixtures run 4 times (once per worker)
4. **Large File Hidden Dependencies:** Test methods in monolith files may depend on shared state
5. **Pygame Module State:** `test_research_renderer.py` skips under xdist due to module corruption

**Mitigation Strategies:**
- Consolidate cleanup into single conftest mechanism
- Run tests with `--random-order` before and after splitting to detect order dependencies
- Use `--dist=loadfile` with xdist to keep same-file tests in same worker
- Add isolation verification tests

### Opportunities Discovered

1. **Create Assertion Helpers:** No custom assertion helpers exist - opportunity to add `assert_success()`, `assert_list_length()`
2. **Centralize Mock Factories:** 3086 mock/patch usages scattered - opportunity for `tests/fixtures/mocks.py`
3. **BDD-Style Naming:** No `test_should_*` or `test_when_*` patterns - could improve readability
4. **Fixture Documentation:** Add `tests/README.md` with fixture hierarchy diagram

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

## Monolith Splitting Strategy

**Top 4 Monoliths (Split into directories):**

| File | LOC | Target | New Files |
|------|-----|--------|-----------|
| test_ship_stats_service.py | 1756 | `ship_stats/` | 5 files |
| test_ship_instance_proj08.py | 1458 | `ship_instance/` | 3 files |
| test_battle_controller.py | 1317 | `battle_controller/` | 4 files |
| test_fleet.py | 1103 | `fleet/` | 3 files |

**Splitting Principle:** Each new directory gets:
- `__init__.py`
- `conftest.py` with shared fixtures extracted from original file
- Test files split by test class groupings

**Total: 50 files to split, creating ~120 smaller files**

## Weak Assertion Patterns

**Files with most issues:**
1. `test_save_game_service.py` - 25+ bare `assert success`
2. `test_design_library.py` - 5 bare `assert success`
3. `test_auto_save.py` - 4 bare `assert success`
4. `test_workshop_viewmodel.py` - 5 weak length assertions

**Fix Template:**
```python
# Before
assert success

# After
assert success, f"Operation failed: {message}"
```

## Naming Convention Standards

| Aspect | Current | Recommended |
|--------|---------|-------------|
| Test File | `test_*.py` | Keep |
| Disabled Test | `_test_*.py` | `@pytest.mark.skip` |
| Test Class | `Test*` | `Test<SourceClassName>` |
| Test Method | `test_*()` | Keep (consider `test_should_*` for new) |
| Mock Class | `Mock*` | Keep (standardize) |
| Fixture | Various | `{scope}_{resource}` |
| Factory | `create_*()` | Keep |

## Directory Structure Target

```
tests/
├── conftest.py              # Root fixtures, cleanup
├── fixtures/                # Shared fixtures and factories
│   ├── battle.py
│   ├── components.py
│   ├── mocks.py            # NEW: Centralized mock factories
│   ├── paths.py
│   ├── ships.py
│   └── README.md           # NEW: Fixture documentation
├── infrastructure/          # Test infrastructure
│   └── session_cache.py
├── unit/                    # Unit tests (by module)
│   ├── conftest.py
│   ├── ai/
│   ├── builder/
│   ├── combat/
│   ├── core/
│   ├── entities/
│   ├── research/
│   ├── simulation/
│   │   ├── battle_controller/  # NEW: Split from monolith
│   │   └── ...
│   ├── strategy/
│   │   ├── fleet/              # NEW: Split from monolith
│   │   ├── ship_instance/      # NEW: Split from monolith
│   │   ├── ship_stats/         # NEW: Split from monolith
│   │   └── ...
│   ├── systems/
│   ├── test_framework/     # MOVED: from tests/test_framework/
│   └── ui/
├── integration/             # Integration tests
│   ├── strategy/           # MOVED: from tests/strategy/
│   ├── ui/                 # MOVED: from tests/ui/
│   └── ...
├── regression/              # Regression tests
├── performance/             # Benchmarks (not pytest)
└── README.md               # NEW: Test guide with hierarchy
```

## Issues Mapping

| Issue ID | Description | Phase | Status |
|----------|-------------|-------|--------|
| TSR-001 | Disabled Integration Tests | 1 | Pending |
| TSR-002 | Incomplete Test with Dead Code | 1 | Pending |
| TSR-003 | Non-Isolated Test Framework | 1, 2 | Pending |
| TSR-004 | Weak Assertion Patterns | 4 | Pending |
| TSR-005 | Large Test Monoliths | 3 | Pending |
| TSR-006 | Multiple Mock Patterns | 7 | Pending |
| TSR-007 | Fixture Scope Mismatch | 2 | Pending |
| TSR-008 | Test Organization Inconsistency | 6 | Pending |
| TSR-009 | Skipped/Deferred Tests | 8 | Pending |
| TSR-010 | Empty/Stub Test Classes | 8 | Pending |
| TSR-011 | Print Statements in Tests | 8 | Pending |
| TSR-012 | Mixed Test Patterns | 8 | Pending |
| TSR-013 | Hardcoded Test Data | 8 | Pending |
| TSR-014 | Duplicate Test Setup | 8 | Pending |
| TSR-015 | No Docstrings for Complex Tests | 8 | Pending |
| TNC-001 | Non-Standard Test File Naming | 5 | Pending |
| TNC-002 | Inverted Directory Structure | 6 | Pending |
| TNC-003 | Disabled Test Files Leading Underscores | 1 | Pending |
| TNC-004 | Incomplete Directory Structure | 6 | Pending |
| TNC-005 | Duplicate Test Filenames | 6 | Pending |
| TNC-006 | Test Class Naming No Mapping | 5 | Pending |
| TNC-007 | Mixed Test and Support Code | 5 | Pending |
| TNC-008 | Inconsistent Fixture Naming | 2 | Pending |
| TNC-009 | Mock/Stub Naming Inconsistency | 7 | Pending |
| TNC-010 | Factory Function Naming | 7 | Pending |
| TNC-011 | No Descriptive Test Method Naming | 5 | Pending |
| TC-06 | Test Isolation with GameRegistries | 1 | Pending |
