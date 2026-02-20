# Planetary Complex System

**Status:** COMPLETE (All Phases 1-4 Implemented)
**Last Updated:** 2026-01-17
**Test Pass Rate:** 100% (38/38 tests passing)
**Total Development Time:** 4 sessions (~1,700 lines of production + test code)

This is the living design document for the Planetary Complex Building System. It serves as the source of truth for architecture, implementation details, and agent handoff.

---

## Quick Links

- **Manual Testing Guide:** [planetary_complex_testing.md](planetary_complex_testing.md)
- **Implementation Plan:** `~/.claude/plans/purrfect-questing-peach.md`

---

## System Overview

### Purpose
Allow players to design and build planetary complexes (facilities) on colonies, including resource harvesters and space shipyards. Shipyards are required to build ships.

### Key Features Implemented
- Design complexes in workshop (same UI as ships)
- Build queue UI with 4 categories (Complexes, Ships, Satellites, Fighters)
- One item completes per turn
- Complexes spawn as facilities on planets
- Space Shipyard enables ship construction
- Backwards compatible with old savegames
- 38 automated tests (100% passing)

### User Workflow
```
1. Design Complex in Workshop
   - Select "Planetary Complex (Tier 1-11)"
   - Place components (harvesters, shipyard)
   - Save design to designs/ folder

2. Queue Complex for Building
   - In strategy mode, select owned planet
   - Click "Build Yard" button
   - Select "Complexes" category
   - Choose design, click "Add to Queue"

3. Build Complex Over Turns
   - Advance turns (each turn decrements counter)
   - When turns reach 0, complex completes
   - Facility appears in planet.facilities list

4. Use Facility
   - Shipyard: Enables ship building
   - Harvesters: (Future) Generate resources
```

---

## Architecture

### Key Design Principles
1. **Separation of Concerns** - Planet owns data, BuildQueueScreen manages UI, TurnEngine spawns
2. **Leverage Existing Systems** - Workshop, DesignLibrary, pygame_gui patterns
3. **Backwards Compatibility** - Supports old and new queue formats
4. **Extensibility** - design_data enables future features

### UI Architecture
```
+--------------------------------------------------+
|  Planet Report Panel (150px height)               |
|  [Name] [Type] [Resources] [Facilities Count]    |
+------------+------------------+-------------------+
| Items List |  Build Queue     | Filter Panel      |
| (300px)    |  (flex width)    | (250px)           |
|            |                  |                    |
| [Design 1] |  [Item 1] 3 t.  | [Complexes]       |
| [Design 2] |  [Item 2] 5 t.  | [Ships]           |
| [Design 3] |                  | [Satellites]      |
|            |                  | [Fighters]        |
|            |                  |                    |
|            |                  | [Add to Queue]    |
|            |                  | [Remove]          |
+------------+------------------+-------------------+
|  Bottom Bar: [Close] [Turn: N]                    |
+---------------------------------------------------+
```

---

## Critical Files

### Production Code
| File | Description |
|------|-------------|
| `game/strategy/data/planet.py` | PlanetaryFacility, facilities, has_space_shipyard |
| `game/ui/screens/build_queue_screen.py` | Build queue UI (~450 lines) |
| `game/strategy/engine/turn_engine.py` | Turn processing, production delegation to ProductionEngine |
| `game/simulation/components/abilities/harvester.py` | Harvester abilities (~40 lines) |
| `data/components.json` | 6 new components |

### UI Integration
| File | Description |
|------|-------------|
| `game/ui/screens/strategy_screen.py` | Renamed button to "Build Yard", shows facilities |
| `game/ui/screens/strategy_input_handler.py` | Routes btn_build_yard clicks |
| `game/ui/screens/strategy_scene.py` | on_build_yard_click() and close callback |

### Test Code
| File | Tests |
|------|-------|
| `tests/strategy/test_planetary_facilities.py` | 7 facility tests |
| `tests/strategy/test_production.py` | 9 production tests |
| `tests/ui/test_build_queue_screen.py` | 10 UI tests |
| `tests/ui/test_strategy_buttons.py` | 4 button tests |
| `tests/integration/test_complex_workflow.py` | 8 E2E tests |

