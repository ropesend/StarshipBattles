"""Validation module for ship design rules.

Provides a template method pattern base class for validation rules,
reducing duplication of guard clauses across rule implementations.
"""
from .base import ValidationRule, ValidationResult

__all__ = ['ValidationRule', 'ValidationResult']
