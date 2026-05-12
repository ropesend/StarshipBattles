# Phase 6: Secondary Phase Optimizations (energy / environmental / movement)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply the cache pattern proven in Phase 4 to the remaining redundant per-tick scans (`PlanetEnergyEngine`, `EnvironmentalHazardEngine`, `FleetMovementEngine`). Each task is independently gated on the Phase 1 measurement — if a phase's bucket is < 50 ms / turn on the tiny scenario by Phase 5 completion, drop that task.

This phase is the cleanest place to stop if the user is satisfied with Phase 4+5's reduction. Re-evaluate scope at the start of this phase.

---

## Tasks

### Task 6.1: Reduce remaining `PlanetEnergyEngine` per-tick work [Simple] ⚠ scope reduced (codex consult)

**Files:** `game/strategy/engine/planet_energy_engine.py`
**Tests:** existing `tests/unit/strategy/engine/test_planet_energy_engine.py`; bench

- [ ] `PlanetEnergyEngine` **already has** `_energy_cache` keyed by planet_id with a facility-fingerprint cache invalidator and a public `invalidate_energy_cache(planet_id)` method ([planet_energy_engine.py:154-179, 204-240](../../../game/strategy/engine/planet_energy_engine.py#L154)). The bulk of the per-tick scan is already cached. The original Phase 5.1 task description was wrong.
- [ ] If Phase 1 profile still shows `planet_energy` as a measurable cost, identify what remains: most likely shield drain / auto-deactivate logic on the **active** code path, not the cached generation/capacity scan.
- [ ] Add per-tick short-circuits where they exist: e.g. `no_active_shields_and_no_energy_consumers` skip; skip the entire phase when no planet has energy storage > 0
- [ ] Failing test first: shield activated at tick 30 starts draining energy at tick 31 (only add if not already covered)
- [ ] If Phase 1 shows this phase is < 50 ms / turn (or already reduced by Phase 4's universal-pipeline cache benefiting from `IAbilitySource` invalidation hooks), **cut this task** and document the cut in `decisions.md`

**Notes:**

### Task 6.2: `EnvironmentalHazardEngine` short-circuit and storm cache [Simple]

**Files:** `game/strategy/engine/environmental_hazard_engine.py`
**Tests:** existing environmental tests; bench

- [ ] If Phase 2 didn't already add the `no_active_storms_on_galaxy` short-circuit, add it now
- [ ] Cache the storm-effect lookup per-turn-per-system (storms don't appear/disappear mid-tick except via combat, which is out of scope)
- [ ] Failing test first: storm appearing mid-turn (if any in-scope path causes this) still applies effect at the correct tick
- [ ] Verify: bench shows `environmental` phase reduced; storm-damage integration tests still pass

**Notes:**

### Task 6.3: `FleetMovementEngine` pathfinding memoization [Complex]

**Files:** `game/strategy/engine/fleet_movement_engine.py`, possibly `game/strategy/services/galaxy_pathfinding_service.py`
**Tests:** new characterization test for path invalidation; bench

- [ ] Per swarm-01: pathfinding fires every eligible tick for every fleet. With stable fleet speed and galaxy map, the path is deterministic. Memoize the computed path per `(fleet_id, target_hex, fleet.speed, galaxy_version)`.
- [ ] Galaxy mutations (warp point open/close, system destruction) must invalidate; those mutations route through superweapon handlers which are in scope.
- [ ] Fleet speed change (damage, component activation, modifier) must invalidate the fleet's entry.
- [ ] Failing test first: speed change at tick 50 causes re-pathfind at tick 51 (or whenever the fleet next becomes movement-eligible); stable speed across ticks reuses the cached path.
- [ ] Verify: bench shows `move_calc` phase reduced; intercept tests, mutual-pursuit tests, and jump-past-collision tests still green

**Notes:**

### Task 6.4: Final benchmark and documentation update [Medium]

**Files:** `tests/performance/bench_turn_processing.baseline.json`, `docs/systems/strategy_layer.md`, `docs/systems/production_system.md` if relevant
**Tests:** full sharded suite

- [ ] Run `bench_turn_processing.py` and write the final baseline JSON
- [ ] Compute Phase 1 → final delta on total time and on each phase bucket
- [ ] Update `docs/systems/strategy_layer.md` to mention the new caching contracts (per-turn `_storage_dirty` / `_booster_dirty` flags, who flips them, who clears them)
- [ ] Update `docs/guides/performance_profiling.md` with a one-paragraph reference to `bench_turn_processing.py` as the canonical turn-processing benchmark
- [ ] Update `docs/03_CONVENTIONS.md` only if a new convention was introduced (e.g. "dirty-flag invalidation lives on `Empire` and is cleared by the engine that owns the cache")
- [ ] Run full sharded suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Cross-check: the docs/code consistency rule — any doc claim that disagrees with code must be surfaced

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Final `bench_turn_processing.py` total time vs. the Phase-1 baseline: agreed reduction met (target to be confirmed with user at end of Phase 5)
- [ ] All sub-engine unit tests green
- [ ] All three Phase-1 mid-turn characterization tests still green
- [ ] Full sharded suite green
- [ ] `docs/` updated where behavior or pattern changed
- [ ] No new save migration / fallback / compatibility shim
- [ ] User has verified the tiny-scenario turn time on their own machine
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Project Complete`
- [ ] Move project to `Projects/completed_projects/` per the standard close-out flow
