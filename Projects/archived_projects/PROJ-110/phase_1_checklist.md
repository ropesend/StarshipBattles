# Phase 1: Foundation Layer - CRITICAL + MAJOR

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for all Foundation layer CRITICAL and MAJOR coverage gaps (TCG-FND-001 through TCG-FND-010). Expected: ~100 new tests.

**Progress:** All 10 tasks complete. +173 new tests total.

---

## Tasks

### Task 1.1: Hex Math Unit Tests (TCG-FND-001) [Medium] - COMPLETE
**File:** `tests/unit/core/test_hex_math_core.py` (NEW)
**Source:** `game/core/hex_math.py` (250 LOC, 8 public functions + HexCoord class)
**Existing:** Integration tests only at `tests/integration/strategy/test_hex_math_strategy.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`
**Result:** 43 tests added

---

### Task 1.2: AI Behaviors Unit Tests (TCG-FND-002) [Complex] - COMPLETE
**File:** `tests/unit/ai/test_behavior_units.py` (NEW)
**Source:** `game/ai/behaviors.py` (514 LOC, 13 behavior classes)
**Tests:** `pytest tests/unit/ai/test_behavior_units.py`
**Result:** 41 tests added

---

### Task 1.3: Resource Loading Error Paths (TCG-FND-003) [Medium] - COMPLETE
**File:** `tests/unit/core/test_resource_loading.py` (NEW)
**Source:** `game/core/resources.py` (143 LOC)
**Tests:** `pytest tests/unit/core/test_resource_loading.py`
**Result:** 14 tests added

---

### Task 1.4: Input Mapper Coverage Gaps (TCG-FND-004) [Medium] - COMPLETE
**File:** `tests/unit/core/test_input_mapper.py` (EXPAND existing)
**Source:** `game/core/input_mapper.py` (379 LOC)
**Tests:** `pytest tests/unit/core/test_input_mapper.py`
**Result:** 17 new tests added

---

### Task 1.5: Paths Module Unit Tests (TCG-FND-005) [Medium] - COMPLETE
**File:** `tests/unit/core/test_paths_config.py` (NEW)
**Source:** `game/core/paths.py` (134 LOC)
**Tests:** `pytest tests/unit/core/test_paths_config.py`
**Result:** 18 tests added

---

### Task 1.6: Screenshot Manager Unit Tests (TCG-FND-006) [Medium] - COMPLETE
**File:** `tests/unit/core/test_screenshot_manager.py` (NEW)
**Source:** `game/core/screenshot_manager.py` (219 LOC)
**Tests:** `pytest tests/unit/core/test_screenshot_manager.py`
**Result:** 11 tests added

---

### Task 1.7: AI Controller Coverage Expansion (TCG-FND-007) [Medium] - COMPLETE
**File:** `tests/unit/ai/test_ai_controller_unit.py` (NEW)
**Source:** `game/ai/controller.py` (480 LOC)
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`
**Result:** 14 tests added

---

### Task 1.8: Strategy Manager Error Paths (TCG-FND-008) [Medium] - COMPLETE
**File:** `tests/unit/ai/test_strategy_manager_singleton.py` (EXPAND existing)
**Source:** `game/ai/strategy_manager.py` (159 LOC)
**Tests:** `pytest tests/unit/ai/test_strategy_manager_singleton.py`
**Result:** 17 total tests (16 existing + 1 new explicit test for clear() flag reset)

**Coverage verification:** All 7 checklist items already covered by existing tests:
- `test_get_strategy_returns_default_for_unknown_id` covers missing ID default
- `test_get_targeting_policy_returns_default_for_unknown_id` covers targeting default
- `test_get_movement_policy_returns_default_for_unknown_id` covers movement default
- `test_resolve_strategy_combines_policies` covers assembles all parts
- `test_clear_resets_loaded_flag` (NEW) covers clear flag reset
- `test_ensure_loaded_triggers_once` covers only loads once
- `test_load_data_with_missing_files_uses_defaults` covers missing files

---

### Task 1.9: Target Evaluator Edge Cases (TCG-FND-009) [Medium] - COMPLETE
**File:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (NEW)
**Source:** `game/ai/target_evaluator.py` (500+ LOC)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_edge_cases.py`
**Result:** 15 tests added

Tests implemented:
- Zero weight rule handling (2 tests)
- Required flag rejection (3 tests)
- Empty rules returns zero (1 test)
- Distance cache usage (2 tests)
- Capabilities cache usage (1 test)
- Missile PDC arc rules (3 tests)
- Multiple rules accumulation (2 tests)
- Default stat helpers (1 test)

---

### Task 1.10: Research Service Edge Cases (TCG-FND-010) [Medium] - COMPLETE
**File:** `tests/unit/research/test_research_service.py` (existing comprehensive coverage)
**Source:** `game/research/systems/research_service.py` (231 LOC)
**Tests:** `pytest tests/unit/research/test_research_service.py`
**Result:** 0 new tests needed - all 9 checklist items already covered by existing tests

**Coverage verification:**
- `test_decay_on_locked_nodes` covers locked node decay
- `test_chance_capped_at_max` covers 95% cap
- `test_no_allocations` covers zero allocation decay
- `test_breakthrough_resets_chance` covers chance reset
- `test_breakthrough_updates_tech_levels_for_same_turn` covers mid-turn updates
- `TestCalculateAddedChance.test_zero_rp` covers zero RP
- `TestCalculateAddedChance.test_positive_rp` covers positive RP formula
- `TestEstimateTurnsToBreakthrough.test_zero_rp` covers zero RP infinity
- `TestEstimateTurnsToBreakthrough.test_decay_exceeds_gain` covers net gain zero infinity

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] All new tests pass
- [x] Full test suite still passes: `pytest tests/ -n 12` (8411 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
