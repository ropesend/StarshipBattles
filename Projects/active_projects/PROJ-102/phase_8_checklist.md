# Phase 8: UI Module - Superweapon Operations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the UI workflow module with targeting, confirmation dialogs, system picker, and ship picker.

---

## Tasks

### Task 8.1: Create SuperweaponOperations Module [Complex]
**New File:** `game/ui/screens/strategy_superweapons.py`
**Pattern:** Follow `game/ui/screens/strategy_colonization.py` (ColonizationSystem)
**Tests:** `pytest tests/unit/ui/test_superweapon_operations.py`

- [ ] Create `SuperweaponOperations` class:
  ```python
  class SuperweaponOperations:
      def __init__(self, scene, facade):
          self.scene = scene
          self.facade = facade
  ```

- [ ] `handle_implode_planet_designation(self, mx, my, fleet) -> dict`:
  - Convert screen coords to world coords -> hex via `pixel_to_hex()`
  - Find planet at hex (check `galaxy.get_planets_at_global_hex()`)
  - If multiple planets: show planet selection prompt (reuse existing pattern)
  - Validate fleet has DestroyPlanet ability
  - Show confirmation dialog: "Destroy {planet.name}? This action is irreversible. The Planet Imploder will be consumed."
  - On confirm: issue `QueueImplodePlanetMissionCommand(fleet.id, target_hex, planet.id)`
  - Return `{'type': 'success'}` or `{'type': 'error', 'message': ...}`

- [ ] `handle_stellerate_star_designation(self, mx, my, fleet) -> dict`:
  - Convert to hex, find star system
  - Show WARNING confirmation: "STELLERATE STAR: This will destroy {system.name}'s star, ALL planets, and ALL ships in the system - INCLUDING YOUR FLEET. This is irreversible. Proceed?"
  - On confirm: issue `QueueStellerateStarMissionCommand(fleet.id, target_hex)`

- [ ] `handle_open_warp_designation(self, mx, my, fleet) -> dict`:
  - Convert to hex (this is where near-end warp point will be placed)
  - Open system picker dialog to select target system
  - On system selected: issue `QueueOpenWarpPointMissionCommand(fleet.id, target_hex, selected_system_name)`

- [ ] `handle_close_warp_designation(self, mx, my, fleet) -> dict`:
  - Convert to hex, find warp point at hex
  - If no warp point: return error
  - Show confirmation: "Close warp link to {warp_point.destination_id}? Both ends will be destroyed."
  - On confirm: issue `QueueCloseWarpPointMissionCommand(fleet.id, target_hex, warp_point.destination_id)`

- [ ] `handle_dyson_sphere_designation(self, mx, my, fleet) -> dict`:
  - Convert to hex, find star system
  - Show confirmation: "Create Dyson Sphere at {system.name}? The star and all planets within 9 hexes will be consumed. A colonizable Dyson Sphere will be created."
  - On confirm: issue `QueueCreateDysonSphereMissionCommand(fleet.id, target_hex)`

- [ ] `handle_self_destruct(self, fleet)`:
  - Get ships with SelfDestruct ability from fleet (check design_data abilities)
  - If none: show error message
  - Open multi-select ship picker dialog with eligible ships
  - On confirm: issue `IssueSelfDestructCommand(fleet.id, selected_ship_ids)`

**Notes:**

### Task 8.2: Create System Picker Dialog [Medium]
**New File:** `game/ui/screens/strategy_system_picker.py`
**Tests:** `pytest tests/unit/ui/test_superweapon_operations.py`

- [ ] Create `SystemPickerDialog` class using `pygame_gui`:
  - Show list of all star systems in the galaxy
  - Filter out: current system, systems already linked via warp
  - Display system name and distance
  - Callback on selection: `on_system_selected(system_name: str)`
  - Cancel button returns to input mode
  - Use `pygame_gui.elements.UISelectionList` or `UIWindow` with list

**Notes:**

### Task 8.3: Create Ship Picker Dialog [Medium]
**New File:** `game/ui/screens/strategy_ship_picker.py`
**Tests:** `pytest tests/unit/ui/test_superweapon_operations.py`

- [ ] Create `ShipPickerDialog` class using `pygame_gui`:
  - Multi-select dialog showing ships from fleet
  - Only ships with specified ability are selectable
  - Show ship name, class, status
  - Select All / Deselect All buttons
  - Confirm button: callback with list of selected ship IDs
  - Cancel button: close dialog
  - Use `UIWindow` with checkboxes or `UISelectionList` with multi-select

**Notes:**

### Task 8.4: Add Confirmation Dialog Helper [Simple]
**File:** `game/ui/screens/strategy_superweapons.py` or utility
**Tests:** Manual verification

- [ ] Create helper method `_show_confirmation(title, message, on_confirm)`:
  - Use `pygame_gui.windows.UIConfirmationDialog` or `UIMessageWindow`
  - Center on screen
  - Call `on_confirm()` callback when user confirms
  - For Stellerate Star: use red/warning styling for the message text

**Notes:**

### Task 8.5: Wire Into Strategy Scene [Simple]
**File:** Strategy screen initialization (find where `_fleet_ops` and `_colonization` are created)
**Tests:** Manual verification

- [ ] Add `self._superweapons = SuperweaponOperations(self, facade)` in StrategyScreen init
- [ ] Ensure `strategy_input_handler.py` references `self.scene._superweapons` work correctly

**Notes:**

### Task 8.6: Add Generic Fleet Capability Methods [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/data/ --testmon`

- [ ] Add `has_ability(self, ability_name: str) -> bool`:
  - Iterate `self._fleet.get_combat_capable_ships()`
  - Check `ship.design_data["layers"]` -> components -> abilities for ability_name
  - Return True if any ship has it

- [ ] Add `ships_with_ability(self, ability_name: str) -> list`:
  - Same iteration but returns list of matching ShipInstance objects

- [ ] Add Fleet facade properties (optional, for UI convenience):
  ```python
  @property
  def has_destroy_planet(self) -> bool:
      return self._capabilities.has_ability("DestroyPlanet")
  ```

**Notes:**

### Task 8.7: Write Phase 8 Tests [Medium]
**New File:** `tests/unit/ui/test_superweapon_operations.py`
**Tests:** `pytest tests/unit/ui/test_superweapon_operations.py -v`

- [ ] Test `SuperweaponOperations` initializes with scene and facade
- [ ] Test designation handlers convert screen coords to hex correctly (mock camera)
- [ ] Test handle_self_destruct filters ships by SelfDestruct ability
- [ ] Test confirmation dialog is shown for destructive actions
- [ ] Test command creation has correct parameters
- [ ] Test `FleetCapabilityCalculator.has_ability()` returns True/False correctly
- [ ] Test `FleetCapabilityCalculator.ships_with_ability()` returns matching ships
- [ ] Verify: all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 9