### Files Created (New)
- `game/ui/screens/build_queue_screen.py` - Build queue UI
- `game/simulation/components/abilities/harvester.py` - Harvester abilities
- `tests/strategy/test_planetary_facilities.py` - Facility CRUD tests
- `tests/ui/test_build_queue_screen.py` - UI tests
- `tests/integration/test_complex_workflow.py` - E2E tests

### Files Modified
- `data/components.json` - Added 6 components
- `game/strategy/data/planet.py` - Added PlanetaryFacility, facilities, has_space_shipyard
- `game/strategy/engine/turn_engine.py` - Enhanced process_production(), added spawners
- `game/ui/screens/strategy_screen.py` - Renamed button, show facilities
- `game/ui/screens/strategy_input_handler.py` - Route button press
- `game/ui/screens/strategy_scene.py` - Added callbacks
- `game/simulation/components/abilities/__init__.py` - Registered new abilities
- `tests/ui/test_strategy_buttons.py` - Updated for btn_build_yard
- `tests/strategy/test_production.py` - Added 5 new tests

---

## Data Models

### PlanetaryFacility
```python
@dataclass
class PlanetaryFacility:
    instance_id: str          # UUID
    design_id: str            # e.g. "mining_complex_mk1"
    name: str                 # From design
    design_data: Dict[str, Any]  # Full JSON
    is_operational: bool = True
```

**Design Decisions:**
- Facilities stored as separate instances (not just counts)
- Each facility has unique UUID for future damage tracking
- design_data embedded in facility for offline querying
- has_space_shipyard checks all operational facilities for SpaceShipyard ability

### Planet Enhancements
```python
@dataclass
class Planet:
    facilities: List[PlanetaryFacility] = field(default_factory=list)
    construction_queue: list = field(default_factory=list)

    @property
    def has_space_shipyard(self) -> bool:
        """Check for operational SpaceShipyard component in any facility."""
```

### Construction Queue Formats

**Old (Backwards Compatible):**
```python
["Colony Ship", 5]  # Ship name, turns
```

**New:**
```python
{
    "design_id": "mining_complex_mk1",
    "type": "complex",
    "turns_remaining": 5
}
```

**Queue Format Migration:**
- `add_production()` supports both formats:
  - Legacy: `add_production("Colony Ship", 5)` -> `["Colony Ship", 5]`
  - New: `add_production("design_id", turns=5, vehicle_type="complex")` -> dict

---

## Components

### 6 New Components Added to data/components.json

All restricted to `"allowed_vehicle_types": ["Planetary Complex"]`

1. **metal_harvester** - Harvests Metals (10.0/turn base)
2. **organic_harvester** - Harvests Organics
3. **vapor_harvester** - Harvests Vapors
4. **radioactive_harvester** - Harvests Radioactives
5. **exotic_harvester** - Harvests Exotics
6. **space_shipyard** - Enables ship construction

### Ability Classes

**File:** `game/simulation/components/abilities/harvester.py`

```python
class ResourceHarvesterAbility(Ability):
    resource_type: str
    base_harvest_rate: float

class SpaceShipyardAbility(Ability):
    construction_speed_bonus: float
    max_ship_mass: int
```

Both registered in ABILITY_REGISTRY.

---

## Turn Processing

### Flow
```
Turn Advance (TurnEngine.process_turn)
    |
    +-- 100-tick subturn loop:
    |       |
    |       ProductionEngine.process_construction_tick(tick, empires, galaxy)
    |           |
    |           For each colony/fleet queue:
    |               - Calculate dynamic resource consumption per tick
    |               - Deduct resources from empire pool
    |               - Track resources_consumed in queue item
    |               - When resources_consumed >= total_cost:
    |                   - Route by vehicle_type:
    |                       - "complex" -> _spawn_complex()
    |                       - Other -> _spawn_ship()
    |
    +-- End-of-turn orders (colonize, etc)
    +-- Population growth
```

PROJ-79 migrated all production to tick-based dynamic resource consumption.
Items complete mid-turn when their resource cost is fully consumed.
The old `process_production()` method has been removed (PROJ-158).

### Key Methods

**process_construction_tick():** (ProductionEngine)
- Called 100 times per turn via the subturn loop
- Processes dynamic resource consumption based on production rates
- Triggers mid-turn completion and spawning when resources_consumed >= total_cost

