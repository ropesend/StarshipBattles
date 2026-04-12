# Phase 1: DTO Boundary + Spec Compilers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce the `BattleSpec` / `BattleOutcome` DTO boundary and the three context-specific spec compilers. Add `battle_runner.run_battle(spec)` as the single engine entry. The legacy factories (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) still exist and still work — the new path runs alongside them. Each context wires ONE of its entry points through `run_battle` as a smoke test.

---

### Task 1.1: Create `BattleSpec` / `BattleOutcome` DTOs [Medium]
**Files:**
- `game/simulation/battle_spec.py` (new)
- `game/simulation/battle_outcome.py` (new)
- `game/simulation/__init__.py` (add exports)

**Tests:** `pytest tests/unit/simulation/test_battle_spec.py tests/unit/simulation/test_battle_outcome.py --testmon`

- [ ] Write failing unit tests for DTO shape (`tests/unit/simulation/test_battle_spec.py`):
  - `BattleSpec` is a frozen dataclass; all fields match [design.md §2.1](design.md)
  - `TeamSpec`, `TaskForceSpec`, `SquadronSpec`, `ShipSpec`, `ComponentStateSpec`, `EntryVector` all frozen
  - `BattleOutcome`, `TeamOutcome`, `ShipOutcome`, `HitRecord`, `WeaponSummary`, `ShipStats` all frozen
  - `ShipStatus` and `EndReason` enums exist with correct members
  - Round-trip test: construct a minimal `BattleSpec`, assert all fields reachable by attribute access, pickle-round-trip reproduces identical DTO
- [ ] Implement `battle_spec.py` with all dataclasses from [design.md §2.1–§2.3](design.md)
- [ ] Implement `battle_outcome.py` with all dataclasses from [design.md §2.4](design.md)
- [ ] Add exports to `game/simulation/__init__.py`
- [ ] Verify: imports `from game.simulation import BattleSpec, BattleOutcome` succeed
- [ ] All tests pass

**Notes:**

---

### Task 1.2: Stub `BoundaryRegion` types [Simple]
**File:** `game/simulation/combat/boundary.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_boundary.py --testmon`

The real enforcement lands in Phase 3. Phase 1 only needs the type shape so `BattleSpec.boundary` is well-typed.

- [ ] Write failing tests asserting `RectBoundary`, `CircleBoundary`, `UnboundedRegion` all implement the `BoundaryRegion` protocol (see [design.md §2.5](design.md))
- [ ] Test that `UnboundedRegion.contains(any_point)` returns True
- [ ] Test that `RectBoundary.contains` / `CircleBoundary.contains` work (basic geometry)
- [ ] Implement `boundary.py` with the three concrete types + `BoundaryRegion` protocol + `ExitPolicy` enum
- [ ] All tests pass

**Notes:**

---

### Task 1.3: Stub `ModifierStack` DTO [Simple]
**File:** `game/simulation/combat/modifier_stack.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_modifier_stack.py --testmon`

Full application lives in the engine wiring (end of Phase 1). For now we need the shape.

- [ ] Write failing tests for `ModifierStack(per_team: Mapping, global_: Tuple)` and `ModifierEntry(source: str, stack_group: Optional[str], effect: ModifierEffect)`
- [ ] Test that an empty `ModifierStack.empty()` class method exists and returns an empty stack
- [ ] Implement `modifier_stack.py`
- [ ] All tests pass

**Notes:**

---

### Task 1.4: Stub `FormationSpec` [Simple]
**File:** `game/simulation/combat/formation.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_formation.py --testmon`

Full resolver lands in Phase 4. Phase 1 only needs the type.

- [ ] Write failing tests for `FormationShape` enum and `FormationSpec(shape, spacing, custom_positions)` dataclass
- [ ] Implement enum + dataclass per [design.md §2.7](design.md)
- [ ] All tests pass

**Notes:**

---

### Task 1.5: Stub `TelemetryLevel` [Simple]
**File:** `game/simulation/combat/telemetry.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_telemetry.py --testmon`

