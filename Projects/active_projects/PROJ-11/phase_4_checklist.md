# Phase 4: Simulation Module Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-11 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up simulation module internals for better extensibility
**Priority:** MAJOR

---

## Tasks

### Task 4.1: MOD-SIM-01 - Unify Ability Systems [Medium]
**File:** `game/simulation/components/component.py:50,61,64`
**Tests:** `pytest tests/unit/simulation/test_component.py`

**Issue:** Components maintain parallel ability systems:
- `abilities` dict (raw JSON data)
- `ability_instances` list (instantiated Ability objects)

This creates confusion about source of truth.

**Implementation:**
- [ ] Audit all code that reads from `abilities` dict
- [ ] Migrate all reads to use `ability_instances`
- [ ] Deprecate `abilities` dict with warning
- [ ] Remove `abilities` dict after verification
- [ ] Update AbilityAggregator to use only ability_instances

**Notes:** This affects how stats are calculated. Test thoroughly.

---

### Task 4.2: MOD-SIM-02 - Extract Stat Calculation Phases [High]
**File:** `game/simulation/entities/ship_stats.py:15-372`
**Tests:** `pytest tests/unit/simulation/test_ship_stats.py`

**Issue:** Single 250+ line method with 7 phases. Interdependencies make extension difficult.

**Implementation:**
- [ ] Extract Phase 1: `_calculate_mass_and_hp()`
- [ ] Extract Phase 2: `_gather_resources()`
- [ ] Extract Phase 3: `_allocate_crew()`
- [ ] Extract Phase 4: `_aggregate_stats()` (the big one)
- [ ] Extract Phase 5: `_calculate_physics()`
- [ ] Extract Phase 6: `_calculate_to_hit()`
- [ ] Extract Phase 7: `_calculate_endurance()`
- [ ] Create clear phase ordering mechanism
- [ ] Document phase dependencies

**Notes:** Extract one phase at a time. Run tests after each extraction.

---

### Task 4.3: MOD-SIM-07 - Fix Modifier Dependency Resolution [Medium]
**File:** `game/simulation/components/modifier_effects.py:109-150`
**Tests:** `pytest tests/unit/simulation/test_modifier_effects.py`

**Issue:** Modifier effects can reference other stats, but there's no dependency ordering. If effect A depends on B, and B is evaluated second, formula fails.

**Implementation:**
- [ ] Add dependency tracking to modifier schema
- [ ] Implement topological sort for effect evaluation order
- [ ] Validate DAG (no cycles) at load time
- [ ] Add tests for dependency ordering
- [ ] Document modifier dependency system

**Notes:** This is a data-driven solution. Modifiers declare dependencies in JSON.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Single ability system (ability_instances only)
- [ ] Stat phases extracted and documented
- [ ] Modifier dependencies resolved correctly
- [ ] All simulation tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
