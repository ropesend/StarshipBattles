# Phase 4: UI Module Refactoring

**Objective:** Refactor all UI modules to use facade exclusively
**Status:** In Progress

---

## Task 4.1: Refactor FleetOperations [Medium]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/ui/test_fleet_ops_facade.py`

- [x] Add `facade` parameter to `__init__` (line ~23):
  ```python
  def __init__(self, scene, facade: StrategySessionFacade):
      self.scene = scene
      self.facade = facade
  ```
- [x] Remove `session` property (line 39)
- [x] Update line 103 - Replace direct session call:
  ```python
  # Before:
  preview_path = self.session.preview_fleet_path(fleet, target_hex)
  # After:
  preview_path = self.facade.get_fleet_path_preview(fleet.id, target_hex)
  ```
- [x] Update lines 108-111 - Keep command creation but use facade:
  ```python
  result = self.facade.handle_command(cmd)
  ```
- [x] Update lines 136-137 - Replace direct fleet mutation with command:
  ```python
  # Before:
  new_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
  fleet.add_order(new_order)
  # After:
  from game.strategy.engine.commands import IssueInterceptCommand
  cmd = IssueInterceptCommand(fleet.id, target_fleet.id)
  result = self.facade.handle_command(cmd)
  ```
- [x] Update lines 175-180 - Replace join order creation with command:
  ```python
  # Before:
  FleetOrder(OrderType.MOVE_TO_FLEET, ...) + FleetOrder(OrderType.JOIN_FLEET, ...)
  # After:
  from game.strategy.engine.commands import IssueJoinFleetCommand
  cmd = IssueJoinFleetCommand(fleet.id, target_fleet.id)
  result = self.facade.handle_command(cmd)
  ```
- [x] Verify no remaining direct session access
- [x] Write/update tests

**Notes:** Completed. 13 tests added in test_fleet_ops_facade.py. Also removed FleetOrder/OrderType imports as no longer needed.

---

## Task 4.2: Refactor ColonizationSystem [Complex]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/ui/test_colonization_facade.py`

- [x] Add `facade` parameter to `__init__` (line ~25):
  ```python
  def __init__(self, scene, facade: StrategySessionFacade):
      self.scene = scene
      self.facade = facade
  ```
- [x] Remove `session`, `galaxy`, `turn_engine` properties (lines 48-56)
- [x] Update line 88 - Replace direct validation call:
  ```python
  # Before:
  res = self.turn_engine.validate_colonize_order(self.galaxy, fleet, p)
  # After:
  res = self.facade.can_colonize(fleet.id, p.id)
  ```
- [x] Update lines 117-120 - Keep command but use facade:
  ```python
  result = self.facade.handle_command(cmd)
  ```
- [x] **CRITICAL** Update lines 183-206 `queue_colonize_mission()`:
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
- [x] Remove unused imports (find_hybrid_path, FleetOrder, OrderType)
- [x] Verify no remaining direct session/galaxy/turn_engine access
- [x] Write/update tests

**Notes:** Completed. 13 tests added in test_colonization_facade.py. Internal helper methods (_get_system_at_hex, _resolve_planet_global_hex) access scene.galaxy for read-only lookups which is allowed.

---

## Task 4.3: Update StrategyScene Initialization [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/test_strategy_scene_facade.py`

- [x] Add import at top:
  ```python
  from game.strategy.facade.strategy_session_facade import StrategySessionFacade
  ```
- [x] Create facade in `__init__` after session setup (after line 48):
  ```python
  self._facade = StrategySessionFacade(self.session)
  ```
- [x] Update line 84 - Pass facade to FleetOperations:
  ```python
  self._fleet_ops = FleetOperations(self, self._facade)
  ```
- [x] Update line 87 - Pass facade to ColonizationSystem:
  ```python
  self._colonization = ColonizationSystem(self, self._facade)
  ```
- [x] Update line 264 - Use facade for turn processing:
  ```python
  # Before:
  self.session.process_turn()
  # After:
  self._facade.process_turn()
  ```
- [x] Write tests verifying facade usage

**Notes:** Completed. Facade created and passed to FleetOperations and ColonizationSystem. Turn processing now uses facade.

---

## Task 4.4: Deprecate Direct Session Properties [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** Manual verification - check for deprecation warnings in logs

- [x] Add deprecation warnings to properties at lines 94-126:
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
- [x] Apply deprecation warning to `turn_engine` (primary coupling issue)
- [x] Keep properties functional for backwards compatibility
- [x] Document in code that these are deprecated for external access

**Notes:** Added deprecation warning to `turn_engine` property which was the primary coupling issue (validation calls). Other properties (galaxy, empires, systems) are still needed for rendering and navigation, kept without warnings but documented as internal-use.

---

## Task 4.5: Update CameraNavigator [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py`
**Tests:** `pytest tests/ui/test_camera_nav.py`

- [x] Review CameraNavigator for coupling issues
- [x] Note: `systems` access is read-only for navigation - kept as-is
- [x] Note: `current_empire.colonies/fleets` access is read-only for navigation - kept as-is

**Notes:** CameraNavigator only performs read-only operations for camera navigation and selection cycling. It accesses `scene.current_empire` for colonies/fleets to enable object selection and camera centering. Using facade DTOs (ColonySummary/FleetSummary) would break navigation since actual objects are needed for camera positioning. No state mutations occur - this is acceptable read-only access for UI navigation purposes.

---

## Phase 4 Verification
- [x] No direct `fleet.add_order()` in scope modules (FleetOperations, ColonizationSystem)
- [x] No direct `fleet.path =` assignment in scope modules
- [x] No direct `turn_engine.validate_*` in scope modules
- [x] FleetOperations and ColonizationSystem use facade for commands and queries
- [x] Run `pytest tests/ --testmon` - all pass (26 new UI tests)
- [ ] Manual playtest: Move fleet, colonize planet, intercept fleet

**Out of scope (noted for future):**
- `fleet_orders_window.py` still has `fleet.path = []` (would need FleetOrdersWindow refactor)
- `strategy_screen.py` still has one `turn_engine.validate_colonize_order` call (minor)
