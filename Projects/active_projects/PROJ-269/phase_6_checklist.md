# Phase 6: Delete Legacy Paths

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** With all three contexts (Combat Lab, Battle Setup, Strategy) proven to run through `run_battle(spec)`, delete the legacy scaffolding. `BattleMode` enum, `BattleModeHandler` hierarchy, all `create_*_battle` half-factories, `SimulationBattleResolver` ship mutation, `FleetBattleAdapter.update_from_battle_results`, Combat Lab direct-engine construction, and the Phase 1 `USE_BATTLE_RUNNER` feature flag — all removed. `run_battle` is the only way into the simulator. Documentation rewritten to reflect the unified flow.

---

### Task 6.1: Delete `BattleModeHandler` classes [Medium]
**File:** `game/simulation/combat/battle_mode_handler.py`

**Tests:** `pytest tests/unit/simulation/combat/ --testmon`

- [ ] Grep for every importer of `BattleModeHandler`, `ManualBattleModeHandler`, `TestBattleModeHandler`, `StrategyBattleModeHandler`, `HypotheticalBattleModeHandler`, `get_handler_for_mode`
- [ ] Update each importer to use the equivalent `BattleSpec` fields instead
- [ ] Delete `game/simulation/combat/battle_mode_handler.py`
- [ ] Delete `tests/unit/simulation/combat/test_battle_mode_handler.py` (if exists) — replaced by the DTO-level tests
- [ ] Verify: `pytest tests/` green; no broken imports

**Notes:**

---

### Task 6.2: Remove `BattleMode` enum and reshape/delete `BattleConfig` [Medium]
**File:** `game/simulation/battle_config.py`

**Tests:** Full pytest suite

- [ ] Grep for every importer of `BattleMode`, `BattleConfig`
- [ ] Determine if `BattleConfig` still holds useful fields after removing `mode`, `return_destination`, `show_results`, `start_paused`, `allow_retreat`, `allow_reinforcements`, `headless`, `source_fleets`, `per_tick_callback`, `team_modifiers`, `global_modifiers`, `environmental_effects`, `test_scenario`:
  - If everything moved to `BattleSpec`: **delete the file entirely**
  - If a subset remains (operational settings like `headless`, `per_tick_callback`): reshape as `BattleRunOptions` and pass separately to `run_battle` (already supported as function arguments per [design.md §3](design.md))
- [ ] Update every importer
- [ ] Verify: suite green; file is either deleted or drastically reduced

**Notes:**

---

### Task 6.3: Delete `create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle` [Medium]
**File:** `game/ui/services/battle_factories.py`

**Tests:** Full pytest suite

- [ ] Grep for every call site of these four factories (expect: `game/app.py::start_battle`, possibly others after prior phases have migrated callers)
- [ ] Replace each with the appropriate `build_*_battle_spec(...)` + `run_battle(spec, ...)` pattern
- [ ] Delete the four factory functions
- [ ] Consider: does `battle_factories.py` have a purpose after this? If only the four deleted functions lived there, **delete the file entirely**
- [ ] Update `create_started_battle_controller` — either remove (fully obsolete), or preserve if something external still calls it (unlikely)
- [ ] Verify: suite green; the UI's battle-start flow goes through `run_battle`

**Notes:**

---

### Task 6.4: Remove `FleetBattleSetupScreen._apply_complex_modifiers` in-place mutation [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`

**Tests:** Manual: launch Battle Setup, toggle complex modifiers, start battle — modifier effects still visible

- [ ] The modifier logic moved into `build_manual_battle_spec` in Phase 1 (via `ModifierStack`). Today's `_apply_complex_modifiers` mutates ships in-place before `create_manual_battle` is called.
- [ ] Remove `_apply_complex_modifiers` and its callers
- [ ] Replace `self._start_battle` to build a spec via `build_manual_battle_spec` and call `run_battle` directly
- [ ] Manual smoke: launch Battle Setup; toggle a modifier like "shield arc boost"; start battle; confirm the modifier visibly affects the battle

**Notes:**

---

### Task 6.5: Remove `SimulationBattleResolver` ship-mutation side channels [Medium]
**File:** `game/strategy/combat/simulation_battle_resolver.py`

**Tests:** `pytest tests/unit/strategy/combat/ --testmon`

