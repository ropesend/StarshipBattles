# Planetary Complex System - Design Document

**Status:** ✅ COMPLETE (All Phases 1-4 Implemented)
**Last Updated:** 2026-01-17
**Test Pass Rate:** 100% (38/38 tests passing)

This is the living design document for the Planetary Complex Building System. It serves as the source of truth for architecture, implementation details, and agent handoff.

---

## Quick Links

- **Implementation Summary:** [planetary_complex_implementation_summary.md](planetary_complex_implementation_summary.md)
- **Manual Testing Guide:** [planetary_complex_manual_testing.md](planetary_complex_manual_testing.md)
- **Implementation Plan:** `~/.claude/plans/purrfect-questing-peach.md`

---

## System Overview

### Purpose
Allow players to design and build planetary complexes (facilities) on colonies, including resource harvesters and space shipyards. Shipyards are required to build ships.

### Key Features Implemented
- ✅ Design complexes in workshop (same UI as ships)
- ✅ Build queue UI with 4 categories (Complexes, Ships, Satellites, Fighters)
- ✅ One item completes per turn
- ✅ Complexes spawn as facilities on planets
- ✅ Space Shipyard enables ship construction
- ✅ Backwards compatible with old savegames
- ✅ 38 automated tests (100% passing)

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

See [planetary_complex_implementation_summary.md](planetary_complex_implementation_summary.md#architecture) for detailed architecture diagrams.

**Key Design Principles:**
1. Separation of Concerns (Planet owns data, BuildQueueScreen manages UI, TurnEngine spawns)
2. Leverage Existing Systems (Workshop, DesignLibrary, pygame_gui patterns)
3. Backwards Compatibility (Supports old and new queue formats)
4. Extensibility (design_data enables future features)

---

## Critical Files

### Production Code
- [game/strategy/data/planet.py](game/strategy/data/planet.py) - PlanetaryFacility, facilities, has_space_shipyard
- [game/ui/screens/build_queue_screen.py](game/ui/screens/build_queue_screen.py) - Build queue UI (~450 lines)
- [game/strategy/engine/turn_engine.py](game/strategy/engine/turn_engine.py) - process_production(), spawners
- [game/simulation/components/abilities/harvester.py](game/simulation/components/abilities/harvester.py) - Harvester abilities
- [data/components.json](data/components.json) - 6 new components

### Test Code
- [tests/strategy/test_planetary_facilities.py](tests/strategy/test_planetary_facilities.py) - 7 facility tests
- [tests/strategy/test_production.py](tests/strategy/test_production.py) - 9 production tests
- [tests/ui/test_build_queue_screen.py](tests/ui/test_build_queue_screen.py) - 10 UI tests
- [tests/ui/test_strategy_buttons.py](tests/ui/test_strategy_buttons.py) - 4 button tests
- [tests/integration/test_complex_workflow.py](tests/integration/test_complex_workflow.py) - 8 E2E tests

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

---

## Turn Processing

### Flow
```
Turn Advance
    ↓
process_production(empires, galaxy)
    ↓
For each colony:
    - Decrement first item's turns_remaining
    - If reaches 0:
        - Remove from queue
        - Route by vehicle_type:
            - "complex" → _spawn_complex() → Add to planet.facilities
            - Other → _spawn_ship() → Spawn fleet
```

### Key Methods

**process_production():** Supports both dict and list formats via isinstance() check

**_spawn_complex():**
- Loads design_data from DesignLibrary
- Creates PlanetaryFacility with UUID
- Adds to planet.facilities

**_spawn_ship():**
- Creates Fleet with design_id
- Spawns at planet location

---

## Test Coverage

### 38 Tests Total (100% Pass Rate)

| Category | Count | Files |
|----------|-------|-------|
| Unit | 16 | test_planetary_facilities.py (7), test_production.py (9) |
| Integration | 8 | test_complex_workflow.py (8) |
| UI | 14 | test_build_queue_screen.py (10), test_strategy_buttons.py (4) |

**Run Tests:**
```bash
python -m pytest tests/strategy/test_planetary_facilities.py \
                 tests/strategy/test_production.py \
                 tests/ui/test_build_queue_screen.py \
                 tests/ui/test_strategy_buttons.py \
                 tests/integration/test_complex_workflow.py -v
```

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

See [planetary_complex_implementation_summary.md](planetary_complex_implementation_summary.md#common-issues--solutions) for complete list.

---

## Implementation Status

### ✅ Phase 1: Data Model & Components (COMPLETE)
- PlanetaryFacility dataclass
- Planet.facilities field
- Planet.has_space_shipyard property
- 6 new components
- Ability classes
- 7 tests passing

### ✅ Phase 2: Build Queue UI (COMPLETE)
- BuildQueueScreen class
- 5 panels (Planet Report, Items List, Queue, Filter, Bottom Bar)
- Category filtering (4 types)
- Integration with StrategyScreen
- "Build Yard" button
- 14 tests passing

### ✅ Phase 3: Turn Processing (COMPLETE)
- Enhanced process_production()
- _spawn_complex() method
- _spawn_ship() helper
- Backwards compatibility
- 9 tests passing

### ✅ Phase 4: Integration Testing (COMPLETE)
- 8 integration tests
- Workshop verification
- Manual testing guide
- Documentation
- 38/38 tests passing (100%)

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
   - [game/strategy/data/planet.py](game/strategy/data/planet.py)
   - [game/ui/screens/build_queue_screen.py](game/ui/screens/build_queue_screen.py)
   - [game/strategy/engine/turn_engine.py](game/strategy/engine/turn_engine.py)

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

---

## Manual Testing

See [planetary_complex_manual_testing.md](planetary_complex_manual_testing.md) for 27 detailed test cases.

**Quick 5-Minute Test:**
1. Workshop → Select "Planetary Complex (Tier 1)" → See 6 components
2. Design complex with 2 harvesters, save as "Test Complex"
3. Strategy mode → Select owned planet → Click "Build Yard"
4. Add "Test Complex" to queue
5. Advance turns until complete
6. Verify facility appears in planet details

---

## Conclusion

**Status:** ✅ COMPLETE
**Test Coverage:** 100% (38/38)
**Production Ready:** Yes (manual testing recommended)

All Phase 1-4 objectives achieved. System is fully functional for core workflow: Design → Queue → Build → Facility.

For detailed implementation summary, see [planetary_complex_implementation_summary.md](planetary_complex_implementation_summary.md).
