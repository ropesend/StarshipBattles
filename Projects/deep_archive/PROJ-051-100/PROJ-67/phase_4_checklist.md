# PROJ-67 Phase 4: BuildContext Abstraction & UI Generalization

**Objective:** Create BuildContext protocol, refactor BuildQueueScreen/Controller to work with both planets and fleets.

## Completion Criteria
- [x] All tasks below checked off
- [x] `pytest tests/unit/strategy/ -k build_context` passes
- [x] `pytest tests/integration/ui/build_queue_screen/` passes
- [x] `pytest tests/ --testmon` passes (no regressions)

---

## Task 4.1: Create BuildContext Protocol [Simple]
**File:** `game/strategy/data/build_context.py` (new file)
**Tests:** `pytest tests/unit/strategy/ -k build_context`

- [x] Create `BuildContext` Protocol class with properties: `name`, `construction_queue`, `has_space_shipyard`, `owner_id`
- [x] Add `can_build_type(vehicle_type: str) -> bool` method
- [x] Add `context_type` property returning `"planet"` or `"fleet"` (for UI branching)
- [x] Write test: Planet satisfies BuildContext protocol
- [x] Write test: Fleet satisfies BuildContext protocol

**Notes:** Created as runtime_checkable Protocol. 7 tests pass.

---

## Task 4.2: Add BuildContext Compliance to Planet [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/ -k planet`

- [x] Add `can_build_type()` method to Planet (complexes always, ships only if has_space_shipyard)
- [x] Add `context_type` property returning `"planet"`
- [x] Write test: planet.can_build_type("complex") always True
- [x] Write test: planet.can_build_type("ship") requires has_space_shipyard

**Notes:** Also added name and context_type properties to Fleet. 18 tests pass.

---

## Task 4.3: Generalize BuildQueueController [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue` and `pytest tests/integration/ui/build_queue_screen/`

- [x] Change `self.planet` to `self.build_context` (or use Union type)
- [x] Update `__init__` parameter: `planet: Planet` → `build_context` (accepts Planet or Fleet)
- [x] Update `add_to_queue()`: use `self.build_context.can_build_type()` instead of hardcoded `has_space_shipyard` check (line 129)
- [x] Update diagnostic logging to use `self.build_context.name` instead of `self.planet` specifics
- [x] For fleet context: skip facility-specific logging (lines 119-126)
- [x] Write test: controller works with Planet build context
- [x] Write test: controller works with Fleet build context
- [x] Write test: controller blocks complex for fleet not at planet

**Notes:** All existing tests pass with the generalized controller.

---

## Task 4.4: Generalize BuildQueueScreen [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`

- [x] Change constructor: `planet: Planet` → `build_context` (accept Planet or Fleet)
- [x] Store `self.build_context` instead of `self.planet`
- [x] Update `_create_planet_report_panel()`: conditionally show planet report OR fleet info panel
- [x] For fleet context: create a simple fleet info header instead of PlanetReportPanel
- [x] Update `_refresh_queue_display()`: use `self.build_context.construction_queue`
- [x] Update `handle_event()`: reference `self.build_context` instead of `self.planet`
- [x] Pass `self.build_context` to controller and drag handler
- [x] Update category filtering: hide "Complexes" category when fleet is not at planet
- [x] Write test: screen initializes with Planet context (existing behavior preserved)
- [x] Write test: screen initializes with Fleet context

**Notes:** Maintained backward compatibility by keeping `self.planet` as alias for `self.build_context`. 15 tests pass.

---

## Task 4.5: Update BuildQueueDragHandler [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`

- [x] Update method signatures that accept `planet` parameter to accept build_context
- [x] `handle_mouse_down()`, `handle_mouse_motion()`, `handle_mouse_up()` - update planet refs
- [x] Write test: drag handler works with fleet context

**Notes:** All handler methods now use build_context parameter. Existing tests pass.
