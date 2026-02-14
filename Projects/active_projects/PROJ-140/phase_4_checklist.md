# Phase 4: Fix Mission Command Handler Validation (Bug 4)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** `ColonizeMissionCommandHandler` should validate pod match before queuing MOVE + COLONIZE orders.

---

## Tasks

### Task 4.1: Write Tests for Mission Handler Pod Validation [Simple]
**File:** `tests/unit/strategy/engine/test_colonize_mission_handler.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py -v`

Create test file with mock session, turn_engine, and fleet objects:
- [x] Test: `test_mission_rejects_wrong_pod_type` — Fleet with CONTINENTAL pod, queuing mission to ICE_DWARF planet. Assert `result.is_valid is False`, `error_code == "NO_COLONY_POD"`
- [x] Test: `test_mission_accepts_matching_pod` — Fleet with ICE_DWARF pod, queuing mission to ICE_DWARF planet. Assert `result.is_valid is True`
- [x] Test: `test_mission_rejects_exhausted_pods` — Fleet with 1 ICE_DWARF pod, already has queued COLONIZE order for ICE_DWARF. Assert `result.is_valid is False`, `error_code == "COLONY_POD_EXHAUSTED"`
- [x] Test: `test_mission_with_none_planet_skips_pod_check` — Fleet with any pod, planet_id=None ("any planet"). Assert `result.is_valid is True`
- [x] Test: `test_mission_no_pods_fails` — Fleet with zero colony pods, specific planet target. Assert `result.is_valid is False`
- [x] Verify: New tests fail initially (TDD)

**Notes:** Created `tests/unit/strategy/engine/test_colonize_mission_handler.py` with 5 tests. All tests failed initially (TDD verified), then passed after implementation.

### Task 4.2: Add Pod Validation to `ColonizeMissionCommandHandler` [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py -v`

Modify `ColonizeMissionCommandHandler.execute()` (after planet resolution, ~line 246):
- [x] When `planet is not None` (specific target planet):
  - Get component_registry: `component_registry = getattr(getattr(session, 'turn_engine', None), '_registries', None)` → if not None: `getattr(component_registry, 'components', None)`
  - Call `ColonizeValidator.find_ship_with_colony_pod(fleet, planet.planet_type.name, component_registry)`
  - If no match: return `ValidationResult(is_valid=False, errors=[f"No ship in fleet has {planet.planet_type.name} colony pod."], error_code="NO_COLONY_POD")`
  - Check chain limits: `get_available_colony_pods()` vs `get_committed_colony_pods()`
  - If exhausted: return `ValidationResult(is_valid=False, errors=[f"All {planet.planet_type.name} colony pods already assigned."], error_code="COLONY_POD_EXHAUSTED")`
- [x] Add import: `from game.strategy.validation import ColonizeValidator`
- [x] When `planet is None` (any planet): skip pod check (can't validate without knowing target)
- [x] Verify: All new tests pass
- [x] Verify: `pytest tests/integration/gameplay_loop/test_commands_colonization.py -v` — existing tests pass

**Notes:** Also updated 3 integration tests (`test_command_handlers.py`) and 1 facade test (`test_facade_integration.py`) to include colony ships with matching pods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
