# Phase 4: Planet Orders Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create PlanetActionEngine, PlanetActionTimeResolver, command handlers, and validators for tick-based planet order execution. This is the reusable framework for all future planet actions.

---

## Tasks

### Task 4.1: Create PlanetActionTimeResolver [Simple]
**File:** `game/strategy/services/planet_action_time_resolver.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/services/test_planet_action_time_resolver.py -v`

Follow `game/strategy/services/action_time_resolver.py` as template:

- [ ] Create new file
- [ ] Define mapping: `PLANET_ORDER_TO_ABILITY_MAP`:
  ```python
  PLANET_ORDER_TO_ABILITY_MAP = {
      PlanetOrderType.ACTIVATE_SHIELD: 'PlanetaryShield',
      PlanetOrderType.DEACTIVATE_SHIELD: 'PlanetaryShield',
  }
  ```
- [ ] Define mapping: `PLANET_ORDER_TO_TIME_FIELD`:
  ```python
  PLANET_ORDER_TO_TIME_FIELD = {
      PlanetOrderType.ACTIVATE_SHIELD: 'activation_time',
      PlanetOrderType.DEACTIVATE_SHIELD: 'deactivation_time',
  }
  ```
- [ ] Create `PlanetActionTimeResolver`:
  ```python
  @staticmethod
  def resolve_action_time(planet, order, component_registry=None) -> int:
      """Resolve action_time from the target facility's component ability data."""
      # 1. Get ability_name from PLANET_ORDER_TO_ABILITY_MAP
      # 2. Get time_field from PLANET_ORDER_TO_TIME_FIELD
      # 3. Find target facility by order.target['facility_instance_id']
      # 4. Scan facility design_data for ability_name
      # 5. Extract time_field value from ability data
      # 6. Return value or default (1)
  ```
- [ ] Write tests in `tests/unit/strategy/services/test_planet_action_time_resolver.py` (NEW)

**Notes:**

---

### Task 4.2: Create PlanetActionEngine [Complex]
**File:** `game/strategy/engine/planet_action_engine.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/engine/test_planet_action_engine.py -v`

Follow `game/strategy/engine/action_execution_engine.py` as template:

- [ ] Create new file
- [ ] Create `IPlanetActionEngine` interface (add to `interfaces/engines.py`):
  ```python
  class IPlanetActionEngine(ABC):
      @abstractmethod
      def process_planet_actions_tick(self, tick: int, empires: List,
                                      component_registry=None) -> List: ...
  ```
- [ ] Add `'IPlanetActionEngine'` to `__all__` in `interfaces/engines.py`
- [ ] Create `PlanetActionEngine(IPlanetActionEngine)`:
  ```python
  def __init__(self, *, registries: Optional[GameRegistries] = None,
               action_time_resolver: Optional[PlanetActionTimeResolver] = None): ...
  ```
- [ ] Implement `process_planet_actions_tick()`:
  - For each empire → each colony with `planet_orders`:
    1. Get current order: `planet.get_current_planet_order()`
    2. Increment: `order.execution_progress += 1` (planets act every tick — no speed)
    3. Resolve: `action_time = resolver.resolve_action_time(planet, order, registry)`
    4. If `order.execution_progress >= action_time`: execute order, pop it
    5. Return list of results
- [ ] Implement order execution handlers:
  - `_execute_activate_shield(planet, order)`: find target facility by `order.target['facility_instance_id']`, call `facility.set_component_active(component_id, True)`, set `planet.shield_active = True`, log event
  - `_execute_deactivate_shield(planet, order)`: find target facility, call `facility.set_component_active(component_id, False)`, set `planet.shield_active = False`, log event
- [ ] Guard execution: if target facility no longer exists (destroyed), skip order and pop it

**Notes:** Unlike fleet actions, planets act every tick (no speed-based interval).

---

### Task 4.3: Create Planet Order Validator [Medium]
**File:** `game/strategy/validation/planet_order_validator.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/validation/test_planet_order_validator.py -v`

