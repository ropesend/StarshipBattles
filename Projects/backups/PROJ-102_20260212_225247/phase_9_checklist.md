# Phase 9: Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** End-to-end pipeline tests, save/load round-trips, and full suite verification.

---

## Tasks

### Task 9.1: Integration Tests [Medium]
**New File:** `tests/integration/strategy/test_superweapon_integration.py`
**Tests:** `pytest tests/integration/strategy/test_superweapon_integration.py -v`

- [x] Test full Implode Planet flow:
  - Create galaxy with system containing planet
  - Create fleet with ship carrying Planet Imploder
  - Issue QueueImplodePlanetMissionCommand
  - Process turns until fleet arrives at planet
  - Verify planet removed from system and galaxy indexes
  - Verify ship carrying Planet Imploder removed from fleet

- [x] Test full Stellerate Star flow:
  - Create galaxy with system, planets, fleets from multiple empires
  - Create fleet with Stellerator ship in same system
  - Issue QueueStellerateStarMissionCommand
  - Process turn
  - Verify: star removed, all planets removed, ALL fleets destroyed (including actor)
  - Verify: warp points survive

- [x] Test full Open Warp Point flow:
  - Create galaxy with 2 systems (no warp link)
  - Create fleet with QTI ship
  - Issue QueueOpenWarpPointMissionCommand
  - Process turn
  - Verify: warp point in system A -> system B
  - Verify: warp point in system B -> system A
  - Verify: ship consumed

- [x] Test full Close Warp Point flow:
  - Create galaxy with 2 systems linked by warp points
  - Create fleet with QTD ship at warp point hex
  - Issue QueueCloseWarpPointMissionCommand
  - Process turn
  - Verify: warp points removed from BOTH systems
  - Verify: ship consumed

- [x] Test full Create Dyson Sphere flow:
  - Create galaxy with system, star, planets at various distances
  - Create fleet with Dyson Sphere Constructor ship
  - Issue QueueCreateDysonSphereMissionCommand
  - Process turn
  - Verify: star removed
  - Verify: planets within 9 hexes removed
  - Verify: planets beyond 9 hexes preserved
  - Verify: DYSON_SPHERE planet created at system center
  - Verify: Dyson Sphere is colonizable (owner_id=None, PlanetType.DYSON_SPHERE)
  - Verify: ship consumed

- [x] Test full Self-Destruct flow:
  - Create fleet with 3 ships (2 with SelfDestruct device, 1 without)
  - Issue IssueSelfDestructCommand with IDs of the 2 SelfDestruct ships
  - Process next turn (self-destruct at start of turn)
  - Verify: 2 ships destroyed, 1 ship remains
  - Verify: fleet still exists (not empty)

**Notes:** All 6 integration tests implemented and passing.

### Task 9.2: Save/Load Round-Trip Tests [Simple]
**File:** `tests/integration/strategy/test_superweapon_integration.py` (or separate file)
**Tests:** `pytest tests/integration/strategy/test_superweapon_integration.py -v`

- [x] Test Fleet with IMPLODE_PLANET order: to_dict() -> from_dict() -> order preserved
- [x] Test Fleet with SELF_DESTRUCT order (ship ID list): round-trip
- [x] Test Fleet with OPEN_WARP_POINT order (dict target): round-trip
- [x] Test Fleet with STELLERATE_STAR order: round-trip
- [x] Test Fleet with CREATE_DYSON_SPHERE order: round-trip
- [x] Test Fleet with CLOSE_WARP_POINT order: round-trip

**Notes:** All 6 serialization tests passing.

### Task 9.3: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All tests pass (7689+ baseline + new tests)
- [x] No regressions introduced
- [x] Document final test count

**Notes:** 8167 tests passing (+12 from Phase 9 integration tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table rows ALL to `Complete`
- [x] Update plan.md Current State to "Project Complete"
