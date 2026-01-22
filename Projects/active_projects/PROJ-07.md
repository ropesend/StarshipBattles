# PROJ-07: Strategy Layer Stats Calculation Refactor

## Overview
Refactor the strategy layer to calculate ship stats from actual components instead of reading from cached `expected_stats` values. The current PROJ-05 implementation incorrectly treats `expected_stats` as runtime data rather than its intended purpose: load-time validation only.

## Goals
- Remove all game logic reads from `expected_stats` in strategy layer
- Create a calculation service that computes stats from component definitions
- Support dynamic stat calculation that respects component damage
- Preserve `expected_stats` usage ONLY for load-time validation in `ship_serialization.py`

## Scope
**In Scope:**
- Refactor `ShipInstance` methods to calculate from components
- Refactor `fleet_report_filters.py` to use calculated values
- Refactor `fleet_mobility_service.py` to use calculated values
- Create component-based stat calculation utility
- Respect component damage in calculations

**Out of Scope:**
- Changes to simulation layer stat calculation
- Changes to `expected_stats` serialization format
- Combat-layer stats (only strategic layer stats)
- Modifiers affecting abilities (future enhancement)

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** Planning Complete - Awaiting Approval
**Last Agent Action:** Swarm review complete, detailed plan created
**Next Action:** User approval, then begin Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** Start with Phase 1, Task 1.1 - create ship_stats_service.py

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| ShipInstance | `game/strategy/data/ship_instance.py` | `ShipInstance` |
| Fleet Report Filters | `game/ui/screens/fleet_report_filters.py` | `has_warp_capability()`, `calculate_fleet_stats()` |
| Fleet Mobility | `game/strategy/services/fleet_mobility_service.py` | `FleetMobilityService` |
| Component Registry | `game/core/registry.py` | `get_component_registry()` |
| Ship Stats Calculator | `game/simulation/entities/ship_stats.py` | `ShipStatsCalculator` |
| Ship Serialization | `game/simulation/entities/ship_serialization.py` | Load validation |
| Design Library | `game/strategy/systems/design_library.py` | `load_design_data()` |
| Component Definitions | `data/components.json` | Raw ability data |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | `expected_stats` is for load validation only | User explicitly stated this is the intended design |
| 2026-01-21 | Damage model: Gradual degradation to 30%, then inactive | Default behavior. Components define own thresholds in JSON. |
| 2026-01-21 | Warp drives require 100% HP to function | User requirement - any damage disables warp |
| 2026-01-21 | Armor does not degrade (effective at any HP) | User requirement - armor special case |
| 2026-01-21 | New utility module: `ship_stats_service.py` | Clean separation, easy to test |
| 2026-01-21 | Cache stats with invalidation on damage change | Balance accuracy and performance |

## Initial Analysis

### Architecture Summary
The exploration agents identified **16 code locations** in the strategy layer that incorrectly read from `expected_stats`:

**`ship_instance.py` (11 locations):**
- Lines 155, 167, 180, 189, 202, 219, 228, 241, 318, 336, 498, 519
- HP calculations, resource levels, fuel/energy costs, display strings, repair/resupply

**`fleet_mobility_service.py` (3 locations):**
- Lines 79-81: mass, strategic_movement for speed calculation

**`fleet_report_filters.py` (5 locations):**
- Lines 24-32: mass, warp_max_tonnage for warp capability
- Lines 73, 87-98: mass, max_fuel, max_energy for fleet stats

### Simulation Layer Patterns (to reuse)
From `ship_stats.py`, stats are calculated by:
1. Iterating **active** components only (damage threshold check)
2. Aggregating abilities: `comp.get_abilities('WarpJump')`, etc.
3. Using accumulator patterns:
   - `warp_max_tonnage = max(all WarpJump.max_tonnage)`
   - `warp_energy_cost = sum(all WarpJump.energy_cost)`
   - `strategic_fuel_per_hex = sum(ResourceConsumption where trigger='strategic_per_hex')`
   - `strategic_movement = sum(all StrategicMovement.movement_points)`