- [ ] Write failing test for `TelemetryLevel` enum with MINIMAL / NORMAL / DETAILED members and ordered comparison (`NORMAL > MINIMAL`)
- [ ] Implement enum
- [ ] All tests pass

**Notes:**

---

### Task 1.6: Implement `run_battle(spec)` engine entry [Complex]
**File:** `game/simulation/battle_runner.py` (new)

**Tests:** `pytest tests/unit/simulation/test_battle_runner.py --testmon`

- [ ] Write failing tests for the engine entry:
  - `run_battle(spec)` accepts a `BattleSpec` and returns a `BattleOutcome`
  - Simple 1v1 spec with TickLimitCondition ends at `max_ticks`, returns outcome with `end_reason=TICK_LIMIT`
  - Outcome's team_ids match spec's team_ids in order
  - Every `ShipSpec` has a matching `ShipOutcome` by `instance_id`
  - Seed is echoed in the outcome
  - Function signature: `run_battle(spec, *, ai_factory, headless=True, per_tick_callback=None) -> BattleOutcome`
- [ ] Implement `run_battle`:
  - Construct `BattleEngine` via the existing `BattleController` internally
  - Attach ships built from `ShipSpec` (Phase 1 — just use existing `Ship.from_dict`/`Ship.from_design`; per-component HP from `ComponentStateSpec` lands properly in Phase 2 once `Ship.from_spec` can accept it)
  - Wire end condition from `spec.end_condition`
  - Ignore boundary for Phase 1 (stub it)
  - Ignore modifier_stack for Phase 1 (stub it — log a warning if non-empty)
  - Ignore telemetry_level for Phase 1 (always NORMAL)
  - Call `per_tick_callback(engine)` each tick if provided
  - After engine stops, build `BattleOutcome` via a new `extract_outcome(engine, spec)` helper
- [ ] Implement `extract_outcome(engine, spec) -> BattleOutcome` (minimal: team/ship structure, status, final pose, weapon summaries, empty hit log)
- [ ] Verify: a hand-built spec with 2 ships per team runs to completion and produces a valid outcome
- [ ] All tests pass

**Notes:**

---

### Task 1.7: Combat Lab spec compiler [Medium]
**File:** `combat_lab/spec_compiler.py` (new)

**Tests:** `pytest tests/unit/combat_lab/test_spec_compiler.py --testmon`

- [ ] Write failing tests:
  - `build_test_battle_spec(scenario, registries)` returns a `BattleSpec`
  - For a `StaticTargetScenario` subclass, the spec has 2 teams with expected ship counts
  - Seed from `scenario.metadata.seed` is placed in `BattleSpec.seed`
  - `telemetry_level` defaults to DETAILED for Combat Lab
  - `end_condition` comes from `scenario.metadata` (via existing `_create_end_condition` logic)
