# Phase 8: Research System Polish

**Status:** Not Started
**Estimated Effort:** 2-3 hours
**Priority:** Low-Medium

## Overview
Address issues in `game/research/` - mostly minor type hints, validation, and UI improvements.

---

## Tasks

### 8.1 Add Missing Type Hints (NEW-RES-001, NEW-RES-010)
**Location:** `game/research/ui/research_renderer.py:199-200`
**Effort:** Simple

- [ ] Add type hints: `_draw_node_text(self, node: TechNode, state: NodeState) -> None`
- [ ] Add imports for type annotations if needed
- [ ] Run mypy if available

---

### 8.2 Fix Font Cache Unbounded Growth (NEW-RES-002)
**Location:** `game/research/ui/research_renderer.py:59-63`
**Effort:** Simple

- [ ] Use `functools.lru_cache` with fixed size (e.g., maxsize=50)
- [ ] Or quantize font sizes to discrete steps (nearest 0.5)
- [ ] Add cache clearing on zoom level change
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.3 Fix State Reference Inconsistency (NEW-RES-003)
**Location:** `game/research/ui/research_controls.py:273-276`
**Effort:** Simple

- [ ] Review `_selected_node` vs `selected_node_id` usage
- [ ] Use consistent reference source throughout
- [ ] Add assertion to validate state synchronization
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.4 Add Validation for Unknown price_curve (NEW-RES-004)
**Location:** `game/research/data/tech_node.py:127-145`
**Effort:** Simple

- [ ] Add validation during node creation
- [ ] Log warning for unknown curve types
- [ ] Raise error or use explicit fallback
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.5 Add Cycle Detection Call (NEW-RES-005)
**Location:** `game/research/ui/research_scene.py:68-71`
**Effort:** Simple

- [ ] Add `tree.detect_cycles()` call during validation
- [ ] Handle cycle detection result appropriately
- [ ] Log error if cycles found
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.6 Document RP Allocation Validation (NEW-RES-006)
**Location:** `game/research/data/research_tracker.py:109-130`
**Effort:** Simple

- [ ] Document return value semantics in docstring
- [ ] Add warning log when value is clamped
- [ ] Consider raising for explicitly invalid input (negative)
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.7 Add Negated Requirement Visibility (NEW-RES-007)
**Location:** `game/research/data/tech_node.py:21, 48-50`
**Effort:** Medium

- [ ] Add visual indicator for negated requirements in renderer
- [ ] Use different line style/color for "NOT" dependencies
- [ ] Update detail panel to show negated requirements
- [ ] Run: `pytest tests/unit/research/ -v`

---

### 8.8 Document Fragile State Assumption (NEW-RES-009)
**Location:** `game/research/ui/research_controls.py:368`
**Effort:** Simple

- [ ] Add explicit invariant check or assertion
- [ ] Or add defensive `get()` call
- [ ] Document assumption in code comment
- [ ] Run: `pytest tests/unit/research/ -v`

---

## Verification

- [ ] Run research tests: `pytest tests/unit/research/ -v`
- [ ] Manual test: open research screen, verify no errors
- [ ] Test with various tech tree configurations

---

## Notes
- All tasks in this phase are relatively simple
- Most are documentation or minor code improvements
- Task 8.7 (negate visibility) is the most complex
