"""Validation module for ship design rules.

Provides a template method pattern base class for validation rules,
reducing duplication of guard clauses across rule implementations.

Note: ValidationResult should be imported directly from game.core.validation.
"""
from .base import ValidationRule, DesignValidationRule, AdditionValidationRule

__all__ = ['ValidationRule', 'DesignValidationRule', 'AdditionValidationRule']
