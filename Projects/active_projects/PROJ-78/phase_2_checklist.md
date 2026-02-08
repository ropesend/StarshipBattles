# Phase 2: Add spawn_initial_complexes() to QuickstartBuilder

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-78 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `spawn_initial_complexes()` method to QuickstartBuilder class

---

## Task 2.1: Add spawn_initial_complexes() method [Medium]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/ --testmon`

Add the following after `copy_quickstart_designs()` method (around line 237):

- [x] Add INITIAL_COMPLEXES constant at module level:
```python
INITIAL_COMPLEXES = [
    'qs_complex',           # Shipyard (existing)
    'qs_metals_complex',
    'qs_organics_complex',
    'qs_vapors_complex',
    'qs_radioactives_complex',
    'qs_exotics_complex',
    'qs_resupply_depot',
]
```

- [x] Add imports at top of file:
```python
import uuid
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.systems.design_library import DesignLibrary
```

- [x] Add spawn_initial_complexes() method:
```python
@staticmethod
def spawn_initial_complexes(save_path: str, session: 'GameSession') -> bool:
    """
    Spawn pre-built complexes on all home planets.

    Called after designs are copied and save_path is set.

    Args:
        save_path: Path to save folder (designs already copied here)
        session: GameSession with empires and colonies initialized

    Returns:
        True if all complexes spawned successfully
    """
    success = True

    for empire in session.empires:
        # Get home planet (first colony)
        if not empire.colonies:
            log_warning(f"Empire {empire.id} has no colonies - skipping complex spawn")
            continue

        home_planet = empire.colonies[0]
        library = DesignLibrary(save_path, empire.id)

        for design_id in INITIAL_COMPLEXES:
            design_data = library.load_design_data(design_id)

            if not design_data:
                log_warning(f"Could not load design {design_id} for empire {empire.id}")
                success = False
                continue

            facility = PlanetaryFacility(
                instance_id=str(uuid.uuid4()),
                design_id=design_id,
                name=design_data.get("name", design_id),
                design_data=design_data,
                is_operational=True
            )

            home_planet.facilities.append(facility)
            log_info(f"Spawned {facility.name} on {home_planet.name} (Empire {empire.id})")

    return success
```

- [x] Verify method compiles without errors
- [x] Check import statements are at file top

**Notes:**

---

## Task 2.2: Add TYPE_CHECKING import [Simple]
**File:** `game/strategy/quickstart_builder.py`

- [x] Add TYPE_CHECKING import for GameSession type hint:
```python
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession
```

**Notes:**

---

## Reference: Existing Pattern from ProductionEngine

The `_spawn_complex()` method in `game/strategy/engine/production_engine.py` (lines 239-280) shows the pattern:

```python
def _spawn_complex(self, planet, design_id: str, empire, save_path: Optional[str] = None) -> None:
    design_data = {}
    if save_path:
        library = DesignLibrary(save_path, empire.id)
        loaded_data = library.load_design_data(design_id)
        if loaded_data:
            design_data = loaded_data

    facility = PlanetaryFacility(
        instance_id=str(uuid.uuid4()),
        design_id=design_id,
        name=design_data.get("name", design_id),
        design_data=design_data,
        is_operational=True
    )
    planet.facilities.append(facility)
```

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Method compiles without import errors
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
