# PROJ-234 Phase 3: Extract ShipInstanceBridge [Medium]

**Objective:** Move to_ship/update_from_ship/_capture_resource_levels to eager delegate class. ShipInstance keeps facade methods.
**Status:** Complete

---

#### Task 3.1: Create ShipInstanceBridge class [Medium]
**File:** `game/strategy/data/ship_instance_bridge.py` **(NEW)**
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`
- [ ] Create new file with delegate class. Constructor takes `ship_instance`, stores as `self._ship`.
- [ ] Move `_capture_resource_levels` (ship_instance.py lines 194-201) to `@staticmethod` on bridge
- [ ] Move `to_ship` logic (lines 537-575) to `ShipInstanceBridge.to_ship(position, team_id, *, registries)`:
  - Replace `self.X` with `self._ship.X` for all attribute access
  - Keep the `ShipSerializer` late import inside method body
  - Keep `logger.debug()` call
- [ ] Move `update_from_ship` logic (lines 583-610) to `ShipInstanceBridge.update_from_ship(ship)`:
  - Replace `self.X` with `self._ship.X` for all attribute access
  - Call `self._capture_resource_levels(ship)` for resource extraction
  - Call `self._ship.invalidate_stats_cache()` at end
  - Call `self._ship.battles_survived += 1` for counter increment
- [ ] Add runtime import: `from game.core.protocols import IPostBattleShip`
- [ ] Add TYPE_CHECKING imports for `ShipInstance`, `Ship`, `GameRegistries`
**Notes:**

#### Task 3.2: Wire bridge into ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -x`
- [ ] Add import: `from game.strategy.data.ship_instance_bridge import ShipInstanceBridge`
- [ ] Add field: `_bridge: Optional['ShipInstanceBridge'] = field(default=None, repr=False, init=False)`
- [ ] Add to `__post_init__`: `self._bridge = ShipInstanceBridge(self)`
- [ ] Delete `_capture_resource_levels` static method entirely (only called by bridge internally now)
- [ ] Replace `to_ship` body with: `return self._bridge.to_ship(position, team_id, registries=registries)`. Keep full signature and docstring.
- [ ] Replace `update_from_ship` body with: `self._bridge.update_from_ship(ship)`. Keep full signature and docstring.
- [ ] Remove the late import comment + `from game.simulation.entities.ship_serialization import ShipSerializer` from any remaining locations in ship_instance.py (moved to bridge)
- [ ] Run fleet adapter tests: `pytest tests/unit/strategy/fleet/ -x`
**Notes:**

#### Task 3.3: Write bridge unit tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` **(NEW)**
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_bridge.py -v`
- [ ] Test `_capture_resource_levels` extracts values from mock IPostBattleShip
- [ ] Test `to_ship` creates Ship with correct position and team_id (requires mock ShipSerializer or fresh_registries)
- [ ] Test `to_ship` applies HP damage when `current_hp` is set
- [ ] Test `to_ship` applies component damage from `component_damage` dict
- [ ] Test `to_ship` applies resource levels from `resource_levels` dict
- [ ] Test `update_from_ship` updates HP/alive/derelict state correctly (alive with damage, alive full health, dead)
- [ ] Test `update_from_ship` captures component damage
- [ ] Test `update_from_ship` increments `battles_survived`
- [ ] Test `update_from_ship` invalidates stats cache
**Notes:**

---

**Phase 3 Complete When:**
- [ ] All 3 tasks checked off
- [ ] `pytest tests/unit/strategy/ship_instance/ -x` passes (all existing + new tests)
- [ ] `pytest tests/unit/strategy/fleet/ -x` passes (fleet battle adapter)
- [ ] `pytest tests/unit/strategy/ -n 4` passes (broader strategy layer)
