# Phase 11: Validation Audit Findings

## Overview

This audit analyzes the existing validation infrastructure across the codebase to understand the current state before consolidation.

## Summary of Findings

**Key Discovery:** The codebase already has significant validation infrastructure in place from previous projects (PROJ-21, PROJ-36, PROJ-38). The core `ValidationResult` class in `game/core/validation.py` is already the canonical implementation, and most validators already use it.

**Recommendation:** The scope of Phase 11 should be reduced. Rather than creating a new `ValidationEngine`, we should:
1. Verify all validators use `ValidationResult` consistently (already mostly done)
2. Create a unified `IValidationRule` protocol in core for cross-layer contracts
3. Document the validation architecture

---

## Existing Validation Files

### 1. game/core/validation.py (Core Layer)
**Status:** CANONICAL - Already the single source of truth

**Purpose:** Provides `ValidationResult` dataclass used by all layers

**Interface:**
```python
@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error_code: Optional[str] = None

    def add_error(self, error: str, code: Optional[str] = None) -> None
    def add_warning(self, warning: str) -> None
    def merge(self, other: 'ValidationResult') -> None
    @property
    def message(self) -> str  # Backwards compatibility
    @classmethod
    def create(cls, is_valid, message, error_code) -> 'ValidationResult'

def validation_result(is_valid, message, error_code) -> ValidationResult  # Convenience factory
```

**Used By:** All validation modules import from here (PROJ-21 consolidation)

---

### 2. game/simulation/validation/base.py (Simulation Layer)
**Status:** Template method pattern base classes

**Purpose:** Provides base classes for ship design validation rules

**Interface:**
```python
class ValidationRule(ABC):
    """Template method pattern - subclasses implement _do_validate()"""
    def validate(self, ship, component=None, layer_type=None) -> ValidationResult
    def _should_validate(self, component, layer_type) -> bool  # Hook method
    @abstractmethod
    def _do_validate(self, ship, component, layer_type) -> ValidationResult

class DesignValidationRule(ValidationRule):
    """Always runs (validates whole ship design)"""

class AdditionValidationRule(ValidationRule):
    """Only runs when component and layer_type provided"""
```

**Imports:** `from game.core.validation import ValidationResult`

**Notes:** Well-designed template method pattern. Could be promoted to core if other layers need it.

---

### 3. game/simulation/ship_validator.py (Simulation Layer)
**Status:** Main simulation validator - comprehensive

**Purpose:** Validates ship designs and component additions

**Rules Implemented:**
- `LayerConstraintRule` - Component can be placed in target layer
- `UniqueComponentRule` - Unique components not duplicated
- `ExclusiveGroupRule` - Only one from exclusive group
- `MountDependencyRule` - Required mounts available
- `LayerRestrictionDefinitionRule` - Layer-specific restrictions
- `MassBudgetRule` - Mass constraints
- `ClassRequirementsRule` - Class-specific requirements (crew, etc.)
- `ResourceDependencyRule` - Resource consumers have storage

**Main Class:**
```python
class ShipDesignValidator:
    def __init__(self, *, registries: Optional['GameRegistries'] = None)
    def validate_addition(self, ship, component, layer_type) -> ValidationResult
    def validate_design(self, ship) -> ValidationResult
```

**Imports:** `from game.core.validation import ValidationResult` (via simulation/validation/base.py)

**Notes:** Already uses DI (PROJ-38). Very mature implementation.

---

### 4. game/simulation/systems/validator.py (Simulation Layer)
**Status:** DUPLICATE/LEGACY - older version of ship_validator.py

**Purpose:** Similar to ship_validator.py but less refined

**Notes:**
- Has similar rules but without template method pattern
- Still imports from `game.core.validation`
- **Action Required:** Verify this is actually used or if ship_validator.py supersedes it

---

### 5. game/ui/screens/race_validator.py (UI Layer)
**Status:** Simple, already uses core ValidationResult

**Purpose:** Validates race configuration before saving

**Interface:**
```python
class RaceValidator:
    def validate(self, race_config: 'RaceConfig') -> ValidationResult
```

**Rules:**
- Race name required
- Flag selection required
- Portrait selection required
- Ship theme selection required

**Imports:** `from game.core.validation import ValidationResult, validation_result`

**Notes:** Clean, simple implementation. Already using core types.

---

### 6. game/strategy/validation/base.py (Strategy Layer)
**Status:** Minimal base class

