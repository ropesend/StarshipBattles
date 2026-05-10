# Phase 2: Data Model Changes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add energy/shield/order fields to Planet, component_states to PlanetaryFacility, create PlanetOrder types, update IPlanet protocol and PlanetInfo DTO.

---

## Tasks

### Task 2.1: Add Energy and Shield Fields to Planet [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `python -m pytest tests/unit/strategy/data/ tests/integration/save_load/ -v`

- [ ] Add new fields to `Planet` dataclass (after `radius_hexes: int = 0`, line 102):
  ```python
  # Energy system (PROJ-237)
  energy: float = 0.0              # Current energy level
  energy_capacity: float = 0.0     # Max (recalculated from batteries each tick)
  energy_generation: float = 0.0   # Rate (recalculated from generators each tick)

  # Shield state (PROJ-237)
  shield_active: bool = False      # Whether shield is currently active
  ```
- [ ] Add `planet_orders` field (after shield_active):
  ```python
  # Planet order queue (PROJ-237) - parallel to Fleet.orders
  planet_orders: List['PlanetOrder'] = field(default_factory=list)
  ```
  - Add TYPE_CHECKING import: `from game.strategy.data.planet_order_types import PlanetOrder`
- [ ] Add order management methods (after `can_build_type()` method, ~line 186):
  ```python
  def get_current_planet_order(self) -> Optional['PlanetOrder']:
      return self.planet_orders[0] if self.planet_orders else None

  def pop_planet_order(self) -> Optional['PlanetOrder']:
      return self.planet_orders.pop(0) if self.planet_orders else None

  def add_planet_order(self, order: 'PlanetOrder', index: Optional[int] = None) -> None:
      if index is not None:
          self.planet_orders.insert(index, order)
      else:
          self.planet_orders.append(order)

  def clear_planet_orders(self) -> None:
      self.planet_orders.clear()
  ```
- [ ] Update `to_dict()` method (~line 203) — add new fields to returned dict:
  ```python
  'energy': self.energy,
  'energy_capacity': self.energy_capacity,
  'energy_generation': self.energy_generation,
  'shield_active': self.shield_active,
  'planet_orders': [o.to_dict() for o in self.planet_orders],
  ```
  - Also update facility serialization to include `component_states`
- [ ] Update `from_dict()` method (~line 324) — add new fields with safe defaults:
  ```python
  energy=data.get('energy', 0.0),
  energy_capacity=data.get('energy_capacity', 0.0),
  energy_generation=data.get('energy_generation', 0.0),
  shield_active=data.get('shield_active', False),
  ```
  - Deserialize `planet_orders` from data with `data.get('planet_orders', [])`

**Notes:**

---

### Task 2.2: Add component_states to PlanetaryFacility [Simple]
**File:** `game/strategy/data/planetary_facility.py`
**Tests:** `python -m pytest tests/unit/strategy/data/ tests/integration/save_load/ -v`

- [ ] Add new field to `PlanetaryFacility` dataclass (after `resource_levels`, line 26):
  ```python
  component_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
  ```
- [ ] Add helper methods:
  ```python
  def is_component_active(self, component_id: str) -> bool:
      state = self.component_states.get(component_id, {})
      return state.get('active', False)

  def set_component_active(self, component_id: str, active: bool) -> None:
      if component_id not in self.component_states:
          self.component_states[component_id] = {}
      self.component_states[component_id]['active'] = active
  ```
- [ ] Update `from_dict()` (line 41) — add `component_states`:
  ```python
  component_states=data.get('component_states', {})
  ```
- [ ] Update Planet's `to_dict()` facility serialization to include `'component_states': f.component_states.copy()`

**Notes:**

---

### Task 2.3: Create PlanetOrder Types [Medium]
**File:** `game/strategy/data/planet_order_types.py` (NEW)
**Tests:** `python -m pytest tests/unit/strategy/data/test_planet_order_types.py -v`

Follow `game/strategy/data/order_types.py` as template:

- [ ] Create new file `game/strategy/data/planet_order_types.py`
- [ ] Define `PlanetOrderType` enum:
  ```python
  class PlanetOrderType(Enum):
      ACTIVATE_SHIELD = auto()
      DEACTIVATE_SHIELD = auto()
      # Future: LAUNCH_FIGHTERS, CONVERT_RESOURCES, TOGGLE_COMPONENT
  ```
- [ ] Define `PLANET_ACTION_ORDER_TYPES` frozenset
- [ ] Create `PlanetOrder` class:
  ```python
  class PlanetOrder:
      def __init__(self, order_type: PlanetOrderType, target: Any = None):
          self.type = order_type
          self.target = target  # dict with facility_instance_id, component_id
          self.execution_progress: int = 0

      def to_dict(self) -> Dict[str, Any]: ...

      @classmethod
      def from_dict(cls, data: dict) -> 'PlanetOrder': ...
  ```
- [ ] Write unit tests in `tests/unit/strategy/data/test_planet_order_types.py` (NEW):
  - Construction, repr, to_dict, from_dict round-trip

**Notes:**

---

### Task 2.4: Update IPlanet Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `python -m pytest tests/unit/core/ -v`

- [ ] Add new properties to `IPlanet` protocol (after `image_rotation`, ~line 252):
  ```python
  @property
  def energy(self) -> float:
      """Current stored energy level."""
      ...

  @property
  def energy_capacity(self) -> float:
      """Maximum energy storage capacity."""
      ...

  @property
  def shield_active(self) -> bool:
      """Whether planetary shield is currently active."""
      ...
  ```

**Notes:**

---

### Task 2.5: Update PlanetInfo DTO [Simple]
**File:** `game/strategy/facade/dto/planet_dto.py`
**Tests:** `python -m pytest tests/unit/strategy/facade/ -v`

- [ ] Add new fields to `PlanetInfo` (after `population_details`, line 42):
  ```python
  energy: float = 0.0
  energy_capacity: float = 0.0
  shield_active: bool = False
  ```
- [ ] Update `from_planet()` factory method (~line 60) to include:
  ```python
  energy=planet.energy,
  energy_capacity=planet.energy_capacity,
  shield_active=planet.shield_active,
  ```

**Notes:**

---

### Task 2.6: Write Data Model Tests [Medium]
**File:** Multiple test files
**Tests:** `python -m pytest tests/unit/strategy/data/ -v`

- [ ] Test Planet serialization round-trip with new fields (update existing tests)
- [ ] Test PlanetaryFacility with `component_states` round-trip
- [ ] Test Planet with `planet_orders` round-trip
- [ ] Test backward compatibility: load old save data without new fields → defaults applied
- [ ] Test `Planet.get_current_planet_order()`, `pop_planet_order()`, `add_planet_order()`
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Planet has energy/shield/orders fields with serialization
- [ ] PlanetaryFacility has component_states with serialization
- [ ] PlanetOrder dataclass created with serialization
- [ ] IPlanet protocol updated
- [ ] PlanetInfo DTO updated
- [ ] Backward compatibility verified (old saves load with defaults)
- [ ] `python -m pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
