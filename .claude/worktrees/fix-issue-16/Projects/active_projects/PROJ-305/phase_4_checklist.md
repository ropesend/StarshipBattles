# Phase 4: Performance check + UI verification + docs

**Status:** Complete (2026-04-27)
**Objective:** Profile `collect_sector_effects` under realistic load; add per-turn caching if needed. Manual UI verification. Final docs sync. Run the canonical "all 7 source kinds active at one hex" smoke test.

---

## Tasks

### Task 4.1: Performance profiling [Medium]
**File:** N/A (profiling); changes go to `game/strategy/services/system_effects_collector.py` if needed.

- [ ] Generate a representative galaxy: 100 systems, ~1000 fleets total across empires. Or use an existing benchmark fixture.
- [ ] Profile a turn end-to-end with `cProfile` or `pytest-profiling`. Identify time spent in `collect_sector_effects` and `iter_ability_sources_at_hex`.
- [ ] **If above target** (target: collector should not exceed 5% of turn time, or whatever the user specifies): add per-turn cache:
  ```python
  _SECTOR_EFFECTS_CACHE: Dict[Tuple[int, Tuple[int,int], Optional[int]], List[Dict]] = {}
  # key: (turn_number, hex_coord_axial, empire_id)

  def collect_sector_effects(system, hex_coord, empire_id, registries=None):
      key = (system.galaxy.turn, hex_coord.axial(), empire_id)
      if key in _SECTOR_EFFECTS_CACHE:
          return _SECTOR_EFFECTS_CACHE[key]
      result = ...  # original computation
      _SECTOR_EFFECTS_CACHE[key] = result
      return result
  ```
- [ ] Hook cache invalidation to `TurnEngine.process_turn()` start (clear before phase 0).
- [ ] Add tests:
  - [ ] `test_cache_returns_same_object_within_turn`.
  - [ ] `test_cache_invalidates_at_turn_start`.
  - [ ] `test_fleet_movement_invalidates_relevant_cache_entries` — moving a fleet within a turn must invalidate the source/destination hex caches. (Or: cache is conservative and clears on fleet move.)
- [ ] **If under target**: skip caching entirely; document in decisions.md.

**Notes:**

### Task 4.2: Manual UI verification [Manual]

- [ ] Generate a galaxy. Build a flagship with the new Sensor Array component (PROJ-305 Phase 3).
- [ ] Click the flagship's hex from the owner's perspective — Sector panel shows the Sensor Boost effect with correct source_label.
- [ ] Switch to enemy perspective (or simulate via test) — confirm the effect is NOT visible (allied_sector scope).
- [ ] Move the fleet — effect follows.
- [ ] Combat in the same hex — the fleet's combat-only fleet-aura abilities still work; they don't appear in the Sector panel (only strategic-scope ones do).

**Notes:**

### Task 4.3: Canonical "all 7 source kinds" smoke test [Medium]
**File:** `tests/integration/strategy/test_unified_ability_framework_complete.py` (NEW)

- [ ] Build a fixture hex containing:
  1. A facility on a planet (sector-scope `ShieldModifier`).
  2. An overlapping storm.
  3. A volcanic planet (intrinsic `EnvironmentalDamage`).
  4. The hex is inside a system whose star is a neutron star (system-scope `EnvironmentalDamage`).
  5. The hex contains a warp point (sector-scope `EnvironmentalDamage`).
  6. The system has a `nebula` archetype (system-scope `ShieldModifier`).
  7. A fleet with a flagship sensor array sits at the hex (sector-scope `SensorBoost`).
- [ ] Assert `collect_sector_effects` returns the expected aggregate. Specifically:
  - Multiple `ShieldModifier` providers (facility, nebula archetype) — multiply correctly.
  - Multiple `EnvironmentalDamage` providers grouped per `damage_type`, summed correctly across types.
  - `SensorBoost` filtered by allied_sector ownership.
- [ ] This is the **regression baseline** for the entire ability framework. Treat as a high-priority test.

**Notes:**

### Task 4.4: Update docs [Medium]

- [ ] `docs/systems/strategy_layer.md` — final framework section now describes all 7 source kinds; reference all six PROJ-300..305 projects.
- [ ] `docs/systems/ability_reference.md` — add `SensorBoost` (or whatever new ability) entry; document the strategic-vs-combat scope dichotomy.
- [ ] `docs/02_PATTERNS.md` — update "Universal Ability Source" pattern (introduced in PROJ-300) with the full list of 7 source kinds.
- [ ] `docs/01_ARCHITECTURE.md` — final list of `IAbilitySource` adapters.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] Performance acceptable (profiled or cached)
- [ ] Canonical 7-source smoke test green
- [ ] Manual UI verification passes
- [ ] Docs updated
- [ ] `python Tools/test_sharded/test_sharded.py` clean
- [ ] Update plan.md → "Awaiting Verification"
- [ ] Notify user: full ability framework ships with this project — PROJ-300..305 complete.
