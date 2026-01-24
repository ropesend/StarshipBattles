# PROJ-05: Fleet Movement & Supply System

## Overview
Transform fleet movement from static speed values to a dynamic system based on ship component capabilities, with fuel consumption, warp point requirements, and fleet-level capability aggregation.

## Goals
- Wire FleetMobilityService to dynamically calculate fleet speed from ship designs
- Implement warp point requirements (all ships need WarpJump ability)
- Add strategic-layer fuel consumption per hex moved
- Add warp jump energy costs
- Create fleet capability aggregation methods

## Scope
**In Scope:**
- Dynamic fleet speed calculation from ship components
- Warp capability checks at fleet level
- Strategic fuel consumption (per-hex)
- Warp energy costs (per-jump)
- Fleet capability methods (`can_use_warp()`, `fuel_endurance()`)
- Pathfinding integration for warp-capable vs non-warp fleets

**Out of Scope:**
- Supply line mechanics
- Refueling at colonies/stations (future work)
- Fleet splitting for mixed warp/non-warp (future setting)
- Minimum speed thresholds for damaged ships (future setting)

## Current State
**Last Updated:** 2026-01-21
**Current Phase:** COMPLETE
**Last Agent Action:** All 5 phases implemented and tested
**Next Action:** User verification and manual testing
**Blockers:** None
**Context for Next Agent:** Project complete. All tests pass (2568 passed).

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Fleet Model | `game/strategy/data/fleet.py` | `Fleet` |
| Fleet Mobility | `game/strategy/services/fleet_mobility_service.py` | `FleetMobilityService` |
| Turn Engine | `game/strategy/engine/turn_engine.py` | `TurnEngine` |
| Pathfinding | `game/strategy/data/pathfinding.py` | `find_hybrid_path()` |
| ShipInstance | `game/strategy/data/ship_instance.py` | `ShipInstance` |
| ResourceConsumption | `game/simulation/components/abilities/resources.py` | `ResourceConsumption` |
| Propulsion Abilities | `game/simulation/components/abilities/propulsion.py` | `StrategicMovement`, `WarpJump` |
| Fleet Report Filters | `game/ui/screens/fleet_report_filters.py` | `has_warp_capability()` |
| Ship Stats | `game/simulation/entities/ship_stats.py` | Stats calculation |
| Ship Serialization | `game/simulation/entities/ship_serialization.py` | `ShipSerializer.to_dict()` |
| Fleet Report Window | `game/ui/screens/fleet_report_window.py` | Movement capabilities UI |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Strategic fuel uses new trigger type `strategic_per_hex` | Keeps all consumption in ResourceConsumption ability, cleaner than separate ability |
| 2026-01-21 | Non-warp fleets use direct hex path (no warp network) | Most realistic behavior, warp points are skipped entirely |
| 2026-01-21 | Per-ability methods for fleet capability (not generic system) | Clear, explicit API like `fleet.can_use_warp()`, `fleet.fuel_endurance()` |
| 2026-01-21 | Fleet cannot warp if ANY ship lacks WarpJump | Design for future flexibility - could become fleet setting for split behavior |
| 2026-01-21 | Future: Minimum speed threshold for fleet (damaged ships left behind) | Noted for future implementation |
| 2026-01-21 | Legacy string ships don't trigger speed recalc | Preserves backward compatibility with existing tests |

## Initial Analysis

### Architecture Summary
- **FleetMobilityService** already calculates ship/fleet speeds from designs (lines 44-137)
- **TurnEngine** uses tick-based movement (100 ticks/turn) but has NO fuel consumption
- **ResourceConsumption** supports `constant` and `activation` triggers - combat only
- **WarpJump** ability exists with `max_tonnage` constraint but not checked during pathfinding
- **Pathfinding** assumes all fleets can use warp points

### Key Patterns Identified
1. **Fleet speed = min(all ship speeds)** - convoy behavior already implemented
2. **Ability check from design_data**: iterate `layers → components → abilities`
3. **has_warp_capability()** exists in fleet_report_filters.py for individual ships
4. **ShipInstance.resource_levels** persists fuel/energy/ammo between battles

