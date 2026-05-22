# Phase 2: Migrate the explicit `.session` reader tail onto the facade

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate each deferred `.session` reader onto the Phase 1 surfaces
(or an existing one), then REMOVE its allowlist entry from the relevant guard so
the boundary tightens. Per migration: the guard test for that file flips from
allowlisted to enforcing. TDD = the guard (and a behavior test) is the failing test.

---

## Tasks

### Task 2.1: empire_panel_ctrl registries DI [Simple]
**File:** `game/ui/screens/strategy_windows/empire_panel_ctrl.py:62`
**Tests:** `tests/static_guards/test_facade_read_path_session_guard.py`

- [ ] Replace `c.scene.session.registries` with `c.scene.registries`
      (delegates to `facade.session_meta.registries()`, exists).
- [ ] REMOVE allowlist entry `('game/ui/screens/strategy_windows/empire_panel_ctrl.py', 'session.registries')`.
- [ ] Verify: session guard green; empire-panel tests green.

**Notes:**

---

### Task 2.2: BUG-125 gates → active_empire_id [Simple]
**Files:** `strategy_screen_selection.py:93`, `strategy_screen_order_editing.py:42`
**Tests:** `test_facade_read_path_session_guard.py`; existing BUG-125 gate tests

- [ ] Replace `screen.session.active_empire` (id-compare only) with
      `screen.active_empire_id` in both gates (compare `fleet.owner_id != screen.active_empire_id`).
- [ ] REMOVE allowlist entries `('...strategy_screen_selection.py', 'session.active_empire')`
      and `('...strategy_screen_order_editing.py', 'session.active_empire')`. The
      `order_editing` mutator WRITE entry (`session.fleet_mutator`) STAYS (out of scope).
- [ ] Verify: session guard green; BUG-125 hot-seat gate tests green.

**Notes:** `active_empire_id` still routes through the `active_empire` property
until Phase 3 rewires it to `_session`; that's fine — this task only removes the
direct `.session` read.

---

### Task 2.3: event_router race-config → facade.empires.race_config [Medium]
**File:** `game/ui/screens/strategy_event_router.py:223`, `:368`
**Tests:** `test_facade_read_path_session_guard.py`; event-router atmosphere-editor tests

- [ ] FAILING TEST: opening the atmosphere editor for a planet seeds the species-ideal
      button from the facade race-config (not `scene.session.get_empire`). Confirm fails.
- [ ] Replace both `scene.session.get_empire(planet.owner_id)` → race_config blocks
      with `facade.empires.race_config(planet.owner_id)`. Preserve the broad-except
      fallback semantics (`:232`, `:377`).
- [ ] REMOVE allowlist entry `('...strategy_event_router.py', 'session.get_empire')`.
- [ ] Verify: session guard green; editor tests green.

**Notes:**

---

### Task 2.4: Save seams → facade.session_meta.save_current_game [Medium]
**Files (all 3 verified live 2026-05-22):**
- `strategy_game_state_manager.py:397` — AUTO-save `SaveGameService.save_game(self._screen.session)`.
- `strategy_screen_lifecycle.py:155` — MANUAL-save `SaveGameService.save_game(screen.session)` in `on_save_game_click` (`SaveGameService` late-imported `:150`).
- `strategy_screen_lifecycle.py:51` — `on_design_click` workshop context dict `game_session: screen.session`; consumed at `game/app.py:448-486` (reads only `.save_path`).
**Tests:** `test_facade_read_path_session_guard.py`; `test_facade_read_path_imports_guard.py`;
save/load suites

- [ ] FAILING TEST: auto-save after turn calls `facade.session_meta.save_current_game()`
      (assert via stub) and no longer references `SaveGameService` or `self._screen.session`.
- [ ] Replace auto-save `SaveGameService.save_game(self._screen.session)` (`strategy_game_state_manager.py:397`)
      with `self._screen.facade.session_meta.save_current_game()`.
- [ ] Replace manual-save `SaveGameService.save_game(screen.session)` (`strategy_screen_lifecycle.py:155`)
      with `screen.facade.session_meta.save_current_game()`; drop the late `SaveGameService` import (`:150`).
- [ ] `on_design_click` (`strategy_screen_lifecycle.py:51`): replace `game_session: screen.session`
      in the workshop context dict with a scalar `save_path` (re-confirm `app.py:448-486`
      only reads `.save_path` on the live session); update `app.py` to read the scalar.
