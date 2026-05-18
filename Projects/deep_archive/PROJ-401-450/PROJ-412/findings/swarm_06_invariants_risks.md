# PROJ-412 Risk/Invariant Audit: Strategy Turn Optimization

## Summary

Optimization risks mid-turn cache staleness. The 100-tick loop is inviolable; caching must respect mutations during ticks: production spawns facilities (Phase 0e), environmental damage destroys ships/facilities (Phase 0f), fleets move (Phase 3). Phase order is frozen by golden test.

---

## 5 Critical Invariants

### 1. Storage Aggregation (max_stockpile)

**Invariant:** Colony.max_stockpile reflects all operational storage facilities at harvest time.

**Mutation:** add_facility() at production_engine.py:664 (tick T, Phase 0e). Environmental damage at Phase 0f.

**Currently:** Recalculated every tick in harvesting_engine.py:221 (full facility scan, O(facilities x components)).

**Risk:** Cache at tick 1 → facility spawned at tick 50 → cache reports pre-tick-50 capacity → overflow occurs.

**Safe:** Invalidate on facility mutation or recalculate every tick (~1ms cost).

### 2. Harvester List Per Colony

**Invariant:** Harvesters on a colony stable for harvest duration (can change between ticks).

**Mutation:** add_facility() spawns complex with new harvester components (Phase 0e).

**Currently:** Scanned every tick via iter_components(facility.design_data).

**Risk:** Cache at tick 1 → new harvester complex at tick 50 → ticks 50-100 ignore new resource type → starvation.

**Safe:** Invalidate on facility mutation or scan every tick (~2ms cost).

### 3. Booster Scope Coverage

**Invariant:** Boosters enumerated at harvest reflect fleet locations at harvest time.

**Mutation:** Fleet.location changes at Phase 3 (movement_apply).

**Currently:** Scanned every tick; no caching evident.

**Risk:** Booster cache at Phase 0 → fleet enters hex at Phase 3 → cache stale for ticks 1-100 → next turn's harvest uses stale cache.

**Safe:** Phase 0 (harvest) precedes Phase 3 (movement), so fleet cannot affect same-tick harvest. No cache needed; scan is ~2ms/tick.

### 4. Habitability Multiplier

**Invariant:** Per-turn cache reflects current species composition.

**Mutation:** None mid-tick (population changes end-of-turn only).

**Currently:** Cached per turn; TurnEngine.set_current_turn() invalidates at turn boundary.

**Risk:** Very low. Cache key is (turn); no mid-turn species death path.

**Safe:** Already mitigated by design. No changes needed.

### 5. Phase Ordering Enforcement

**Invariant:** Harvest (Phase 0) before Production (Phase 0e) before Movement (Phase 3) before Combat (Phase 4).

**Mutation:** If phases reordered, invariants 1-3 break.

**Currently:** Phase registry frozen in PROJ-365; golden test pins order.

**Risk:** Accidental reordering by future code. Breaks all mid-turn mutation assumptions.

**Safe:** Do not reorder without re-auditing invariants. Golden test catches this.

---

## Top 5 Risks Ranked

1. **CRITICAL:** Storage cache misses facility destruction → overflow
2. **CRITICAL:** Harvester cache misses new facility → resource starvation
3. **HIGH:** Booster cache invalidation order wrong → movement effect lost
4. **MEDIUM:** Production rate cache stale (already mitigated)
5. **MEDIUM:** Phase reordering regression (golden test guards)

---

## Recommendation

Recalculate facility-dependent data every tick (~3ms total cost). Caching savings are minimal; correctness risk is high. If caching is required, use version counters on add_facility/remove_facility and invalidate immediately.

The per-turn habitability cache is safe as-is.
