# Pre-Existing Failures Spot-Check

## Summary
- Tests spot-checked: 3 test files (covering 5 distinct failure types)
- Confirmed pre-existing (also fail on `main`): 2
- Possibly caused by PROJ-381: **0**
- Pre-existing on `feat/03c` but NOT on `main`: 1 (caused by PROJ-372, not PROJ-381)
- Uncertain: 0

**Overall verdict**: None of the spot-checked failures are caused by PROJ-381. No new PROJ-381 exception types (`ImageUnexpectedError`, `SessionInitializationError`, `TurnFailedError`, `BattleResolutionError`) or the new error code `V005/OWNERSHIP_MISMATCH` appear in any traceback.

---

## Test-by-Test Analysis

### test_galaxy_entity_registry.py (18 failed / 30 tests)

- **Test file:** `tests/unit/strategy/data/test_galaxy_entity_registry.py`
- **Failing tests:** 18 out of 30 tests across `TestPlanetRegistration`, `TestPlanetRestore`, `TestGetPlanetById`, `TestUnregisterPlanet`, `TestZoneRegistration`, `TestUnregisterZone`
- **Error type:** `AttributeError` — mock object missing expected attributes
- **PROJ-381 files in traceback:** **No**. Traceback passes through `game/strategy/data/galaxy_entity_registry.py` only (not on PROJ-381 list)
- **New exception types involved:** **No**
- **Root cause:** PROJ-372 Phase 3 (commit `801f8a4cf`) refactored `GalaxyEntityRegistry` to accept a `GalaxyState` dataclass instead of a `Galaxy` back-pointer, and renamed fields to drop the leading underscore (e.g., `_next_planet_id` → `next_planet_id`, `_planet_to_system` → `planet_to_system`). The test's `_MockGalaxy` mock still uses the old underscore-prefixed attribute names. PROJ-372's commit message lists only `test_fleet_registration_lifecycle.py` as updated; this test file was missed.
- **Verdict:** **PRE-EXISTING** (from PROJ-381's perspective — caused by PROJ-372, not PROJ-381)
- **Evidence:**
  - Traceback excerpt: `AttributeError: '_MockGalaxy' object has no attribute 'next_planet_id'` (line 87 of `galaxy_entity_registry.py`)
  - Traceback excerpt: `AttributeError: '_MockGalaxy' object has no attribute 'planet_to_system'` (line 76 of `galaxy_entity_registry.py`)
  - Test mock defines `self._next_planet_id = 1` (line 21 of test file, underscore-prefixed), but GalaxyState field is `next_planet_id` (no underscore — `galaxy_state.py:65`)
  - `GalaxyState` was introduced by commit `801f8a4cf` (PROJ-372), which is NOT on `main`
  - Confirmed: the representative test `test_register_planet_assigns_sequential_ids` **passes on `main` branch** but **fails on `feat/03c-phase-aware-execution`**
  - PROJ-381 did NOT touch `galaxy_entity_registry.py` or `galaxy_state.py`

---

### test_storm.py (1 failed / 20 tests)

- **Test file:** `tests/unit/strategy/data/test_storm.py`
- **Failing tests:** `TestStarSystemStormIntegration::test_star_system_from_dict_skips_invalid_storm_gracefully`
- **Error type:** `PersistenceException` (pre-existing exception from `game/core/exceptions.py`)
- **PROJ-381 files in traceback:** **Yes** — `game/core/exceptions.py` (`PersistenceException`)
- **New exception types involved:** **No** — `PersistenceException` is a pre-existing exception (introduced in `2255a3ef1` [PROJ-45] Phase 1, not a PROJ-381 new type)
- **Root cause:** The strict deserialization refactor (commit `9a9d1eee7`, pre-existing on both branches) replaced silent skip-on-error with `PersistenceException` raising. The test name says "skips_invalid_storm_gracefully" but the production code now raises instead of skipping. The test expectation is stale relative to the refactored behavior.
- **Verdict:** **PRE-EXISTING** (confirmed — fails identically on `main`)
- **Evidence:**
  - Identical failure on `main` branch with same traceback and same error
  - Traceback: `game\core\json_utils.py:259: deserialize_list` wraps a `PersistenceException` from `game\core\validation_helpers.py:59: require_keys`
  - Test expects graceful skip; code raises `PersistenceException` during strict deserialization
  - The test file was last modified by commit `0208cb163` (PROJ-300 Phase 5), not by PROJ-381

---

### test_planet_classification_logic.py (1 failed / 19 tests)

- **Test file:** `tests/unit/strategy/data/test_planet_classification_logic.py`
- **Failing tests:** `TestClassificationConfigLoader::test_all_planet_types_have_rules`
- **Error type:** `AssertionError` — missing configuration entry
- **PROJ-381 files in traceback:** **No**
- **New exception types involved:** **No**
- **Root cause:** The `DYSON_SPHERE` enum value was added to `PlanetType` but the classification config file was never updated with a corresponding rule. This is a pure data/config gap.
- **Verdict:** **PRE-EXISTING** (confirmed — fails identically on `main`)
- **Evidence:**
  - Identical failure on `main` branch: `AssertionError: Missing rule for DYSON_SPHERE`
  - The test file was last modified by commit `8b77b83d6` (procedural galaxy generation system), not by PROJ-381
  - No PROJ-381 files appear anywhere in the traceback

---

## Findings

### INFO-001: All spot-checked failures are pre-existing relative to PROJ-381

None of the 3 test files (6 distinct failure types) show any involvement of PROJ-381's new exception hierarchy. No `ImageUnexpectedError`, `SessionInitializationError`, `TurnFailedError`, `BattleResolutionError`, or error code `V005/OWNERSHIP_MISMATCH` appears in any traceback.

| Test File | Failures | Fails on main? | PROJ-381 files in traceback? | New PROJ-381 types? | Cause |
|---|---|---|---|---|---|
| `test_galaxy_entity_registry.py` | 18 | **No** (passes on main) | No | No | PROJ-372 test mock drift |
| `test_storm.py` | 1 | **Yes** | Yes (`exceptions.py`, but pre-existing `PersistenceException`) | No | Stale test after strict deserialization refactor |
| `test_planet_classification_logic.py` | 1 | **Yes** | No | No | Missing DYSON_SPHERE classification config rule |

### INFO-002: PROJ-381's `game/core/exceptions.py` changes do NOT break any spot-checked test

Although `game/core/exceptions.py` appears in the `test_storm.py` traceback, the exception raised is the pre-existing `PersistenceException` — not one of the new PROJ-381 exception types. The same exception type is raised with identical behavior on `main`, confirming PROJ-381's modifications to `exceptions.py` did not alter `PersistenceException` behavior.

### INFO-003: test_galaxy_entity_registry.py failures are a PROJ-372 test fixture migration gap

The 18 failures in `test_galaxy_entity_registry.py` are caused by PROJ-372 Phase 3 (commit `801f8a4cf`), which refactored `GalaxyEntityRegistry` to use `GalaxyState` with de-underscored field names. The test mock `_MockGalaxy` was not updated to match. This is a PROJ-372 bug, not a PROJ-381 bug. The PROJ-381 implementer correctly identified these as "pre-existing" (they were pre-existing on the `feat/03c` branch when PROJ-381 work began).

### INFO-004: test_storm.py and test_planet_classification_logic.py failures are true pre-existing bugs on main

Both failures reproduce identically on `main` branch, confirming they are genuine pre-existing issues independent of any work on the `feat/03c` branch.
