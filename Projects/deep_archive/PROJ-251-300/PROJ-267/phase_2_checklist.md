# Phase 2: Consolidate Colonize Validator Tests [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-267 2`
> 2. Only proceed if output shows PASSED

**Objective:** Reduce test_colonize_validator.py from 1,247 LOC to ~700 LOC without losing coverage.
**Status:** Not Started

---

## Task 2.1: Extract shared fixtures to module level [Simple]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v --cov=game/strategy/validation/colonize_validator`

- [ ] Record baseline coverage and test count
- [ ] Extract `MockPlanetType(Enum)` to module-level (appears ~16 times inline)
- [ ] Extract `mock_component_registry` fixture to single module-level fixture (3 defs)
- [ ] Extract `_make_planet()` helper to module-level function (2 defs)
- [ ] Extract `_make_ship_with_pod()` to module-level function
- [ ] Run tests — all pass, coverage unchanged

## Task 2.2: Remove semantically duplicate tests [Medium]
- [ ] Find/remove duplicate "fleet with drop pod can colonize" tests (keep most thorough)
- [ ] Find/remove duplicate "no pod succeeds at command time" tests (keep one)
- [ ] Find/remove duplicate "overcommitted pods succeed" tests (keep one)
- [ ] Find/remove duplicate `test_count_drop_pods` (keep multi-ship version)
- [ ] Run tests — all pass, coverage UNCHANGED

## Task 2.3: Consolidate test classes [Simple]
- [ ] Merge classes testing same method with only planet-type differences (use parametrize)
- [ ] Merge advanced edge cases into main classes
- [ ] Verify final LOC is ~600-800
- [ ] Run tests — all pass, coverage unchanged

## Phase 2 Verification
- [ ] Coverage UNCHANGED from baseline
- [ ] File under 800 LOC
