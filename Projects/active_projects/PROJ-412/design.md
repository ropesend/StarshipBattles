# PROJ-412: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).

## Initial Analysis

### Where the time goes today (real measurement, not hypothesis)

Real `TURN PERF` log lines pulled from QA session `Tools/qa_observer/session_data/20260510_165332/logs/battle.log` on the user's tiny game:

```
TURN PERF: total=7.993s | harvesting=3.924s resources=0.001s fuel_gen=0.020s
  planet_energy=0.002s resupply=0.006s production=0.056s environmental=0.136s
  instant_orders=0.001s actions=0.001s planet_actions=0.000s activation_timers=0.001s
  planet_modifier_effects=0.002s move_calc=0.126s move_apply=0.000s combat=0.002s
  organics_consumption=0.000s happiness=0.000s quality_improvement=0.000s
  atmosphere=0.000s water_modification=0.000s population=0.000s
```

Across ~20 representative turns:

| Bucket | Time per turn | Share |
|--------|---------------|-------|
| `harvesting` | ~3.9 s | ≈ 50% |
| `environmental` + `move_calc` | ~0.15–0.30 s | ≈ 3% |
| `production` + `fuel_gen` + `resupply` | ~0.03–0.10 s | ≈ 1% |
| All other phases combined | < 0.05 s | < 1% |
| **Sum of named phases** | **~4.3 s** | **~55%** |
| **Total turn time** | **~7.5–8.0 s** | **100%** |
| **Unaccounted overhead** | **~2.5–3.7 s** | **≈ 30–45%** |

The "unaccounted" gap is the most surprising finding. It is *outside* every `_time_phase()` bucket and therefore *between* phases or in `process_turn()` infrastructure. The Phase-1 measurement task must locate it before any Phase 2+ optimization is justified.

## Swarm Findings Summary

The six parallel Explore agents are individually documented in `findings/swarm_0[1-6]_*.md`. Key consolidated conclusions:

### Architecture (swarm_01)

`TurnEngine` is a thin orchestrator over 18 sub-engines plus a frozen 15-phase per-tick descriptor list and a 6-phase end-of-turn list. Each phase runs through `_run_phases` → `_time_phase` (timed) → sub-engine call. Phase ordering is enforced by golden tests (`test_default_tick_phase_list.py`, `test_default_end_of_turn_phase_list.py`). Multiple phases redundantly re-scan the same facility/component data every tick when the tiny scenario rarely mutates between ticks — most visibly in `HarvestingEngine.recalculate_storage` and `PlanetEnergyEngine.process_energy_tick`.

### Harvesting hot path (swarm_02)

Pre-profile hypothesis, **co-equal top items, ranking not locked**. Swarm_02's own internal cost estimates (e.g. "6.5–9.5 s" for harvesting) overshoot the observed 3.9 s, so treat the numbers below as candidate ranges and let Phase 1 measurement decide priority.

