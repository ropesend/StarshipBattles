# Phase 8: Research System Polish

**Status:** Complete
**Estimated Effort:** 2-3 hours
**Priority:** Low-Medium

## Overview
Address issues in `game/research/` - mostly minor type hints, validation, and UI improvements.

> **Note:** This phase was reduced from 8 tasks to 7 after Category 3 audit verification:
> - Task 8.4 (NEW-RES-004) REMOVED - Proper fallback exists at lines 144-145

---

## Tasks

### 8.1 Add Missing Type Hints (NEW-RES-001, NEW-RES-010)
**Location:** `game/research/ui/research_renderer.py:199-200`
**Effort:** Simple

- [x] Add type hints: `_draw_node_text(self, node: TechNode, state: NodeState) -> None`
- [x] Add imports for type annotations if needed
- [x] Run mypy if available (210 research tests pass)

**Notes:** Added TYPE_CHECKING imports for TechNode and NodeState, added type hints to `_draw_node_text` method.

---

### 8.2 Fix Font Cache Unbounded Growth (NEW-RES-002)
**Location:** `game/research/ui/research_renderer.py:59-63`
**Effort:** Simple

- [x] Use `functools.lru_cache` with fixed size (e.g., maxsize=50)
- [x] Or quantize font sizes to discrete steps (nearest 2)
- [ ] Add cache clearing on zoom level change (not needed with quantization)
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Implemented font size quantization to nearest 2 pixels. Added 2 new tests for cache bounds. All 212 research tests pass.

---

### 8.3 Fix State Reference Inconsistency (NEW-RES-003)
**Location:** `game/research/ui/research_controls.py:273-276`
**Effort:** Simple

- [x] Review `_selected_node` vs `selected_node_id` usage
- [x] Use consistent reference source throughout (`_selected_node.id`)
- [x] Add assertion to validate state synchronization (tests added)
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Changed allocation slider handler to use `self._selected_node.id` instead of the external `selected_node_id` parameter. Added 2 new tests for state reference consistency. All 214 research tests pass.

---

### ~~8.4 Add Validation for Unknown price_curve (NEW-RES-004)~~
**Status:** REMOVED - ALREADY COMPLETE
**Reason:** Proper fallback exists at lines 144-145 in tech_node.py.

---

### 8.4 Add Cycle Detection Call (NEW-RES-005)
**Location:** `game/research/ui/research_scene.py:68-71`
**Effort:** Simple

- [x] Add `tree.detect_cycles()` call during validation
- [x] Handle cycle detection result appropriately
- [x] Log error if cycles found
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Added `detect_cycles()` call after `validate_requirements()`. Cycles are logged similar to validation errors. Added 2 new tests. All 216 research tests pass.

---

### 8.6 Document RP Allocation Validation (NEW-RES-006)
**Location:** `game/research/data/research_tracker.py:109-130`
**Effort:** Simple

- [x] Document return value semantics in docstring
- [x] Add warning log when value is clamped
- [x] Consider raising for explicitly invalid input (negative) - decided to clamp with warning instead
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Enhanced docstring with clear return value semantics. Added warning logs for both negative input and budget limit clamping. All 216 research tests pass.

---

### 8.7 Add Negated Requirement Visibility (NEW-RES-007)
**Location:** `game/research/data/tech_node.py:21, 48-50`
**Effort:** Medium

- [x] Add visual indicator for negated requirements in renderer
- [x] Use different line style/color for "NOT" dependencies (red dashed lines)
- [ ] Update detail panel to show negated requirements (deferred - requires UI panel changes)
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Added COLOR_LINE_NEGATED and COLOR_LINE_NEGATED_MET colors. Modified _draw_dependency_lines to iterate requirements directly and check negate flag. Added _draw_dashed_line helper for visual distinction. Negated requirements now appear as red dashed lines. All 216 research tests pass.

---

### 8.8 Document Fragile State Assumption (NEW-RES-009)
**Location:** `game/research/ui/research_controls.py:368`
**Effort:** Simple

- [x] Add explicit invariant check or assertion (documented why not needed)
- [x] Or add defensive `get()` call (used local variable for clarity)
- [x] Document assumption in code comment
- [x] Run: `pytest tests/unit/research/ -v`

**Notes:** Added docstring documenting the state assumption and why get_state() is safe. Refactored to use local variable for clarity. All 216 research tests pass.

---

## Verification

- [x] Run research tests: `pytest tests/unit/research/ -v` (216 passed)
- [ ] Manual test: open research screen, verify no errors
- [ ] Test with various tech tree configurations

---

## Notes
- All tasks in this phase are relatively simple
- Most are documentation or minor code improvements
- Task 8.7 (negate visibility) is the most complex