**_spawn_complex():** (ProductionEngine)
- Loads design_data from DesignLibrary
- Creates PlanetaryFacility with UUID
- Adds to planet.facilities
- Gracefully handles missing design files (logged as warnings, not errors)
- Uses Empire.savegame_path for DesignLibrary lookup

**_spawn_ship():**
- Creates Fleet with design_id
- Spawns at planet location
- Uses design_id instead of name

---

## Test Coverage

### 38 Tests Total (100% Pass Rate)

| Category | Count | Files |
|----------|-------|-------|
| Unit | 16 | test_planetary_facilities.py (7), test_production.py (9) |
| Integration | 8 | test_complex_workflow.py (8) |
| UI | 14 | test_build_queue_screen.py (10), test_strategy_buttons.py (4) |

### Coverage Matrix

| Layer | Unit | Integration | UI | Total |
|-------|------|-------------|-----|-------|
| Data Model | 7 | 3 | - | 10 |
| Turn Processing | 9 | 5 | - | 14 |
| UI Components | - | - | 14 | 14 |
| **Total** | **16** | **8** | **14** | **38** |

### Testing Strategy

**TDD Approach (Red-Green-Refactor):**
1. **Red Phase:** Write failing tests first
2. **Green Phase:** Implement code to pass tests
3. **Refactor Phase:** Improve code while maintaining passing tests

**Test Pyramid:**
```
         /\
        /E2\     8 Integration Tests
       /----\    (Full workflow)
      /      \
     / Unit   \  16 Unit Tests
    / Tests    \ (Components, logic)
   /------------\
  /    UI        \ 14 UI Tests
 /    Tests       \ (Screens, buttons)
/------------------\
```

### Integration Test Details
- test_design_save_load_complex() - Design persistence
- test_complex_design_in_build_queue() - Category filtering
- test_full_build_workflow() - Complete Design -> Facility flow
- test_shipyard_enables_ship_building() - Shipyard validation
- test_multiple_complexes_on_planet() - Multiple facilities
- test_backwards_compat_mixed_queue() - Legacy format support
- test_shipyard_detection_with_multiple_facilities() - has_space_shipyard
- test_non_operational_shipyard_not_detected() - Damaged shipyard

**Run Tests:**
```bash
python -m pytest tests/strategy/test_planetary_facilities.py \
                 tests/strategy/test_production.py \
                 tests/ui/test_build_queue_screen.py \
                 tests/ui/test_strategy_buttons.py \
                 tests/integration/test_complex_workflow.py -v
```

---

## Architecture Strengths

### 1. Separation of Concerns
- **Strategy Layer:** Planet owns facilities (business logic)
- **UI Layer:** BuildQueueScreen manages display (presentation)
- **Turn Processing:** TurnEngine spawns entities (game loop)

### 2. Leverages Existing Systems
- Uses DesignLibrary for design loading (no duplication)
- Uses existing workshop for design creation (no changes needed)
- Uses pygame_gui patterns consistent with other UI screens

### 3. Extensibility
- PlanetaryFacility design_data enables future features:
  - Resource harvesting implementation
  - Facility damage tracking
  - Upgrade/repair mechanics
- Generic vehicle_type field supports future types (e.g., "base", "station")

### 4. Backwards Compatibility
- Supports both old and new queue formats
- Old saves load without migration script
- Graceful handling of missing design files

### 5. Test Coverage
- TDD approach ensures correctness
- 38 automated tests covering all layers
- Integration tests verify E2E workflow

---

## Performance Considerations

### Optimizations Applied
1. **has_space_shipyard:** Computed property (could be cached with invalidation)
2. **DesignLibrary Scans:** Results not cached in BuildQueueScreen (could add 5s TTL)
3. **UI Element Cleanup:** Properly kills child elements to prevent memory leaks

### Performance Notes
- Facilities list iteration is O(n) per facility check
- Design scanning is O(n) per category switch
- Queue processing is O(n) per turn per colony
- All acceptable for typical game scale (10-50 colonies, 10-100 facilities)

---

## Common Issues & Solutions

### Issue 1: DesignLibrary can't find designs
**Solution:** Designs must be at `{savegame_path}/designs/*.json` not `designs/empire_1/`

### Issue 2: has_space_shipyard returns False
**Solution:** Ensure _spawn_complex() loads design_data from DesignLibrary

