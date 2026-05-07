# Phase 2: Planet decomposition (667 LOC → ~350 facade + habitability/query services)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** Phase 1 (verified)
**Review Mode:** cumulative (covers Phase 0 + 1 + 2)
**Files (planned):** see manifest.md Phase 2 row group

**Status:** Not Started
**Objective:** Move `Planet`'s 4 logic-bearing query/calc methods (`active_abilities`, `is_ability_active`, `occupied_hexes`, `can_build_type`) to `PlanetQueryService`. Convert `get_cached_habitability_multiplier` from a late-import logic body to a 1-line facade calling `ApplicationContext.get_default_planet_habitability_service().get_cached(...)`. Wire the real `PlanetHabitabilityService` into context. Preserve all 47 dataclass fields verbatim. Stockpile / staging / order methods stay on `Planet` but conform to `IStockpileHolder` / `IStagingYardHolder` protocols (defined in Phase 0). Save format unchanged.

---

## Reading (Phase 2 prerequisites)

- [ ] Phase 1 outcomes — confirm `stars.py` ≤ 280 LOC, sharded green
- [ ] `game/strategy/data/planet.py` lines 1-667 — full file
- [ ] `game/strategy/formulas/colony_output.py` (`planet_habitability_multiplier` definition)
- [ ] `game/strategy/data/colony_species_config.py` (PROJ-284) — used by `Planet.species_configs`
- [ ] `game/strategy/data/planetary_facility.py` and `species_population.py` (PROJ-210) — Planet field types
- [ ] All 20 external readers of `planet.populations` / `stockpile` / `facilities` (per design.md) — confirm Phase 2 doesn't change their access surface

---

## Pre-flight (TDD baseline)

- [ ] Run `pytest tests/unit/strategy/data/test_planet.py -v` and `pytest tests/unit/strategy/services/test_planet*.py -v` — capture baseline
- [ ] `grep -rn 'get_cached_habitability_multiplier\|active_abilities\|is_ability_active\|occupied_hexes\|can_build_type' game/ tests/` — capture every caller of each method
- [ ] Verify `Planet.get_cached_habitability_multiplier` returns deterministic values for a fixture planet (pin the expected float in `Notes:` for regression checking)

---

## Tasks

### Task 2.1: Acceptance test for habitability service swappability (TDD-first) [Medium]
**File:** `tests/unit/strategy/services/test_planet_habitability_service.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_planet_habitability_service.py -v`

