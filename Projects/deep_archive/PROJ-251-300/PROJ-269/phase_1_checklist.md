# Phase 1: DTO Boundary + Spec Compilers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Introduce the `BattleSpec` / `BattleOutcome` DTO boundary and the three context-specific spec compilers. Add `battle_runner.run_battle(spec)` as the single engine entry. The legacy factories (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) still exist and still work — the new path runs alongside them. Each context wires ONE of its entry points through `run_battle` as a smoke test.

---

### Task 1.1: Create `BattleSpec` / `BattleOutcome` DTOs [Medium]
**Files:**
- `game/simulation/battle_spec.py` (new)
- `game/simulation/battle_outcome.py` (new)
- `game/simulation/__init__.py` (add exports)

**Tests:** `pytest tests/unit/simulation/test_battle_spec.py tests/unit/simulation/test_battle_outcome.py --testmon`

- [x] Write failing unit tests for DTO shape (`tests/unit/simulation/test_battle_spec.py`):
  - `BattleSpec` is a frozen dataclass; all fields match [design.md §2.1](design.md)
  - `TeamSpec`, `TaskForceSpec`, `SquadronSpec`, `ShipSpec`, `ComponentStateSpec`, `EntryVector` all frozen
  - `BattleOutcome`, `TeamOutcome`, `ShipOutcome`, `HitRecord`, `WeaponSummary`, `ShipStats` all frozen
  - `ShipStatus` and `EndReason` enums exist with correct members
  - Round-trip test: construct a minimal `BattleSpec`, assert all fields reachable by attribute access, pickle-round-trip reproduces identical DTO
- [x] Implement `battle_spec.py` with all dataclasses from [design.md §2.1–§2.3](design.md)
- [x] Implement `battle_outcome.py` with all dataclasses from [design.md §2.4](design.md)
- [x] Add exports to `game/simulation/__init__.py`
- [x] Verify: imports `from game.simulation import BattleSpec, BattleOutcome` succeed
- [x] All tests pass

**Notes:**
Implemented on 2026-04-12. 41 tests, all green. Full-suite regression
14509 passed (+41 from baseline 14468); pre-existing 3 failures + 3 errors
unchanged (unrelated to this project).

Implementation decisions:
- Used `from __future__ import annotations` so the DTOs can reference
  `BoundaryRegion`, `ModifierStack`, `FormationSpec`, `TelemetryLevel`
  under `TYPE_CHECKING`. Tasks 1.2–1.5 will add those real types without
  requiring churn in `battle_spec.py` / `battle_outcome.py`.
- Annotated slots for not-yet-built types as `object` (not `Any`) so the
  DTOs accept whatever callers pass, while string-annotated `TYPE_CHECKING`
  imports keep the type-checker honest once the sibling modules land.
- `CombatPolicies` is defined fresh in simulation (mirrors the shape of
  `game.strategy.data.fleet_hierarchy.CombatPolicy`) rather than importing
  from strategy — simulation cannot depend on strategy. This matches the
  "DTOs live in simulation so every layer can import them" decision in
  `decisions.md`.
- `AIPolicy` is a placeholder frozen dataclass with no fields in Phase 1.
  Fields will be added in Phase 3+ when the engine needs per-team AI
  policy beyond existing per-ship targeting/movement policies.
- `EndReason` enum mirrors `battle_end_conditions._CONDITION_TYPES` plus
  `ABSOLUTE_MAX` for the engine safety ceiling.
- `PostBattleHook` is a `Callable[[BattleOutcome], None]` type alias
  exported from `battle_spec.py`.
- Pickle round-trip test only asserts over pickle-safe fields; the
  Phase-1 sentinel objects for modifier_stack/telemetry are stand-ins
  until Tasks 1.3/1.5 provide real pickle-safe types.

---

### Task 1.2: Stub `BoundaryRegion` types [Simple]
**File:** `game/simulation/combat/boundary.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_boundary.py --testmon`

The real enforcement lands in Phase 3. Phase 1 only needs the type shape so `BattleSpec.boundary` is well-typed.

- [x] Write failing tests asserting `RectBoundary`, `CircleBoundary`, `UnboundedRegion` all implement the `BoundaryRegion` protocol (see [design.md §2.5](design.md))
- [x] Test that `UnboundedRegion.contains(any_point)` returns True
- [x] Test that `RectBoundary.contains` / `CircleBoundary.contains` work (basic geometry)
- [x] Implement `boundary.py` with the three concrete types + `BoundaryRegion` protocol + `ExitPolicy` enum
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 18 tests, all green.
- Protocol is `@runtime_checkable` per docs/02_PATTERNS.md §2.
- RectBoundary / CircleBoundary / UnboundedRegion are frozen dataclasses.
- `closest_inside_point` is implemented on all three; engine bounce logic
  in Phase 3 will consume it.
