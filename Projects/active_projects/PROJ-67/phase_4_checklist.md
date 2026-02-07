# PROJ-67 Phase 4: BuildContext Abstraction & UI Generalization

**Objective:** Create BuildContext protocol, refactor BuildQueueScreen/Controller to work with both planets and fleets.

## Completion Criteria
- [ ] All tasks below checked off
- [ ] `pytest tests/unit/strategy/ -k build_context` passes
- [ ] `pytest tests/integration/ui/build_queue_screen/` passes
- [ ] `pytest tests/ --testmon` passes (no regressions)

---

## Task 4.1: Create BuildContext Protocol [Simple]
**File:** `game/strategy/data/build_context.py` (new file)
**Tests:** `pytest tests/unit/strategy/ -k build_context`

- [ ] Create `BuildContext` Protocol class with properties: `name`, `construction_queue`, `has_space_shipyard`, `owner_id`
- [ ] Add `can_build_type(vehicle_type: str) -> bool` method
- [ ] Add `context_type` property returning `"planet"` or `"fleet"` (for UI branching)
- [ ] Write test: Planet satisfies BuildContext protocol
- [ ] Write test: Fleet satisfies BuildContext protocol

**Notes:**

---

## Task 4.2: Add BuildContext Compliance to Planet [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/ -k planet`

- [ ] Add `can_build_type()` method to Planet (complexes always, ships only if has_space_shipyard)
- [ ] Add `context_type` property returning `"planet"`
- [ ] Write test: planet.can_build_type("complex") always True
- [ ] Write test: planet.can_build_type("ship") requires has_space_shipyard

**Notes:**

---

## Task 4.3: Generalize BuildQueueController [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue` and `pytest tests/integration/ui/build_queue_screen/`

- [ ] Change `self.planet` to `self.build_context` (or use Union type)
- [ ] Update `__init__` parameter: `planet: Planet` → `build_context` (accepts Planet or Fleet)
- [ ] Update `add_to_queue()`: use `self.build_context.can_build_type()` instead of hardcoded `has_space_shipyard` check (line 129)
- [ ] Update diagnostic logging to use `self.build_context.name` instead of `self.planet` specifics
- [ ] For fleet context: skip facility-specific logging (lines 119-126)
- [ ] Write test: controller works with Planet build context
- [ ] Write test: controller works with Fleet build context
- [ ] Write test: controller blocks complex for fleet not at planet

**Notes:**

---

## Task 4.4: Generalize BuildQueueScreen [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`

- [ ] Change constructor: `planet: Planet` → `build_context` (accept Planet or Fleet)
- [ ] Store `self.build_context` instead of `self.planet`
- [ ] Update `_create_planet_report_panel()`: conditionally show planet report OR fleet info panel
- [ ] For fleet context: create a simple fleet info header instead of PlanetReportPanel
- [ ] Update `_refresh_queue_display()`: use `self.build_context.construction_queue`
- [ ] Update `handle_event()`: reference `self.build_context` instead of `self.planet`
- [ ] Pass `self.build_context` to controller and drag handler
- [ ] Update category filtering: hide "Complexes" category when fleet is not at planet
- [ ] Write test: screen initializes with Planet context (existing behavior preserved)
- [ ] Write test: screen initializes with Fleet context

**Notes:**

---

## Task 4.5: Update BuildQueueDragHandler [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`

- [ ] Update method signatures that accept `planet` parameter to accept build_context
- [ ] `handle_mouse_down()`, `handle_mouse_motion()`, `handle_mouse_up()` - update planet refs
- [ ] Write test: drag handler works with fleet context

**Notes:**
