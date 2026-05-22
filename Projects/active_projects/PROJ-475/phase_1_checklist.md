# Phase 1: New facade read surfaces

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] FAILING TEST: `facade.empires.race_config(empire_id)` returns the empire's
      `race_config` (and `race_id`) for a seeded empire; returns `None` for unknown id.
      Confirm it fails (no such method) before implementing.
- [ ] Add `EmpireSlice.get_empire_race_config(empire_id)` reading
      `_state.get_empire_by_id(empire_id)` → `.race_config`. Mirror the
      `RaceLibrary` fallback the UI does today (`strategy_event_router.py:226-231`)
      OR return raw and keep the fallback in the caller — decide and record.
- [ ] Add `FacadeEmpireQueries.race_config(empire_id)` delegating to the slice,
      returning the live `RaceConfig` or `None`.
- [ ] **Post-flesh review B12:** do NOT add an `EmpireIdentityInfo` DTO — `Empire`
      owns `race_config` directly and there is no `Empire.race_id` field. Return the
      `RaceConfig` (immutable race-definition value object). Record in decisions.md.
- [ ] Verify: test green; `pytest tests/unit/strategy/facade --testmon` green.

**Notes:**

---

### Task 1.2: Facade save-action surface [Medium]
**Files:** `game/strategy/facade/grouped_namespaces.py` (`FacadeSessionInfo`),
`game/strategy/facade/slices/event_slice.py` (host slice).
**Tests:** `tests/unit/strategy/facade/test_session_meta_queries.py` —
`pytest tests/unit/strategy/facade -k save_current_game`

- [ ] FAILING TEST: `facade.session_meta.save_current_game()` returns
      `(success, message, save_path)` and internally calls
      `SaveGameService.save_game(session, save_name)` (assert via a stubbed service or
      a tmp save dir). Pass-through `save_name=None`. Confirm fails first.
- [ ] Implement `FacadeSessionInfo.save_current_game(save_name=None)` calling
      `SaveGameService.save_game(self._session, save_name)`. The namespace already
      holds `_session` (`grouped_namespaces.py:307-314`). Keep `SaveGameService`
      engine-internal — the UI must NOT import it after Phase 2.
- [ ] Verify: test green; existing save/load suites still green
      (`pytest tests/ -k save --testmon`).

**Notes:**

---

### Task 1.3: Colony build-yard projection [Simple]
**Files:** `game/strategy/facade/dto/planet_dto.py` (`PlanetInfo`) and/or
`game/strategy/facade/dto/empire_dto.py` (`ColonySummary`).
**Tests:** `tests/unit/strategy/facade/test_planet_dto.py` (nearest existing) —
`pytest tests/unit/strategy/facade -k has_build_yard`

- [ ] FAILING TEST: `PlanetInfo.has_build_yard` is `True` when the colony has a
      planetary yard OR a space shipyard, else `False`. Mirror the truth of
      `colony_has_planetary_yard(colony, registries)` (`build_queue_source.py:132-172`)
      ORed with `has_space_shipyard`. Confirm fails first.
- [ ] Add `has_build_yard` to the DTO + populate in `from_planet` / slice projection.
      If `colony_has_planetary_yard` needs `registries`, resolve them at slice
      projection time (the DTO `from_*` cannot reach registries — mirror PROJ-472's
      `owner_system_name` slice-resolution pattern).
- [ ] Verify: test green; targeted suite green.

**Notes:**

---

### Task 1.4: Per-ship spaceyard projection on `ShipInfo` [Medium]
**Files:** `game/strategy/facade/dto/fleet_dto.py` (`ShipInfo` `:127`, built by
`FleetInfo.from_fleet` via `fleet_slice.py:60`).
**Tests:** `tests/unit/strategy/facade/test_fleet_dto.py` (nearest) —
`pytest tests/unit/strategy/facade -k has_spaceyard`

- [ ] FAILING TEST: `ShipInfo.has_spaceyard` equals
      `FleetCapabilityCalculator.ship_has_spaceyard(ship)` for the source ship.
      Confirm fails first.
- [ ] Populate `has_spaceyard` in `ShipInfo` projection (call the calculator at
      projection time, in the facade/slice layer — keep it OUT of the UI).
- [ ] Verify: test green; targeted suite green.

**Notes:** **Post-flesh review B3:** `ShipInfo` exists and is built by
`FleetInfo.from_fleet`, but the fleet report does NOT consume it yet (it runs on
raw `ShipInstance`). The CONSUMER bridge is Phase 2 Task 2.6, not here. This task
only adds the DTO field.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/facade --testmon` green; save/load suites green
- [ ] No UI files touched yet (Phase 2 consumes these surfaces)
- [ ] Update status at top to `Complete`; update plan.md phase table + Current State
