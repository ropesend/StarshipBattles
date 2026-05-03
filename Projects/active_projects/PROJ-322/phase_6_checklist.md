# Phase 6: DUP/HLP consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate the cross-shard DUP-* duplicate-test patterns and HLP-* helper duplications into shared `tests/fixtures/` factories and per-package conftest modules.

---

## Tasks

### Task 6.1: DUP-001 - parameterized fixture factory for superweapon handler tests [Complex]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_handler_validation.py`

- [ ] DUP-001 (NEEDS_REWORK): create a parameterized fixture factory that supplies BOTH contract variants (execution path in `test_superweapon_command_handlers.py` and DI validation path in `test_superweapon_handler_validation.py`); do NOT merge the test classes - DI vs execution are different concerns. Affected files: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` and `tests/unit/strategy/engine/test_superweapon_handler_validation.py`. _(verification adjusted from review's "Merge SHARD_07 DI validation tests into SHARD_03 test classes as additional methods or single parametrized class" - see verification_report.md)_
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_handler_validation.py` passes; LOC delta approximately -100 (~200 LOC duplication minus shared factory cost)

---

### Task 6.2: DUP-002 - parametrized fleet-not-found handler tests [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/test_command_handlers.py`

- [ ] DUP-002: extract the fleet-not-found assertion pattern (identical across superweapon handlers in `test_superweapon_command_handlers.py` and core command handlers in `test_command_handlers.py`) into `@pytest.mark.parametrize('handler_cls,cmd_kwargs', [...])`. Affected files: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` and `tests/unit/strategy/test_command_handlers.py`. Coordinate with Task 1.13 in Phase 1.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/test_command_handlers.py` passes; LOC delta approximately -120 (~180 LOC duplication minus parametrize)

---

### Task 6.3: DUP-003 - shared make_cargo_mock_ship factory [Medium]
**File:** `tests/fixtures/cargo_mock_ship.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] DUP-003: create `tests/fixtures/cargo_mock_ship.py` exposing `make_cargo_mock_ship(cargo_capacity, cargo_contents)`; replace the closure-based cargo mock helpers (`_make_ship` and `_make_mock_ship`) in `tests/unit/strategy/data/test_fleet_cargo_resources.py` and `tests/unit/strategy/engine/test_resupply_engine.py` with calls into the shared factory.
- [ ] Verify: `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py` passes; LOC delta approximately -30 (~50 LOC dedup minus shared file)

---

### Task 6.4: HLP-001 - shared test_entities fixtures (ship/fleet/empire/planet) [Complex]
**File:** `tests/fixtures/test_entities.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] HLP-001: create `tests/fixtures/test_entities.py` with `make_mock_ship`, `make_mock_fleet`, `make_mock_empire`, `make_mock_planet` (kwargs overrides). Migrate the duplicated helpers in `tests/unit/ui/screens/test_fleet_report_filters.py`, `tests/unit/strategy/data/test_fleet_cargo_resources.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, and `tests/unit/strategy/facade/test_strategy_session_facade.py` to import from the shared module. Coordinate with Tasks 2.8, 2.9, 2.15 in Phase 2.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/facade/test_strategy_session_facade.py` passes; LOC delta approximately -200 (~300 LOC dedup minus shared module)

---

### Task 6.5: HLP-002 - move BattleRunner test helpers into simulation conftest [Medium]
**File:** `tests/unit/simulation/conftest.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py`

- [ ] HLP-002: move `_make_ship_spec`, `_make_team`, and the `ship_builder` fixture into `tests/unit/simulation/conftest.py` with class scope; reference from both `test_battle_runner.py` and `test_battle_runner_di.py`. Coordinate with Task 1.5 in Phase 1.
- [ ] Verify: `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py` passes; LOC delta approximately -30 (~55 LOC dedup minus shared conftest entries)

---

### Task 6.6: HLP-003 - shared yard-facility factory [Medium]
**File:** `tests/fixtures/yard_facility.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/fleet/test_space_yard.py`

- [ ] HLP-003: create `tests/fixtures/yard_facility.py` exposing `make_yard_facility(...)`, `make_planetary_yard_facility(...)`, `make_ship_with_yard(...)`. Migrate the duplications in `tests/unit/strategy/engine/test_planetary_yard_requirement.py`, `tests/unit/strategy/production_engine/test_tick_consumption.py`, and the two duplicates within `tests/unit/strategy/fleet/test_space_yard.py`. Coordinate with Task 1.15 in Phase 1.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/fleet/test_space_yard.py` passes; LOC delta approximately -20 (~35 LOC dedup minus shared module)

---

### Task 6.7: HLP-004 - shared make_mock_planet factory [Medium]
**File:** `tests/fixtures/mock_planet.py` (new)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/test_planet_specific_colonization.py`

- [ ] HLP-004: create `tests/fixtures/mock_planet.py` exposing `make_mock_planet(**overrides)`. Migrate the triplicated `make_planet` helpers (and similar duplications) in `tests/unit/strategy/validation/test_colonize_validator.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, and `tests/unit/strategy/test_planet_specific_colonization.py`.
- [ ] Verify: `pytest tests/unit/strategy/validation/test_colonize_validator.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/test_planet_specific_colonization.py` passes; LOC delta approximately -50 (~80 LOC dedup minus shared module)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
