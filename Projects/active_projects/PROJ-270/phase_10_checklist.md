# Phase 10: Visual-Mode Contract Completion + Shim Eradication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 10`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started — BLOCKER FOR ARCHIVAL
**Risk:** MEDIUM-HIGH (touches live visual-mode code; migrates ~60 legacy tests)
**Depends On:** Phase 9 (to avoid double-migrating during a math fix)
**Objective:** Eradicate the compat shims that PROJ-270 closure retained as "test-convenience" or "scope trim". The visual-mode entry path must genuinely route through `start_engine_from_spec`, not through a hand-rolled replica. The `BattleScreen.start(team0, team1)` bypass + `_build_fallback_outcome` synthesizer must go. `ReturnDestination` re-export must be deleted.

## Context (from skeptic audit)

Converging findings from 3 independent skeptics:
- **Visual mode never routes through `start_engine_from_spec`.** 3 call sites (`app.py:572-574`, `test_lab/screen.py:437-439`, `test_execution_service.py:80-82`) duplicate the `engine.boundary = spec.boundary; engine.modifier_stack = spec.modifier_stack` plumbing by hand. Task 4.2 explicitly trimmed this refactor. Any future `BattleSpec` field will silently drop for visual mode.
- **`BattleScreen.start(team0, team1)` + `_build_fallback_outcome`** — two layers of shims to preserve one legacy entry point. `_build_fallback_outcome` synthesizes a `BattleOutcome` with hardcoded `seed=0`, `telemetry_level=NORMAL` (with empty aggregator data), and `end_reason=TEAM_ELIMINATED` regardless of what actually happened.
- **`BattleScreen._run_single_tick` else-branch** (`if self._controller: ... else: self.engine.update()`) — direct engine update path that no regression guard covers.
- **`battle_config.py` re-exports `ReturnDestination`** with self-admitted "backwards compatibility" docstring. 5 importers still use the old path.
- **`set_spec` public + optional `spec=None` on configure** — both retained solely for the legacy `BattleScreen.start` + ~60 unit tests.

---

## Tasks

### Task 10.1: `BattleController.start_from_spec(spec, ai_factory, ship_builder)` [Complex]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ -q`

- [ ] Write failing test: `controller.start_from_spec(spec)` produces a running engine with `engine.boundary == spec.boundary` and `engine.modifier_stack is spec.modifier_stack` — without any manual `engine.boundary = ...` assignment from the caller
- [ ] Run — fails (method doesn't exist)
- [ ] Implement `start_from_spec` that internally calls `start_engine_from_spec(spec, ...)` (the same code path `run_battle` uses)
- [ ] Ensure it takes over the per-frame ticking shape so visual mode can drive `.update()` per-frame afterwards
- [ ] Run — passes

---

### Task 10.2: Migrate 3 visual call sites [Medium]
**File:** `game/app.py:568-576`, `game/ui/screens/test_lab/screen.py:432-453`, `combat_lab/services/test_execution_service.py:76-95`

- [ ] Delete the hand-rolled `engine.boundary = spec.boundary; engine.modifier_stack = spec.modifier_stack; materialize_spec_ships(...); controller.add_ships(...); controller.start()` block from each call site
- [ ] Replace with `controller.start_from_spec(spec, ai_factory=...)`
- [ ] Run `pytest tests/` — ≥ baseline; no new failures

---

### Task 10.3: Make `spec` required on `configure` [Medium]
**File:** `game/simulation/battle_controller.py`

- [ ] Change signature from `configure(self, config, spec: Optional[BattleSpec] = None)` to `configure(self, config, spec: BattleSpec)` — required positional/keyword
- [ ] Remove the spec-None branch
- [ ] Migrate ~60 legacy unit tests that call `configure(basic_config)` to `configure(basic_config, spec=SPEC_FIXTURE)`. Create a shared test fixture `tests/fixtures/specs.py::minimal_battle_spec` if one doesn't exist
- [ ] Delete `set_spec` public method (it's now redundant — configure sets it)
- [ ] Delete the regression guard `test_battle_controller_has_set_spec` (no longer needed; configure's required-spec signature is the guard)

---

### Task 10.4: Delete `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` [Complex]
**File:** `game/ui/screens/battle_screen.py`

- [ ] Audit callers of `BattleScreen.start(team0, team1)` — grep; likely test-only + `app.py` possibly uses it
- [ ] For each caller: migrate to constructing a `BattleSpec` (use `build_test_battle_spec` or `build_manual_battle_spec` depending on context)
- [ ] Delete `BattleScreen.start(team0_ships, team1_ships, ...)` method entirely
- [ ] Delete `BattleScreen._build_fallback_outcome()` method
- [ ] Delete `BattleScreen._get_or_build_outcome()` method (if exists as separate dispatcher)
- [ ] Delete the `else: self.engine.update()` branch in `_run_single_tick` — if `self._controller is None` at ticking time, raise `StateException`

---

### Task 10.5: Delete `ReturnDestination` re-export from `battle_config.py` [Simple]
**File:** `game/simulation/battle_config.py:11-25`, 5 importers

- [ ] Grep for `from game.simulation.battle_config import ReturnDestination` — expect ~5 hits in production code
- [ ] sed-replace all 5 importers to `from game.core.return_destination import ReturnDestination`
- [ ] Delete the re-export + backwards-compat docstring block from `battle_config.py`
- [ ] Run pytest — passes

**Notes:** Skeptic called this a "10-minute task that the project left hanging". Do not carry it into Phase 10's completion without doing it.

---

### Task 10.6: Direct `engine.update()` / `engine.start()` regression guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py` (extend)

- [ ] Add `TestNoDirectEngineUpdate.test_no_unwhitelisted_engine_update` — grep-based guard that scans live code for `engine\.update\(\)` and `engine\.start\(\)` outside `BattleEngine` / `BattleService.create_battle` / `start_engine_from_spec` / `BattleController._run_single_tick` (controller method is OK; direct `self.engine.update()` from screens is NOT OK)
- [ ] Add to the list of regression guards in findings/acceptance_audit.md

---

### Task 10.7: Resolve `load_state` boundary degradation [Simple]
**File:** `game/simulation/battle_controller.py:478-483`

Skeptic finding: `load_state` silently defaults to `UnboundedRegion` on restore, losing retreat behavior.

Pick one:
- [ ] Option A: **Delete `load_state` entirely** if no production caller exists (grep shows only tests + `BattleStateManager` reference it). Saves are disposable per CLAUDE.md.
- [ ] Option B: **Persist boundary in `BattleState`** — add `boundary: Optional[BoundaryRegion]` field, extend `BattleStateManager.capture_from_engine` + `restore_config_from_state` to round-trip it.

Document decision in `decisions.md`.

---

### Task 10.8: Phase 10 regression gate
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — baseline green
- [ ] Combat Lab fast + full green
- [ ] 28 regression guards + new Task 10.6 guard all green
- [ ] Grep audit: no `BattleScreen.start(team0` call sites anywhere
- [ ] Grep audit: no `spec=None` in `configure` callers anywhere
- [ ] Grep audit: `set_spec` method no longer exists on `BattleController`

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Visual-mode battles flow through `start_from_spec` (no hand-rolled engine.boundary plumbing)
- [ ] Shims deleted: `BattleScreen.start(team0, team1)`, `_build_fallback_outcome`, `_get_or_build_outcome`, `set_spec` public method, `spec=None` on configure, `ReturnDestination` re-export
- [ ] Direct-engine regression guard in place
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