- [ ] REMOVE: session-guard Category E entries
      `('...strategy_game_state_manager.py', 'session.__extract__')` and
      `('...strategy_screen_lifecycle.py', 'session.__extract__')` (the single lifecycle
      entry covers BOTH `:51` and `:155`); and the import-guard `SaveGameService` TAIL
      entries for `strategy_game_state_manager.py` / `strategy_screen_lifecycle.py` once
      the UI no longer imports `SaveGameService`. NOTE: `save_selection_window.py` still
      imports `SaveGameService` for list/delete/load (out of scope) — that entry STAYS.
- [ ] Verify: both guards green; save/load suites green.

**Notes:** `strategy_game_state_manager.py:164` `self._screen.session.active_empire = current_empire`
is a WRITE (turn rotation), allowlisted as Category B — STAYS, out of scope.

---

### Task 2.5: transfer_controller catalog read [Medium]
**File:** `game/ui/screens/transfer_controller.py:160`
**Tests:** `test_facade_read_path_session_guard.py`; transfer-dialog pod-design tests

- [ ] Replace `session = scene.session` + manual `services.design_catalogs_by_empire`
      walk with `scene.facade.facade_state.get_design_catalog_for_empire(scene.viewing_empire_id)`
      (use `viewing_empire_id`, NOT active-turn empire — decisions.md).
- [ ] REMOVE allowlist entry `('...transfer_controller.py', 'session.__extract__')`.
- [ ] Verify: session guard green; pod-design discovery tests green.

**Notes:**

---

### Task 2.6: Fleet-report spaceyard BRIDGE → has_spaceyard projection [Complex]
**Files:** `fleet_data_source.py:238-245` (`_format_spaceyard`),
`fleet_report_filters.py:157-165`, `:300-303`. The report path runs on raw
`ShipInstance` (`fleet_report_window.py:185,238`, `fleet_report_view_model.py:49,152`).
**Tests:** `test_facade_read_path_imports_guard.py`; fleet-report filter/sort/format tests

- [ ] **Post-flesh review B3:** the report does NOT consume `ShipInfo` today, so a
      bridge is required, not a one-line swap. FAILING TEST: the spaceyard column /
      filter / sort reads the facade-projected `has_spaceyard`, not
      `FleetCapabilityCalculator`. Confirm fails first.
- [ ] Build the bridge: in the report path, fetch `facade.fleets.get(fleet_id)` →
      `FleetInfo.ships` and build an `instance_id → has_spaceyard` lookup; the row
      formatter (`_format_spaceyard`) + filter + sort key read from that lookup.
      Decide where the lookup is held (view-model is the natural home) and record it.
- [ ] Replace the three `FleetCapabilityCalculator.ship_has_spaceyard(ship)` calls.
- [ ] REMOVE the 2 FLEETCAP import-guard entries (`fleet_data_source.py`,
      `fleet_report_filters.py`).
- [ ] Verify: import guard green; fleet-report filter + sort + spaceyard-column tests green.

**Notes:** if the bridge proves too entangled with the report's raw-`ShipInstance`
architecture, escalate — it may warrant its own phase. The DTO field (Task 1.4)
is cheap; the consumer rewire is the real work.

---

### Task 2.7: colony_has_planetary_yard → has_build_yard (with query wiring) [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py` (`_show_planet_report`
`:134,193,241`, gate `:277`)
**Tests:** `test_facade_read_path_imports_guard.py`; detail-formatter Build-Yard tests

- [ ] **Post-flesh review B4:** `_show_planet_report` renders a live `Planet`, not a
      `PlanetInfo`. FAILING TEST: the Build-Yard button gate reads the facade-projected
      `has_build_yard`, not `colony_has_planetary_yard`. Confirm fails first.
- [ ] Inside `_show_planet_report`, query `facade.planets.get(obj.id)` (or a narrow
      helper) and read `has_build_yard` off the DTO; replace the
      `colony_has_planetary_yard(colony, registries)` import + call.
- [ ] REMOVE the CLUSTER import-guard entry
      `('...strategy_detail_formatter.py', 'game.strategy.data.build_queue_source', 'colony_has_planetary_yard')`.
- [ ] Verify: import guard green; detail-formatter tests green.

**Notes:** the formatter already has the screen/facade in scope; confirm the planet
id is available at the gate (`obj.id`).

---

## Phase Completion Checklist
- [ ] All task checkboxes checked; every migrated site's allowlist entry REMOVED
- [ ] Both read-path guards green (remaining allowlist = pass-throughs +
      mutator WRITE seams + the still-deferred broad-pass-through readers)
- [ ] `python Tools/test_sharded/test_sharded.py` green (or targeted + `--testmon`)
- [ ] Update status to `Complete`; update plan.md phase table + Current State
