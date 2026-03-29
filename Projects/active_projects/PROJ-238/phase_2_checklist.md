# Phase 2: Rename FleetOrder → Order & Unify Queue Interface

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rename FleetOrder class to Order. Merge PlanetOrder into Order. Rename Planet queue methods to match Fleet convention. Create IOrderable protocol. Update all 94+ import sites.

---

## Tasks

### Task 2.1: Rename FleetOrder → Order in order_types.py [Simple]
**File:** `game/strategy/data/order_types.py`
- [ ] Rename `class FleetOrder` → `class Order`
- [ ] Keep `FleetOrder = Order` alias temporarily for gradual migration
- [ ] Update docstring

### Task 2.2: Merge PlanetOrder into Order [Medium]
**File:** `game/strategy/data/order_types.py` and `game/strategy/data/planet_order_types.py`
- [ ] Verify Order class handles all PlanetOrder use cases (dict targets, execution_progress)
- [ ] Update Order.to_dict() to handle planet-style dict targets (already supported via raw fallback)
- [ ] Add Order.from_dict() classmethod (currently only FleetOrderSerializer handles this)
- [ ] Delete `PlanetOrderType` enum from `planet_order_types.py` (already done in Phase 1)
- [ ] Delete `PlanetOrder` class from `planet_order_types.py`
- [ ] Update all `PlanetOrder` references to `Order`
- [ ] Delete `planet_order_types.py` file (or leave as re-export alias)

### Task 2.3: Create IOrderable Protocol [Simple]
**File:** `game/core/protocols.py`
- [ ] Add `IOrderable` protocol:
  ```python
  @runtime_checkable
  class IOrderable(Protocol):
      @property
      def orders(self) -> List[Any]: ...
      def get_current_order(self) -> Optional[Any]: ...
      def add_order(self, order: Any, index: Optional[int] = None) -> None: ...
      def pop_order(self) -> Optional[Any]: ...
      def clear_orders(self) -> None: ...
  ```

### Task 2.4: Rename Planet Queue Methods [Medium]
**File:** `game/strategy/data/planet.py`
- [ ] Rename `planet_orders` → `orders`
- [ ] Rename `get_current_planet_order()` → `get_current_order()`
- [ ] Rename `pop_planet_order()` → `pop_order()`
- [ ] Rename `add_planet_order()` → `add_order()`
- [ ] Rename `clear_planet_orders()` → `clear_orders()`
- [ ] Update `to_dict()` key from `'planet_orders'` to `'orders'` (keep `'planet_orders'` fallback in `from_dict()`)
- [ ] Update `_deserialize_planet_orders()` to use Order class

### Task 2.5: Update All FleetOrder Import Sites [Complex]
**Files:** 94+ files (use `grep -r "FleetOrder" game/ tests/`)
- [ ] Batch 1: `game/strategy/data/` files (fleet.py, fleet_order_serializer.py, etc.)
- [ ] Batch 2: `game/strategy/engine/` files (command_handlers.py, superweapon_command_handlers.py, etc.)
- [ ] Batch 3: `game/strategy/validation/` and `game/strategy/services/` files
- [ ] Batch 4: `game/ui/` files (fleet_orders_window.py, etc.)
- [ ] Batch 5: Test files — mechanical rename across ~66 test files
- [ ] Run full test suite after each batch
- [ ] Remove FleetOrder alias once all references updated

### Task 2.6: Verify All Tests Pass [Simple]
- [ ] `python -m pytest tests/ -n 12 -q` — same count as baseline
- [ ] `grep -r "FleetOrder" game/ tests/` returns 0 results (or only alias)
- [ ] `grep -r "PlanetOrder" game/ tests/` returns 0 results (or only alias)

---

## Phase Completion Checklist
- [ ] FleetOrder renamed to Order everywhere
- [ ] PlanetOrder merged into Order, planet_order_types.py deleted or empty
- [ ] Planet.orders (not planet_orders), Planet.get_current_order() etc.
- [ ] IOrderable protocol created
- [ ] All tests pass
