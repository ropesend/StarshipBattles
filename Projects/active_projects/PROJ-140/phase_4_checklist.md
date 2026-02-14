# Phase 4: Fix Mission Command Handler Validation (Bug 4)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** `ColonizeMissionCommandHandler` should validate pod match before queuing MOVE + COLONIZE orders.

---

## Tasks

### Task 4.1: Write Tests for Mission Handler Pod Validation [Simple]
**File:** `tests/unit/strategy/engine/test_colonize_mission_handler.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py -v`

Create test file with mock session, turn_engine, and fleet objects:
- [ ] Test: `test_mission_rejects_wrong_pod_type` — Fleet with CONTINENTAL pod, queuing mission to ICE_DWARF planet. Assert `result.is_valid is False`, `error_code == "NO_COLONY_POD"`
- [ ] Test: `test_mission_accepts_matching_pod` — Fleet with ICE_DWARF pod, queuing mission to ICE_DWARF planet. Assert `result.is_valid is True`
- [ ] Test: `test_mission_rejects_exhausted_pods` — Fleet with 1 ICE_DWARF pod, already has queued COLONIZE order for ICE_DWARF. Assert `result.is_valid is False`, `error_code == "COLONY_POD_EXHAUSTED"`
- [ ] Test: `test_mission_with_none_planet_skips_pod_check` — Fleet with any pod, planet_id=None ("any planet"). Assert `result.is_valid is True`
- [ ] Test: `test_mission_no_pods_fails` — Fleet with zero colony pods, specific planet target. Assert `result.is_valid is False`
- [ ] Verify: New tests fail initially (TDD)

**Notes:** Need to mock `session` with `_get_fleet_by_id()`, `_get_planet_by_id()`, `turn_engine._registries.components`, `galaxy` for pathfinding. Follow patterns from `tests/integration/gameplay_loop/test_commands_colonization.py`.

### Task 4.2: Add Pod Validation to `ColonizeMissionCommandHandler` [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py -v`

Modify `ColonizeMissionCommandHandler.execute()` (after planet resolution, ~line 246):
- [ ] When `planet is not None` (specific target planet):
  - Get component_registry: `component_registry = getattr(getattr(session, 'turn_engine', None), '_registries', None)` → if not None: `getattr(component_registry, 'components', None)`
  - Call `ColonizeValidator.find_ship_with_colony_pod(fleet, planet.planet_type.name, component_registry)`
  - If no match: return `ValidationResult(is_valid=False, errors=[f"No ship in fleet has {planet.planet_type.name} colony pod."], error_code="NO_COLONY_POD")`
  - Check chain limits: `get_available_colony_pods()` vs `get_committed_colony_pods()`
  - If exhausted: return `ValidationResult(is_valid=False, errors=[f"All {planet.planet_type.name} colony pods already assigned."], error_code="COLONY_POD_EXHAUSTED")`
- [ ] Add import: `from game.strategy.validation import ColonizeValidator`
- [ ] When `planet is None` (any planet): skip pod check (can't validate without knowing target)
- [ ] Verify: All new tests pass
- [ ] Verify: `pytest tests/integration/gameplay_loop/test_commands_colonization.py -v` — existing tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
