# Phase 3: Fleet Aura Aggregation Reuse & Caching

**Objective:** Replace the inline MAX-then-SUM stacking logic in `FleetAuraManager._recalculate()` with the shared `ability_aggregator._aggregate_ability_groups()`, and add provider-state caching.

**Key Principle:** The MAX-then-SUM two-phase aggregation pattern is documented in `docs/02_PATTERNS.md` and implemented in `ability_aggregator.py`. Fleet aura aggregation must use that single canonical implementation, not a reimplementation.

---

## Background

`FleetAuraManager._recalculate()` (CC ~20-25) reimplements the same stacking pattern as `ability_aggregator._aggregate_ability_groups()`:
- Intra-group MAX (redundancy within a stack group)
- Inter-group SUM (contributions from different sources add up)

It also rescans all provider ships and their components on every update call, with no caching for when the fleet composition hasn't changed.

## Design

1. Refactor `_recalculate()` to build ability groups in the dict shape `_aggregate_ability_groups()` expects
2. Call the shared aggregator for the MAX-then-SUM pass instead of inline logic
3. Add `_providers_dirty: bool` flag — only recalculate when fleet composition or provider operational status changes
4. Cache team bonuses in `_cached_team_bonuses: Dict[int, Dict[str, float]]`
5. Invalidation triggers: ship joins/leaves fleet, ship destroyed, aura-providing component toggled/destroyed

---

## Checklist

### Discovery
- [ ] Read `fleet_aura_manager.py:137-214` — map the full `_recalculate()` flow
- [ ] Read `ability_aggregator.py:19-61` — understand the shared aggregator's input/output contract
- [ ] Compare the two implementations — confirm they produce identical results for same input
- [ ] Identify all callers of `_recalculate()` — understand when it's triggered

### Tests First (TDD)
- [ ] Write test: aura values from refactored code match original for fleet with mixed providers
- [ ] Write test: aura values correct after adding a new provider ship to fleet
- [ ] Write test: aura values correct after removing a provider ship from fleet
- [ ] Write test: aura values correct after provider ship is destroyed
- [ ] Write test: cache works — 10 consecutive `_recalculate()` calls with no fleet change result in 1 actual computation
- [ ] Write test: cache invalidates when provider component is toggled
- [ ] Run tests — confirm they fail (no caching exists yet)

### Implementation
- [ ] Refactor `_recalculate()` — extract provider/component scanning into group-building step
- [ ] Transform group data into the shape `_aggregate_ability_groups()` expects
- [ ] Replace inline MAX-then-SUM with call to shared aggregator
- [ ] Add `_providers_dirty: bool` flag and cache storage
- [ ] Add invalidation method `invalidate_aura_cache()`
- [ ] Add invalidation calls at fleet composition change points (join/leave/destroy)
- [ ] Verify CC of refactored `_recalculate()` is significantly lower (~10-12)
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Verify aura bonuses are identical in a strategy-layer integration test
- [ ] Confirm no duplicate MAX-then-SUM logic remains in `fleet_aura_manager.py`
