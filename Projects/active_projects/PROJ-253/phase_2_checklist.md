# Phase 2: Planet Energy Caching

**Objective:** Cache facility energy metadata (generation rate, storage capacity, drain rate) per planet, recalculated only on build/damage/toggle events instead of every energy tick.

**Key Principle:** Energy calculation per tick should be O(1) — read cached values and update energy level. The expensive facility/component/ability scan only runs when the facility configuration changes.

---

## Background

`PlanetEnergyEngine._process_planet()` performs 3 separate iteration passes per energy tick:
1. Scan facilities → components → abilities for generation and storage (lines 161-182)
2. `_compute_activation_drain()` rescans facilities → component_states for drain (lines 191-201)
3. `_cancel_all_draining_components()` rescans facilities → component_states again (lines 223-235)

For a planet with 10 facilities averaging 5 components each, that's 150+ iterations per tick, repeated for every planet.

## Design

1. Create `PlanetEnergyCache` dataclass: `generation_rate`, `storage_capacity`, `drain_per_tick`, `draining_components`
2. Cache is stored per planet (on the planet object or in the engine's state dict)
3. Cache is populated on first access and invalidated on: facility built, facility destroyed, component toggled, component damaged/repaired
4. `_process_planet()` reads from cache — becomes simple arithmetic per tick
5. Invalidation call sites: `ProductionEngine` (builds), `DamageCalculator` (damage), toggle command handlers

---

## Checklist

### Discovery
- [ ] Read `planet_energy_engine.py` fully — map all iteration paths
- [ ] Identify all code paths that modify facility state (build, destroy, toggle, damage, repair)
- [ ] Read `_compute_activation_drain()` and `_cancel_all_draining_components()` — understand dependencies
- [ ] Identify where to add invalidation calls (which engines/handlers modify facilities)

### Tests First (TDD)
- [ ] Write test: planet with facilities — cached generation rate matches manual scan
- [ ] Write test: planet with no facilities — cache returns zeros
- [ ] Write test: build new facility — cache invalidates and recalculates with new facility included
- [ ] Write test: destroy facility — cache invalidates and recalculates without destroyed facility
- [ ] Write test: toggle component — cache invalidates and drain rate changes
- [ ] Write test: process 100 energy ticks on stable planet — facility scan runs once (initial), not 100 times
- [ ] Run tests — confirm they fail

### Implementation
- [ ] Create `PlanetEnergyCache` dataclass with generation_rate, storage_capacity, drain fields
- [ ] Add cache storage to `PlanetEnergyEngine` (dict keyed by planet ID)
- [ ] Add `invalidate_energy_cache(planet_id)` method to `PlanetEnergyEngine`
- [ ] Refactor `_process_planet()` to read from cache instead of scanning
- [ ] Move facility scanning logic into a `_rebuild_cache(planet)` method
- [ ] Add invalidation calls at facility build/destroy/toggle/damage points
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Verify energy values are identical before/after for a multi-planet test scenario
- [ ] Instrument cache rebuilds with counter — confirm rebuilds only on mutation events
