# Phase 1: ValidationResult Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-21 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create unified ValidationResult in core layer and update all imports
**Complexity:** Medium

---

## Tasks

### Task 1.1: Create canonical ValidationResult in core [Simple]
**File:** `game/core/validation.py` (NEW FILE)
**Tests:** `pytest tests/unit/simulation/validation/test_base_rule.py -v`

- [ ] Create `game/core/validation.py` with unified ValidationResult class
- [ ] Include fields: is_valid (bool), errors (List[str]), warnings (List[str]), error_code (Optional[str])
- [ ] Include methods: add_error(), add_warning(), merge()
- [ ] Add message property for UI/strategy compatibility: `return self.errors[0] if self.errors else ""`
- [ ] Add comprehensive docstrings explaining cross-layer usage

**Implementation Reference:**
```python
"""Validation utilities shared across all layers."""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ValidationResult:
    """Result of a validation operation.

    This is a Data Transfer Object (DTO) that can be safely imported
    by all layers (simulation, strategy, UI). It provides a unified
    interface for validation results across the codebase.
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error_code: Optional[str] = None

    @property
    def message(self) -> str:
        """First error message (compatibility with UI/strategy layers)."""
        return self.errors[0] if self.errors else ""

    def add_error(self, error: str, code: Optional[str] = None) -> None:
        """Add an error and mark result as invalid."""
        self.errors.append(error)
        self.is_valid = False
        if code and not self.error_code:
            self.error_code = code

    def add_warning(self, warning: str) -> None:
        """Add a warning (does not affect validity)."""
        self.warnings.append(warning)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another result into this one."""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
```

**Notes:**

---

### Task 1.2: Update simulation layer imports [Simple]
**File:** `game/simulation/validation/base.py`
**Tests:** `pytest tests/unit/simulation/validation/ -v`

- [ ] Import ValidationResult from `game.core.validation`
- [ ] Remove local ValidationResult class definition (lines 16-43)
- [ ] Keep ValidationRule, DesignValidationRule, AdditionValidationRule classes
- [ ] Re-export ValidationResult in `__all__` for backward compatibility
- [ ] Update `game/simulation/validation/__init__.py` to export from core

**Notes:**

---

### Task 1.3: Remove legacy duplicate in systems/validator.py [Simple]
**File:** `game/simulation/systems/validator.py`
**Tests:** `pytest tests/unit/systems/ -v`

- [ ] Remove duplicate ValidationResult class (lines 7-18)
- [ ] Add import: `from game.core.validation import ValidationResult`
- [ ] Verify ShipDesignValidator still works correctly

**Notes:**

---

### Task 1.4: Update strategy layer imports [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -v`

- [ ] Remove ValidationResult dataclass (lines 54-58)
- [ ] Add import: `from game.core.validation import ValidationResult`
- [ ] Review `validate_colonize_order()` - may need to adapt to use .message property
- [ ] Update `game/strategy/engine/game_session.py` if it imports ValidationResult from turn_engine

**Notes:**

---

### Task 1.5: Update UI layer imports [Simple]
**File:** `game/ui/screens/race_validator.py`
**Tests:** `pytest tests/unit/ui/test_race_validator.py -v`

- [ ] Remove ValidationResult dataclass (lines 16-25)
- [ ] Add import: `from game.core.validation import ValidationResult`
- [ ] Update RaceValidator.validate() to use canonical class
- [ ] Uses .message property - should work seamlessly

**Notes:**

---

### Task 1.6: Update test imports [Simple]
**Files:** Multiple test files
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Update `tests/unit/simulation/validation/test_base_rule.py` imports
- [ ] Update `tests/integration/test_colonization.py` if needed
- [ ] Update `tests/integration/test_gameplay_loop.py` if needed
- [ ] Search for other files: `grep -r "from.*ValidationResult" tests/`
- [ ] Run full test suite to verify no import errors

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/core/validation.py` exists with complete ValidationResult class
- [ ] All 5 original locations now import from core
- [ ] No duplicate ValidationResult class definitions remain
- [ ] `pytest tests/unit/simulation/validation/ -v` passes
- [ ] `pytest tests/ -v --tb=short` passes (no import errors)
- [ ] `python -c "from game.core.validation import ValidationResult; print('OK')"` works
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
