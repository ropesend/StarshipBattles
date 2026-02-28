# Phase 3: Eliminate Dual Static/Instance Patterns

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize service APIs to instance-only methods
**Complexity:** Medium

---

## Pre-Phase Checklist
- [x] Phase 2 complete
- [x] Read [design.md](design.md) - review "Static/Instance Method Patterns" section
- [x] Verify: `pytest tests/` passes

---

## Task 3.1: Refactor ShipStatsService.calculate_stats() [Medium]
**Issue:** LPH-003
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/services/test_ship_stats_service*.py tests/unit/strategy/`

### Subtasks
- [x] Simplify `calculate_stats()` signature - remove parameter introspection:
  ```python
  # FROM: 8 parameters with overloading
  def calculate_stats(self_or_design, design_or_damage=None, ...)

  # TO: Clean instance method
  def calculate_stats(self, design_data: Dict,
                      component_damage: Optional[Dict] = None,
                      component_toggles: Optional[Dict] = None) -> Dict:
  ```
- [x] Remove the `isinstance(self_or_design, ShipStatsService)` check logic
- [x] Find all static callers using grep:
  ```bash
  grep -r "ShipStatsService\.calculate_stats" game/ --include="*.py"
  ```
- [x] Update each caller to create service instance first:
  - `game/strategy/data/ship_instance.py:190`
  - `game/core/registry.py` (if still present)
  - Any other callers found
- [x] Run tests: `pytest tests/unit/services/test_ship_stats_service*.py`

**Notes:**

---

## Task 3.2: Refactor ModifierService Dual Methods [Medium]
**Issue:** BCD-003
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service*.py`

### Subtasks
- [x] Refactor `is_modifier_allowed()` - remove static support:
  ```python
  # FROM: Parameter introspection
  if isinstance(self_or_mod_id, ModifierService):
      # Instance method call
  else:
      # Static-style call

  # TO: Clean instance method
  def is_modifier_allowed(self, mod_id: str, component) -> bool:
  ```
- [x] Refactor `get_mandatory_modifiers()` - remove static support
- [x] Refactor `is_modifier_mandatory()` - remove static support
- [x] Refactor `get_initial_value()` - remove static support
- [x] Refactor `ensure_mandatory_modifiers()` - remove static support
- [x] Refactor `get_local_min_max()` - remove static support
- [x] Run tests: `pytest tests/unit/services/test_modifier_service*.py`

**Notes:**

---

## Task 3.3: Update All Callers to Instance Pattern [Medium]
**Files:** Multiple (see grep results from Task 3.2)
**Tests:** `pytest tests/unit/`

### Subtasks
- [x] Find all static ModifierService callers:
  ```bash
  grep -r "ModifierService\." game/ --include="*.py" | grep -v "def \|class \|#"
  ```
- [x] Update callers in `game/ui/screens/builder/modifier_logic.py`
- [x] Update callers in `game/ui/screens/builder/legacy_components.py`
- [x] Update callers in `game/ui/panels/builder_widgets.py`
- [x] Update callers in `game/simulation/entities/ship.py`
- [x] Update callers in `game/simulation/entities/ship_component_manager.py`
- [x] Update any callers in `ui/builder/modifier_logic.py`
- [x] Ensure service instances are created/injected at appropriate points
- [x] Run tests: `pytest tests/unit/`

**Notes:**

---

## Task 3.4: Remove Parameter Introspection Logic [Simple]
**Files:**
- `game/strategy/services/ship_stats_service.py`
- `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/`

### Subtasks
- [x] In ShipStatsService: Remove all `isinstance()` checks for self detection
- [x] In ModifierService: Remove all `isinstance()` checks for self detection
- [x] Verify no remaining dual-pattern code:
  ```bash
  grep -r "isinstance.*Service" game/ --include="*.py"
  ```
- [x] Run tests: `pytest tests/unit/services/`
- [x] Run full tests: `pytest tests/`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass (5360 passed, 3 skipped)
- [x] Verify no `isinstance(self_or_*, Service)` patterns remain
- [x] Verify all service calls use instance pattern
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
- [x] Commit: "PROJ-42 Phase 3: Standardize services to instance-only methods"
