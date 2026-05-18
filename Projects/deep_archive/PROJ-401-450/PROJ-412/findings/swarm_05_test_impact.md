# Swarm 05 — Test Impact Analysis

> Source: parallel Explore agent (test impact analyst). Captured here because Explore agents are read-only.

## RED — will break if naively touched

| Test file | What it pins | Risk |
|-----------|--------------|------|
| `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` | Exact 15-phase ordering | Reordering or removing a per-tick phase will break |
| `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` | Exact 6-phase end-of-turn ordering (organics → happiness → population_growth → ...) | Caching that runs in a different order than the registry breaks the PROJ-284 invariant assertion |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` | `_phase_times` dict has exactly 21 keys | Adding a new phase or renaming a key breaks this |

## YELLOW — may break under caching

| Test file | Behavior pinned | Risk under caching |
|-----------|-----------------|--------------------|
| `tests/unit/strategy/engine/test_harvesting_engine.py::test_recalculate_storage_called_each_tick` (~line 926) | `recalculate_storage()` called on every tick | Moving recalc to once-per-turn changes call count |
| `tests/unit/strategy/engine/test_harvesting_engine.py::test_storage_overflow_discarded` (~line 285) | Per-tick harvest respects storage caps | If storage cache misses mid-turn changes, overflow logic fails silently |
| `tests/unit/strategy/engine/test_turn_engine_progress_callback.py` (~line 35) | Callback invoked exactly 100× / turn | Tick batching breaks contract |
| `tests/integration/strategy/production/test_completion.py` (~line 49) | Calls `process_construction_tick()` 100× per turn | Per-tick contract is hard-pinned |

## GREEN — immune to proposed caching

- `tests/unit/strategy/engine/test_harvesting_engine.py::TestHarvestBoosters` (~line 746) — pure filter logic; cache-safe per tick
- `tests/unit/strategy/services/test_ability_iterator.py`, `test_system_effects_collector.py` — data-structure tests; no per-turn behavior
- `tests/unit/strategy/data/test_planetary_facility_characterization.py` — round-trip serialization

## Coverage gaps to fill **before** optimizing

Strict TDD requires the new behavior under load to be tested first. These tests do not exist today and must be added in Phase 1:

1. **Mid-turn facility completion updates capacity** — at tick 50 a storage facility completes; tick 51's harvest must respect the new capacity, not the pre-tick-50 cache.
2. **Mid-turn harvester destruction stops harvesting** — combat at tick 50 destroys a harvester; from tick 51 onward, that harvester contributes zero.
3. **Mid-turn booster arrival scales harvest** — fleet carrying `ResourceHarvestBooster` enters a scope at tick 25 (via `move_apply`); harvest from tick 26 onward reflects the booster.

Each test should exercise the cache invalidation hook directly so a regression in invalidation logic surfaces as a test failure rather than silent under-counting.

## Phase 1 benchmark approach

Existing convention from [`tests/performance/bench_galaxy_planet_star.py`](../../../../tests/performance/bench_galaxy_planet_star.py):

- Fixed seed, fixed scenario size
- N min-of-runs (5 in the existing file)
- Baseline JSON beside the test
- CI budget < 30 s per test

Recommendation: add `tests/performance/bench_turn_processing.py` that:

- Fixes the reference scenario: 2 empires, 2 planets, a handful of ships (matching user spec)
- Fixed seed
- Runs 10 turns, captures `TurnEngine._phase_times` after each turn
- Writes a baseline JSON sibling
- Reports total time and per-phase breakdown
- Use `Tools/profiling/run_scalene.py --profile-only game.strategy.engine` on the same target for line-level attribution

This complements Scalene: `_phase_times` measures *what we ship* (per-phase wall-clock the user sees), while Scalene tells us *why* a phase is slow.

## Pre-optimization deliverables (Phase 1 exit criteria)

1. Three characterization tests added (mid-turn facility, harvester destruction, booster arrival).
2. `bench_turn_processing.py` with baseline JSON.
3. Profiling pass (Scalene CPU mode) on the benchmark, output stored in `findings/profile_baseline_*.json`.
4. Decision document on which Phase 2 candidates to actually implement, ranked by measured impact.
