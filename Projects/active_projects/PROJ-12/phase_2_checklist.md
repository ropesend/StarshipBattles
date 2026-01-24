# Phase 2: AI & Spatial Queries

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-12 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce redundant spatial queries in AI system
**Priority:** MAJOR

---

## Tasks

### Task 2.1: PERF-03 - Consolidate AI Spatial Queries [Medium]
**File:** `game/ai/controller.py:63,76,105,119,293`
**Tests:** `pytest tests/unit/ai/test_controller.py`

**Issue:** Each AI controller queries spatial grid 3-5 times per update:
- `find_target()` - Line 63
- `find_target()` - Line 76 (duplicate!)
- `find_secondary_targets()` - Line 105
- `find_secondary_targets()` - Line 119 (duplicate!)
- `check_avoidance()` - Line 293

With 60 ships = 180-300 queries per frame.

**Implementation:**
- [ ] Create single query at start of AI update with largest radius
- [ ] Cache results in AIController instance
- [ ] Filter cached results for specific needs
- [ ] Clear cache at end of update cycle
- [ ] Benchmark with 60+ ships

**Expected Improvement:** 40-50% reduction in spatial query overhead

---

### Task 2.2: Optimize Spatial Query Radius [Medium]
**File:** `game/engine/spatial.py:23-35`
**Tests:** `pytest tests/unit/engine/test_spatial.py`

**Issue:** Query uses square pattern (iterates cells in square grid), not circular. Returns 10-20% false positive candidates.

**Implementation:**
- [ ] Add distance filter after cell query
- [ ] Pre-allocate candidates list with estimated size
- [ ] Consider circular query pattern if performance-critical
- [ ] Benchmark query accuracy vs performance tradeoff

**Expected Improvement:** 5-8% reduction in false positive filtering

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] AI queries consolidated (max 1-2 per controller per frame)
- [ ] Profile shows AI < 10% of frame time
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