- [ ] Create new file
- [ ] Create `PlanetOrderValidator` class:
  ```python
  @staticmethod
  def validate_activate_shield(planet, facility_instance_id, component_registry) -> ValidationResult:
      # Check: facility exists on planet
      # Check: facility is operational
      # Check: facility has PlanetaryShield ability
      # Check: shield is not already active
      # Check: no conflicting ACTIVATE_SHIELD order already queued

  @staticmethod
  def validate_deactivate_shield(planet, facility_instance_id, component_registry) -> ValidationResult:
      # Check: facility exists on planet
      # Check: shield is currently active (or activating)
  ```
- [ ] Write tests

**Notes:**

---

### Task 4.4: Create Planet Command Handlers [Medium]
**File:** `game/strategy/engine/planet_command_handlers.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/engine/test_planet_command_handlers.py -v`

Follow `game/strategy/engine/superweapon_command_handlers.py` as template:

- [ ] Create new file
- [ ] Create `IssuePlanetOrderCommandHandler(BaseCommandHandler)`:
  ```python
  def execute(self, session, cmd) -> ValidationResult:
      # 1. Resolve planet via _resolve_planet(session, cmd.planet_id)
      # 2. Validate ownership (planet.owner_id == session.player_empire.id)
      # 3. Find facility by cmd.facility_instance_id
      # 4. Validate via PlanetOrderValidator
      # 5. Create PlanetOrder and add to planet.planet_orders
  ```
- [ ] Create `ClearPlanetOrdersCommandHandler(BaseCommandHandler)`
- [ ] Create `DeletePlanetOrderCommandHandler(BaseCommandHandler)`

**Notes:**

---

### Task 4.5: Create Planet Command Dataclasses [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `python -m pytest tests/unit/strategy/engine/test_commands.py -v`

- [ ] Add new section after Construction Queue Commands (~line 359):
  ```python
  # =============================================================================
  # Planet Order Commands (PROJ-237)
  # =============================================================================

  @dataclass
  class IssuePlanetOrderCommand(Command):
      """Command to issue an order to a planet (e.g., activate/deactivate shield)."""
      planet_id: int
      order_type: str  # PlanetOrderType name (e.g., "ACTIVATE_SHIELD")
      facility_instance_id: str
      component_id: Optional[str] = None

  @dataclass
  class ClearPlanetOrdersCommand(Command):
      """Command to clear all orders from a planet."""
      planet_id: int

  @dataclass
  class DeletePlanetOrderCommand(Command):
      """Command to remove a specific order from a planet's order queue."""
      planet_id: int
      order_index: int
  ```

**Notes:**

---

### Task 4.6: Register Command Handlers [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `python -m pytest tests/unit/strategy/ -v`

- [ ] In `create_default_registry()`, add imports and registrations:
  ```python
  from game.strategy.engine.planet_command_handlers import (
      IssuePlanetOrderCommandHandler,
      ClearPlanetOrdersCommandHandler,
      DeletePlanetOrderCommandHandler,
  )
  registry.register('IssuePlanetOrderCommand', IssuePlanetOrderCommandHandler())
  registry.register('ClearPlanetOrdersCommand', ClearPlanetOrdersCommandHandler())
  registry.register('DeletePlanetOrderCommand', DeletePlanetOrderCommandHandler())
  ```

**Notes:**

---

### Task 4.7: Write Planet Action Engine Tests [Complex]
**File:** `tests/unit/strategy/engine/test_planet_action_engine.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/engine/test_planet_action_engine.py -v`

- [ ] Test: order queued → execution_progress increments each tick
- [ ] Test: execution_progress reaches action_time → order executed and popped
- [ ] Test: ACTIVATE_SHIELD order completes → `planet.shield_active = True`, facility component active
- [ ] Test: DEACTIVATE_SHIELD order completes → `planet.shield_active = False`, facility component inactive
- [ ] Test: target facility destroyed before order completes → order skipped and popped
- [ ] Test: empty order queue → no action taken
- [ ] Test: multi-turn order (action_time > 100) → progress persists, completes next turn
- [ ] Test: multiple orders in queue → processed FIFO
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] PlanetActionTimeResolver resolves action_time from ability JSON
- [ ] PlanetActionEngine processes orders with tick-based progress
- [ ] Command handlers validate and queue planet orders
- [ ] Command dataclasses created and handlers registered
- [ ] All tests pass
- [ ] `python -m pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