- [ ] Today `SimulationBattleResolver` mutates ship shield values + attributes with environmental_effects and team/global modifiers before handing to the engine. Post-Phase 5, those modifiers flow via `ModifierStack`.
- [ ] Remove the pre-battle mutation logic
- [ ] Simplify `resolve_battle(...)` to: `spec = build_strategy_battle_spec(...)` + `return run_battle(spec, ai_factory=self._ai_factory)`
- [ ] Verify: strategy-mode battles still produce equivalent outcomes (regression via integration test)

**Notes:**

---

### Task 6.6: Remove `FleetBattleAdapter.update_from_battle_results` [Medium]
**File:** `game/strategy/fleets/fleet_battle_adapter.py`

**Tests:** `pytest tests/unit/strategy/fleets/ --testmon`

- [ ] After Phase 2 the strategy `PostBattleHook` handles outcome → fleet updates. The adapter method is now unused.
- [ ] Grep for callers — should be zero (PostBattleHook replaced the one caller, `ConflictResolutionEngine.resolve_combat_simulated` or similar)
- [ ] Delete `update_from_battle_results` method
- [ ] If the adapter's only remaining method is `to_battle_ships` (replaced by the compiler), delete the entire `FleetBattleAdapter` class
- [ ] Verify: suite green

**Notes:**

---

### Task 6.7: Rewrite `combat_lab/runner.py` to go only through `run_battle` [Medium]
**File:** `combat_lab/runner.py`

**Tests:** `python -m combat_lab.run_tests --fast` — 162+ passing

- [ ] Remove `USE_BATTLE_RUNNER` feature flag and the legacy branch (Phase 1 scaffolding)
- [ ] `TestRunner.run_scenario(scenario_cls, ...)`:
  - `scenario = scenario_cls()`
  - `spec = scenario.to_spec(registries)`  (calls `build_test_battle_spec(self, registries)`)
  - `outcome = run_battle(spec, ai_factory=AIControllerFactory())`
  - Map outcome to `scenario.results` and run `scenario._run_validation(engine)` — engine is still accessible if needed via the `BattleOutcome` or a peer inspector
- [ ] Decision needed: does scenario validation need live `engine` access, or only `BattleOutcome`?
  - If BattleOutcome is sufficient → rewrite validation to consume outcome
  - If engine is needed → `run_battle` returns `(outcome, final_engine_snapshot)` or similar
- [ ] Remove direct `BattleEngine(...)` construction
- [ ] Verify: Combat Lab fast suite green

**Notes:**

---

### Task 6.8: Rewrite `ComparisonScenario._run_baseline_battle` to use `run_battle` [Medium]
**File:** `combat_lab/scenarios/templates.py`

**Tests:** `python -m combat_lab.run_tests --fast` — comparison scenarios still pass

