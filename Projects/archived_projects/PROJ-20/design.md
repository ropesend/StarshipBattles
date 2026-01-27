# PROJ-20: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project implements Phase 7 of the Legacy Code Cleanup: Standardize Data Formats. The objective is to remove dual-format support for various data structures throughout the codebase.

**Key Context from Legacy Cleanup README:**
- No save game migration is required
- Backward compatibility for save files is NOT a concern
- This enables clean removal of all legacy format handling

**Baseline Test Status:** 4542 passed, 1 flaky (test_quickstart_designs intermittent)

## Swarm Findings Summary

### Architecture

**Layer Boundaries:**
```
UI Layer (game/ui/)              → Uses calculated stats from services
Strategy Layer (game/strategy/)  → Primary target for format standardization
Simulation Layer (game/simulation/) → Has some legacy field dependencies
Core Layer (game/core/)          → Not affected
```

### Key Patterns to Reuse

- **Dict format for production queue**: `game/ui/screens/build_queue_screen.py:610-614`
  ```python
  queue_item = {"design_id": design_id, "type": cat, "turns_remaining": turns}
  ```

- **ShipInstance creation**: `game/strategy/engine/production_engine.py:175`
  ```python
  new_fleet.add_ship_instance(ship_instance)
  ```

- **New resource system**: `game/strategy/services/ship_stats_service.py:240-243`
  ```python
  'resource_storage': resource_storage,
  'resource_consumption_per_hex': resource_consumption_per_hex,
  'warp_resource_costs': warp_resource_costs,
  ```

### Dependencies & Risks

1. **Fleet Ship Format (12 callers of get_ship_instances)**
   - `fleet_report_window.py`, `turn_engine.py`, `fleet_mobility_service.py`
   - 5 test files with mocks
   - Mitigation: Replace with direct `fleet.ships` access

2. **Production Queue Format (5 files with isinstance checks)**
   - `production_engine.py`, `planet.py`, `build_queue_screen.py`
   - Mitigation: Update all creation points to use dict format

3. **Legacy Ship Stats Fields (33 files reference legacy fields)**
   - Heavy UI usage, simulation layer dependencies
   - Mitigation: Phase 4 as final phase, thorough testing

4. **Test Fixtures with Legacy Data**
   - `conftest.py` fixtures include legacy fields
   - `legacy_string_fleet` fixture exists
   - Mitigation: Update fixtures before removing legacy code

### Opportunities Discovered

- Production code already uses only ShipInstance (production_engine.py:175)
- Build queue UI already creates dict format (build_queue_screen.py:610-614)
- Legacy fields are re-exported from new dict fields (not stored separately)
- Tech tree format change is localized to one file (tech_tree.py:64-70)

## Detailed Findings by Task

### Task 7.1: Fleet Ship Format

**Current State:**
- Type: `List[Union[str, 'ShipInstance']]` (fleet.py:60)
- `get_ship_instances()` filters out strings (lines 101-104)
- `has_ship_instances()` checks for any ShipInstance (lines 124-127)
- Speed recalc guard for string-only fleets (lines 85-99)
- Serialization preserves both formats (lines 589-666)

**Files Using get_ship_instances():**
- `game/strategy/services/fleet_mobility_service.py:106`
- `game/ui/screens/fleet_report_window.py:752, 790`
- `game/strategy/engine/turn_engine.py:277, 464, 468`
- 5 test files

**Risk:** Medium - methodical replacement needed

### Task 7.2: Production Queue Format

**Current State:**
- Legacy: `["design_id", turns]`
- New: `{"design_id": "...", "type": "...", "turns_remaining": N}`

**Legacy Format Checks:**
- `production_engine.py:58, 74` - isinstance(item, list)
- `planet.py:139-149` - dual format creation
- `build_queue_screen.py:477, 483-485, 702, 760-761, 770`

**Risk:** Low - changes are isolated

### Task 7.3: Ship Stats Legacy Fields

**Legacy Fields (re-exported from new dicts):**
- `max_fuel`, `max_energy`, `max_ammo` → from `resource_storage`
- `strategic_fuel_per_hex` → from `resource_consumption_per_hex`
- `warp_energy_cost`, `warp_fuel_cost` → from `warp_resource_costs`

**Files Affected (33 total):**
- Strategy layer: `ship_instance.py`, `fleet.py`
- Services: `ship_stats_service.py`
- UI: `fleet_report_window.py`, `renderer.py`
- Simulation: `ship_stats.py`, `ship_serialization.py`
- 15+ test files

**Risk:** Medium - extensive changes but legacy fields are computed, not stored

### Task 7.4: Design Metadata Layer Format

**Current State:**
- Legacy: `{"components": [...]}`
- New: Direct list `[...]`

**Files with dual handling:**
- `design_metadata.py:163-169, 210-215`
- `planet.py:110-119`
- `ship_stats_service.py:347-354`

**Risk:** Low - straightforward pattern simplification

### Task 7.5: Tech Tree Requirement Format

**Current State:**
- Legacy: `{"level": 5}`
- New: `{"level_range": [5, 10]}`

**Single location:** `tech_tree.py:64-70`

**Risk:** Very Low - localized change

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