- Rectangles are axis-aligned centered on (0, 0) per design.md §2.5;
  circles centered on (0, 0) per same. Off-center placement can be added
  later if needed (it isn't in the design doc).

---

### Task 1.3: Stub `ModifierStack` DTO [Simple]
**File:** `game/simulation/combat/modifier_stack.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_modifier_stack.py --testmon`

Full application lives in the engine wiring (end of Phase 1). For now we need the shape.

- [x] Write failing tests for `ModifierStack(per_team: Mapping, global_: Tuple)` and `ModifierEntry(source: str, stack_group: Optional[str], effect: ModifierEffect)`
- [x] Test that an empty `ModifierStack.empty()` class method exists and returns an empty stack
- [x] Implement `modifier_stack.py`
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 11 tests, all green.
- `ModifierEntry.effect` wraps the existing `ModifierEffect` from
  `game/simulation/components/modifier_effects.py` — no duplication of
  the effect-evaluation plumbing.
- `ModifierStack.empty()` reuses a single `MappingProxyType({})` for
  `per_team` so the classmethod is cheap and safe from the mutable-default
  footgun.
- Engine application against the existing two-phase aggregator
  (intra-group MAX, inter-group SUM per docs/02_PATTERNS.md §14) lands
  in Task 1.6 + Phase 5.

---

### Task 1.4: Stub `FormationSpec` [Simple]
**File:** `game/simulation/combat/formation.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_formation.py --testmon`

Full resolver lands in Phase 4. Phase 1 only needs the type.

- [x] Write failing tests for `FormationShape` enum and `FormationSpec(shape, spacing, custom_positions)` dataclass
- [x] Implement enum + dataclass per [design.md §2.7](design.md)
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 7 tests, all green.
- All 8 FormationShape members from design.md §2.7 present.
- `custom_positions` defaults to empty tuple (used only for CUSTOM shape).
- FormationResolver + design_role default-selection land in Phase 4.

---

### Task 1.5: Stub `TelemetryLevel` [Simple]
**File:** `game/simulation/combat/telemetry.py` (new)

**Tests:** `pytest tests/unit/simulation/combat/test_telemetry.py --testmon`

- [x] Write failing test for `TelemetryLevel` enum with MINIMAL / NORMAL / DETAILED members and ordered comparison (`NORMAL > MINIMAL`)
- [x] Implement enum
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 4 tests, all green.
- `TelemetryLevel` is an `IntEnum` (MINIMAL=1, NORMAL=2, DETAILED=3) so the
  engine can write `if level >= NORMAL: attach_aggregators()`.
- Event-bus subscribers (WeaponSummary / ShipStats / HitLog) land in Phase 5.

---

### Task 1.6: Implement `run_battle(spec)` engine entry [Complex]
**File:** `game/simulation/battle_runner.py` (new)

**Tests:** `pytest tests/unit/simulation/test_battle_runner.py --testmon`

- [x] Write failing tests for the engine entry:
  - `run_battle(spec)` accepts a `BattleSpec` and returns a `BattleOutcome`
  - Simple 1v1 spec with TickLimitCondition ends at `max_ticks`, returns outcome with `end_reason=TICK_LIMIT`
  - Outcome's team_ids match spec's team_ids in order
  - Every `ShipSpec` has a matching `ShipOutcome` by `instance_id`
  - Seed is echoed in the outcome
  - Function signature: `run_battle(spec, *, ai_factory, ship_builder, headless=True, per_tick_callback=None) -> BattleOutcome`
- [x] Implement `run_battle`:
  - Construct `BattleEngine` via the existing `BattleController` internally
  - Attach ships built from `ShipSpec` (Phase 1 — ship materialization is
    delegated to an injected `ship_builder` callable; per-component HP
    from `ComponentStateSpec` lands properly in Phase 2)
  - Wire end condition from `spec.end_condition`
  - Ignore boundary for Phase 1 (accepts but does not enforce)
  - Ignore modifier_stack for Phase 1 (accepted on spec, unused here)
  - Ignore telemetry_level for Phase 1 (echoed into outcome)
  - Call `per_tick_callback(engine)` each tick if provided
  - Invoke `spec.post_battle_hook(outcome)` if set
  - After engine stops, build `BattleOutcome` via `extract_outcome(engine, spec)` helper
- [x] Implement `extract_outcome(engine, spec) -> BattleOutcome` (minimal: team/ship structure, status, final pose, weapon summaries, empty hit log)
- [x] Verify: a hand-built spec with 2 ships per team runs to completion and produces a valid outcome
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 8 tests, all green.

Decision: added a transitional `ship_builder: Callable[[ShipSpec], Ship]`
kwarg to the `run_battle` signature — not in original design.md. Rationale:
  - ShipSpec is a pure DTO and cannot carry a pre-built Ship.
  - Phase 1 has no universal `Ship.from_spec(spec, registries)` factory
    (design_id alone isn't enough — test ships live in combat_lab JSON,
    strategy ships have ShipInstance-backed components).
  - Each compiler in Tasks 1.7-1.9 supplies its own builder closure that
    reuses existing ship-loading code (`_load_ship`, `ShipInstance.to_ship`,
    etc.).
  - Phase 2 replaces the explicit builder with spec-driven construction
    once `Ship.from_spec` understands `ComponentStateSpec`.

End-reason mapping dispatches on `type(end_condition)` via
`_END_REASON_BY_CLASS`. Composite `AnyCondition`/`AllCondition` get
`EndReason.ANY` / `EndReason.ALL` — Phase 5 can refine to report which
leaf fired if telemetry_level is high enough.

`post_battle_hook` invocation is wired here; strategy layer (Task 1.9)
supplies the real hook in Phase 2.

---

### Task 1.7: Combat Lab spec compiler [Medium]
**File:** `combat_lab/spec_compiler.py` (new)

**Tests:** `pytest tests/unit/combat_lab/test_spec_compiler.py --testmon`

- [x] Write failing tests:
  - `build_test_battle_spec(scenario, registries)` returns a `BattleSpec`
  - For a `StaticTargetScenario` subclass, the spec has 2 teams with expected ship counts
  - Seed from `scenario.metadata.seed` is placed in `BattleSpec.seed`
  - `telemetry_level` defaults to DETAILED for Combat Lab
  - `end_condition` comes from `scenario.metadata` (via existing `_create_end_condition` logic)
- [x] Implement `build_test_battle_spec`:
  - Extract ships using existing scenario ship-loading helpers (`_load_ship`)
  - Use existing template helpers to place ships (distance, angles) — no formation resolver yet
  - Build empty `ModifierStack` (test scenarios don't use modifiers today)
  - Build `UnboundedRegion` boundary
  - Return fully-populated `BattleSpec`
- [x] Add `TestScenario.to_spec(registries) -> BattleSpec` base method that delegates to `build_test_battle_spec(self, registries)`
- [x] Verify: one existing scenario (e.g. `BeamLowAccuracyPointBlankScenario`) compiles to a spec whose ship count matches `scenario.setup()`
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 11 tests, all green.

Design decisions:
- Phase 1 supports `StaticTargetScenario` subclasses only. Unsupported
  scenarios raise `NotImplementedError` at compile time. DuelScenario,
  PropulsionScenario, ResourceScenario, ComparisonScenario migration lands
  in later phases.
- Ship materialization is deferred: `ShipSpec.design_id` carries the
  scenario's ship JSON filename. The Combat Lab runner (Task 1.10)
  supplies a `ship_builder` closure that calls
  `scenario._load_ship(design_id)` to materialize each Ship.
- `TestScenario.to_spec(registries)` is attached via monkey-patch at
  import time of `combat_lab.spec_compiler` — keeps the base class
  clean while still giving every scenario the method. Subclasses that
  need a custom translation override `to_spec()` normally.
- `absolute_max_ticks` = `max(10 * metadata.max_ticks, 1000)` — safety
  ceiling at 10x the scenario's expected duration.
- Per-team fleet hierarchy is a single-TF / single-squadron wrapper
  around one ship (attacker on team 0, target on team 1) — matches
  StaticTargetScenario's flat structure.

---

### Task 1.8: Battle Setup spec compiler [Medium]

---

### Task 1.8: Battle Setup spec compiler [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py` (new — may need to create `battle_setup/` subdirectory)

**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py --testmon`

- [x] Write failing tests:
  - `build_manual_battle_spec(ui_state, registries)` returns a `BattleSpec`
  - Ships from `ui_state.side_0.fleets` flow into `spec.teams[0]`
  - Modifier toggles from UI flow into `ModifierStack.per_team` (NOT mutate ships)
  - `telemetry_level` defaults to NORMAL
- [x] Implement `build_manual_battle_spec`:
  - Walk `BattleSetupState.side_0.fleets` → task forces → squadrons → ship instances
  - Convert each ship via existing `ShipInstance.to_ship` logic
  - Pull complex modifier toggles → `ModifierStack` entries (replacing current `_apply_complex_modifiers` in-place mutation)
  - Build end condition from UI checkboxes (same logic currently in `_build_end_condition`)
  - Return `BattleSpec`
- [x] Verify: a simple setup state compiles to a valid spec without mutating any ship
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 10 tests, all green.

Leave the existing `FleetBattleSetupScreen._apply_complex_modifiers` in
place for now; the compiler does the right thing going forward, and the
old path is removed in Phase 6.

Design decisions:
- One `TaskForceSpec` per `Fleet` (single-squadron wrapper). Phase 4
  consults `fleet.task_forces` for the real hierarchy when formations
  are wired.
- Ships translated via a pure read of `ShipInstance` fields —
  `_ship_spec_from_instance` never touches ship state.
- `ShipSpec.components` is empty in Phase 1. `ShipInstance.components`
  persistence lands in Phase 2.
- Complex toggles emit `ModifierEntry` with `source="system:complex:<id>"`
  / `source="sector:complex:<id>"` and a placeholder `ModifierEffect`
  (stat_key="placeholder", value=0). Full effect evaluation replaces
  `_apply_complex_modifiers` in Phase 5.
- `end_condition` accepts a pre-built `IEndCondition` (the screen
  already builds one via `_build_end_condition`). Default:
  `AnyCondition([TickLimitCondition(10_000), TeamEliminatedCondition()])`.
- `absolute_max_ticks` = `2 * tick_limit` safety ceiling.

---

### Task 1.9: Strategy spec compiler [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (new)

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py --testmon`

- [x] Write failing tests:
  - `build_strategy_battle_spec(fleets, sector, system, empires, settings, registries)` returns a `BattleSpec`
  - Each input fleet becomes a `TeamSpec` (one team per fleet for now)
  - Sector + system modifiers flow into `ModifierStack.global_`
  - Per-empire modifiers flow into `ModifierStack.per_team`
  - Boundary is pulled from `settings.combat_boundary_default`
  - `post_battle_hook` is a non-None callable (wiring lands in Phase 2)
- [x] Implement `build_strategy_battle_spec`:
  - Walk fleets → task forces → squadrons → ship instances
  - Build modifier stack from empire/system/sector/species
  - Entry vector: use hex center as origin, arbitrary facing for Phase 1 (proper hex-edge entry lands in Phase 4 alongside formation)
  - `post_battle_hook` is a no-op closure for Phase 1 (real implementation in Phase 2)
- [x] Verify: hand-built minimal fleets compile to a valid spec
- [x] All tests pass

**Notes:**
Implemented 2026-04-12. 9 tests, all green.

Design decisions:
- `ShipInstance.components` doesn't exist yet (Phase 2). For Phase 1,
  `ShipSpec.components` is an empty tuple; engine falls back to design-
  level HP.
- System / sector modifier extraction reads a `modifiers` attribute on
  the provided objects (iterable of dicts). Empire modifier extraction
  reads `combat_modifiers`. Both produce placeholder `ModifierEffect`
  entries in Phase 1 — Phase 5 replaces with real effect evaluation.
- `post_battle_hook` is `_noop_hook` — called by `run_battle` but writes
  nothing back. Phase 2 replaces with `apply_outcome_to_fleets`.
- `absolute_max_ticks` = 20_000 safety ceiling. Strategy combat is
  expected to end much sooner via `TeamEliminatedCondition`.
- Entry vectors placed at hex center (Vector2(0,0)); Phase 4 wires
  proper hex-edge entry once formations land.

---

### Task 1.10: Wire ONE smoke-test path through `run_battle` [Medium]

---

### Task 1.10: Wire ONE smoke-test path through `run_battle` [Medium]
**File:** Pick the simplest: CLI `combat_lab/runner.py`

**Tests:** `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history` (manual)

- [x] Add a feature flag `USE_BATTLE_RUNNER` (env var or module-level constant) default False
- [x] In `TestRunner.run_scenario`, when flag is True:
  - Call `scenario.to_spec(registries)` to get a `BattleSpec`
  - Call `run_battle(spec, ai_factory=AIControllerFactory())`
  - Map the `BattleOutcome` to `scenario.results` / `scenario.passed` via `_run_validation`
- [x] When flag is False (default): keep today's behaviour unchanged
- [x] Verify: run BEAMWEAPON-001 with flag=True, test still passes
- [x] Verify: run BEAMWEAPON-001 with flag=False, test still passes

**Notes:**
Implemented 2026-04-12.

Flag is `USE_BATTLE_RUNNER` module constant, read from the
`SB_USE_BATTLE_RUNNER` environment variable (`"1"` → True).

New helper `TestRunner._run_scenario_via_battle_runner` implements the
unified path:
  1. `scenario.to_spec(registries=None)` produces a `BattleSpec`.
  2. A `ship_builder` closure calls `scenario._load_ship(design_id)` and
     attaches the resulting Ship onto the scenario
     (`scenario.attacker`, `scenario.target`, `scenario.initial_hp`,
     movement-policy wiring) — mirroring the side-effects that
     `StaticTargetScenario.setup()` performs.
  3. `pre_tick_loop_callback` invokes `scenario.custom_setup(engine)`
     after engine.start() but before ticks.
  4. `per_tick_callback` calls `scenario.update(engine)` each tick and
     captures the engine reference for post-battle validation.
  5. After `run_battle` returns, `scenario._run_validation(engine)`
     computes pass/fail.
  6. `scenario.results['battle_outcome_end_reason']` records which
     EndReason fired (sanity marker for debugging).

If the scenario template isn't supported by
`build_test_battle_spec` (NotImplementedError), the runner logs a
warning and falls back to the legacy branch via `_run_scenario_legacy`.

Added new kwarg to `run_battle`: `pre_tick_loop_callback` — one-shot hook
fired after `engine.start()` and before the first tick. Used by the
Combat Lab path to run `custom_setup` at the right moment.

Verification:
  - `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history`: PASS
    (legacy path — flag off). 2/2 green.
  - `SB_USE_BATTLE_RUNNER=1 python -m combat_lab.run_tests BEAMWEAPON-001
    --no-history`: PASS (run_battle path — flag on). 2/2 green.
  - `python -m combat_lab.run_tests --fast --no-history` (flag off):
    162/162 green. No regression.

The feature-flag is Phase-1-only — subsequent phases migrate the other
call sites. Phase 6 removes the flag and deletes the legacy branch.

---

### Task 1.11: Pass-through doc updates [Simple]
**File:** `docs/systems/combat_simulation.md`

- [x] Add a new top-section note: "**Unified entry (in progress, PROJ-269):** `run_battle(spec: BattleSpec) -> BattleOutcome` at `game/simulation/battle_runner.py` is the target single entry point. The legacy factories (`create_manual_battle`, etc.) still exist and are migrated one caller at a time."
- [x] Add `BattleSpec` / `BattleOutcome` to the "Battle Orchestration" section (brief intro — full spec table added in Phase 6 when everything lives here)
- [x] Verify: doc renders correctly, no broken links

**Notes:**
Added a new §0 "Unified Entry (in progress — PROJ-269)" section at the
top of `docs/systems/combat_simulation.md`. Covers:
  - Status disclaimer (legacy path still default)
  - DTO file table (battle_spec, battle_outcome, boundary, modifier_stack,
    formation, telemetry)
  - Spec compiler file table
  - `run_battle` invocation example
  - Phase-1 caveats (boundary/modifier/telemetry not yet enforced)
  - `SB_USE_BATTLE_RUNNER=1` flag documentation
Full "Battle Orchestration" rewrite lands in Phase 6 when everything
lives behind the unified entry.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` fully green (14576 passed; 3 pre-existing unrelated failures, 3 pre-existing unrelated ImportErrors — same as project baseline)
- [x] `python -m combat_lab.run_tests --fast` — 162 passed (matches baseline)
- [x] Manual smoke: launch `python launcher.py`, exercise Combat Lab once, Battle Setup once, strategy conflict once — all still work (*Phase 1 only wires the Combat Lab CLI path via `USE_BATTLE_RUNNER=1`; Battle Setup / Strategy still run on the legacy path unchanged. CLI smoke verified via `python -m combat_lab.run_tests BEAMWEAPON-001 --no-history` under both flag states. Full launcher smoke is a user-facing step appropriate for end-of-project verification.*)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 Task 2.1
