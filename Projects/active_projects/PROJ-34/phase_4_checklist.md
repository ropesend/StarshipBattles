# Phase 4: UI Module Refactoring

**Objective:** Refactor all UI modules to use facade exclusively
**Status:** Not Started

---

## Task 4.1: Refactor FleetOperations [Medium]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/ui/test_fleet_ops_facade.py`

- [ ] Add `facade` parameter to `__init__` (line ~23):
  ```python
  def __init__(self, scene, facade: StrategySessionFacade):
      self.scene = scene
      self.facade = facade
  ```
- [ ] Remove `session` property (line 39)
- [ ] Update line 103 - Replace direct session call:
  ```python
  # Before:
  preview_path = self.session.preview_fleet_path(fleet, target_hex)
  # After:
  preview_path = self.facade.get_fleet_path_preview(fleet.id, target_hex)
  ```
- [ ] Update lines 108-111 - Keep command creation but use facade:
  ```python
  result = self.facade.handle_command(cmd)
  ```
- [ ] Update lines 136-137 - Replace direct fleet mutation with command:
  ```python
  # Before:
  new_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
  fleet.add_order(new_order)
  # After:
  from game.strategy.engine.commands import IssueInterceptCommand
  cmd = IssueInterceptCommand(fleet.id, target_fleet.id)
  result = self.facade.handle_command(cmd)
  ```
- [ ] Update lines 175-180 - Replace join order creation with command:
  ```python
  # Before:
  FleetOrder(OrderType.MOVE_TO_FLEET, ...) + FleetOrder(OrderType.JOIN_FLEET, ...)
  # After:
  from game.strategy.engine.commands import IssueJoinFleetCommand
  cmd = IssueJoinFleetCommand(fleet.id, target_fleet.id)
  result = self.facade.handle_command(cmd)
  ```
- [ ] Verify no remaining direct session access
- [ ] Write/update tests

**Notes:**

---

## Task 4.2: Refactor ColonizationSystem [Complex]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/ui/test_colonization_facade.py`

- [ ] Add `facade` parameter to `__init__` (line ~25):
  ```python
  def __init__(self, scene, facade: StrategySessionFacade):
      self.scene = scene
      self.facade = facade
  ```
- [ ] Remove `session`, `galaxy`, `turn_engine` properties (lines 48-56)
- [ ] Update line 88 - Replace direct validation call:
  ```python
  # Before:
  res = self.turn_engine.validate_colonize_order(self.galaxy, fleet, p)
  # After:
  res = self.facade.can_colonize(fleet.id, p.id)
  ```
- [ ] Update lines 117-120 - Keep command but use facade:
  ```python
  result = self.facade.handle_command(cmd)
  ```
- [ ] **CRITICAL** Update lines 183-206 `queue_colonize_mission()`:
  ```python
  # Before (entire method does path calculation + direct mutation):
  def queue_colonize_mission(self, target_hex, planet, fleet):
      start_hex = ...
      path = find_hybrid_path(...)
      move = FleetOrder(...)
      fleet.add_order(move)
      fleet.path = path
      col = FleetOrder(...)
      fleet.add_order(col)

  # After (delegate to command):
  def queue_colonize_mission(self, target_hex, planet, fleet):
      from game.strategy.engine.commands import QueueColonizeMissionCommand
      cmd = QueueColonizeMissionCommand(fleet.id, target_hex, planet.id)
      result = self.facade.handle_command(cmd)
      if not result.is_valid:
          log_warning(f"Colonize mission failed: {result.message}")
      return result
  ```
- [ ] Remove unused imports (find_hybrid_path, FleetOrder, OrderType)
- [ ] Verify no remaining direct session/galaxy/turn_engine access
- [ ] Write/update tests

**Notes:**

---

## Task 4.3: Update StrategyScene Initialization [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/test_strategy_scene_facade.py`

- [ ] Add import at top:
  ```python
  from game.strategy.facade.strategy_session_facade import StrategySessionFacade
  ```
- [ ] Create facade in `__init__` after session setup (after line 48):
  ```python
  self._facade = StrategySessionFacade(self.session)
  ```
- [ ] Update line 84 - Pass facade to FleetOperations:
  ```python
  self._fleet_ops = FleetOperations(self, self._facade)
  ```
- [ ] Update line 87 - Pass facade to ColonizationSystem:
  ```python
  self._colonization = ColonizationSystem(self, self._facade)
  ```
- [ ] Update line 264 - Use facade for turn processing:
  ```python
  # Before:
  self.session.process_turn()
  # After:
  self._facade.process_turn()
  ```
- [ ] Write tests verifying facade usage

**Notes:**

---

## Task 4.4: Deprecate Direct Session Properties [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** Manual verification - check for deprecation warnings in logs

- [ ] Add deprecation warnings to properties at lines 94-126:
  ```python
  @property
  def galaxy(self):
      import warnings
      warnings.warn(
          "Direct galaxy access deprecated, use facade queries",
          DeprecationWarning,
          stacklevel=2
      )
      return self.session.galaxy
  ```
- [ ] Apply to all 9 properties: galaxy, empires, systems, turn_engine, player_empire, enemy_empire, human_player_ids, current_empire
- [ ] Keep properties functional for backwards compatibility
- [ ] Document in CHANGELOG that these will be removed

**Notes:**

---

## Task 4.5: Update CameraNavigator [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py`
**Tests:** `pytest tests/ui/test_camera_nav.py`

- [ ] Add `facade` parameter to `__init__`
- [ ] Update line 170 - Replace direct empire access:
  ```python
  # Before:
  colonies = self.scene.current_empire.colonies
  # After:
  empire_id = self.scene.human_player_ids[self.scene.current_player_index]
  colonies = self.facade.get_empire_colonies(empire_id)
  ```
- [ ] Note: `systems` access may need similar update or can be left as-is if only read

**Notes:**

---

## Phase 4 Verification
- [ ] No direct `fleet.add_order()` in any UI module
- [ ] No direct `fleet.path =` assignment in any UI module
- [ ] No direct `turn_engine.validate_*` in any UI module
- [ ] All modules use facade for commands and queries
- [ ] Run `pytest tests/ --testmon` - all pass
- [ ] Manual playtest: Move fleet, colonize planet, intercept fleet
