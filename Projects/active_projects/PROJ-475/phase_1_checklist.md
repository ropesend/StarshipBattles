# Phase 1: New facade read surfaces

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add the four facade read surfaces the Phase 2 reader migrations
need, so each migration has a target. Read-only projections, no behavior change.
Strict TDD: write the failing facade test first, run to confirm fail, implement.

---

## Tasks

### Task 1.1: Empire race-config read surface [Medium]
**Files:** `game/strategy/facade/grouped_namespaces.py` (`FacadeEmpireQueries`),
`game/strategy/facade/slices/empire_slice.py`, optionally
`game/strategy/facade/dto/empire_dto.py` (`EmpireIdentityInfo`).
**Tests:** `tests/unit/strategy/facade/test_empire_queries.py` (or nearest existing
empire-slice test module) — `pytest tests/unit/strategy/facade -k race_config`

- [x] FAILING TEST: `facade.empires.race_config(empire_id)` returns the empire's
      `race_config` (and `race_id`) for a seeded empire; returns `None` for unknown id.
      Confirm it fails (no such method) before implementing.
- [x] Add `EmpireSlice.get_empire_race_config(empire_id)` reading
      `_state.get_empire_by_id(empire_id)` → `.race_config`. Mirror the
      `RaceLibrary` fallback the UI does today (`strategy_event_router.py:226-231`)
      OR return raw and keep the fallback in the caller — decide and record.
- [x] Add `FacadeEmpireQueries.race_config(empire_id)` delegating to the slice,
      returning the live `RaceConfig` or `None`.
- [x] **Post-flesh review B12:** do NOT add an `EmpireIdentityInfo` DTO — `Empire`
      owns `race_config` directly and there is no `Empire.race_id` field. Return the
      `RaceConfig` (immutable race-definition value object). Record in decisions.md.
- [x] Verify: test green; `pytest tests/unit/strategy/facade --testmon` green.

**Notes:** DECISION: slice returns raw `empire.race_config` (via `getattr(empire,
"race_config", None)`); the `RaceLibrary` fallback stays in the caller
(event_router) so this surface returns only what the empire owns. New test:
`tests/unit/strategy/facade/test_empire_race_config.py` (3 cases). Implemented in
`empire_slice.py` (`get_empire_race_config`) + `grouped_namespaces.py`
(`FacadeEmpireQueries.race_config`).

---

### Task 1.2: Facade save-action surface [Medium]
**Files:** `game/strategy/facade/grouped_namespaces.py` (`FacadeSessionInfo`),
`game/strategy/facade/slices/event_slice.py` (host slice).
**Tests:** `tests/unit/strategy/facade/test_session_meta_queries.py` —
`pytest tests/unit/strategy/facade -k save_current_game`

- [x] FAILING TEST: `facade.session_meta.save_current_game()` returns
      `(success, message, save_path)` and internally calls
      `SaveGameService.save_game(session, save_name)` (assert via a stubbed service or
      a tmp save dir). Pass-through `save_name=None`. Confirm fails first.
- [x] Implement `FacadeSessionInfo.save_current_game(save_name=None)` calling
      `SaveGameService.save_game(self._session, save_name)`. The namespace already
      holds `_session` (`grouped_namespaces.py:307-314`). Keep `SaveGameService`
      engine-internal — the UI must NOT import it after Phase 2.
- [x] Verify: test green; existing save/load suites still green
      (`pytest tests/ -k save --testmon`).

**Notes:** Implemented `FacadeSessionInfo.save_current_game(save_name=None)` —
late-imports `SaveGameService` inside the method (engine-internal) and calls
`SaveGameService.save_game(self._session, save_name)`, returning the triple.
New test: `tests/unit/strategy/facade/test_session_meta_save.py` (2 cases,
patches `SaveGameService.save_game`). Save/load suites green (329 passed).

---

### Task 1.3: Colony build-yard projection [Simple]
**Files:** `game/strategy/facade/dto/planet_dto.py` (`PlanetInfo`) and/or
`game/strategy/facade/dto/empire_dto.py` (`ColonySummary`).
**Tests:** `tests/unit/strategy/facade/test_planet_dto.py` (nearest existing) —
`pytest tests/unit/strategy/facade -k has_build_yard`

- [x] FAILING TEST: `PlanetInfo.has_build_yard` is `True` when the colony has a
      planetary yard OR a space shipyard, else `False`. Mirror the truth of
      `colony_has_planetary_yard(colony, registries)` (`build_queue_source.py:132-172`)
      ORed with `has_space_shipyard`. Confirm fails first.
- [x] Add `has_build_yard` to the DTO + populate in `from_planet` / slice projection.
      If `colony_has_planetary_yard` needs `registries`, resolve them at slice
      projection time (the DTO `from_*` cannot reach registries — mirror PROJ-472's
      `owner_system_name` slice-resolution pattern).
- [x] Verify: test green; targeted suite green.

**Notes:** `PlanetInfo.has_build_yard: bool = False` added; `from_planet` gains a
keyword-only `has_planetary_yard` param ORed with `planet.has_space_shipyard`.
`PlanetSlice._project_planet` / `_resolve_has_planetary_yard` resolve the
planetary-yard bit against `session.registries` (mirrors `_resolve_owner_scalars`)
and feed it in; both `get_planet` and `get_planets_at_hex` route through
`_project_planet`. The resolver degrades to `False` on `(AttributeError, TypeError)`
for stub colonies. New test: `test_planet_has_build_yard.py` (5 cases). Updated two
pre-existing `test_planet_slice.py` `from_planet` stubs to accept `**kwargs`.

---

### Task 1.4: Per-ship spaceyard projection on `ShipInfo` [Medium]
**Files:** `game/strategy/facade/dto/fleet_dto.py` (`ShipInfo` `:127`, built by
`FleetInfo.from_fleet` via `fleet_slice.py:60`).
**Tests:** `tests/unit/strategy/facade/test_fleet_dto.py` (nearest) —
`pytest tests/unit/strategy/facade -k has_spaceyard`

- [x] FAILING TEST: `ShipInfo.has_spaceyard` equals
      `FleetCapabilityCalculator.ship_has_spaceyard(ship)` for the source ship.
      Confirm fails first.
- [x] Populate `has_spaceyard` in `ShipInfo` projection (call the calculator at
      projection time, in the facade/slice layer — keep it OUT of the UI).
- [x] Verify: test green; targeted suite green.

**Notes (impl):** `ShipInfo.has_spaceyard: bool = False` added; populated in
`FleetInfo.from_fleet` via new static helper `_ship_has_spaceyard(ship)` that
late-imports `FleetCapabilityCalculator` and degrades to `False` on
`(ValidationException, AttributeError)` for stub ships. New test:
`test_ship_has_spaceyard.py` (3 cases). **Post-flesh review B3:** `ShipInfo` exists and is built by
`FleetInfo.from_fleet`, but the fleet report does NOT consume it yet (it runs on
raw `ShipInstance`). The CONSUMER bridge is Phase 2 Task 2.6, not here. This task
only adds the DTO field.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/facade --testmon` green (425 passed); save/load suites green (329 passed)
- [x] No UI files touched yet (Phase 2 consumes these surfaces)
- [x] Update status at top to `Complete`; update plan.md phase table + Current State
