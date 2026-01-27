# Phase 1: Add Missing Interface Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extend IControllable with methods needed for full migration

---

## Tasks

### Task 1.1: Add new abstract methods to IControllable [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [x] Add `get_turn_speed() -> float` abstract method (after line 63, in Position section)
- [x] Add `get_acceleration_rate() -> float` abstract method
- [x] Add `get_is_thrusting() -> bool` abstract method
- [x] Add `set_rotation(angle: float) -> None` abstract method (Movement Controls section, after line 92)
- [x] Add `set_in_formation(value: bool) -> None` abstract method (Formation section, after line 159)
- [x] Add `set_formation_master(master: Optional[Any]) -> None` abstract method
- [x] Add `get_secondary_targets() -> List[Any]` abstract method (Combat section, after line 135)
- [x] Add `set_secondary_targets(targets: List[Any]) -> None` abstract method
- [x] Add `get_components_by_ability(name: str, operational_only: bool = True) -> List[Any]` abstract method
- [x] Add `adjust_position(delta: Vector2) -> None` abstract method (Movement Controls section)
- [x] Add `get_layers() -> Dict[str, Any]` abstract method (for component inspection)

**Notes:** All 11 abstract methods added to IControllable interface.

---

### Task 1.2: Implement new methods in ShipControllableAdapter [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [x] Implement `get_turn_speed()` - returns `self._ship.turn_speed`
- [x] Implement `get_acceleration_rate()` - returns `self._ship.acceleration_rate`
- [x] Implement `get_is_thrusting()` - returns `self._ship.is_thrusting`
- [x] Implement `set_rotation(angle)` - sets `self._ship.angle = angle`
- [x] Implement `set_in_formation(value)` - sets `self._ship.in_formation = value`
- [x] Implement `set_formation_master(master)` - sets `self._ship.formation_master = master`
- [x] Implement `get_secondary_targets()` - returns `self._ship.secondary_targets or []`
- [x] Implement `set_secondary_targets(targets)` - sets `self._ship.secondary_targets = targets`
- [x] Implement `get_components_by_ability(name, operational_only)` - returns `self._ship.get_components_by_ability(name, operational_only)`
- [x] Implement `adjust_position(delta)` - applies `self._ship.position += delta`
- [x] Implement `get_layers()` - returns `self._ship.layers`

**Notes:** All 11 adapter implementations complete.

---

### Task 1.3: Add tests for new interface methods [Simple]
**File:** `tests/unit/ai/test_controllable_interface.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [x] Add test `test_icontrollable_has_get_turn_speed_method`
- [x] Add test `test_icontrollable_has_get_acceleration_rate_method`
- [x] Add test `test_icontrollable_has_get_is_thrusting_method`
- [x] Add test `test_icontrollable_has_set_rotation_method`
- [x] Add test `test_icontrollable_has_set_in_formation_method`
- [x] Add test `test_icontrollable_has_set_formation_master_method`
- [x] Add test `test_icontrollable_has_get_secondary_targets_method`
- [x] Add test `test_icontrollable_has_set_secondary_targets_method`
- [x] Add test `test_icontrollable_has_get_components_by_ability_method`
- [x] Add test `test_icontrollable_has_adjust_position_method`
- [x] Add test `test_icontrollable_has_get_layers_method`
- [x] Add adapter implementation tests for each new method

**Notes:** Added TestIControllableNewMethods class with 15 tests for all new methods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ai/test_controllable_interface.py -v` - all pass (73 tests)
- [x] Run `pytest tests/unit/ai/ -v` - all AI tests pass (214 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