### Component Data Access Pattern
Strategy layer can access component abilities via:
```python
from game.core.registry import get_component_registry
comp_def = get_component_registry().get(component_id)
abilities = comp_def.abilities  # Dict of ability name -> data
```

### Critical Gap
**No existing mechanism** in strategy layer to:
1. Calculate stats from `design_data['layers']` + component registry
2. Apply damage effects (reduced stats for damaged components)

---

## Swarm Findings Summary

### Architecture Analysis
- New service should be independent of simulation layer (no imports from `game.simulation`)
- Access component registry via `game.core.registry.get_component_registry()`
- Cache calculated stats on ShipInstance with invalidation on damage change
- Component IDs in `component_damage` dict match component entries in `design_data['layers']`

### Dependency Map (16 files affected)
**Direct consumers of `expected_stats`:**
- `ship_instance.py` - 11 methods read from expected_stats
- `fleet_mobility_service.py` - speed calculation reads mass, strategic_movement
- `fleet_report_filters.py` - warp check, fleet stats read multiple fields

**Downstream callers:**
- `Fleet` class methods call ShipInstance fuel/energy methods
- `FleetReportWindow` calls `calculate_fleet_stats()`
- 54+ tests rely on expected_stats structure

### Test Impact
**Existing tests:** 76+ tests in `tests/unit/strategy/`
**Coverage gaps identified:**
- No tests for damaged component stat calculation
- No tests for warp capability with damaged warp drive
- No fixtures with component_damage scenarios
**New tests needed:** ~30 tests for ship_stats_service and damage scenarios

### Key Patterns to Reuse
- **Damage threshold check:** `(current_hp / max_hp) <= threshold` → component inactive
- **Ability aggregation:** `comp.get_abilities('WarpJump')` returns list of abilities
- **Accumulator pattern:** Initialize accumulators, iterate components, apply atomically
- **Registry lookup:** `get_component_registry().get(component_id)` for definitions

### Risks Identified
1. **HIGH - Stale cache after damage:** ShipInstance cache must invalidate when component_damage changes
2. **HIGH - Multiple warp drives:** Only count ACTIVE drives for energy cost sum
3. **MEDIUM - Component ID matching:** Design uses base ID, damage dict may use indexed ID (e.g., `"bridge_0"`)
4. **MEDIUM - Backward compatibility:** Old saves without `component_damage` must default to `{}`
5. **LOW - Performance:** 100+ ship fleets should still be fast with caching

### Data Flow: Component Damage
```
component_damage: Dict[str, int]  # component_id -> current_hp
```
- Only stores DAMAGED components (current_hp < max_hp)
- Max HP comes from component registry
- Damage percentage: `current_hp / max_hp`
- Effectiveness: `max(0, (current_hp / max_hp - 0.3) / 0.7)` for default 30% threshold

---

## Phases

### Phase 1: Create Ship Stats Service [Medium]
**Objective:** Create new service that calculates stats from component definitions
**Status:** Not Started

#### Task 1.1: Create ship_stats_service.py skeleton [Simple]
**File:** `game/strategy/services/ship_stats_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`
- [ ] Create new file with class `ShipStatsService`
- [ ] Add method stub: `calculate_stats(design_data, component_damage=None) -> Dict`
- [ ] Add method stub: `get_component_effectiveness(comp_id, design_data, component_damage) -> float`
- [ ] Import only from `game.core.registry`
**Notes:**

#### Task 1.2: Implement component iteration [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** Same
- [ ] Implement `_iterate_design_components(design_data)` generator
- [ ] Yield `(layer_name, comp_entry, comp_registry_def)` tuples
- [ ] Handle missing components in registry gracefully (log warning, skip)
- [ ] Support both list and dict layer formats for backward compatibility
**Notes:**

