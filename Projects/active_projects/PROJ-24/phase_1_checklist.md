# Phase 1: Add Missing Interface Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extend IControllable with methods needed for full migration

---

## Tasks

### Task 1.1: Add new abstract methods to IControllable [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [ ] Add `get_turn_speed() -> float` abstract method (after line 63, in Position section)
- [ ] Add `get_acceleration_rate() -> float` abstract method
- [ ] Add `get_is_thrusting() -> bool` abstract method
- [ ] Add `set_rotation(angle: float) -> None` abstract method (Movement Controls section, after line 92)
- [ ] Add `set_in_formation(value: bool) -> None` abstract method (Formation section, after line 159)
- [ ] Add `set_formation_master(master: Optional[Any]) -> None` abstract method
- [ ] Add `get_secondary_targets() -> List[Any]` abstract method (Combat section, after line 135)
- [ ] Add `set_secondary_targets(targets: List[Any]) -> None` abstract method
- [ ] Add `get_components_by_ability(name: str, operational_only: bool = True) -> List[Any]` abstract method
- [ ] Add `adjust_position(delta: Vector2) -> None` abstract method (Movement Controls section)
- [ ] Add `get_layers() -> Dict[str, Any]` abstract method (for component inspection)

**Notes:**

---

### Task 1.2: Implement new methods in ShipControllableAdapter [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [ ] Implement `get_turn_speed()` - returns `self._ship.turn_speed`
- [ ] Implement `get_acceleration_rate()` - returns `self._ship.acceleration_rate`
- [ ] Implement `get_is_thrusting()` - returns `self._ship.is_thrusting`
- [ ] Implement `set_rotation(angle)` - sets `self._ship.angle = angle`
- [ ] Implement `set_in_formation(value)` - sets `self._ship.in_formation = value`
- [ ] Implement `set_formation_master(master)` - sets `self._ship.formation_master = master`
- [ ] Implement `get_secondary_targets()` - returns `self._ship.secondary_targets or []`
- [ ] Implement `set_secondary_targets(targets)` - sets `self._ship.secondary_targets = targets`
- [ ] Implement `get_components_by_ability(name, operational_only)` - returns `self._ship.get_components_by_ability(name, operational_only)`
- [ ] Implement `adjust_position(delta)` - applies `self._ship.position += delta`
- [ ] Implement `get_layers()` - returns `self._ship.layers`

**Notes:**

---

### Task 1.3: Add tests for new interface methods [Simple]
**File:** `tests/unit/ai/test_controllable_interface.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [ ] Add test `test_icontrollable_has_get_turn_speed_method`
- [ ] Add test `test_icontrollable_has_get_acceleration_rate_method`
- [ ] Add test `test_icontrollable_has_get_is_thrusting_method`
- [ ] Add test `test_icontrollable_has_set_rotation_method`
- [ ] Add test `test_icontrollable_has_set_in_formation_method`
- [ ] Add test `test_icontrollable_has_set_formation_master_method`
- [ ] Add test `test_icontrollable_has_get_secondary_targets_method`
- [ ] Add test `test_icontrollable_has_set_secondary_targets_method`
- [ ] Add test `test_icontrollable_has_get_components_by_ability_method`
- [ ] Add test `test_icontrollable_has_adjust_position_method`
- [ ] Add test `test_icontrollable_has_get_layers_method`
- [ ] Add adapter implementation tests for each new method

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ai/test_controllable_interface.py -v` - all pass
- [ ] Run `pytest tests/unit/ai/ -v` - all AI tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
