"""Ship design validation rules.

PROJ-43 Phase 11: This file now re-exports from the canonical location
at game/simulation/ship_validator.py. The implementation was consolidated
to use the template method pattern in game/simulation/validation/base.py.

For backward compatibility, all previously exported classes are available
from this module.

DEPRECATED: Import directly from game.simulation.ship_validator or use
the package-level import from game.simulation (ShipDesignValidator).
"""

# Re-export all validation classes from canonical location
from game.simulation.ship_validator import (
    # Main validator
    ShipDesignValidator,
    # Individual rules (for direct use in UI filtering, etc.)
    LayerConstraintRule,
    UniqueComponentRule,
    ExclusiveGroupRule,
    MountDependencyRule,
    LayerRestrictionDefinitionRule,
    MassBudgetRule,
    ClassRequirementsRule,
    ResourceDependencyRule,
)

# Re-export base classes for type checking
from game.simulation.validation.base import (
    ValidationRule,
    DesignValidationRule,
    AdditionValidationRule,
)

# Re-export ValidationResult for convenience
from game.core.validation import ValidationResult

__all__ = [
    # Main validator
    'ShipDesignValidator',
    # Individual rules
    'LayerConstraintRule',
    'UniqueComponentRule',
    'ExclusiveGroupRule',
    'MountDependencyRule',
    'LayerRestrictionDefinitionRule',
    'MassBudgetRule',
    'ClassRequirementsRule',
    'ResourceDependencyRule',
    # Base classes
    'ValidationRule',
    'DesignValidationRule',
    'AdditionValidationRule',
    # Result type
    'ValidationResult',
]
