# PROJ-157: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Four independent validation reviews examined the original 8-agent code review findings against the actual codebase. Each validator read every test file directly and compared test methods 1:1 against claimed replacements.

### Key Finding: Original Reviewers Had Blind Spots

1. **Repro tests ARE collected by pytest.** The original review incorrectly claimed 4 root-level repro tests were "scaffold/repro tests not collected by pytest." In fact, `unittest.TestCase` subclasses and `test_`-prefixed functions ARE collected. The claimed replacement tests do NOT cover the same bug scenarios.

2. **The "12,766 lines of old directories" claim was misleading.** Old files use real game objects (integration-style) while new files use MagicMock (unit-style). File-by-file verification is required, not wholesale deletion.

3. **MockComponent duplication was overcounted.** Only 18 definitions exist (not 39), and they are intentionally different per testing context.

## Validated Categories

### Category 1: Scripts & Non-Tests (~760 lines)
Files that are not tests at all - diagnostic scripts, utility generators, profiling tools.
These are never collected by pytest and provide zero test value.

### Category 2: Trivial Scaffolds (~900 lines)
Files containing only `import X; assert X is not None` or `hasattr(X, 'method')` checks.
These provide zero functional coverage - they pass whether the code is correct or broken.

### Category 3: Over-Mocked Tests (~1,300 lines)
Files that create MagicMock objects, manually write logic inline (reimplementing production code), and then test the inline reimplementation. Zero production code is ever imported or called.

### Category 4: Old Simulation Framework (~1,300 lines)
A standalone test framework (`run_component_tests.py`, `component_logger.py`, etc.) that runs outside pytest, with custom `TestGrid`, `TestConfig`, and log parsers. Entirely superseded by proper pytest tests.

### Category 5: Duplicate Files Requiring Merge (~3,500 lines after merge)
Files where the validation found 60-80% overlap with a canonical version, but 5-15 unique tests that must be preserved. Strategy: merge unique tests, then delete source.

### Category 6: Old Directory Trees (~12,700 lines)
Four directories (services/, combat/, entities/, components/) containing older versions of tests that were reorganized into tests/unit/simulation/. Spot-checks confirmed 5 of 6 pairs are strict subsets. One pair (test_projectile_movement) needs special verification.

## Key Patterns to Reuse

### Test Migration Pattern
When merging unique tests from a duplicate file:
1. Read both source and target files completely
2. List all test methods in source with their assertions
3. For each source test, search target for equivalent (may have different name)
4. Identify tests with NO equivalent in target
5. Copy ONLY those unique tests to target, adapting imports/fixtures as needed
6. Delete source file
7. Run target file's test suite to verify

### File-By-File Subset Verification Pattern
For old directory tree cleanup:
1. List all test methods in old file (use grep for `def test_`)
2. Find corresponding new file in simulation/
3. For each old test method, find equivalent in new file
4. If ALL old tests have equivalents → safe to delete
5. If any old test lacks equivalent → SKIP (do not delete)

## Dependencies & Risks

1. **conftest.py deletion** - Verified: none of the 8 conftest files provide fixtures used by any test. Safe.
2. **__init__.py cleanup** - After deleting simulation framework files, must update `tests/unit/simulation/__init__.py` exports.
3. **Projectile movement coverage gap** - `test_projectile_movement` from old `test_projectile_manager.py` may not have a 1:1 mapping in the new file. Must verify before deletion.
4. **Test count tracking** - Should record baseline test count and track delta after each phase to ensure no unexpected losses.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
