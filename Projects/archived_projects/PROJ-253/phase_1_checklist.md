# Phase 1: Dirty-Flagged Ship Stat Invalidation

**Objective:** Add `_stats_dirty` flag to Ship so the 5-phase `ShipStatsCalculator.calculate()` pipeline only runs when component state has actually changed.

**Key Principle:** The transient per-tick update (resource consumption, component ticks) always runs. The expensive stat aggregation pipeline (phases 1-5) only runs when something changed that would affect stats (component destroyed, toggled, HP changed, etc.).

---

## Background

`ShipCombatManager.update()` calls `self._ship.recalculate_stats()` unconditionally on every tick. The 5-phase pipeline in `ShipStatsCalculator.calculate()` iterates all components 4+ times:
- Phase 1: `_phase_damage_check_and_supply()` — iterate all components
- Phase 2: `_phase_resource_allocation()` — sort + iterate all components
- Phase 3: `_phase_stats_aggregation()` — iterate all active components
- Phase 4: `_phase_physics_and_limits()` — O(1)
- Phase 5: `_phase_sensor_defense_scores()` — iterate pool

For a ship with 30 components over 1000 ticks, that's 120,000+ component iterations just for stats — most yielding identical results.

## Design

1. Add `_stats_dirty: bool = True` to `Ship.__init__`
2. `recalculate_stats()` checks flag: if False, return immediately
3. After full recalc, set `_stats_dirty = False`
4. State-change events set `_stats_dirty = True`:
   - Component destroyed (`current_hp` reaches 0)
   - Component HP changes (damage or repair)
   - Component toggled on/off
   - Component operational status changes
   - Resource depleted or restored
5. Split `ShipCombatManager.update()` into:
   - Transient update (always): resource ticks, component `update()` calls
   - Stat rebuild (only when dirty): the 5-phase pipeline
6. Debug assertion: in debug mode, every N ticks run full recalc and compare against cached values

---

## Checklist

### Discovery
- [ ] Read `ship_combat_manager.py:80-128` — map the full per-tick update flow
- [ ] Read `ship.py:516-538` — understand `recalculate_stats()` current behavior
- [ ] Read `ship_stats.py:103-184` — understand the 5-phase pipeline
- [ ] Identify all state-change points in `component.py` that should set dirty flag
- [ ] Identify all external callers of `recalculate_stats()` — ensure they still work

### Tests First (TDD)
- [ ] Write test: ship with no state changes — `recalculate_stats()` called twice, second call is a no-op (pipeline does not re-execute)
- [ ] Write test: ship takes damage — `_stats_dirty` becomes True, next `recalculate_stats()` runs full pipeline
- [ ] Write test: component toggled off — `_stats_dirty` becomes True
- [ ] Write test: component destroyed — `_stats_dirty` becomes True
- [ ] Write test: resource depleted causing component to become non-operational — `_stats_dirty` becomes True
- [ ] Write test: after full recalc, stats values are identical whether dirty flag was used or unconditional recalc
- [ ] Write test: initial ship creation has `_stats_dirty = True` (ensures first recalc always runs)
- [ ] Run tests — confirm dirty-flag tests fail (no dirty flag exists yet)

### Implementation
- [ ] Add `_stats_dirty: bool = True` field to `Ship.__init__`
- [ ] Add `mark_stats_dirty()` method to Ship (sets `_stats_dirty = True`)
- [ ] Update `recalculate_stats()` to check `_stats_dirty` — skip pipeline if False
- [ ] Set `_stats_dirty = False` at end of successful `recalculate_stats()`
- [ ] Add `mark_stats_dirty()` call to `Component` when `current_hp` changes
- [ ] Add `mark_stats_dirty()` call to `Component` when operational status changes
- [ ] Add `mark_stats_dirty()` call when component is toggled
- [ ] Add `mark_stats_dirty()` call when resource state changes affect component operation
- [ ] Ensure `_invalidate_components_cache()` also sets `_stats_dirty = True` (cache invalidation implies stat change)
- [ ] Update `ShipCombatManager.update()` to separate transient update from conditional stat rebuild
- [ ] Run tests — confirm they pass

### Debug Safety Net
- [ ] Add debug-mode assertion: every 100 ticks, run full recalc and compare key stats (max_hp, max_shields, max_speed, total_defense_score) against cached values
- [ ] If assertion fires, it indicates a missing dirty-flag call site — fix and add test

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Run simulation tests (`python -m simulation_tests.run_tests`) — all pass
- [ ] Instrument `calculate()` with a call counter in a test: 100 ticks on stable ship should show 1-2 calls (initial + maybe one), not 100
