# Phase 3: Component & Stats Optimization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-12 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce overhead in component creation and stat calculation
**Priority:** MAJOR

---

## Tasks

### Task 3.1: PERF-05 - Reduce Deep Copy on Component Creation [Medium]
**File:** `game/simulation/components/component.py:20`
**Tests:** `pytest tests/unit/simulation/test_component.py`

**Issue:** Every component creation does `copy.deepcopy(data)` - full recursive copy of JSON definition including nested abilities, modifiers, formulas.

**Implementation:**
- [ ] Analyze which fields actually need copying (mutable state)
- [ ] Store reference to shared definition data (immutable parts)
- [ ] Only copy mutable fields (current values, state)
- [ ] Consider copy-on-write pattern for modifiers
- [ ] Benchmark ship creation (30 components)

**Expected Improvement:** 15-25% faster component creation

---

### Task 3.2: PERF-06/PERF-14 - Cache Ability Lookups [Medium]
**File:** `game/simulation/entities/ship.py:217-236`
**Tests:** `pytest tests/unit/simulation/test_ship.py`

**Issue:** `max_weapon_range` and similar properties recalculate every call by iterating all components and abilities. Called 60+ times/second in AI behaviors.

**Implementation:**
- [ ] Cache result during `recalculate_stats()`
- [ ] Store in instance variable
- [ ] Invalidate only on component add/remove
- [ ] Apply same pattern to:
  - `max_weapon_range`
  - `get_total_sensor_score()`
  - `get_total_ecm_score()`
  - Other frequently-accessed ability totals

**Expected Improvement:** 10-15% reduction in behavior calculation time

---

### Task 3.3: PERF-10 - Build Ability Index [Medium]
**File:** `game/simulation/entities/ship.py:640-663`
**Tests:** `pytest tests/unit/simulation/test_ship.py`

**Issue:** `get_components_by_ability()` iterates all layers and components every call.

**Implementation:**
- [ ] Build ability index during `recalculate_stats()`: `{ability_name: [components]}`
- [ ] Use index for lookups instead of iteration
- [ ] Invalidate index on component add/remove
- [ ] Use set membership for existence checks

**Expected Improvement:** 20-25% reduction in component lookup overhead

---

### Task 3.4: PERF-04 - Single-Pass Component Iteration [High]
**File:** `game/simulation/entities/ship_stats.py:30-260`
**Tests:** `pytest tests/unit/simulation/test_ship_stats.py`

**Issue:** `calculate()` iterates components 5+ times for different phases.

**Implementation:**
- [ ] Redesign to single-pass iteration
- [ ] Collect all ability data in one loop
- [ ] Build aggregation dictionary during iteration
- [ ] Apply phase calculations to aggregated data
- [ ] Benchmark with 60-component ships

**Expected Improvement:** 35-45% reduction in stat recalculation time

**Notes:** This may conflict with PROJ-11 Phase 4 (stat phase extraction). Coordinate.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Component creation < 1ms per component
- [ ] Stat calculation < 5ms per ship
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
