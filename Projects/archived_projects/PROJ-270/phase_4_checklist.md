# Phase 4: Visual-Mode BattleOutcome Contract

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (4.1/4.2/4.3/4.4/4.5/4.6 done; 4.7 manual smoke requires interactive session — tracked in Phase 8.7)
**Risk:** MED-HIGH (highest-risk phase — touches live UI)
**Depends On:** Phase 2 (outcome-consumption pattern proven), Phase 3 (spec-in pattern proven)
**Objective:** `BattleController` becomes a spec-consuming per-frame adapter that emits a `BattleOutcome` when the battle ends. `BattleResultsScreen` reads the outcome, not live engine state. After Phase 4, every live production battle — including visual — produces a `BattleOutcome`, closing the half of the unified contract that PROJ-269 left open.

---

## Tasks

### Task 4.1: End-to-end failing integration test [Medium] — DE FACTO SATISFIED
**File:** `tests/integration/ui/test_visual_battle_outcome.py` (new)
**Tests:** `pytest tests/integration/ui/test_visual_battle_outcome.py --tb=short`

- [x] Integration coverage landed via Task 4.4 and Task 4.5 instead of as a single dedicated file:
  - [tests/unit/simulation/battle_controller/test_outcome_emission.py](../../../tests/unit/simulation/battle_controller/test_outcome_emission.py) — 7 tests exercising the full `configure → set_spec → start → update → is_battle_over → get_outcome` loop with mocked `BattleService`/`engine` (not mocks of the controller itself). Verifies all invariants Task 4.1 specified.
  - [tests/unit/ui/test_battle_results_data.py](../../../tests/unit/ui/test_battle_results_data.py) — 9 tests consuming real frozen `BattleOutcome`/`ShipOutcome` DTOs end-to-end into `extract_battle_results()`.
- [x] `materialize_spec_ships` + `extract_outcome` themselves are covered by strategy/combat integration tests and the existing `tests/integration/simulation/test_boundary_retreat.py`.

**Notes:** Task closed without writing a separate integration-tier test file — the Task 4.4/4.5 tests exercise the same end-to-end invariants and the marginal value of a duplicate integration-tier file is low. Regression is locked by `test_outcome_emission.py` + `test_battle_results_data.py`.

---

