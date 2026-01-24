# Phase 1: Circular Dependencies

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-11 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate circular import workarounds and establish clean dependency graph
**Priority:** CRITICAL - Blocks safe refactoring

---

## Tasks

### Task 1.1: AR-03 - Map Current Circular Dependencies [Medium]
**Files:** Multiple (11+ files with late imports)
**Tests:** N/A (analysis task)

**Issue:** Scattered late imports to avoid circular dependencies. Import order is fragile. Files include:
- `game/simulation/ship_stats.py:19`
- `game/simulation/ship_validator.py:238`
- `game/simulation/ship_serialization.py:119`
- `game/simulation/components/component.py:76,198,242`
- And more...

**Implementation:**
- [ ] Create dependency graph of current imports
- [ ] Identify all files with TYPE_CHECKING or late imports
- [ ] Document the circular chains (A → B → C → A)
- [ ] Prioritize which cycles to break first

**Notes:** This is analysis - don't change code yet. Need full picture first.

---

### Task 1.2: MOD-SIM-03 - Break Simulation Circular Dependencies [High]
**Files:** `game/simulation/` module
**Tests:** All simulation tests must pass after changes

**Issue:** Ship ↔ Component ↔ Ability ↔ formula_system cycles cause fragile imports.

**Implementation:**
- [ ] Extract FormulaSafeEvaluator as independent module (no imports from simulation)
- [ ] Create ShipStatsContext parameter object to pass data without imports
- [ ] Use lazy property pattern for stats calculator initialization
- [ ] Replace late imports with proper interfaces
- [ ] Verify import order doesn't matter anymore

**Notes:** Start with formula_system - it's the simplest to extract.

---

### Task 1.3: Implement Dependency Injection Pattern [High]
**Files:** `game/core/`, `game/app.py`
**Tests:** All tests must pass

**Implementation:**
- [ ] Create `game/core/container.py` - simple DI container
- [ ] Define interfaces for cross-module dependencies
- [ ] Register implementations at app startup
- [ ] Replace direct imports with interface lookups where appropriate
- [ ] Document the pattern for future developers

**Notes:** Don't over-engineer - simple service locator pattern is sufficient.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No late imports in simulation module
- [ ] Import order is deterministic
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
