# Swarm 03 — Overhead Hunt: The Missing 2.5–3.7 s

> Source: parallel Explore agent (overhead hunter). Captured here because Explore agents are read-only.

## Goal

`TURN PERF` log lines from QA session `20260510_165332` show total turn time ≈ 7-8 s for a tiny game, but the sum of the 21 named phase buckets is only ~4.3 s. The remaining **2.5-3.7 s** is not attributed to any phase. Find it.

## Hypothesis verification

| # | Hypothesis | Verdict | Cost estimate | Evidence |
|---|------------|---------|---------------|----------|
| 1 | `TurnStateSnapshot.capture` at turn start deep-copies state | **CONFIRMED** | 200–400 ms | [turn_engine.py:533-537](../../../../game/strategy/engine/turn_engine.py#L533); calls `empire.to_dict()` and `galaxy.to_dict()`; bounded by content size |
| 2 | `_run_phases` orchestration: 1500 invocations × lambda + args_resolver + perf_counter + dict update | **CONFIRMED** | 100–200 ms | [turn_engine.py:323-357](../../../../game/strategy/engine/turn_engine.py#L323); 25 `args_resolver` lambdas in `turn_phase_registry.py` allocate fresh tuples each call; perf_counter is two system calls per phase × 1500 |
| 3 | Progress callback invoked 100× / turn; UI may pump pygame events | **CONFIRMED, high risk** | 100–500 ms (potentially > 1 s if callback pumps events) | [turn_engine.py:698-703](../../../../game/strategy/engine/turn_engine.py#L698); `game_session.py:299-327` passes the callback through |
| 4 | Per-tick `logger.debug` f-strings | **REJECTED** | negligible | Default level WARNING; debug strings not evaluated |
| 5 | `_log_empire_state` per tick | **REJECTED** | ~2 ms total | [turn_engine.py:552, 571](../../../../game/strategy/engine/turn_engine.py#L552); called at TURN START / TURN END only |
| 6 | `_validate_tick_inputs` in harvesting every tick | **REJECTED** | 1–2 ms | [harvesting_engine.py:189-206](../../../../game/strategy/engine/harvesting_engine.py#L189); cheap None-check across colonies |
| 7 | `TickContext` allocation per tick | **REJECTED** | <1 ms | 100 small dataclass instances; minor |
| 8 | `set_current_turn` + `getattr` walks at process_turn entry | **REJECTED** | negligible | one-shot |
| 9 | `empire.colonies` / `colony.facilities` are computed properties | **REJECTED** | negligible | `empire.py:34` and `planet.py:85-86` are plain list attributes; `empire.resource_pool` *is* a computed property but is not called per-tick in the hot path |

## Top 3 attributed overhead sources

1. **Progress callback pumping** (~100–500 ms; possibly higher) — biggest unknown. The UI's callback may pump pygame events or trigger a partial redraw per tick. Easy to verify: replace the callback with a noop and re-measure.
2. **`TurnStateSnapshot.capture`** (~200–400 ms) — `empire.to_dict()` + `galaxy.to_dict()` once per turn. Optimization options: lighter-weight snapshot (only mutator-protocol fields), copy-on-write, or skip when no session is supplied.
3. **`_run_phases` per-call overhead** (~100–200 ms) — 1500 lambda evaluations + tuple allocations + two perf_counter calls each. Pre-resolving the callable and reusing args tuples could save measurable time.

Sum of confirmed sources: ~400–1100 ms attributed. **Roughly 1.5–2.6 s is still unaccounted** — Phase 1 profiling (Scalene + cProfile) needs to locate it. Strong candidates per `swarm_01`: redundant work *inside* the harvesting bucket (already in its 3.9 s but possibly understating what's reusable elsewhere), `PlanetEnergyEngine` rescans, `EnvironmentalHazardEngine` no-storm scans, `FleetMovementEngine` per-tick pathfinding.

## Isolating these in tests

- Mock `TurnStateSnapshot.capture` → no-op and re-measure total turn time.
- Replace `progress_callback` with `lambda *a: None` and re-measure.
- Replace each per-tick phase with `lambda *a, **k: None` one at a time to isolate per-bucket contribution beyond the timed slice.
- Run `cProfile` / `pyinstrument` over the same scenario for ground truth.

The first two are tiny experiments that Phase 1 should run before any optimization, to decide whether the snapshot or the callback dominates the unattributed overhead.
