# Phase 1: Critical Fixes (URGENT)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-41 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix documentation that causes broken code or severe developer confusion

---

## Tasks

### Task 1.1: Fix adding_abilities.md [Medium]
**File:** `docs/adding_abilities.md`
**Source:** DOC-GD-001 in Guide & Reference Analyst Report

**Issues to fix:**
- [ ] Remove false claim about `apply_stat_bindings()` method (does NOT exist in Ability base class)
- [ ] Update parameter names in STAT_BINDINGS examples:
  - `attribute` → `attribute_name`
  - `base_attr` → `base_attribute`
- [ ] Document actual pattern: `get_effective_stat()` calls in `recalculate()` method
- [ ] Fix base attribute naming convention (document shows `_base_thrust` but actual code uses `base_thrust`)
- [ ] Remove unnecessary `get_effect_summary()` example (inherited from base class)

**Verify:**
- [ ] Code examples match actual `game/simulation/components/abilities/base.py`
- [ ] Parameter names match `game/simulation/components/abilities/stat_keys.py:121-124`
- [ ] Example pattern matches `game/simulation/components/abilities/propulsion.py` implementation

**Notes:** [Filled during implementation]

---

### Task 1.2: Fix adding_modifiers.md [Simple]
**File:** `docs/adding_modifiers.md`
**Source:** DOC-GD-002 in Guide & Reference Analyst Report

**Issues to fix:**
- [ ] Add missing stat keys to reference table:
  - `PROJECTILE_STEALTH_LEVEL` = `"projectile_stealth_level"`
  - `PROJECTILE_STEALTH_MULT` (if exists)
- [ ] Add clarification that JSON uses string values while Python code uses StatKey enum

**Verify:**
- [ ] Stat keys table matches `game/simulation/components/abilities/stat_keys.py`
- [ ] All stat keys from code are documented

**Notes:** [Filled during implementation]

---

### Task 1.3: Update SERVICES.md [Medium]
**File:** `docs/architecture/SERVICES.md`
**Source:** DOC-AR-003 in Architecture Doc Analyst Report

**Issues to fix:**
- [ ] Rename `ShipBuilderService` section to `VehicleDesignService`
- [ ] Update file path to `game/simulation/services/vehicle_design_service.py`
- [ ] Add note that DataService functionality is distributed (not a single service)
- [ ] Add documentation for `ShipStatsService` at `game/strategy/services/ship_stats_service.py`
- [ ] Clarify which services live in `game/simulation/services/` vs `game/strategy/services/`

**Verify:**
- [ ] All documented services exist at stated paths
- [ ] Service layer diagram is accurate

**Notes:** [Filled during implementation]

---

### Task 1.4: Fix simulation_testing_principles.md [Simple]
**File:** `docs/simulation_testing_principles.md`
**Source:** DOC-TS-003 in Testing Doc Analyst Report

**Issues to fix:**
- [ ] Remove reference to non-existent `tests/verify_themes.py`
- [ ] Update outdated file path `tests/test_ai_behaviors.py` → `tests/unit/ai/test_ai_behaviors.py`
- [ ] Add "Historical Context" heading to troubleshooting log section (mark as resolved issues)
- [ ] Update any other outdated paths found

**Verify:**
- [ ] All file paths in document exist in codebase
- [ ] No references to non-existent files

**Notes:** [Filled during implementation]

---

### Task 1.5: Fix UI_STYLE_GUIDE.md [Simple]
**File:** `docs/UI_STYLE_GUIDE.md`
**Source:** DOC-FT-004 in Feature Doc Analyst Report

**Issues to fix:**
- [ ] Remove reference to non-existent `ui/colors.py` file (line ~265)
- [ ] OR create a note that this file should be created when adding direct pygame drawing
- [ ] Add note that most UI uses pygame_gui with theme.json rather than direct color constants

**Verify:**
- [ ] No references to non-existent files
- [ ] Color codes still match `builder_theme.json`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Spot-check: Open `adding_abilities.md` and verify `apply_stat_bindings` is removed
- [ ] Spot-check: Open `SERVICES.md` and verify VehicleDesignService rename
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
