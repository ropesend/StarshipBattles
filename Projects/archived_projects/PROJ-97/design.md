# PROJ-97: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Build Rate System (Current)
- `BuildQueueSource.build_rate` is a single `float` (default 2000.0)
- Hardcoded: 2000.0 for planet base queues, 3000.0 for shipyards/fleets
- `_get_facility_build_rate()` returns `3000.0 * construction_speed_bonus`
- `PLANETARY_YARD_BUILD_RATE = 2000.0` constant in build_queue_controller.py:18

### Turn Calculation (Current)
- `_calculate_build_turns()` uses: `ceil(max(cost.values()) / build_rate)` — takes the single highest-cost resource and divides by scalar rate
- `_build_cost_tracking()` divides total cost evenly across `turns * 100` ticks with no per-resource cap

### ProductionEngine (No Changes Needed)
- `process_construction_tick()` only reads `cost_per_tick` from queue items
- Never accesses `build_rate` — fully rate-agnostic
- Confirmed zero changes required to production_engine.py

### SpaceShipyardAbility (Current)
- Located at `game/simulation/components/abilities/harvester.py:95-128`
- Has `construction_speed_bonus` (float multiplier) and `max_ship_mass`
- No per-resource rate information currently

### ResourceStorage on Shipyards
- `space_shipyard` has `ResourceStorage: {Metals: 1000, Organics: 500}`
- `fleet_space_yard` has `ResourceStorage: {Metals: 500, Organics: 250}`
- **Confirmed dead code**: never read by ProductionEngine, HarvestingEngine, MaintenanceEngine, ResupplyEngine, any UI, or any test

---

## Swarm Findings Summary

### Architecture Analysis
- Build rate flows from `BuildQueueSource` → controller → queue item metadata
- ProductionEngine consumes only `cost_per_tick` — decoupled from rate definition
- Two parallel queue discovery functions: `collect_build_queues_at_hex()` and `collect_all_build_queues_for_empire()` — both hardcode rates at 6 locations total
- Queue items are created with `_build_cost_tracking()` which embeds cost_per_tick at creation time (not recalculated)

### Dependency Map
- **`build_rate` read in production code** (10 locations):
  - `build_queue_source.py`: lines 40, 44-65, 129, 146, 164, 199, 216, 232
  - `build_queue_controller.py`: lines 18, 196-214, 216-234, 389, 432, 476, 516
  - `build_queue_selector.py`: line 102
  - `empire_build_queue_window.py`: line 549
- **`build_rate` in test files** (15 locations):
  - `test_build_queue_source.py`: lines 469, 485, 494, 497, 509, 538, 541, 550
  - `test_build_queue_controller.py`: lines 383, 394, 401, 409, 416-417, 425
  - `test_empire_build_queue_window.py`: line 475
  - `test_empire_build_queue_formatter.py`: line 34

### Test Impact
- **Tests that directly assert `build_rate` value**: ~15 tests across 4 test files
- **Tests that use `cost_per_tick` only (no build_rate)**: All production engine tick consumption tests — should be unaffected
- **Integration tests**: `test_controller_multi_queue.py` creates `BuildQueueSource` without explicit `build_rate` — relies on default, which changes from float to dict

### Key Patterns to Reuse
- **JSON loading**: `game.core.json_utils.load_json(file_path, default=None)` — standard JSON file loading with error handling
- **Ability data parsing**: `SpaceShipyardAbility.__init__` pattern — `data.get("field_name", default)` for optional fields
- **Module-level caching**: Common pattern for expensive loads — use `_cache = None` with lazy init

### Dependencies & Risks
1. **Dual queue discovery functions** — Both `collect_build_queues_at_hex()` and `collect_all_build_queues_for_empire()` independently hardcode rates. Must update both consistently.
2. **Default value change** — `BuildQueueSource.build_rate` default changes from `2000.0` to `{}`. Any code that creates a `BuildQueueSource` without specifying `build_rate` will get an empty dict instead of 2000.0. Must audit all instantiation sites.
3. **UI display assumption** — Two UI sites assume `build_rate` is a number and call `int(source.build_rate)`. Must handle dict → display string.
4. **cost_per_tick is set once at queue creation** — Changing rates won't retroactively affect items already in a queue. This is correct behavior.

### Opportunities Discovered
- `ResourceType` constants class only has ship resources (fuel, energy, ammo), not economy resources. Economy resource names (Metals, Organics, Radioactives, Vapors, Exotics) are string literals throughout the codebase. Adding economy resource constants is out of scope but noted for future.
- The JSON config approach naturally supports future migration to component abilities (just read from component data instead of JSON file).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
