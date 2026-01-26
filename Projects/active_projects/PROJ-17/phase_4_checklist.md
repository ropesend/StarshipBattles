# Phase 4: Create BattleOrchestrator [High Risk]

**Objective:** Move AI controller creation from BattleEngine (simulation) to a new BattleOrchestrator (UI layer), properly separating concerns.

**Status:** Not Started

**Depends on:** Phase 1 complete (AI layer must be clean)

**Tests to run after phase:** Full test suite `pytest tests/`

---

## Task 4.1: Create Orchestration Module [Simple]

**Directory:** `game/ui/orchestration/`

- [ ] Create directory: `mkdir game/ui/orchestration`
- [ ] Create `game/ui/orchestration/__init__.py`:

```python
"""Battle orchestration - coordinates simulation, AI, and UI layers."""
from .battle_orchestrator import BattleOrchestrator

__all__ = ['BattleOrchestrator']
```

**Notes:**

---

## Task 4.2: Create BattleOrchestrator Class [Complex]

**File:** `game/ui/orchestration/battle_orchestrator.py`

- [ ] Create new file with content:

```python
"""
BattleOrchestrator - UI-layer orchestration for battle setup.

This class handles AI controller creation, which requires importing from
the AI layer. By placing this in the UI layer instead of Simulation,
we maintain proper layer boundaries:
  - Simulation depends on Core only
  - UI coordinates between all layers
"""
from typing import List, Optional, TYPE_CHECKING

from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.engine.spatial import SpatialGrid

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class BattleOrchestrator:
    """
    Orchestrates battle setup in the UI layer.

    Responsibilities:
    - Creating AIController instances for ships
    - Wrapping ships with ShipControllableAdapter
    - Providing pre-configured AI list to BattleEngine
    """

    def __init__(self, grid: SpatialGrid):
        """
        Initialize the orchestrator.

        Args:
            grid: Spatial grid for AI target queries
        """
        self.grid = grid

    def create_ai_controllers(
        self,
        team0_ships: List['Ship'],
        team1_ships: List['Ship']
    ) -> List[AIController]:
        """
        Create AI controllers for all ships in a battle.

        Args:
            team0_ships: Ships for team 0
            team1_ships: Ships for team 1

        Returns:
            List of AIController instances ready to use
        """
        controllers = []

        # Team 0 ships target team 1
        for ship in team0_ships:
            adapter = ShipControllableAdapter(ship)
            controller = AIController(adapter, self.grid, enemy_team_id=1)
            controllers.append(controller)

        # Team 1 ships target team 0
        for ship in team1_ships:
            adapter = ShipControllableAdapter(ship)
            controller = AIController(adapter, self.grid, enemy_team_id=0)
            controllers.append(controller)

        return controllers

    def create_ai_for_ship(
        self,
        ship: 'Ship',
        enemy_team_id: int
    ) -> AIController:
        """
        Create a single AI controller for a ship (e.g., for reinforcements).

        Args:
            ship: Ship to control
            enemy_team_id: ID of the enemy team to target

        Returns:
            Configured AIController
        """
        adapter = ShipControllableAdapter(ship)
        return AIController(adapter, self.grid, enemy_team_id)
```

- [ ] Save file

**Notes:**

---

## Task 4.3: Modify BattleEngine.start() to Accept Pre-created Controllers [Complex]

**File:** `game/simulation/systems/battle_engine.py`

### Step 1: Update imports (lines 60-61)
- [ ] Remove from top of file:
  ```python
  from game.ai.controller import AIController
  from game.ai.interfaces import ShipControllableAdapter
  ```

### Step 2: Add TYPE_CHECKING import for AIController
- [ ] Add to TYPE_CHECKING block (create if needed):
  ```python
  if TYPE_CHECKING:
      from game.ai.controller import AIController
  ```

### Step 3: Update start() signature (lines 171-177)
- [ ] Add `ai_controllers` parameter:
  ```python
  def start(
      self,
      team1_ships: List['Ship'],
      team2_ships: List['Ship'],
      seed: Optional[int] = None,
      end_condition: Optional[BattleEndCondition] = None,
      ai_controllers: Optional[List['AIController']] = None  # NEW
  ) -> None:
  ```