### Issue 3: UIScrollingContainer.clear() doesn't exist
**Solution:** Manually kill children:
```python
for element in container.get_container().elements:
    element.kill()
```

### Issue 4: TypeError with None savegame_path
**Solution:** Check for None before using DesignLibrary

### Issue 5: Build button doesn't appear
**Solution:** Update show_detailed_report() to show/hide based on ownership

---

## Implementation Status

### Phase 1: Data Model & Components (COMPLETE)
- PlanetaryFacility dataclass
- Planet.facilities field, Planet.has_space_shipyard property
- 6 new components and ability classes
- 7 tests passing

### Phase 2: Build Queue UI (COMPLETE)
- BuildQueueScreen class with 5 panels
- Category filtering (4 types)
- Integration with StrategyScreen ("Build Yard" button)
- 14 tests passing

### Phase 3: Turn Processing (COMPLETE)
- Enhanced process_production() with backwards compatibility
- _spawn_complex() and _spawn_ship() methods
- 9 tests passing

### Phase 4: Integration Testing (COMPLETE)
- 8 integration tests covering full workflow
- Workshop verification (11 tiers, 6 components)
- Manual testing guide and documentation
- 38/38 tests passing (100%)

### Implementation Timeline
- **Phase 1:** Completed in 1 session (data model + components)
- **Phase 2:** Completed in 1 session (build queue UI)
- **Phase 3:** Completed in 1 session (turn processing)
- **Phase 4:** Completed in 1 session (integration tests)

---

## Future Enhancements (Not Implemented)

### High Priority
1. Resource harvesting logic (components exist, logic deferred)
2. IssueBuildCommand with validation
3. Build queue cancellation
4. Shipyard requirement enforcement

### Medium Priority
1. Construction speed bonuses
2. Queue reordering
3. Build progress bars
4. Resource cost validation

### Low Priority
1. Facility damage mechanics
2. Facility upgrades
3. Design preview in build queue
4. Cache has_space_shipyard result

---

## Agent Handoff Instructions

### If Picking Up This Task

1. **Read This Document** - Source of truth
2. **Run Tests** - Verify 38/38 passing
3. **Review Key Files:**
   - `game/strategy/data/planet.py`
   - `game/ui/screens/build_queue_screen.py`
   - `game/strategy/engine/turn_engine.py`
4. **Check Status** - All phases complete, ready for manual testing or future enhancements

### If Debugging

1. Check logs (log_debug/log_info/log_warning)
2. Verify design files exist
3. Print queue contents
4. Test has_space_shipyard detection

### If Extending

1. **Add New Vehicle Type:** Update type_map, add button, add spawn case
2. **Add Resource Harvesting:** Check for ResourceHarvesterAbility, update planet.resources
3. **Add Facility Damage:** Set is_operational = False
4. **Add Build Commands:** Create command, add validation, route through session

### Quick Reference

**Key Classes:**
- `PlanetaryFacility` - Represents a built complex
- `BuildQueueScreen` - Full-screen build queue UI
- `DesignLibrary` - Manages design files
- `TurnEngine` - Processes production queue

**Key Methods:**
- `Planet.has_space_shipyard` - Checks for operational shipyard
- `Planet.add_production()` - Adds item to build queue
- `ProductionEngine.process_construction_tick()` - Processes per-tick resource consumption and mid-turn completion
- `ProductionEngine._spawn_complex()` - Spawns completed complex as facility
- `ProductionEngine._spawn_ship()` - Spawns completed ship as fleet

---

## Manual Testing

See [planetary_complex_testing.md](planetary_complex_testing.md) for 27 detailed test cases.

**Quick 5-Minute Test:**
1. Workshop -> Select "Planetary Complex (Tier 1)" -> See 6 components
2. Design complex with 2 harvesters, save as "Test Complex"
3. Strategy mode -> Select owned planet -> Click "Build Yard"
4. Add "Test Complex" to queue
5. Advance turns until complete
6. Verify facility appears in planet details

---

## Conclusion

**Status:** COMPLETE
**Test Coverage:** 100% (38/38)
**Production Ready:** Yes (manual testing recommended)

All Phase 1-4 objectives achieved. System is fully functional for core workflow: Design -> Queue -> Build -> Facility.