- **`_get_harvest_booster_mult` performs 4-scope ability scans per harvester per tick** ([harvesting_engine.py:388-419](../../../game/strategy/engine/harvesting_engine.py#L388)). Co-top candidate.
- **`recalculate_storage` walks all colonies × facilities × components every tick** ([harvesting_engine.py:204-223](../../../game/strategy/engine/harvesting_engine.py#L204)). Co-top candidate.
- **Late `import` inside the hot loop** at [harvesting_engine.py:405-407](../../../game/strategy/engine/harvesting_engine.py#L405). Free fix.
- **Registry lookups via `_get_ability_info`**. Cache candidate, contribution to be measured.
- **Dict copies in `set_max_stockpile` / `replace_max_storage`** — minor.

### Overhead hunt (swarm_03)

The 2.5–3.7 s unaccounted overhead is most plausibly:

1. **Progress callback that fires per-tick UI redraw + display flip** — **verified by code read**: [`strategy_game_state_manager.py:170-177`](../../../game/ui/screens/strategy_game_state_manager.py#L170) calls `pygame.event.pump()`, `self._screen.draw(surface)`, and `pygame.display.flip()` on every one of the 100 ticks. At a typical full-strategy-screen redraw cost (5–20 ms each), this alone could explain 0.5–2.0 s per turn. Phase 1 should run the noop-callback probe **early** and may promote the callback fix above Phase 3 if the delta is large.
2. **`TurnStateSnapshot.capture`** at turn start ([turn_state_snapshot.py:53-68](../../../game/strategy/engine/turn_state_snapshot.py#L53)) — full `to_dict()` of every empire and galaxy; estimated 200–400 ms.
3. **`_run_phases` per-call overhead** — 1500 invocations × tuple alloc + perf_counter ≈ 100–200 ms.

Phase-1 Scalene profiling is needed to confirm attribution.

### Cache patterns (swarm_04)

Reusable patterns already in the codebase:

- **PROJ-285 per-turn habitability multiplier on `Planet`** — implicit turn-key invalidation; the gold-standard model for any new per-turn cache here.
- **PROJ-254 facade index caches on `FacadeSessionState`** — explicit `invalidate_all()` at turn boundary.

Proposed reuse for this project:

- Per-turn `(turn, empire_id)` cache on storage aggregation, invalidated by a `_storage_dirty` flag set inside `PlanetWriteService.add_facility` / `remove_facility` / `set_facility_operational`.
- Per-turn `(turn, colony_id, resource_type)` cache on booster scope scan, invalidated when any in-scope `IAbilitySource` mutates (facility built/destroyed/toggled, fleet movement that crosses a scope boundary).

### Test impact (swarm_05)

- **RED** (must preserve): `test_default_tick_phase_list.py`, `test_default_end_of_turn_phase_list.py`, `test_turn_engine_phase_timing.py`. Phase ordering and `_phase_times` keys must not change.
- **YELLOW**: `test_recalculate_storage_called_each_tick` pins call count rather than behavior. We will rewrite it to assert the **invariant** (storage capacity updates within the turn a facility completes) rather than the implementation (called 100×).
- **GAPS** to fill with new tests before optimizing: mid-turn facility completion, mid-turn harvester destruction, mid-turn booster arrival via fleet movement.

### Invariants & risks (swarm_06)

1. **Highest risk**: caching `max_stockpile` or harvester sets without invalidation hooks would silently lose mid-turn changes. Mid-turn mutation surfaces are: `ProductionEngine._complete_item` (facility spawn at phase 0e), `PlanetWriteService.add_facility`/`remove_facility`, and `ComponentActivationEngine` state flips. Combat (out of scope here) is the other mid-turn destroyer but does not affect this project's facilities directly.
2. **Phase-ordering risk**: harvest runs at phase 0, production at 0e, movement_apply at 3. A booster carried by a fleet that moves at tick N's phase 3 will not affect harvest of tick N's phase 0 — that's existing behavior, and caches must preserve it (i.e. the booster takes effect at tick N+1, not tick N).
3. **Phase ordering is frozen** by golden tests; no accidental reorder risk.

## Key Patterns to Reuse

- **Per-turn cache with implicit turn-key invalidation** (PROJ-285): planet/empire transient field + `set_current_turn` setter wired through `TurnEngine.process_turn`. Documented in [`docs/systems/strategy_layer.md`](../../../docs/systems/strategy_layer.md).
- **Explicit `invalidate_all()` at turn boundary** (PROJ-254 facade caches).
- **`dirty` flag bumped from mutator path**: rather than version counters, set a single dirty bool inside write-service methods and clear it on cache rebuild. Keeps the invalidation surface small and discoverable.
- **`tests/performance/bench_galaxy_planet_star.py`** as the template for `bench_turn_processing.py`: fixed seed, fixed scenario, N min-of-runs, baseline JSON sibling, CI budget < 30 s.

## Dependencies & Risks

| Item | Risk | Mitigation |
|------|------|------------|
| Mid-turn facility mutation | Caching storage / harvester / booster results without invalidation would silently lose mid-turn changes. | Single `dirty` flag bumped by every `add_facility` / `remove_facility` / `set_facility_operational` / `_complete_item` path. Add characterization tests for all three mid-turn surfaces *before* any cache lands. |
| `_phase_times` key set | Renaming or removing a phase key breaks `test_turn_engine_phase_timing.py`. | Keep all 21 keys; only add new buckets if they appear in both descriptor lists and the timing test. |
| Phase ordering | Reordering would break `test_default_tick_phase_list.py`. | Do not reorder. All optimizations live inside sub-engines or in `_run_phases` orchestration, not in the descriptor lists. |
| Floating-point accumulation | Caching capacity and multiplier results that preserve iteration order should produce the same aggregate values. Risk is narrower than initially stated; the real danger is changing provider order, switching from `find_abilities_in_scope` to the universal effect pipeline, or reusing a multiplier after an invalidating mutation. | Tolerance-based end-state assertions in characterization tests **plus** provider/order equivalence assertions around `aggregate_multipliers` calls. Any drift beyond ≈ 1e-9 surfaced to user before merging. |
| Progress callback assumptions | If the callback genuinely needs to fire per tick for UI smoothness, batching it would degrade UX. | Measure first; UI callback is verified to redraw + flip per tick (see swarm_03). User has confirmed callback coarsening is in scope. |
| Rollback-and-retry cache staleness | `GameSession.process_turn` increments `turn_number` only on success ([game_session.py:321-329](../../../game/strategy/engine/game_session.py#L321)). On `EnginePhaseError`, `TurnStateSnapshot.restore` replaces galaxy + empires from the snapshot, but caches owned by `TurnEngine` / `HarvestingEngine` survive. A retry with the same turn number could hit stale `(turn, empire_id)` cache. | Phase 1 adds a rollback-and-retry characterization test. Phase 3 caches must clear / invalidate per-turn caches in the `EnginePhaseError` path (via a hook on `_NullBattleResolver` etc., or a direct `engine._invalidate_turn_caches()` call in the rollback site). |
| Caching the wrong thing | `_harvest_resource` mutates `planet.deposits[resource]["quantity"]` and stockpile every harvester tick. Caching *those* values would change depletion behavior. | Plan caches only ability metadata, storage capacity, and booster multipliers — never accumulated harvest values. Explicit in Phase 3 task descriptions. |
| Cache observability | `_phase_times` shows phase wall-clock but not whether a cache is hot, cold, or accidentally bypassed. | Phase 3 tasks add debug counters for storage rebuilds, booster cache hits/misses, and invalidation reason. Surface them in tests; do not rely on production benchmarks to detect bypassed caches. |
| Superweapon mutation surface | If fleet-carried ability sources ever feed harvesting, superweapon paths (`SuperweaponOrderProcessor`, `system_destroyer`) become invalidators. | The tiny benchmark excludes superweapons by construction; this is a future scope concern, not an active risk. Document it in benchmark scope notes rather than building the invalidation hook prematurely. |

## Opportunities Discovered

- **Late-import elimination** (free): three confirmed late imports inside hot paths (`harvesting_engine.py:405-407`, `turn_engine.py:276-277`, others). Move to module top.
- **`PlanetEnergyEngine` rescan pattern** is identical to harvesting's; the same cache + dirty-flag approach can apply once the harvesting pattern is validated.
- **`EnvironmentalHazardEngine`** has a `no_active_storms` short-circuit available — pure win when the galaxy has no storms.
- **`TurnStateSnapshot`** could skip when no session is provided, or use a copy-on-write strategy keyed off the same `dirty` flags.

## Design Decisions

See [decisions.md](decisions.md) for the running log. The plan-time decisions are:

1. **Profile before optimize**: Phase 1 is strictly measurement and characterization tests. No production code changes other than the trivial late-import moves explicitly authorized in Phase 2.
2. **Per-turn caches over per-tick recompute**: matches the PROJ-285 pattern already in the codebase.
3. **`dirty` flag invalidation, not version counters**: smaller, simpler, and the mid-turn mutation surface is already narrow.
4. **Phase ordering is frozen**: all optimizations live inside sub-engines or orchestration, never in the descriptor lists.
5. **No bit-for-bit equivalence requirement**, but any observable change in game state (resource totals, population counts, build completions at different ticks) must be surfaced for user approval before merging.
6. **Tiny scenario is the reference**: 2 empires, 2 planets, a handful of ships. Larger scenarios are not targeted by this project — the long-term path is the user's eventual Rust/C++ port.
