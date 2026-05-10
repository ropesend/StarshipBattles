# PROJ-233: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### File Overview (864 lines)
`game/strategy/engine/production_engine.py` processes construction queues for all empires each tick (100 ticks/turn), consuming resources and spawning completed ships/facilities. It was partially refactored in PROJ-209, which decomposed the core loop into helpers.

### Responsibility Map
| Lines | Responsibility | Status |
|-------|---------------|--------|
| 1-53 | Imports, constants, TickExpenditure | Clean |
| 55-107 | Class init + `_calculate_design_cost` | Clean |
| 109-202 | `process_construction_tick` orchestrator | Bloated (77L, 30-line comment) |
| 204-306 | `_process_queue_tick_dynamic` core loop | Well-structured (PROJ-209) |
| 307-558 | PROJ-209 extracted helpers | Clean |
| 560-592 | `_complete_item` dispatch | Can simplify with spawner |
| 594-864 | **Spawn methods (270 lines)** | Extraction target |

### Key Finding: `_process_queue_tick_dynamic` is NOT the problem
Despite being 102 lines, the core loop was refactored in PROJ-209 to delegate to `_validate_queue_item`, `_calculate_tick_expenditure`, `_check_affordability`, `_apply_resource_consumption`, `_check_item_completion`, and `_update_turns_remaining`. Max nesting is 3 levels. The loop reads well and should not be split further.

### Actual Problems
1. **270 lines of spawn logic** form a distinct responsibility that should be a separate module
2. **Location resolution duplication** between `_create_and_place_facility` and `_spawn_ship`
3. **Limiting-resource formula duplication** between `_calculate_tick_expenditure` and `construction_forecast.py`
4. **30-line inline comment** in `process_construction_tick` (design discussion that reached a conclusion)
5. **Magic string validation** — `_validate_queue_item` returns `"valid"/"skip"/"stop"`
6. **Missing type hints** — `empire`, `galaxy`, `colony_or_fleet` untyped throughout
7. **Stale interface** — `IProductionEngine` still has `harvesting_engine` param (removed in PROJ-161)

## Swarm Findings Summary

### Architecture
- `ProductionEngine` implements `IProductionEngine` (single abstract method: `process_construction_tick`)
- Called by `TurnEngine._process_tick()` on every tick (100 per turn), Phase 0e
- Depends on: `DesignCostCalculator`, `DesignLibrary`, `ShipInstance.create()`, `Fleet`, `PlanetaryFacility`
- `TICKS_PER_TURN = 100` defined locally; `construction_forecast.py` uses inline `100` or implicit turn-based math

### Key Patterns to Reuse
- **`DesignCostCalculator`**: `game/strategy/services/design_cost_calculator.py` — already used correctly via `_calculate_design_cost()` delegation
- **`ShipInstance.create()`**: `game/strategy/data/ship_instance.py:134-192` — factory method already used in `_load_and_create_ship()`
- **`IProductionEngine` interface**: `game/strategy/interfaces/engines.py:120-163` — must maintain contract
- **`TickExpenditure` NamedTuple**: Well-designed return type for expenditure calculation
- **DI pattern**: Constructor `registries` parameter passed to spawned entities

### Dependencies & Risks
1. **Test files directly call private methods** — 29 references across 3 test files (`test_spawning.py`, `test_engine_event_emission.py`, `test_production_refactor.py`) need path updates when spawning moves. Mitigation: Mechanical find-and-replace.
2. **`MockProductionEngine`** in 2 locations includes stale `harvesting_engine` param. Both must be updated when interface is cleaned.
3. **`construction_forecast.py`** mirrors the limiting-resource formula — must produce identical results when shared function is extracted.
4. **Deferred import** (`build_queue_source`) inside `process_construction_tick` — verify no circular import when moved to top-level.

### Opportunities Discovered
- `_spawn_complex` is a trivial 1-line wrapper — can be inlined to eliminate a method
- `_load_design` is only called by `_create_and_place_facility` — stays as private helper in spawner
- Location resolution is an obvious extraction target with two near-identical implementations

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## New Module: `ProductionSpawner`

### Responsibility
Handles all entity spawning when construction items complete: ships (new fleets at planets, added to existing fleets), and facilities (complexes on planets).

### API
```python
class ProductionSpawner:
    def __init__(self, registries=None): ...
    def spawn_completed_item(self, item, empire, colony_or_fleet, galaxy, save_path, tick): ...
```

### Internal Methods
- `_load_design(design_id, empire, save_path) -> dict`
- `_load_and_create_ship(design_id, empire, save_path) -> Optional[ShipInstance]`
- `_create_and_place_facility(planet, design_id, empire, save_path, galaxy, log_prefix) -> None`
- `_spawn_ship(planet, design_id, empire, galaxy, save_path) -> None`
- `_spawn_fleet_ship(fleet, design_id, empire, save_path) -> None`
- `_spawn_fleet_complex(fleet, design_id, empire, galaxy, save_path, target_planet_id) -> None`
- `_resolve_planet_location(planet, galaxy) -> Tuple[Optional[List], str, Optional[List]]`

## New Module: `production_math.py`

### Responsibility
Single pure function for limiting-resource calculation, shared between `ProductionEngine` and `construction_forecast`.

### API
```python
def find_limiting_resource_ticks(
    remaining_cost: Dict[str, float],
    rate_per_turn: Dict[str, float],
    ticks_per_turn: int = 100,
) -> Optional[float]:
```

Returns total ticks needed, or `None` if any required resource has zero rate. When called with `ticks_per_turn=1`, returns turns directly (for forecast use).
