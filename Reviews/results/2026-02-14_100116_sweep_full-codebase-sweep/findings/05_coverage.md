# Test Coverage Gaps Sweep: Antigravity

## Summary
- **Shard:** Antigravity (Full Sweep)
- **Production Files Scanned:** 370+
- **Test Files Cross-Referenced:** ~60
- **Total Issues Found:** 2
- **Critical:** 0 | **Major:** 1 | **Minor:** 1 | **Info:** 0

## Findings

#### MAJOR: Test File Naming Inconsistencies
**ID:** TCG-AG-001
**Location:** `tests/unit/strategy/engine/`
**Issue:** `ProductionEngine` is tested by `test_production_refactor.py` instead of `test_production_engine.py`.
**Impact:** Developers may believe the class is untested and write duplicate tests or skip testing.
**Recommendation:** Rename `test_production_refactor.py` to `test_production_engine.py` to match the production file.
**Effort:** Simple

#### MINOR: BattleController Integration Tests
**ID:** TCG-AG-002
**Location:** `game/simulation/battle_controller.py`
**Issue:** While components (`BattleService`, `BattleModeHandler`) are tested, the orchestrator `BattleController` has no direct unit test file.
**Impact:** Integration logic and state transitions in the controller might regress.
**Recommendation:** Add a specific test suite for `BattleController`.
**Effort:** Medium

## Top Priority Issues
1. **Rename Test Files**: Align test filenames with production filenames to improve discoverability.