### Step 4: Update start() body (after line 205)
- [ ] Replace the team setup loops with conditional logic:
  ```python
  if ai_controllers is not None:
      # Use pre-created controllers from BattleOrchestrator
      self.ai_controllers = list(ai_controllers)
      for s in team1_ships:
          s.team_id = 0
          self.ships.append(s)
      for s in team2_ships:
          s.team_id = 1
          self.ships.append(s)
  else:
      # Legacy path: create controllers internally (for backward compat)
      from game.ai.controller import AIController
      from game.ai.interfaces import ShipControllableAdapter
      for s in team1_ships:
          s.team_id = 0
          self.ships.append(s)
          self.ai_controllers.append(AIController(ShipControllableAdapter(s), self.grid, 1))
      for s in team2_ships:
          s.team_id = 1
          self.ships.append(s)
          self.ai_controllers.append(AIController(ShipControllableAdapter(s), self.grid, 0))
  ```

**Notes:**

---

## Task 4.4: Update add_ship_mid_battle() [Medium]

**File:** `game/simulation/systems/battle_engine.py` (lines ~237-254)

- [ ] Add optional `ai_controller` parameter:
  ```python
  def add_ship_mid_battle(
      self,
      ship: 'Ship',
      team_id: int,
      ai_controller: Optional['AIController'] = None  # NEW
  ) -> None:
  ```

- [ ] Update body to use provided controller or create one:
  ```python
  ship.team_id = team_id
  self.ships.append(ship)

  if ai_controller is not None:
      self.ai_controllers.append(ai_controller)
  else:
      # Legacy path
      from game.ai.controller import AIController
      from game.ai.interfaces import ShipControllableAdapter
      enemy_team = 1 if team_id == 0 else 0
      ai = AIController(ShipControllableAdapter(ship), self.grid, enemy_team)
      self.ai_controllers.append(ai)
  ```

**Notes:**

---

## Task 4.5: Update Primary Callers [Complex]

This task updates callers to optionally use BattleOrchestrator. The legacy path remains for backward compatibility.

### game/simulation/services/battle_service.py (if it calls engine.start())
- [ ] Check if this file calls engine.start() directly
- [ ] If yes, add optional `ai_controllers` parameter pass-through
- [ ] No changes needed if it doesn't directly call engine.start()

### game/strategy/adapters/simulation_adapter.py
- [ ] Check if SimulationBattleResolver creates BattleEngine
- [ ] If yes, consider adding BattleOrchestrator usage (optional for this phase)
- [ ] Document any changes needed for future

### game/ui/screens/battle_scene.py (primary UI caller)
- [ ] Check how battles are started
- [ ] This is the ideal place to use BattleOrchestrator
- [ ] Document any changes needed for future

**Note:** Full caller updates can be done incrementally. The legacy path ensures existing code continues to work.

**Notes:**

---

## Task 4.6: Create Unit Tests for BattleOrchestrator [Medium]

**File:** `tests/unit/ui/test_battle_orchestrator.py`

- [ ] Create test file with basic tests:

```python
"""Tests for BattleOrchestrator."""
import pytest
from unittest.mock import MagicMock, patch

from game.ui.orchestration import BattleOrchestrator
from game.engine.spatial import SpatialGrid


class TestBattleOrchestrator:
    """Test BattleOrchestrator functionality."""

    def test_create_ai_controllers_creates_correct_count(self):
        """Verify correct number of controllers created."""
        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        # Create mock ships
        team0 = [MagicMock() for _ in range(3)]
        team1 = [MagicMock() for _ in range(2)]

        controllers = orchestrator.create_ai_controllers(team0, team1)

        assert len(controllers) == 5

    def test_create_ai_for_ship(self):
        """Verify single ship AI creation."""
        grid = MagicMock(spec=SpatialGrid)
        orchestrator = BattleOrchestrator(grid)

        ship = MagicMock()
        controller = orchestrator.create_ai_for_ship(ship, enemy_team_id=1)

        assert controller is not None
```

- [ ] Run tests: `pytest tests/unit/ui/test_battle_orchestrator.py -v`

**Notes:**

---

## Phase 4 Verification

After completing all tasks:

- [ ] Run: `pytest tests/` (full suite)
- [ ] Run: `pytest simulation_tests/`
- [ ] Verify no top-level AI imports in BattleEngine:
  `grep -n "from game.ai" game/simulation/systems/battle_engine.py | head -5`
  (Should only show imports inside functions or TYPE_CHECKING)
- [ ] Launch game and play a battle manually
- [ ] Verify AI ships still move and attack correctly

**Phase complete when all boxes checked.**