- [ ] Today `_run_baseline_battle` constructs a throwaway `BattleEngine(...)`. Replace with: build a baseline `BattleSpec` via the scenario's baseline ships + call `run_battle(baseline_spec, ...)`.
- [ ] Read the outcome and stash baseline metrics on `self.baseline_*` attributes (same shape as today — preserve validate()'s expectations)
- [ ] Verify: all ComparisonScenario tests still pass

**Notes:**

---

### Task 6.9: Rewrite `test_executor.py` — all 4 paths through `run_battle` [Complex]
**File:** `game/ui/screens/test_lab/test_executor.py`

**Tests:** Manual: launch Combat Lab in UI, run visual + headless + batch; `python -m combat_lab.run_tests --fast`

- [ ] The four paths: visual single, visual batch, headless single, headless batch
- [ ] For each: build spec via `scenario.to_spec(registries)`; call `run_battle(spec, headless=<appropriate>, per_tick_callback=<renderer hook or None>)`
- [ ] Remove all direct `BattleEngine(...)` references
- [ ] Remove the `_is_started=True` hack in `run_visual` (was Phase-4b-era; lives in `test_execution_service.py`)
- [ ] Verify: Combat Lab UI works — visual runs render correctly, headless completes, batch cycles through
- [ ] Verify: pass/fail dots populate correctly after runs (registry write)

**Notes:**

---

### Task 6.10: Rewrite `test_execution_service.py` — drop `_is_started` hack [Medium]
**File:** `combat_lab/services/test_execution_service.py`

**Tests:** `pytest tests/unit/combat_lab/services/test_test_execution_service.py --testmon`

- [ ] The `_is_started=True` forced assignment (Phase 1 artifact) is no longer needed once the path goes through `run_battle`
- [ ] Remove the hack
- [ ] Update tests
- [ ] Verify: tests pass

**Notes:**

---

### Task 6.11: Rewrite `SimulationBattleResolver.resolve_battle` [Medium]
**File:** `game/strategy/combat/simulation_battle_resolver.py`

**Tests:** `pytest tests/unit/strategy/combat/ tests/integration/strategy/combat/ --testmon`

- [ ] Final form:
  ```python
  def resolve_battle(self, fleets, sector, system, empires, settings, registries) -> BattleOutcome:
      spec = build_strategy_battle_spec(fleets, sector, system, empires, settings, registries)
      return run_battle(spec, ai_factory=self._ai_factory)
  ```
- [ ] Post-hook (populated by compiler) handles fleet mutation as a side effect during `run_battle`
- [ ] Caller (`ConflictResolutionEngine`) treats outcome as a read-only report
- [ ] Verify: integration test — strategy battle updates fleets correctly, damage persists, destroyed ships removed

**Notes:**

---

### Task 6.12: Audit — zero legacy references in active codebase [Simple]
**Command:**
```bash
grep -rn "BattleMode\|BattleModeHandler\|create_manual_battle\|create_test_battle\|create_strategy_battle\|create_hypothetical_battle\|FleetBattleAdapter" \
    --include="*.py" \
    --exclude-dir=Projects/deep_archive \
    --exclude-dir=Projects/archived_projects \
    --exclude-dir=Reviews \
    .
```

- [ ] Run the grep — expect zero hits in active code (archived projects / reviews are frozen, OK to ignore)
- [ ] If any remain: migrate + delete; do not leave dead references
- [ ] Grep for `BattleEngine(` — expect zero matches outside `game/simulation/battle_runner.py` and engine-internal tests
- [ ] Verify: no archived or backup copies live on disk outside the `Projects/*_archive*` directories

**Notes:** This task is the gate for the project's "delete legacy paths" goal. Zero hits required.

---

### Task 6.13: Rewrite `docs/systems/combat_simulation.md` — unified flow [Medium]
**File:** `docs/systems/combat_simulation.md`

- [ ] Rewrite the "Battle Orchestration" section to describe the new flow:
  - Three contexts produce a `BattleSpec` via their own compiler
  - `run_battle(spec) -> BattleOutcome`
  - `BattleSpec` and `BattleOutcome` diagrams
  - Layer contract (simulation is context-blind)
- [ ] Remove references to `BattleMode`, `BattleModeHandler`, the four factories
- [ ] Keep damage pipeline / ability / fleet aura / event bus sections (unchanged)
- [ ] Add pointers to: `battle_runner.py`, `battle_spec.py`, `battle_outcome.py`, the three compilers
- [ ] Verify: doc reads cleanly start-to-finish; no broken references

**Notes:**

---

### Task 6.14: Update `docs/02_PATTERNS.md` if any entries reference deleted types [Simple]
**File:** `docs/02_PATTERNS.md`

- [ ] Grep `02_PATTERNS.md` for `BattleMode`, `BattleModeHandler`, `create_*_battle`, `FleetBattleAdapter` — if present, update or remove
- [ ] If a pattern was specifically illustrating the old `BattleModeHandler` mechanism, replace with a note about the spec-compiler pattern (each context owns a pure compiler → engine entry)
- [ ] Verify: patterns doc consistent with the code

**Notes:**

---

### Task 6.15: Final regression gate [Simple]

- [ ] `pytest tests/` full suite — green; record pass count; compare to project-start baseline
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing
- [ ] `python -m combat_lab.run_tests` (full with -HT) — no unexpected failures
- [ ] Manual: launch `python launcher.py` — open Combat Lab, run 3 scenarios visually; start Battle Setup, run a 2v2 with modifiers; start a strategy game, trigger a fleet conflict, verify damage persists next turn
- [ ] No new DeprecationWarnings

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Task 6.12 audit shows zero legacy references in active code
- [ ] Full pytest suite green
- [ ] Combat Lab fast suite 162+ passing
- [ ] `docs/systems/combat_simulation.md` rewritten for the unified flow
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State: "Implementation complete; awaiting final audit"
- [ ] Run project audit protocol (`Projects/protocols/04_audit_project.md`)
