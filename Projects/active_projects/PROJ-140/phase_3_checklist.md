# Phase 3: Fix UI Designation Filtering (Bug 3)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** `handle_colonize_designation()` should filter candidate planets by available colony pods, matching the pattern in `on_colonize_click()`.

---

## Tasks

### Task 3.1: Write Tests for Designation Pod Filtering [Simple]
**File:** `tests/integration/ui/test_colonization_facade.py` (ADD to existing file)
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py -v`

Add new test class `TestHandleColonizeDesignationPodFiltering`:
- [x] Test: `test_designation_filters_by_pod_type` — Fleet with only CONTINENTAL pod. Target system has ICE_DWARF planet at target hex. Assert returns `no_targets` type (planet filtered out)
- [x] Test: `test_designation_matching_pod_succeeds` — Fleet with ICE_DWARF pod. Target system has ICE_DWARF planet at target hex. Assert returns success or prompt (not filtered out)
- [x] Test: `test_designation_no_pods_returns_no_targets` — Fleet with no colony pods at all. Assert returns `no_targets` type
- [x] Test: `test_designation_mixed_types_filters_correctly` — Fleet with CONTINENTAL pod. Target has [ICE_DWARF, CONTINENTAL] planets. Assert only CONTINENTAL planet remains after filtering
- [x] Verify: New tests fail initially (TDD)

**Notes:** These tests need to mock: scene (with camera, systems, hex_size, galaxy), facade (get_fleet_remaining_pods, handle_command). Follow pattern from existing `TestOnColonizeClickPodFiltering` class (line 432).

### Task 3.2: Add Pod Filtering to `handle_colonize_designation()` [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py -v`

Modify `handle_colonize_designation()` (lines 156-194). After building the `candidates` list (line 179-180):
- [x] Add pod filtering using `self.facade.get_fleet_remaining_pods(fleet.id)` (same pattern as `on_colonize_click()` lines 96-123)
- [x] If no remaining pods: return `{'type': 'no_targets', 'message': 'No colony pods in fleet', 'remaining_pods': remaining_pods}`
- [x] Filter `candidates` by `p.planet_type.name in remaining_pods`
- [x] If no candidates match: return `{'type': 'no_targets', 'message': f'No colonizable planets for available pods ({pod_types})', 'remaining_pods': remaining_pods}`
- [x] Use `pod_filtered` list instead of `candidates` for the `len == 1` / prompt logic
- [x] Verify: All new tests pass
- [x] Verify: `pytest tests/integration/ui/test_colonization_facade.py -v` — all existing tests pass (26 passed)
- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py -v` — input handler tests pass (42 passed)

**Notes:** Implementation adds ~25 lines to handle_colonize_designation() matching pattern from on_colonize_click()

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