**Purpose:** Base class for strategy order validation

**Interface:**
```python
class OrderValidationRule(ABC):
    @abstractmethod
    def validate(self, fleet, galaxy, **kwargs) -> ValidationResult
```

**Imports:** `from game.core.validation import ValidationResult`

**Notes:** Very similar pattern to simulation layer but different signature.

---

### 7. game/strategy/validation/colonize_validator.py (Strategy Layer)
**Status:** Specific order validator

**Purpose:** Validates COLONIZE orders for fleets

**Interface:**
```python
class ColonizeValidator:
    @staticmethod
    def validate(galaxy, fleet, target_planet) -> ValidationResult
```

**Imports:** `from game.core.validation import ValidationResult, validation_result`

**Notes:** Uses static method pattern. Returns error codes for programmatic handling.

---

## Common Patterns Identified

### 1. ValidationResult Usage
All validators already import from `game.core.validation`. This consolidation was completed in PROJ-21.

### 2. Rule Pattern Variations
Three different rule interface patterns exist:

| Layer | Base Class | Signature |
|-------|-----------|-----------|
| Simulation | `ValidationRule` | `validate(ship, component?, layer_type?)` |
| Strategy | `OrderValidationRule` | `validate(fleet, galaxy, **kwargs)` |
| UI | None (standalone) | `validate(race_config)` |

### 3. Template Method Usage
Only simulation layer uses template method pattern with `_should_validate()` hook.

---

## Recommendations

### Do NOT Create ValidationEngine
The original plan suggested creating a `ValidationEngine` class to register and run rules. However:
1. Each domain has different validation contexts (ships, fleets, races)
2. The validators are already well-structured for their domains
3. A generic engine would add complexity without clear benefit

### Recommended Actions for Phase 11

1. **Task 11.2 (Revised): Create IValidationRule Protocol**
   - Add a minimal protocol to `game/core/validation.py`
   - Protocol should be generic enough for all domains
   - Use Python's Protocol for structural typing

2. **Task 11.3-11.5 (Simplified): Verify Consistency**
   - Confirm all validators return `ValidationResult`
   - Confirm all import from `game/core/validation`
   - Document any deviations

3. **Task 11.6 (Skip): Cross-Layer Validation**
   - Not needed - each layer validates its own concerns
   - Cross-layer consistency is ensured by shared `ValidationResult` type

4. **Task 11.7: Standardize Error Messages**
   - Review error message formats across validators
   - Standardize naming conventions if needed

5. **Task 11.8: Integration Testing**
   - Run existing tests to verify nothing broken
   - No new integration tests needed if just documenting

---

## Duplicate File Investigation

### game/simulation/systems/validator.py vs game/simulation/ship_validator.py

Both files contain ship design validation logic.

**Finding:** Both files ARE actively used:

1. `game/simulation/ship_validator.py` (NEWER - uses template method pattern):
   - Exported via `__init__.py` as `ShipDesignValidator`
   - Used by: `ship_loader.py`, most tests
   - Has cleaner implementation with base classes from `validation/base.py`

2. `game/simulation/systems/validator.py` (OLDER - raw implementation):
   - Still imported directly for individual rules:
     - `game/ui/screens/builder/left_panel.py` imports `LayerRestrictionDefinitionRule`
     - `tests/unit/systems/test_mount_validation.py` imports `MountDependencyRule`
     - `tests/unit/builder/test_builder_validation.py` imports `ShipDesignValidator`

**Action Required for Phase 11:**
- The UI and tests import from `systems/validator.py` for individual rules
- Both have the same rule names but different implementations
- Need to either:
  1. Consolidate to one file and update all imports, OR
  2. Make `systems/validator.py` re-export from `ship_validator.py`

**Recommendation:** Add re-exports to `systems/validator.py` to point to `ship_validator.py`:
```python
# Legacy compatibility - re-export from canonical location
from game.simulation.ship_validator import (
    LayerRestrictionDefinitionRule,
    MountDependencyRule,
    ShipDesignValidator,
    # ... etc
)
```

This allows gradual migration without breaking existing code.

---

## Conclusion

The validation infrastructure is already well-consolidated from previous work (PROJ-21, PROJ-36, PROJ-38). Phase 11 can be significantly simplified to:
1. Add optional `IValidationRule` protocol to core
2. Clean up any duplicate code (systems/validator.py)
3. Document the validation architecture
4. Verify all tests pass

No major refactoring is needed.