- [ ] Test `test_swap_habitability_service_via_context`: register a stub `IHabitabilityCalculator` returning `0.42` via `set_default_planet_habitability_service`; call `Planet.get_cached_habitability_multiplier(race_registry, turn=1)` on a fixture planet; assert returns `0.42`.
- [ ] Test `test_default_service_returns_real_calculation`: with no override, assert returned value matches `planet_habitability_multiplier(planet, race_registry)` directly.
- [ ] Test `test_cache_lives_on_planet`: call twice for same turn, assert second call doesn't re-compute (mock the service's `_compute` method and assert called once).
- [ ] Test `test_cache_invalidates_on_turn_change`: call for turn=1, then turn=2, assert re-compute.
- [ ] Confirm tests **FAIL** initially (service doesn't exist yet).
- [ ] **Verify:** all 4 tests fail with `ModuleNotFoundError` or equivalent.

**Notes:**

### Task 2.2: Implement `PlanetHabitabilityService` [Medium]
**File:** `game/strategy/services/planet_habitability_service.py` (new)
**Tests:** Task 2.1's tests

- [ ] Class implementing `IHabitabilityCalculator` from `galaxy_protocols.py`.
- [ ] `def get_cached(self, planet: Planet, race_registry, turn: int) -> float` — read/write `planet._cached_habitability_multiplier` and `planet._cached_multiplier_turn`.
- [ ] On cache miss: call `planet_habitability_multiplier(planet, race_registry)` (late-import to avoid circular).
- [ ] Module ≤ 200 LOC.
- [ ] **Verify:** Task 2.1 tests pass.

**Notes:**

### Task 2.3: Wire `PlanetHabitabilityService` into `ApplicationContext` [Simple]
**File:** `game/context.py` (modify)
**Tests:** `pytest tests/unit/test_context.py -v`

- [ ] At module init, set `_default_planet_habitability_service = PlanetHabitabilityService()` (replacing Phase 0's `None`).
- [ ] Existing fallback in `Planet.get_cached_habitability_multiplier` (Phase 0 Task 0.2) now uses the registered service.
- [ ] **Verify:** `Planet.get_cached_habitability_multiplier(race_registry, turn=1)` returns the same float as before (regression check).

**Notes:**

### Task 2.4: Implement `PlanetQueryService` [Medium]
**File:** `game/strategy/services/planet_query_service.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_planet_query_service.py -v`

- [ ] Class with static methods (or `@classmethod`) — services in this file are pure functions of `Planet`:
  - `active_abilities(planet) -> Dict[str, bool]` — moved from `planet.py:177-190`
  - `is_ability_active(planet, ability_key) -> bool` — moved from `planet.py:192-194`
  - `occupied_hexes(planet) -> FrozenSet[HexCoord]` — moved from `planet.py:196-209`
  - `can_build_type(planet, vehicle_type) -> bool` — moved from `planet.py:371-391`
  - Optional: `total_pressure_atm(planet) -> float` if it grows beyond 1 line in future
- [ ] Per-method unit tests with stub planets (build a minimal `Planet(...)` with just the fields each method touches).
- [ ] Module ≤ 250 LOC.
- [ ] **Verify:** all unit tests pass; method outputs bit-identical to today's `Planet` method outputs (golden snapshot or per-test fixture).

**Notes:**

### Task 2.5: Convert `Planet` methods to facade delegates [Medium]
**File:** `game/strategy/data/planet.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_planet.py -v`

- [ ] Replace `active_abilities` body with `return PlanetQueryService.active_abilities(self)` (1-line property).
- [ ] Replace `is_ability_active` body with `return PlanetQueryService.is_ability_active(self, ability_key)`.
- [ ] Replace `occupied_hexes` body with `return PlanetQueryService.occupied_hexes(self)`.
- [ ] Replace `can_build_type` body with `return PlanetQueryService.can_build_type(self, vehicle_type)`.
- [ ] Replace `get_cached_habitability_multiplier` body with: `from game.context import get_default_planet_habitability_service; svc = get_default_planet_habitability_service(); return svc.get_cached(self, race_registry, turn)`.
- [ ] Keep cache fields (`_cached_habitability_multiplier`, `_cached_multiplier_turn`) on the dataclass exactly as today (PROJ-285 invariant).
- [ ] **Verify:** `tests/unit/strategy/data/test_planet.py` green; existing tests touch the new 1-line bodies and route to the services.

**Notes:**

### Task 2.6: Tighten LOC ceiling for `planet.py` [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` (modify)
**Tests:** as named

- [ ] Change `PLANET_LOC_CEILING` from 667 → 350.
- [ ] **Verify:** test passes; pin actual LOC in `Notes:`.

**Notes:**

### Task 2.7: Save round-trip regression test [Simple]
**File:** `tests/integration/strategy/test_save_round_trip_phase2.py` (new — temporary)
**Tests:** as named

- [ ] Construct a Planet with all 47 fields populated (use `Planet(...)` with named kwargs); `to_dict()` → `from_dict()` → `to_dict()` and assert dict equality.
- [ ] Specifically populate `species_configs` (PROJ-284), `intrinsic_abilities` (PROJ-301), `atmosphere`, `populations`, `stockpile`, `deposits`, `staging_yard`, `orders`, the gravity / water / radiation modifier targets, energy fields.
- [ ] **Verify:** dict equality holds (Phase 2 didn't break save format).

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/data/test_planet.py tests/unit/strategy/services/test_planet*.py -v` green
- [ ] `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count ≥ baseline
- [ ] `planet.py` ≤ 350 LOC; AST guard tightened
- [ ] All 47 Planet fields preserved verbatim
- [ ] Habitability acceptance test green (modders can swap calculator via context)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row + Current State pointing to Phase 3
