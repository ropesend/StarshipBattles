# Phase 6: DUP/HLP consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (5 done across passes 1-2 — pass 2 added 3 shared factories (cargo_mock_ship/yard_facility/mock_planet); 2 satisfied via Phase 1; 2 formally deferred-out-of-scope — DUP-001 + HLP-001 where the shared-factory shape would be net complexity-positive; PROJ-322 pass 3 verified)
**Objective:** Consolidate the cross-shard DUP-* duplicate-test patterns and HLP-* helper duplications into shared `tests/fixtures/` factories and per-package conftest modules.

---

## Tasks

### Task 6.1: DUP-001 - parameterized fixture factory for superweapon handler tests [Complex]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_handler_validation.py`

- [ ] DUP-001 (NEEDS_REWORK): create a parameterized fixture factory that supplies BOTH contract variants (execution path in `test_superweapon_command_handlers.py` and DI validation path in `test_superweapon_handler_validation.py`); do NOT merge the test classes - DI vs execution are different concerns. Affected files: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` and `tests/unit/strategy/engine/test_superweapon_handler_validation.py`. _(verification adjusted from review's "Merge SHARD_07 DI validation tests into SHARD_03 test classes as additional methods or single parametrized class" - see verification_report.md)_ **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** the two files exercise genuinely different contract surfaces — execution-path tests build a session whose handlers actually run; DI-validation tests build a session whose handlers exercise constructor-argument validation only. A `@pytest.fixture(params=[...])` would need to dispatch on parameter to set up either an execution mock or a DI-validation mock; the per-handler shapes differ enough (5+ handlers x 2 contracts = 10 distinct mock setups) that the factory becomes a switch statement and the readability win is negative. **RE-CONFIRMED DEFERRED IN PROJ-327 Phase 3 Task 3.1 (commit pending)** — measurement: combined file runtime is 1.73 s for 39 tests; per-test fixture setup is ~0.05 s post-import (with the first 4 tests taking ~0.42 s each due to one-time imports). Total fixture overhead in the execution file is roughly 1 s. BUT: each test calls `handler.execute()` which mutates `mock_fleet.orders`/`.path` and records calls on the mock session; sharing the session between tests requires resetting orders, path, and call records on every test (the equivalent of re-running the fixture body). 2 tests reassign `mock_fleet.ships`; another 2 reassign `mock_session._get_fleet_by_id.return_value = None`. Builder-pattern factory still resolves to the original switch-statement shape. Original PROJ-322 rationale stands: 5 handlers × 2 contracts = 10 distinct setup shapes, and a parametrized fixture absorbs them only by hiding the difference behind a discriminator. Honoring D-006: re-confirmation is a valid outcome.
- [ ] Factory shape: `@pytest.fixture(params=[(handler_cls, mock_session_factory_for_execution), (handler_cls, mock_session_factory_for_di_validation)], ids=["execution", "di_validation"])` — supplies both contract variants without merging the test classes. _(re-confirmed deferred in PROJ-327 — see above; the proposed factory shape has been re-analyzed with runtime context and remains net complexity-positive.)_
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/engine/test_superweapon_handler_validation.py` passes; LOC delta approximately -100 (~200 LOC duplication minus shared factory cost) _(re-confirmed deferred in PROJ-327 — see above.)_

---

### Task 6.2: DUP-002 - parametrized fleet-not-found handler tests [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/test_command_handlers.py`

- [x] DUP-002: extract the fleet-not-found assertion pattern (identical across superweapon handlers in `test_superweapon_command_handlers.py` and core command handlers in `test_command_handlers.py`) into `@pytest.mark.parametrize('handler_cls,cmd_kwargs', [...])`. Affected files: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` and `tests/unit/strategy/test_command_handlers.py`. Coordinate with Task 1.13 in Phase 1. _(satisfied — same change covered by Tasks 1.13/1.14 in Phase 1; parametrized 5+1 mission handler fleet-not-found tests)_
- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/test_command_handlers.py` passes; LOC delta approximately -120 (~180 LOC duplication minus parametrize) _(satisfied — same change covered by Tasks 1.13/1.14 in Phase 1; parametrized 5+1 mission handler fleet-not-found tests)_