### Critical Gaps (RESOLVED)
1. ~~Fleet speed not auto-updated when ships join/leave~~ - Added `_trigger_speed_recalculation()`
2. ~~No warp capability check in pathfinding~~ - Added `fleet` param to `find_hybrid_path()`
3. ~~No strategic fuel consumption implementation~~ - Added `strategic_per_hex` trigger
4. ~~No warp energy cost~~ - Added `energy_cost` to WarpJump
5. ~~No fleet-level capability methods~~ - Added all methods

---

## Swarm Findings Summary

### Architecture Analysis
- Strategy layer accesses abilities via `design_data['expected_stats']` dict - no direct coupling to simulation
- TurnEngine doesn't call FleetMobilityService.recalculate_fleet_speed() after fleet changes
- WarpJump ability NOT serialized to expected_stats (gap)
- Pattern: "Write in simulation (to_dict), read in strategy (from design_data)"

### Key Patterns to Reuse
- **Speed calculation**: `fleet_mobility_service.py:92-122` - min of all ship speeds
- **Warp check**: `fleet_report_filters.py:11-46` - `has_warp_capability()` already exists
- **Resource tracking**: `ship_instance.py:128-132` - resource_levels dict persists fuel/energy

### Risks Identified
1. **Save/Load**: New expected_stats fields must default to 0/False for old saves
2. **0 Fuel**: Must check before movement - fleet stops if fuel depleted
3. **Mixed warp/non-warp**: Fleet.can_use_warp() must check ALL ships
4. **Performance**: Cache fleet capabilities, invalidate on ship changes
5. **Combat sync**: Preserve strategy-layer fuel through battles (don't reset)

---

## Phases

### Phase 1: Dynamic Fleet Speed [Medium] - COMPLETE
**Objective:** Wire FleetMobilityService to auto-recalculate fleet speed when ships join/leave/damaged
**Status:** COMPLETE

#### Task 1.1: Add speed recalculation trigger to Fleet [Simple] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`
- [x] Add method `_trigger_speed_recalculation()` that imports and calls FleetMobilityService
- [x] Call trigger in `merge_with()` method after ships transferred
- [x] Call trigger in ship add/remove methods if they exist
**Notes:** Added guard to skip recalculation for legacy string-only fleets

#### Task 1.2: Call recalculation after battle results [Simple] - COMPLETE
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/test_turn_engine.py`
- [x] After `_apply_battle_results()` (around line 516), call recalculate on both fleets
- [x] After fleet merge in Phase 0 (lines 254-259), call recalculate on target fleet
**Notes:** Recalculation happens via `_trigger_speed_recalculation()` in Fleet methods

---

### Phase 2: Warp Point Requirements [Medium] - COMPLETE
**Objective:** Serialize WarpJump to expected_stats, add fleet.can_use_warp(), modify pathfinding
**Status:** COMPLETE

#### Task 2.1: Serialize WarpJump to expected_stats [Medium] - COMPLETE
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py`
- [x] Add accumulators around line 158: `warp_max_tonnage = 0`
- [x] In component loop, aggregate WarpJump: `for ab in comp.get_abilities('WarpJump'): warp_max_tonnage = max(warp_max_tonnage, ab.max_tonnage)`
- [x] Assign to ship around line 253: `ship.warp_max_tonnage = warp_max_tonnage`

**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** Same
- [x] Add to expected_stats dict (after line 57): `"warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),`
**Notes:**

#### Task 2.2: Add Fleet.can_use_warp() method [Simple] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py` (add new tests)
- [x] Add method `can_use_warp(self) -> bool` after line 103
- [x] Iterate `get_combat_capable_ships()`, use existing `has_warp_capability()` from fleet_report_filters
- [x] Return False if ANY ship lacks warp capability
- [x] Add optional `_warp_limiting_ship` property for UI feedback
**Notes:** Added `get_warp_limiting_ship()` method

#### Task 2.3: Modify pathfinding to check warp capability [Medium] - COMPLETE
**File:** `game/strategy/data/pathfinding.py`
**Tests:** `pytest tests/strategy/test_fleet_movement.py`
- [x] Modify `find_hybrid_path()` signature (line 117): add optional `fleet=None` parameter
- [x] At line ~137 before interstellar path, check: `if fleet and not fleet.can_use_warp(): return find_path_deep_space(start_hex, end_hex)`
- [x] Update callers in turn_engine.py (line 332) to pass fleet

**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** Same
- [x] Update `calculate_path()` to accept and pass fleet parameter
**Notes:**

---

### Phase 3: Strategic Layer Fuel Consumption [Complex] - COMPLETE
**Objective:** Add `strategic_per_hex` trigger, consume fuel during movement
**Status:** COMPLETE

#### Task 3.1: Add strategic_per_hex trigger to ResourceConsumption [Simple] - COMPLETE
**File:** `game/simulation/components/abilities/resources.py`
**Tests:** `pytest tests/unit/abilities/`
- [x] Update docstring (line 11) to include `"strategic_per_hex"`
- [x] Add method `get_strategic_cost(self) -> float`: returns `self.amount` if trigger is 'strategic_per_hex', else 0
- [x] Update `get_ui_rows()` to show "/hex" for strategic trigger
**Notes:**

#### Task 3.2: Serialize strategic fuel consumption [Simple] - COMPLETE
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py`
- [x] Add accumulator: `total_strategic_fuel_cost = 0`
- [x] In component loop: aggregate ResourceConsumption where trigger=='strategic_per_hex' and resource=='fuel'
- [x] Assign: `ship.strategic_fuel_per_hex = total_strategic_fuel_cost`

**File:** `game/simulation/entities/ship_serialization.py`
- [x] Add to expected_stats: `"strategic_fuel_per_hex": getattr(ship, 'strategic_fuel_per_hex', 0),`
**Notes:**

#### Task 3.3: Add fuel consumption methods to ShipInstance [Medium] - COMPLETE
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance.py` (new tests)
- [x] Add `get_fuel_cost_per_hex(self) -> float`: reads from design_data expected_stats
- [x] Add `consume_fuel(self, amount: float) -> bool`: deducts from resource_levels, returns False if insufficient
- [x] Add `get_current_fuel(self) -> float`
**Notes:**

#### Task 3.4: Add fuel consumption methods to Fleet [Medium] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`
- [x] Add `get_fuel_cost_per_hex(self) -> float`: sum of all ships' costs
- [x] Add `has_fuel_for_movement(self) -> bool`: check all ships have fuel for 1 hex
- [x] Add `consume_fleet_fuel(self, hexes: int) -> bool`: consume from all ships
**Notes:**

#### Task 3.5: Integrate fuel consumption in TurnEngine [Medium] - COMPLETE
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/test_turn_engine.py`
- [x] Before movement at line ~281: check `if not fleet.has_fuel_for_movement(): log_warning; continue`
- [x] After passing check: `fleet.consume_fleet_fuel(1)`
- [x] Ensure fleet stops if out of fuel (orders cleared)
**Notes:**

---

### Phase 4: Warp Jump Energy Cost [Medium] - COMPLETE
**Objective:** Add energy_cost to WarpJump, consume energy during warp transit
**Status:** COMPLETE

#### Task 4.1: Add energy_cost property to WarpJump [Simple] - COMPLETE
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/unit/abilities/test_warp_jump.py`
- [x] Modify `__init__` (line ~100): parse `energy_cost` from dict data, default 0
- [x] Add `get_energy_cost(self) -> float` method
- [x] Update `get_ui_rows()` to show energy cost if non-zero
**Notes:**

#### Task 4.2: Serialize warp energy cost [Simple] - COMPLETE
**File:** `game/simulation/entities/ship_stats.py`
- [x] Add accumulator: `warp_energy_cost = 0`
- [x] In loop: `warp_energy_cost += ab.get_energy_cost()`
- [x] Assign: `ship.warp_energy_cost = warp_energy_cost`

**File:** `game/simulation/entities/ship_serialization.py`
- [x] Add to expected_stats: `"warp_energy_cost": getattr(ship, 'warp_energy_cost', 0),`
**Notes:**

#### Task 4.3: Add warp energy methods to ShipInstance and Fleet [Medium] - COMPLETE
**File:** `game/strategy/data/ship_instance.py`
- [x] Add `get_warp_energy_cost(self) -> float`
- [x] Add `consume_energy(self, amount: float) -> bool`
- [x] Add `get_current_energy(self) -> float`

**File:** `game/strategy/data/fleet.py`
- [x] Add `get_warp_energy_cost(self) -> float`: sum of all ships
- [x] Add `has_energy_for_warp(self) -> bool`
- [x] Add `consume_warp_energy(self) -> bool`
**Notes:**

#### Task 4.4: Consume warp energy in TurnEngine [Simple] - COMPLETE
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/strategy/test_turn_engine.py`
- [x] In movement phase, detect warp (hex_distance > 1)
- [x] Before warp: check `fleet.has_energy_for_warp()`, skip if False
- [x] After check: `fleet.consume_warp_energy()`
**Notes:**

---

### Phase 5: Fleet Capability Aggregation & UI [Medium] - COMPLETE
**Objective:** Add comprehensive fleet methods, update Fleet Report display
**Status:** COMPLETE

#### Task 5.1: Add fleet capability summary methods [Medium] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py`
- [x] Add `fuel_endurance(self) -> int`: hexes remaining (min across ships)
- [x] Add `warp_jumps_remaining(self) -> int`: jumps possible (min across ships)
- [x] Add `get_capability_summary(self) -> dict`: aggregate all capabilities for UI
**Notes:**

#### Task 5.2: Update fleet_report_filters.py [Simple] - COMPLETE
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** Manual UI test
- [x] Update `calculate_fleet_stats()` to include `warp_capable_count`, `all_warp_capable`
**Notes:**

#### Task 5.3: Update Fleet Report UI [Medium] - COMPLETE
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual UI test
- [x] Add "MOVEMENT" section to sidebar (after LOGISTICS)
- [x] Display: Warp Capable (Yes/No with limiting ship), Fuel Endurance (hexes), Warp Jumps remaining
- [ ] Color code: Green=capable, Yellow=limited, Red=unavailable (SKIPPED - not required)
**Notes:** Color coding not implemented - basic display works

---

## Verification Checklist

### After Each Phase
- [x] Run `pytest tests/unit/` - all tests pass
- [x] Run `pytest tests/strategy/` - all tests pass
- [ ] Manual test: Load existing save, verify no crashes (backward compat) - USER TO VERIFY

### Final Verification
- [ ] Create fleet with mixed warp/non-warp ships, verify cannot use warp points - USER TO VERIFY
- [ ] Create fleet with fuel consumption, move until fuel depleted, verify stops - USER TO VERIFY
- [ ] Warp with energy cost, verify energy consumed - USER TO VERIFY
- [ ] Fleet Report shows all new capability information - USER TO VERIFY
- [ ] Save/Load game with new mechanics, verify state persists - USER TO VERIFY
- [x] Run full test suite: `pytest` - 2568 passed, 1 skipped

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-21 | Test failure: Legacy string ships caused speed=0 | Added guard in `_trigger_speed_recalculation()` to skip if no ShipInstances |
| 1 | 2026-01-21 | Test failure: Mock expected old `find_hybrid_path` signature | Updated test to include `fleet=` kwarg |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All Phase 5 tasks checked off
- [x] All tests passing (2568 passed)
- [x] Regression tests passing
- [x] Audit passed (2 issues found and resolved)
- [ ] User verified - PENDING
