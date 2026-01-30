# Phase 8: BattleEngine-AIController Coupling Analysis

## Overview

This document analyzes how BattleEngine creates and uses AIController instances internally.
The goal is to decouple BattleEngine from direct AI layer imports to enable:
- Testing BattleEngine without AI layer
- Custom AI implementations
- Clear layer boundaries (simulation ↔ AI)

---

## BattleEngine AIController Creation Points

**File:** `game/simulation/systems/battle_engine.py`

### 1. Lines 72-73: TYPE_CHECKING Import
```python
if TYPE_CHECKING:
    from game.ai.controller import AIController
```
**Purpose:** Type hints only (acceptable)
**Action:** Keep as-is (TYPE_CHECKING is correct pattern)

---

### 2. Lines 226-241: Legacy Path in `start()` Method
```python
else:
    # Legacy path: create controllers internally (backward compatibility)
    from game.ai.controller import AIController
    from game.ai.interfaces import ShipControllableAdapter

    # Setup Team 1
    for s in team1_ships:
        s.team_id = 0
        self.ships.append(s)
        self.ai_controllers.append(AIController(ShipControllableAdapter(s), self.grid, 1))

    # Setup Team 2
    for s in team2_ships:
        s.team_id = 1
        self.ships.append(s)
        self.ai_controllers.append(AIController(ShipControllableAdapter(s), self.grid, 0))
```
**Purpose:** Backward compatibility when no ai_controllers provided
**Note:** PROJ-17 already added parameter to accept pre-created controllers
**Action:** Remove legacy path, require callers to provide controllers

---

### 3. Lines 284-289: Legacy Path in `add_ship_mid_battle()`
```python
else:
    # Legacy path: create controller internally
    from game.ai.controller import AIController
    from game.ai.interfaces import ShipControllableAdapter
    enemy_team = 1 if team_id == 0 else 0
    ai = AIController(ShipControllableAdapter(ship), self.grid, enemy_team)
    self.ai_controllers.append(ai)
```
**Purpose:** Backward compatibility when no ai_controller provided
**Note:** Already has parameter to accept pre-created controller
**Action:** Remove legacy path, require callers to provide controller

---

### 4. Lines 439-442: Fighter Launch in `update()` Method
```python
# Note: This is an internal operation during battle, uses legacy import path
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
enemy_team = 1 - new_ship.team_id
self.ai_controllers.append(AIController(ShipControllableAdapter(new_ship), self.grid, enemy_team))
```
**Purpose:** Create AI for dynamically spawned fighters
**Note:** This is a mid-battle operation triggered by Hangar abilities
**Action:** This is the trickiest case - need a factory or callback mechanism

---

## AIController Interface Analysis

From `game/ai/controller.py`, the AIController uses:

### Constructor
```python
def __init__(self, ship, grid, enemy_team_id):
```
- `ship`: IControllable (ShipControllableAdapter wrapping Ship)
- `grid`: SpatialGrid for spatial queries
- `enemy_team_id`: int for enemy team identification

### Public Method Called by BattleEngine
```python
def update(self) -> None:
```
Only `update()` is called externally by BattleEngine (line 365).

### Other Public Methods
- `find_target()` - not called by BattleEngine
- `check_avoidance()` - not called by BattleEngine
- `navigate_to()` - not called by BattleEngine

---

## Proposed IAIController Protocol

Based on the analysis, the protocol needs minimal methods:

```python
from typing import Protocol, Any

class IAIController(Protocol):
    """Protocol for AI controllers used by BattleEngine."""

    @property
    def ship(self) -> Any:
        """Access to the controlled ship/adapter for identification."""
        ...

    def update(self) -> None:
        """Execute one AI update cycle."""
        ...
```

Note: The `ship` property is needed because BattleEngine's `remove_ship()` iterates over
`ai_controllers` and compares `ai.ship.ship` to find the matching controller.

---

## Factory Pattern for Fighter Launches

For fighter launches, the BattleEngine needs a way to create AI controllers without
importing from game.ai directly. Options:

### Option A: AI Factory Injection (Recommended)
```python
class BattleEngine:
    def __init__(self, ai_factory: Optional[AIControllerFactory] = None):
        self.ai_factory = ai_factory
```
Pro: Clean DI, testable
Con: Another constructor parameter

### Option B: Callback Function
```python
def start(self, ..., ai_creator: Callable[[Ship, SpatialGrid, int], IAIController] = None):
```
Pro: Flexible
Con: Less explicit typing

### Option C: Event-Based
```python
# BattleEngine emits event, orchestrator creates AI
self.on_fighter_launched(new_ship, enemy_team)
```
Pro: Loose coupling
Con: Complex implementation

**Recommendation:** Option A - AIControllerFactory injected at BattleEngine creation

---

## Impact Assessment

### Files to Modify
1. `game/simulation/systems/battle_engine.py` - Remove internal AI creation
2. `game/simulation/services/battle_service.py` - May need factory
3. `game/strategy/adapters/simulation_adapter.py` - Uses BattleEngine

### Files to Create
1. `game/simulation/interfaces/ai_controller.py` - IAIController protocol
2. `game/simulation/factories/ai_factory.py` - AIControllerFactory
3. `tests/unit/simulation/mocks/mock_ai_controller.py` - Test mock

### Test Files to Update
- Tests that create BattleEngine directly will need to provide AI controllers

---

## Summary Table

| Location | Current Behavior | Proposed Change |
|----------|-----------------|-----------------|
| TYPE_CHECKING import | Type hints | Keep as-is |
| start() legacy path | Creates AIController | Remove, require injection |
| add_ship_mid_battle() legacy | Creates AIController | Remove, require injection |
| update() fighter launch | Creates AIController | Use injected factory |
| remove_ship() | Accesses ai.ship.ship | Keep, protocol needs `ship` property |

---

## Risks and Mitigations

1. **Breaking Tests**: Many tests may create BattleEngine without providing AI
   - Mitigation: Create MockAIController, update test fixtures

2. **Fighter Launch Complexity**: Mid-battle AI creation is complex
   - Mitigation: AIControllerFactory pattern with grid access

3. **Backward Compatibility**: Existing code expects internal creation
   - Mitigation: Update all callers, deprecation period not needed (internal API)
