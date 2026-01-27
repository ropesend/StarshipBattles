"""Validation module for ship design rules.

Provides a template method pattern base class for validation rules,
reducing duplication of guard clauses across rule implementations.

PROJ-21: ValidationResult is now imported from game.core.validation
and re-exported here for backwards compatibility.
"""
from game.core.validation import ValidationResult
from .base import ValidationRule, DesignValidationRule, AdditionValidationRule

__all__ = ['ValidationRule', 'ValidationResult', 'DesignValidationRule', 'AdditionValidationRule']