- [ ] Implement `build_test_battle_spec`:
  - Extract ships using existing scenario ship-loading helpers (`_load_ship`)
  - Use existing template helpers to place ships (distance, angles) — no formation resolver yet
  - Build empty `ModifierStack` (test scenarios don't use modifiers today)
  - Build `UnboundedRegion` boundary
  - Return fully-populated `BattleSpec`
- [ ] Add `TestScenario.to_spec(registries) -> BattleSpec` base method that delegates to `build_test_battle_spec(self, registries)`
- [ ] Verify: one existing scenario (e.g. `BeamLowAccuracyPointBlankScenario`) compiles to a spec whose ship count matches `scenario.setup()`
- [ ] All tests pass

**Notes:**

---

### Task 1.8: Battle Setup spec compiler [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py` (new — may need to create `battle_setup/` subdirectory)

**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py --testmon`

- [ ] Write failing tests:
  - `build_manual_battle_spec(ui_state, registries)` returns a `BattleSpec`
  - Ships from `ui_state.side_0.fleets` flow into `spec.teams[0]`
  - Modifier toggles from UI flow into `ModifierStack.per_team` (NOT mutate ships)
  - `telemetry_level` defaults to NORMAL
- [ ] Implement `build_manual_battle_spec`:
  - Walk `BattleSetupState.side_0.fleets` → task forces → squadrons → ship instances
  - Convert each ship via existing `ShipInstance.to_ship` logic
  - Pull complex modifier toggles → `ModifierStack` entries (replacing current `_apply_complex_modifiers` in-place mutation)
  - Build end condition from UI checkboxes (same logic currently in `_build_end_condition`)
  - Return `BattleSpec`
- [ ] Verify: a simple setup state compiles to a valid spec without mutating any ship
- [ ] All tests pass

**Notes:** Leave the existing `FleetBattleSetupScreen._apply_complex_modifiers` in place for now; the compiler does the right thing going forward, and the old path is removed in Phase 6.

---

### Task 1.9: Strategy spec compiler [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (new)

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py --testmon`

- [ ] Write failing tests:
  - `build_strategy_battle_spec(fleets, sector, system, empires, settings, registries)` returns a `BattleSpec`
  - Each input fleet becomes a `TeamSpec` (one team per fleet for now)
  - Sector + system modifiers flow into `ModifierStack.global_`
  - Per-empire modifiers flow into `ModifierStack.per_team`
  - Boundary is pulled from `settings.combat_boundary_default`
  - `post_battle_hook` is a non-None callable (wiring lands in Phase 2)
- [ ] Implement `build_strategy_battle_spec`:
  - Walk fleets → task forces → squadrons → ship instances
  - Build modifier stack from empire/system/sector/species
  - Entry vector: use hex center as origin, arbitrary facing for Phase 1 (proper hex-edge entry lands in Phase 4 alongside formation)
  - `post_battle_hook` is a no-op closure for Phase 1 (real implementation in Phase 2)
- [ ] Verify: hand-built minimal fleets compile to a valid spec
- [ ] All tests pass

**Notes:** `ShipInstance.components` doesn't exist yet (Phase 2). For Phase 1, build `ShipSpec.components` as an empty tuple; engine falls back to design-level HP.

---

### Task 1.10: Wire ONE smoke-test path through `run_battle` [Medium]
**File:** Pick the simplest: CLI `combat_lab/runner.py`

**Tests:** `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history` (manual)

- [ ] Add a feature flag `USE_BATTLE_RUNNER` (env var or module-level constant) default False
- [ ] In `TestRunner.run_scenario`, when flag is True:
  - Call `scenario.to_spec(registries)` to get a `BattleSpec`
  - Call `run_battle(spec, ai_factory=AIControllerFactory())`
  - Map the `BattleOutcome` to `scenario.results` / `scenario.passed` via `_run_validation`
- [ ] When flag is False (default): keep today's behaviour unchanged
- [ ] Verify: run BEAMWEAPON-001 with flag=True, test still passes
- [ ] Verify: run BEAMWEAPON-001 with flag=False, test still passes

**Notes:** The feature-flag is only for this phase — subsequent phases migrate the other call sites. Phase 6 removes the flag and deletes the legacy branch.

---

### Task 1.11: Pass-through doc updates [Simple]
**File:** `docs/systems/combat_simulation.md`

- [ ] Add a new top-section note: "**Unified entry (in progress, PROJ-269):** `run_battle(spec: BattleSpec) -> BattleOutcome` at `game/simulation/battle_runner.py` is the target single entry point. The legacy factories (`create_manual_battle`, etc.) still exist and are migrated one caller at a time."
- [ ] Add `BattleSpec` / `BattleOutcome` to the "Battle Orchestration" section (brief intro — full spec table added in Phase 6 when everything lives here)
- [ ] Verify: doc renders correctly, no broken links

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` fully green
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing (baseline)
- [ ] Manual smoke: launch `python launcher.py`, exercise Combat Lab once, Battle Setup once, strategy conflict once — all still work
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 Task 2.1
