# Phase 6: ValidationResult Cleanup + Final Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 7 test ValidationResult constructor calls to factory methods, then final audit.

---

## Tasks

### Task 6.1: Migrate test_explicit_orders.py [Simple]
**File:** `tests/integration/colonization/test_explicit_orders.py`
**Tests:** `pytest tests/integration/colonization/test_explicit_orders.py -v`

- [ ] Line 52: `ValidationResult(is_valid=True)` → `ValidationResult.success()`

**Notes:**

---

### Task 6.2: Migrate test_facade_init.py [Simple]
**File:** `tests/integration/strategy/facade/test_facade_init.py`
**Tests:** `pytest tests/integration/strategy/facade/test_facade_init.py -v`

- [ ] Line 36: `ValidationResult(is_valid=True)` → `ValidationResult.success()`

**Notes:**

---

### Task 6.3: Migrate test_colonization_facade.py [Simple]
**File:** `tests/integration/ui/test_colonization_facade.py`
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py -v`

- [ ] Line 163: `ValidationResult(is_valid=False, errors=["Already owned"])` → `ValidationResult.error("Already owned")`
- [ ] Line 243: `ValidationResult(is_valid=False, errors=["No path found"])` → `ValidationResult.error("No path found")`

**Notes:**

---

### Task 6.4: Migrate test_validation_queries.py [Simple]
**File:** `tests/integration/strategy/facade/test_validation_queries.py`
**Tests:** `pytest tests/integration/strategy/facade/test_validation_queries.py -v`

- [ ] Lines 68-70: `ValidationResult(is_valid=False, errors=["Planet already owned."], error_code="ALREADY_OWNED")` → `ValidationResult.error("Planet already owned.", code="ALREADY_OWNED")`

**Notes:**

---

### Task 6.5: Migrate test_superweapon_command_handlers.py [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py -v`

- [ ] Lines 125-127: `ValidationResult(is_valid=False, errors=["No ship in fleet has DestroyPlanet ability."])` → `ValidationResult.error("No ship in fleet has DestroyPlanet ability.")`

**Notes:**

---

### Task 6.6: Migrate test_strategy_session_facade.py [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py -v`

- [ ] Line 560: `ValidationResult(is_valid=True)` → `ValidationResult.success()`

**Notes:**

---

### Task 6.7: Final audit [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: all 12,718+ tests pass
- [ ] Verify: `grep -rn "pygame.font.SysFont\|pygame.font.Font(None" game/` returns zero results (all fonts migrated)
- [ ] Verify: `grep -rn "FONT_MAIN" game/ui/colors.py` returns zero results (removed)
- [ ] Verify: no local `FONT_MAIN` or `FONT_MONO` definitions remain (except `game/ui/fonts.py`)
- [ ] Spot-check 3-4 Test Lab files for consistent theme usage
- [ ] Verify no import errors by running: `python -c "from game.ui.fonts import get_font; from game.ui.screens.test_lab.theme import BG_PRIMARY"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (12,718+ tests)
- [ ] Final audit shows clean migration
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