---

### Task 6.3: DUP-003 - shared make_cargo_mock_ship factory [Medium]
**File:** `tests/fixtures/cargo_mock_ship.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py`

- [x] DUP-003: create `tests/fixtures/cargo_mock_ship.py` exposing `make_cargo_mock_ship(cargo_capacity, cargo_contents)`; replace the closure-based cargo mock helpers (`_make_ship` and `_make_mock_ship`) in `tests/unit/strategy/data/test_fleet_cargo_resources.py` and `tests/unit/strategy/engine/test_resupply_engine.py` with calls into the shared factory. _(Created `tests/fixtures/cargo_mock_ship.py` exposing `make_cargo_mock_ship(cargo_capacity, cargo_contents, *, is_combat_capable)`. Migrated `tests/unit/strategy/data/test_fleet_cargo_resources.py` (kept `_make_ship` as a thin alias). The other file's `_make_mock_ship` is actually a FUEL-resource mock (`get_resource_capacity`, `resupply` for the 'fuel' resource), not cargo — different API surface, no overlap with the cargo factory; left as-is.)_
- [x] Verify: `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py` passes; LOC delta approximately -30 (~50 LOC dedup minus shared file) _(11 cargo tests pass; the resupply-engine `_make_mock_ship` is a different fuel-API mock so it stays.)_

---

### Task 6.4: HLP-001 - shared test_entities fixtures (ship/fleet/empire/planet) [Complex]
**File:** `tests/fixtures/test_entities.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] HLP-001: create `tests/fixtures/test_entities.py` with `make_mock_ship`, `make_mock_fleet`, `make_mock_empire`, `make_mock_planet` (kwargs overrides). Migrate the duplicated helpers in `tests/unit/ui/screens/test_fleet_report_filters.py`, `tests/unit/strategy/data/test_fleet_cargo_resources.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, and `tests/unit/strategy/facade/test_strategy_session_facade.py` to import from the shared module. Coordinate with Tasks 2.8, 2.9, 2.15 in Phase 2. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** the four files use disparate `make_mock_*` shapes — fleet_report_filters needs 20+ display-name params; cargo_resources needs cargo capacity (handled by DUP-003 `cargo_mock_ship`); resupply_engine needs fuel-bearing planets (different surface from `mock_planet`); strategy_session_facade needs facade-specific mocks. Pass 2 created the narrower shared factories where shapes did align (DUP-003 cargo_mock_ship, HLP-003 yard_facility, HLP-004 mock_planet). A blanket `make_mock_ship` would either lose the per-file expressiveness or grow into an unreadable kitchen-sink builder. **RE-CONFIRMED DEFERRED IN PROJ-327 Phase 3 Task 3.2 (commit pending)** — measurement: `make_mock_ship` (fleet_report variant) microbenchmarks at ~627 µs/call (10 000 calls = 6.27 s wall). The file calls it 115 times = ~72 ms total in `make_mock_ship` for the whole file (which itself runs in 1.99 s = ~3.6%). Memoization theoretical max win is ~50 ms after deepcopy-on-retrieval cost. The 4 cited files have confirmed-distinct shapes: cargo_resources uses `_make_ship(cargo_capacity, cargo_contents)` (already factored to DUP-003); resupply uses `_make_mock_ship(fuel_capacity, current_fuel, fuel_cost_per_hex)`; fleet_report uses 11+ display params; strategy_session_facade uses facade-bound mocks. No overlapping shape exists to memoize. Original "kitchen-sink builder" rejection rationale stands. Honoring D-006: re-confirmation is a valid outcome.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/strategy/data/test_fleet_cargo_resources.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/facade/test_strategy_session_facade.py` passes; LOC delta approximately -200 (~300 LOC dedup minus shared module) _(re-confirmed deferred in PROJ-327 — see above.)_

---

### Task 6.5: HLP-002 - move BattleRunner test helpers into simulation conftest [Medium]
**File:** `tests/unit/simulation/conftest.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py`

- [x] HLP-002: move `_make_ship_spec`, `_make_team`, and the `ship_builder` fixture into `tests/unit/simulation/conftest.py` with class scope; reference from both `test_battle_runner.py` and `test_battle_runner_di.py`. Coordinate with Task 1.5 in Phase 1. _(satisfied — same change covered by Task 1.5 in Phase 1; tests/unit/simulation/conftest.py created with _make_ship_spec/_make_team)_
- [x] Verify: `pytest tests/unit/simulation/test_battle_runner.py tests/unit/simulation/test_battle_runner_di.py` passes; LOC delta approximately -30 (~55 LOC dedup minus shared conftest entries) _(satisfied — same change covered by Task 1.5 in Phase 1; tests/unit/simulation/conftest.py created with _make_ship_spec/_make_team)_

---

### Task 6.6: HLP-003 - shared yard-facility factory [Medium]
**File:** `tests/fixtures/yard_facility.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/fleet/test_space_yard.py`

- [x] HLP-003: create `tests/fixtures/yard_facility.py` exposing `make_yard_facility(...)`, `make_planetary_yard_facility(...)`, `make_ship_with_yard(...)`. Migrate the duplications in `tests/unit/strategy/engine/test_planetary_yard_requirement.py`, `tests/unit/strategy/production_engine/test_tick_consumption.py`, and the two duplicates within `tests/unit/strategy/fleet/test_space_yard.py`. Coordinate with Task 1.15 in Phase 1. _(Created `tests/fixtures/yard_facility.py` with `make_planetary_yard_facility(*, instance_id, design_id, name, is_operational, yard_id)` and `make_ship_with_yard(fresh_registries, *, name, has_yard, is_combat_capable)`. Migrated `test_planetary_yard_requirement.py` and `test_tick_consumption.py` to use thin aliases over the shared factory. `test_space_yard.py`'s `make_ship_with_yard` was already module-scoped via PROJ-322 Task 1.15 — left as-is since it's already factored well.)_
- [x] Verify: `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/fleet/test_space_yard.py` passes; LOC delta approximately -20 (~35 LOC dedup minus shared module) _(22 yard tests pass; ~25 LOC removed from the two migrated files.)_

---

### Task 6.7: HLP-004 - shared make_mock_planet factory [Medium]
**File:** `tests/fixtures/mock_planet.py` (new)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/test_planet_specific_colonization.py`

- [x] HLP-004: create `tests/fixtures/mock_planet.py` exposing `make_mock_planet(**overrides)`. Migrate the triplicated `make_planet` helpers (and similar duplications) in `tests/unit/strategy/validation/test_colonize_validator.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, and `tests/unit/strategy/test_planet_specific_colonization.py`. _(Created `tests/fixtures/mock_planet.py` exposing `make_mock_planet(**kwargs)` with the full IPlanet protocol surface (PROJ-193) pre-populated. Migrated `test_colonize_validator.py`'s `_make_planet` to be a thin alias. The `test_resupply_engine.py`'s `_make_planet_with_fuel` is a fuel-storage-bearing mock with its own facility wiring — different surface, left as-is. The third originally-cited file `test_planet_specific_colonization.py` was already deleted upstream — pre-flight obsoletion check confirmed it doesn't exist.)_
- [x] Verify: `pytest tests/unit/strategy/validation/test_colonize_validator.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/test_planet_specific_colonization.py` passes; LOC delta approximately -50 (~80 LOC dedup minus shared module) _(43 colonize-validator tests pass; ~25 LOC removed.)_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or marked deferred-out-of-scope with concrete shape-mismatch rationale)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