#### Task 1.3: Implement damage effectiveness calculation [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** Same
- [ ] Implement `get_component_effectiveness(comp_id, design_data, component_damage) -> float`
- [ ] Get current_hp from `component_damage.get(comp_id, max_hp)`
- [ ] Get max_hp from component registry
- [ ] Apply damage model: gradual degradation to 30%, then 0
- [ ] Special case: Armor always returns 1.0 (no degradation)
- [ ] Special case: Warp drives return 1.0 only at 100% HP, else 0.0
**Notes:** Default threshold is 30% (component becomes useless)

#### Task 1.4: Implement stat aggregation [Complex]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** Same
- [ ] Implement `calculate_stats()` main method
- [ ] Initialize accumulators: mass, max_hp, max_fuel, max_energy, strategic_movement, etc.
- [ ] For each component: `effectiveness = get_component_effectiveness(...)`
- [ ] Aggregate mass: `total_mass += comp_def.mass` (mass doesn't degrade)
- [ ] Aggregate HP: `total_hp += comp_def.hp * effectiveness`
- [ ] Aggregate ResourceStorage: sum by resource type, apply effectiveness
- [ ] Aggregate StrategicMovement: `total += ability_value * effectiveness`
- [ ] Aggregate WarpJump: `max_tonnage = max(...)` only from 100% HP drives
- [ ] Aggregate warp_energy_cost: sum only from 100% HP drives
- [ ] Aggregate strategic_fuel_per_hex: sum ResourceConsumption with trigger='strategic_per_hex'
- [ ] Return dict matching `expected_stats` structure
**Notes:**

#### Task 1.5: Write unit tests for ship_stats_service [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`
- [ ] Test undamaged ship returns correct stats
- [ ] Test damaged component reduces HP contribution
- [ ] Test component at 30% HP contributes 0
- [ ] Test armor at 1% HP still contributes full HP
- [ ] Test warp drive at 99% HP contributes 0 to warp stats
- [ ] Test missing component in registry is skipped
- [ ] Test empty design returns zeros
**Notes:**

---

### Phase 2: Add Caching to ShipInstance [Simple]
**Objective:** Add cached stats property with invalidation
**Status:** Not Started

#### Task 2.1: Add cached stats to ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_detail_panel.py -v`
- [ ] Add attribute: `_cached_stats: Optional[Dict[str, Any]] = None` (line ~46)
- [ ] Add method `get_calculated_stats(self, force_refresh=False) -> Dict`
- [ ] In method: if `_cached_stats` is None or force_refresh, call ShipStatsService
- [ ] Import ShipStatsService inside method (avoid circular imports)
**Notes:**

#### Task 2.2: Add cache invalidation [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** Same
- [ ] Add method `invalidate_stats_cache(self)`
- [ ] Call `invalidate_stats_cache()` in `update_from_ship()` (line ~451)
- [ ] Call `invalidate_stats_cache()` when `component_damage` is modified
- [ ] Call `invalidate_stats_cache()` in `repair()` method (line ~498)
**Notes:**

---

### Phase 3: Refactor ShipInstance Methods [Medium]
**Objective:** Replace all `expected_stats` reads with calculated stats
**Status:** Not Started

#### Task 3.1: Refactor HP methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_detail_panel.py -v`
- [ ] `get_hp_percentage()` (line 155): use `get_calculated_stats()['max_hp']`
- [ ] `get_hp_display()` (line 318): use `get_calculated_stats()['max_hp']`
- [ ] `repair()` (line 498): use `get_calculated_stats()['max_hp']`
**Notes:**

#### Task 3.2: Refactor resource methods [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** Same
- [ ] `get_resource_percentage()` (line 167): use calculated `max_{resource}`
- [ ] `get_resource_display()` (line 336): use calculated max values
- [ ] `resupply()` (line 519): use calculated max values
**Notes:**

#### Task 3.3: Refactor fuel/energy methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py -v`
- [ ] `get_fuel_cost_per_hex()` (line 180): use `get_calculated_stats()['strategic_fuel_per_hex']`
- [ ] `get_current_fuel()` (line 189): use calculated `max_fuel` for default
- [ ] `consume_fuel()` (line 202): use calculated `max_fuel`
- [ ] `get_warp_energy_cost()` (line 219): use `get_calculated_stats()['warp_energy_cost']`
- [ ] `get_current_energy()` (line 228): use calculated `max_energy` for default
- [ ] `consume_energy()` (line 241): use calculated `max_energy`
**Notes:**

---

### Phase 4: Refactor Fleet Mobility Service [Simple]
**Objective:** Use calculated stats for speed calculation
**Status:** Not Started

#### Task 4.1: Update calculate_ship_speed [Simple]
**File:** `game/strategy/services/fleet_mobility_service.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_mobility_service.py -v`
- [ ] Line 79-81: Replace `expected_stats.get()` with `ship_instance.get_calculated_stats()`
- [ ] Get `mass` from calculated stats
- [ ] Get `strategic_movement` from calculated stats
- [ ] Handle case where calculated stats returns 0 for both
**Notes:**

---

### Phase 5: Refactor Fleet Report Filters [Medium]
**Objective:** Use calculated stats for warp checks and fleet stats
**Status:** Not Started

#### Task 5.1: Refactor has_warp_capability [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py -v`
- [ ] Line 24-32: Replace `expected_stats` reads with `ship.get_calculated_stats()`
- [ ] Get `mass` from calculated stats
- [ ] Get `warp_max_tonnage` from calculated stats (will be 0 if warp drive damaged)
- [ ] Simplify logic: if `warp_max_tonnage >= mass` then warp capable
**Notes:**

#### Task 5.2: Refactor calculate_fleet_stats [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** Same
- [ ] Line 73: Use `ship.get_calculated_stats()['mass']` for tonnage
- [ ] Line 87-98: Use calculated `max_fuel`, `max_energy` from each ship
- [ ] Ensure fleet stats reflect damaged ship capacities
**Notes:**

---

### Phase 6: Update Tests and Fixtures [Medium]
**Objective:** Update test fixtures and add damage scenario tests
**Status:** Not Started

#### Task 6.1: Update test fixtures [Simple]
**File:** `tests/unit/strategy/test_fleet_report_filters.py`
**Tests:** Same
- [ ] Update `make_mock_ship()` helper to support `component_damage` parameter
- [ ] Add `get_calculated_stats()` mock that returns computed values
**Notes:**

#### Task 6.2: Add damage scenario tests [Medium]
**File:** `tests/unit/strategy/test_ship_stats_service.py`
**Tests:** Same
- [ ] Test: Damaged engine reduces strategic_movement
- [ ] Test: Damaged warp drive (99% HP) makes ship non-warp-capable
- [ ] Test: Damaged fuel tank reduces max_fuel
- [ ] Test: Fleet with one damaged ship shows correct aggregate stats
**Notes:**

#### Task 6.3: Run full test suite and fix failures [Medium]
**Tests:** `pytest tests/ -v`
- [ ] Run all tests, document failures
- [ ] Fix any test that hardcodes `expected_stats` reads
- [ ] Ensure backward compatibility with existing fixtures
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/` - all tests pass
- [ ] Run `pytest tests/strategy/` - all tests pass
- [ ] Manual test: Ship with warp drive shows warp capability

### Final Verification
- [ ] Create fleet with warp-capable ships, verify Fleet Report shows "Warp: Yes"
- [ ] Damage a ship's warp drive in combat, verify warp capability changes to "No"
- [ ] Create fleet, damage engine, verify speed recalculates correctly
- [ ] Fleet Report shows correct tonnage, fuel, energy for damaged ships
- [ ] Save game with damaged ships, reload, verify damage persists
- [ ] Run full test suite: `pytest` - all pass

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1: Ship Stats Service complete
- [ ] Phase 2: Caching added to ShipInstance
- [ ] Phase 3: ShipInstance methods refactored
- [ ] Phase 4: Fleet Mobility Service refactored
- [ ] Phase 5: Fleet Report Filters refactored
- [ ] Phase 6: Tests updated
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
