# PROJ-412 Harvesting Hotspot Analysis

**Scope**: Line-level breakdown of per-tick harvesting cost and prioritized fixes.
**Context**: 3.9s per turn on tiny game (2 empires, 2 planets, ~15 harvesters total); 100 calls/turn to process_harvesting_tick.

## Item 1: recalculate_storage(empires) Called Every Tick

**Confirmed**: Lines 221, 225-239.
**Analysis**: Walks ALL colonies, ALL operational facilities, ALL components in each facility per tick (100 times/turn) to scan for LocalStorage and StagingYard abilities.

**Allocations per call**:
- colony_storage = {} dict created per colony per tick (line 244)
- storage_totals populated via resolve_size_multiplier(comp) for each component
- empire_total = {} rebuilt wholly per call (lines 257-260)

**Change-detection issue**: Code has no per-facility change tracking. Destroyed facilities rely on !facility.is_operational check (line 247). But re-scanning all operational facilities every tick is O(colonies x facilities x components) per tick.

**Cost estimate**: **DOMINANT** (perhaps 30-40% of 3.9s based on facility iteration overhead).

**Fix proposal**: Move recalculate_storage() to once-per-turn (call before tick loop in TurnEngine._process_tick), not per-tick. Mid-turn facility construction triggers invalidation flag; check flag at loop start.

**References**: harvesting_engine.py:221, 225-262; planet_write_service.py:73-74 (cheap dict assignment).

---

## Item 2: _get_harvest_booster_mult Calls 4 Scope Queries Per Harvester Per Tick

**Confirmed**: Lines 405-419; called from _harvest_resource (line 461).

**Deep analysis** of find_abilities_in_scope (lines 64-99 in strategic_ability_scanner.py):
- **Scope resolution**: Calls _resolve_planets_for_scope (lines 89-91), which:
  - "planet" scope: returns [target_planet] - O(1)
  - "sector" scope: calls galaxy.get_planet_global_hex() + galaxy.get_planets_at_global_hex(), filters by owner - O(planets_at_hex)
  - "system" scope: calls galaxy.get_system_of_planet(), walks system.planets - O(planets_in_system)
  - "empire" scope: walks all empire.colonies - O(colonies)

- **Per-planet scan**: For each resolved planet, calls find_abilities_at_planet (lines 94-96):
  - Walks ALL operational facilities on the planet (line 44)
  - For each facility, iterates components via iter_keyed_components (line 50)
  - Each component extraction calls _extract_ability → extract_abilities_from_component (line 51)
  - Extracts abilities either inline OR via registry lookup

**Four-scope loop**: Each harvester does 4 scope queries. With ~15 harvesters per planet per tick, ~6-10 facilities per planet, 2-4 components per facility. Result: ~1800+ registry walks per tick.

**Cost estimate**: **DOMINANT** (30-40% of turn time, competing with storage recalc).

**Fix proposal**: Cache find_abilities_in_scope results per-turn-per-colony-per-scope before harvester loop; key by (ability_key, colony_id, scope).

**References**: harvesting_engine.py:388-419; strategic_ability_scanner.py:64-99, 185-245; component_inspector.py:49-79.

---

## Item 3: Late Import in _get_harvest_booster_mult

**Confirmed**: Lines 405-407 import find_abilities_in_scope, aggregate_multipliers inside the function, every call.

**Cost estimate**: **MINOR** (5-10% typical import overhead, ~50us per import). Multiplied by 15 harvesters x 100 ticks = 1500 import calls/turn, but Python sys.modules cache makes repeats cheap.

**Fix proposal**: Move imports to module top (lines 20-22). Saves ~75ms/turn if import machinery is not fully optimized.

**References**: harvesting_engine.py:405-407 vs. standard import pattern in lines 20-30.

---

## Item 4: iter_components(facility.design_data) and _get_ability_info Overhead

**Confirmed**: iter_components (layer_iterator.py:42-65) is a generator that walks layers dict once per call. No caching.

**Analysis**:
- Each call parses design_data['layers'] (no per-facility cache)
- _get_ability_info(comp, ability_name, registries) (lines 38-68):
  - First checks inline comp.get('abilities', {}) - O(1), cheap
  - If not found, falls back to registry lookup - O(1) dict lookup
- Called for every component in _process_facility, _collect_storage_from_facility, _collect_staging_capacity

**Cost estimate**: **MINOR-SIGNIFICANT** (10-15% of harvest loop, depends on registry lookup latency). Inline abilities are fast; registry lookups may be slow.

**Fix proposal**: If design_data uses inline abilities (most likely), cost is negligible. If registry lookups dominate: pre-build per-facility ability cache.

**References**: harvesting_engine.py:38-68; layer_iterator.py:42-65; component_inspector.py:49-79, 82-92.

---

## Item 5: set_max_stockpile() and replace_max_storage() Overhead

**Confirmed**: Writes to planet.max_stockpile (line 252) and empire.max_storage (line 261).

**Analysis**:
- set_max_stockpile(): Creates new dict (dict(new_max)) - O(n_resource_types) - then assigns
- replace_max_storage(): Clears and updates (lines 89-94) - O(n_resource_types)
- Neither broadcasts events or serializes

**Cost estimate**: **NEGLIGIBLE** (~2% of harvest tick). Dict creation is O(n), where n ~ 5-8 resource types.

**Fix proposal**: Skip the dict() copy in set_max_stockpile(); direct assignment or in-place update.

**References**: harvesting_engine.py:241-262; planet_write_service.py:73-74; empire_write_service.py:79-94.

---

## Ranked Top 5 Fixes (Highest Impact First)

1. **Cache booster multipliers per-turn-per-colony-per-scope** (~30-40% speedup)
   Move scoped ability queries outside harvester loop. Build cache at turn start.
   File: harvesting_engine.py:388-419, add per-turn cache in set_current_turn().

2. **Move recalculate_storage() to once-per-turn** (~25-35% speedup)
   Call once before tick loop in TurnEngine._process_tick, not 100x per turn. Invalidate on facility mutation.
   File: harvesting_engine.py:221, 225-262; TurnEngine (TBD).

3. **Move imports to module top** (~5-10% speedup)
   Eliminate 1500 redundant imports per turn.
   File: harvesting_engine.py:405-407, move to lines 20-30.

4. **Batch registry lookups at facility-level** (~5-10% speedup)
   Pre-resolve all component IDs to abilities once per facility per turn.
   File: harvesting_engine.py:38-92.

5. **Skip dict() copy in set_max_stockpile()** (~2-5% speedup)
   Direct assignment or in-place update.
   File: planet_write_service.py:73-74.

---

## Profiling Hypothesis for Phase 1

Expect to see:
- recalculate_storage + _aggregate_empire_storage + iter_components loops: **30-40ms per tick**
- _get_harvest_booster_mult + find_abilities_in_scope (4 scopes): **25-35ms per tick**
- Component ability lookups (inline + registry): **5-10ms per tick**
- Late imports: **2-5ms per tick**
- Storage writes: **<1ms per tick**

**Total: ~65-95ms per tick x 100 ticks = 6.5-9.5s expected per turn** (vs. observed 3.9s suggests smaller facility count or caching elsewhere; validate with profiler).