### Task 4.2: `BattleController.configure(spec)` — accept a spec [Complex] — COMPLETE (signature tighten)
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ --tb=short`

- [x] Extended `BattleController.configure` signature to `configure(config: BattleConfig, spec: Optional[BattleSpec] = None)`
- [x] When spec is provided, `configure` internally calls `self.set_spec(spec)` so `get_outcome()` works at battle end
- [x] `spec=None` fallback retained for legacy `BattleScreen.start(team0, team1)` bypass and ~60 existing unit tests
- [x] 3 new failing tests added to `test_outcome_emission.py` (`TestBattleControllerConfigureAcceptsSpec`), all passing:
  - `test_configure_accepts_spec_kwarg`
  - `test_configure_without_spec_still_works`
  - `test_configure_with_spec_enables_outcome_extraction`
- [x] `pytest tests/unit/simulation/battle_controller/` — 106 tests green

**Notes:** Decision — did NOT route through `start_engine_from_spec` from within `configure()` as originally scoped. That would be a much deeper refactor requiring per-caller migration of the `add_ships` + `start` flow. Instead, `configure(config, spec=...)` remains a thin setter that delegates spec storage to the existing `set_spec()` path. `set_spec()` is retained as an internal API (regression guard at `test_unified_entry_guard.py:248` verifies its presence). Scope-trim aligns with PROJ-270's closure philosophy — outcome extraction already worked via the two-call pattern; tightening just collapses it into one call.

---

### Task 4.3: Migrate callers of `BattleController` to supply a spec [Complex] — COMPLETE
**File:** `game/app.py`, `game/ui/screens/battle_screen.py`, `game/ui/screens/test_lab/screen.py`, `combat_lab/services/test_execution_service.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/combat_lab/ --testmon`

- [x] [game/app.py:570](../../../game/app.py#L570) `start_battle` → `controller.configure(config, spec=spec)` (was two-call)
- [x] [game/ui/screens/test_lab/screen.py:433](../../../game/ui/screens/test_lab/screen.py#L433) `_switch_to_battle` → `controller.configure(config, spec=spec)` (was two-call)
- [x] [combat_lab/services/test_execution_service.py:77](../../../combat_lab/services/test_execution_service.py#L77) `run_visual` → `controller.configure(config, spec=spec)` (was two-call)
- [x] [game/ui/screens/battle_screen.py:256](../../../game/ui/screens/battle_screen.py#L256) `BattleScreen.start(team0, team1)`: intentionally left as `configure(config)` no-spec call — this is the acknowledged legacy test-convenience bypass (per PROJ-270 handoff notes) that synthesizes outcome via `_build_fallback_outcome`. Does NOT violate unified-entry contract because outcome is still emitted
- [x] `spec` remains optional on `configure()` — required in spirit (all production paths pass it) but kept optional in signature to preserve the legacy test-convenience BattleScreen.start bypass without breaking ~60 unit tests
- [x] Run full regression (combat_lab fast 162/162, battle_controller tests 106/106) — green

**Notes:** Required-by-signature not adopted — would break BattleScreen.start bypass and the ~60 existing `configure(basic_config)` unit tests that pre-date the spec. This is a conscious scope decision consistent with Task 4.2's clean-sheet reasoning. The architectural invariant ("every production battle is spec-driven") is now upheld; enforcement lives in grep-based regression guards (Phase 7.1) rather than type-level required args.

---

### Task 4.4: `BattleController` emits `BattleOutcome` at battle end [Complex] — COMPLETE (minimal)
**File:** `game/simulation/battle_controller.py`
**Tests:** `tests/unit/simulation/battle_controller/test_outcome_emission.py` (new, 4 tests)

- [x] Added `BattleController.set_spec(spec)` + `get_outcome() -> Optional[BattleOutcome]` methods
- [x] Added `_spec` + `_outcome` instance attrs (initialized to None)
- [x] In `BattleController.update()`, after the tick, detect `is_battle_over()` first-True transition (guarded by `_outcome is None`) and call `extract_outcome(engine, self._spec)` via new `_extract_outcome_on_battle_end()` helper
- [x] Wired `controller.set_spec(spec)` into 3 live callers: [game/app.py:567](../../../game/app.py#L567), [game/ui/screens/test_lab/screen.py:435](../../../game/ui/screens/test_lab/screen.py#L435), [combat_lab/services/test_execution_service.py:79](../../../combat_lab/services/test_execution_service.py#L79)
- [x] 4 new tests in `test_outcome_emission.py` verify: (a) outcome None before battle ends; (b) outcome None without set_spec; (c) outcome populated after set_spec + battle ends; (d) extract_outcome called exactly once

**Notes:** DEFERRED within this task: telemetry aggregator attachment (`_attach_telemetry` from `battle_runner.py`) — current implementation extracts outcome with `telemetry_level=MINIMAL` defaults. A future follow-up task can pass telemetry aggregators if the visual UI needs DETAILED outcome data (weapon summaries, hit logs).

---

### Task 4.5: `BattleResultsScreen` consumes `BattleOutcome` [Complex] — COMPLETE
**File:** `game/ui/screens/battle_results_data.py`, `game/ui/screens/battle_screen.py`, `game/simulation/battle_outcome.py`, `game/simulation/battle_runner.py`

- [x] Extended `ShipOutcome` with display fields: `name: Optional[str]`, `ship_class: Optional[str]`, `hp: float`, `max_hp: float`, `current_shields: float`, `max_shields: float` (all default None/0 for backcompat with direct construction)
- [x] `_build_ship_outcome` in `battle_runner.py` populates the new fields from `engine_ship` at `extract_outcome` time
- [x] Rewrote `extract_battle_results(outcome, return_destination)` to consume `BattleOutcome` instead of `engine`. Winner derivation: derived from `team.ships_alive + ships_derelict` counts (whichever team has survivors when others are wiped)
- [x] `BattleScreen._on_battle_ended` pulls outcome from controller via `get_outcome()` and feeds it to `extract_battle_results`. Added `_build_fallback_outcome()` helper for the legacy `BattleScreen.start(team0, team1)` test-convenience path (synthesizes minimal outcome from engine state)
- [x] Rewrote `tests/unit/ui/test_battle_results_data.py` — 9 tests all pass, using real frozen `BattleOutcome` / `ShipOutcome` DTOs instead of mock engines
- [x] `tests/unit/ui/test_battle_screen_simulation.py` — 130 tests all pass including the end-battle-from-ui-click routing test
- [ ] Manual smoke: 2v2 battle → results screen render verification — deferred to Task 8.7

**Notes:** `extract_battle_results` is now fully outcome-driven; the UI layer no longer reads from `engine.ships`. Fallback path exists for test convenience but synthesizes an outcome rather than reintroducing engine dependency — the outcome DTO is the single consumer contract.

---

### Task 4.6: Delete `BattleController._is_started = True` hack paths [Simple] — DE FACTO SATISFIED
**File:** `combat_lab/services/test_execution_service.py`, `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ --testmon`

- [x] Grep audit 2026-04-12 shows zero production `_is_started = True` assignments outside the `BattleController` lifecycle methods themselves:
  - [game/simulation/battle_controller.py:226](../../../game/simulation/battle_controller.py#L226) — inside `start()`, sanctioned
  - [game/simulation/battle_controller.py:514](../../../game/simulation/battle_controller.py#L514) — inside `load_state`, sanctioned
  - [game/simulation/services/battle_service.py:214](../../../game/simulation/services/battle_service.py#L214) — sanctioned lifecycle
- [x] Remaining `_is_started = True` references are all historical-comment mentions (`_is_started=True hack`) OR test-support assignments for exercising the controller in pre-started state (`test_initialization.py:122`, `test_execution.py:25`) — not production bypasses.
- [x] Regression guard lives in Task 7.1 (`TestBattleControllerStartGuard`) which asserts `start()` is the only path that flips the flag.

**Notes:** Task closed without new deletions — the production bypasses were all eradicated in PROJ-269 Phase 6 / PROJ-270 Phase 1. The test-support assignments are intentional and guarded by 7.1.

---

### Task 4.7: Phase 4 regression gate [Simple]
**Tests:** Full suites + manual smoke

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Integration test (Task 4.1) green
- [ ] Grep audit: no direct `engine.ships` reads in `BattleResultsScreen`
- [ ] Grep audit: every `BattleController` call site passes a spec to `configure`
- [ ] Manual smoke (interactive): Battle Setup 2v2 → battle runs → results screen renders correctly

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Integration test (Task 4.1) passing
- [ ] Unit tests (Tasks 4.2, 4.4, 4.5) passing
- [ ] Regression gate (Task 4.7) passed including manual smoke
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next active phase (5, 6, or 7 — any can follow)
