# Phase 6: Generalize OrdersWindow UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename FleetOrdersWindow → OrdersWindow. Accept IOrderable entity instead of Fleet. Update StrategyWindowManager to support opening for planets. Rename file.

---

## Tasks

### Task 6.1: Generalize FleetOrdersWindow → OrdersWindow [Medium]
**File:** `game/ui/screens/fleet_orders_window.py` → `orders_window.py`
- [ ] Rename file via `git mv`
- [ ] Rename class `FleetOrdersWindow` → `OrdersWindow`
- [ ] Change constructor: accept `entity` (IOrderable) instead of `fleet` (Fleet)
  - Store `self.entity` instead of `self.fleet`
  - Use `self.entity.orders` instead of `self.fleet.orders`
  - Use generic `entity_id` instead of `fleet.id`
- [ ] Add `entity_type` parameter ("fleet" or "planet") for title/display
- [ ] Update `_get_order_description()` to handle planet order types (ACTIVATE_SHIELD, etc.)
- [ ] Update `rebuild_list()` to use `self.entity.orders`
- [ ] Update all internal references from fleet to entity

### Task 6.2: Update StrategyWindowManager [Medium]
**File:** `game/ui/screens/strategy_window_manager.py`
- [ ] Rename `fleet_orders_window` attribute → `orders_window`
- [ ] Rename `open_orders_window(fleet)` → `open_orders_window(entity, entity_type="fleet")`
- [ ] Update callback closures to use generic entity_id and entity_type:
  ```python
  def clear_orders_callback(entity_id, entity_type):
      if entity_type == "fleet":
          cmd = ClearOrdersCommand(fleet_id=entity_id)
      else:
          cmd = ClearPlanetOrdersCommand(planet_id=entity_id)
      self.scene.facade.handle_command(cmd)
  ```
- [ ] Support opening for planet entities (pass planet.id and "planet" type)

### Task 6.3: Update StrategyEventRouter [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
- [ ] Update `fleet_orders_window` references → `orders_window`
- [ ] Update modal detection list
- [ ] Update window close handler

### Task 6.4: Update Imports & References [Simple]
- [ ] Update all `from fleet_orders_window import FleetOrdersWindow` → `from orders_window import OrdersWindow`
- [ ] Update any references in tests

### Task 6.5: Verify [Simple]
- [ ] Fleet orders window still works (open with fleet selected, reorder, delete)
- [ ] `python -m pytest tests/ -n 12 -q` — same count as baseline

---

## Phase Completion Checklist
- [ ] OrdersWindow accepts any IOrderable entity
- [ ] File renamed to orders_window.py
- [ ] Fleet orders window functionality preserved
- [ ] All tests pass
