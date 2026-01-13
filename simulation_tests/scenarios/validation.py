"""
Validation System for Test Scenarios

This module provides infrastructure for validating test scenarios:
1. Exact Validation: Test metadata matches actual component data (0 tolerance)
2. Statistical Validation: Measured outcomes match expected (p-value < 0.05)

Architecture:
- ValidationResult: Dataclass holding validation outcome
- ValidationRule: Base class for validation rules
- ExactMatchRule: Validates exact equality (e.g., component damage)
- StatisticalTestRule: Validates statistical consistency (e.g., hit rates)
- Validator: Runs all validation rules and aggregates results

Usage:
    from simulation_tests.scenarios.validation import (
        ExactMatchRule, StatisticalTestRule, Validator
    )

    rules = [
        ExactMatchRule(
            name='Beam Damage',
            path='attacker.components[0].damage',
            expected=1
        ),
        StatisticalTestRule(
            name='Hit Rate',
            test_type='binomial',
            expected_probability=0.5171,
            trials_expr='ticks_run',
            successes_expr='damage_dealt'
        )
    ]

    validator = Validator(rules)
    results = validator.validate(test_scenario, battle_engine)
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Literal, Dict
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status."""
    PASS = "PASS"     # Validation passed
    FAIL = "FAIL"     # Validation failed
    WARN = "WARN"     # Warning (non-critical)
    INFO = "INFO"     # Informational only


@dataclass
class ValidationResult:
    """
    Result of a validation check.

    Attributes:
        name: Human-readable name of what was validated
        status: ValidationStatus enum
        message: Description of the result
        expected: Expected value
        actual: Actual value measured
        p_value: For statistical tests, the p-value (optional)
        tolerance: Acceptable tolerance for the comparison (optional)
    """
    name: str
    status: ValidationStatus
    message: str
    expected: Any
    actual: Any
    p_value: Optional[float] = None
    tolerance: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'expected': self.expected,
            'actual': self.actual,
            'p_value': self.p_value,
            'tolerance': self.tolerance
        }


class ValidationRule:
    """
    Base class for validation rules.

    Subclasses must implement validate() method.
    """

    def __init__(self, name: str):
        """
        Initialize validation rule.

        Args:
            name: Human-readable name for this validation
        """
        self.name = name

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Perform validation.

        Args:
            context: Dictionary containing test data, ships, results, etc.

        Returns:
            ValidationResult with outcome
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement validate()")


class ExactMatchRule(ValidationRule):
    """
    Validates that a value exactly matches expected (0 tolerance).

    Used for comparing test metadata to component data (e.g., weapon damage,
    ship mass, test duration).

    Example:
        rule = ExactMatchRule(
            name='Beam Weapon Damage',
            path='attacker.weapon.damage',
            expected=1
        )
    """

    def __init__(self, name: str, path: str, expected: Any):
        """
        Initialize exact match rule.

        Args:
            name: Human-readable name
            path: Dot-notation path to value (e.g., 'attacker.weapon.damage')
            expected: Expected value
        """
        super().__init__(name)
        self.path = path
        self.expected = expected

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate exact match.

        Args:
            context: Contains 'attacker', 'target', 'test_scenario', etc.

        Returns:
            ValidationResult
        """
        # Resolve path to get actual value
        actual = self._resolve_path(context, self.path)

        # Check exact equality
        if actual == self.expected:
            return ValidationResult(
                name=self.name,
                status=ValidationStatus.PASS,
                message=f"{self.name}: ✓ Expected {self.expected}, got {actual}",
                expected=self.expected,
                actual=actual,
                tolerance=0.0
            )
        else:
            return ValidationResult(
                name=self.name,
                status=ValidationStatus.FAIL,
                message=f"{self.name}: ✗ Expected {self.expected}, got {actual}",
                expected=self.expected,
                actual=actual,
                tolerance=0.0
            )

    def _resolve_path(self, context: Dict[str, Any], path: str) -> Any:
        """
        Resolve dot-notation path to value.

        Args:
            context: Context dictionary
            path: Dot-notation path (e.g., 'attacker.weapon.damage')

        Returns:
            Value at path, or None if not found
        """
        parts = path.split('.')
        current = context

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)

            if current is None:
                return None

        return current


class StatisticalTestRule(ValidationRule):
    """
    Validates that measured outcome matches expected using statistical test.

    Supports:
    - Binomial test: For hit rates, success/failure outcomes
    - Future: t-test, chi-square, etc.

    Uses p-value < 0.05 as threshold:
    - p >= 0.05: Result is consistent with expectation (PASS)
    - p < 0.05: Result is statistically different from expectation (FAIL)

    Example:
        rule = StatisticalTestRule(
            name='Beam Hit Rate',
            test_type='binomial',
            expected_probability=0.5171,
            trials_expr='ticks_run',
            successes_expr='damage_dealt',
            description='Each hit = 1 damage, so damage_dealt = hits'
        )
    """

    def __init__(
        self,
        name: str,
        test_type: Literal['binomial', 't_test', 'chi_square'],
        expected_probability: Optional[float] = None,
        expected_mean: Optional[float] = None,
        trials_expr: Optional[str] = None,
        successes_expr: Optional[str] = None,
        samples_expr: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize statistical test rule.

        Args:
            name: Human-readable name
            test_type: Type of statistical test ('binomial', 't_test', 'chi_square')
            expected_probability: For binomial test, expected success probability
            expected_mean: For t-test, expected mean
            trials_expr: For binomial, expression for number of trials (e.g., 'ticks_run')
            successes_expr: For binomial, expression for successes (e.g., 'damage_dealt')
            samples_expr: For t-test, expression for sample values
            description: Human-readable description of what's being measured
        """
        super().__init__(name)
        self.test_type = test_type
        self.expected_probability = expected_probability
        self.expected_mean = expected_mean
        self.trials_expr = trials_expr
        self.successes_expr = successes_expr
        self.samples_expr = samples_expr
        self.description = description

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Perform statistical test.

        Args:
            context: Contains 'results' dict with test outcomes

        Returns:
            ValidationResult with p-value
        """
        if self.test_type == 'binomial':
            return self._binomial_test(context)
        elif self.test_type == 't_test':
            return self._t_test(context)
        elif self.test_type == 'chi_square':
            return self._chi_square_test(context)
        else:
            return ValidationResult(
                name=self.name,
                status=ValidationStatus.FAIL,
                message=f"Unknown test type: {self.test_type}",
                expected=None,
                actual=None
            )

    def _binomial_test(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Perform binomial test.

        H0: The observed success rate is consistent with expected probability
        H1: The observed success rate differs from expected probability

        Args:
            context: Contains 'results' dict

        Returns:
            ValidationResult with p-value
        """
        try:
            from scipy.stats import binomtest
        except ImportError:
            return ValidationResult(
                name=self.name,
                status=ValidationStatus.WARN,
                message="scipy not available for statistical testing",
                expected=self.expected_probability,
                actual=None
            )

        results = context.get('results', {})

        # Get trials and successes
        trials = self._eval_expr(results, self.trials_expr)
        successes = self._eval_expr(results, self.successes_expr)

        if trials is None or successes is None:
            return ValidationResult(
                name=self.name,
                status=ValidationStatus.WARN,
                message=f"{self.name}: Missing data for validation",
                expected=self.expected_probability,
                actual=None
            )

        # Perform binomial test
        result = binomtest(k=int(successes), n=int(trials), p=self.expected_probability)
        p_value = result.pvalue

        # Calculate observed rate
        observed_rate = successes / trials if trials > 0 else 0.0

        # Determine status
        if p_value >= 0.05:
            status = ValidationStatus.PASS
            symbol = "✓"
        else:
            status = ValidationStatus.FAIL
            symbol = "✗"

        # Build message
        message = (
            f"{self.name}: {symbol} Expected {self.expected_probability:.2%}, "
            f"observed {observed_rate:.2%} ({int(successes)}/{int(trials)}), "
            f"p={p_value:.4f}"
        )

        if self.description:
            message += f"\n  ({self.description})"

        return ValidationResult(
            name=self.name,
            status=status,
            message=message,
            expected=self.expected_probability,
            actual=observed_rate,
            p_value=p_value,
            tolerance=0.05  # p-value threshold
        )

    def _t_test(self, context: Dict[str, Any]) -> ValidationResult:
        """Placeholder for t-test implementation."""
        return ValidationResult(
            name=self.name,
            status=ValidationStatus.WARN,
            message="t-test not yet implemented",
            expected=self.expected_mean,
            actual=None
        )

    def _chi_square_test(self, context: Dict[str, Any]) -> ValidationResult:
        """Placeholder for chi-square test implementation."""
        return ValidationResult(
            name=self.name,
            status=ValidationStatus.WARN,
            message="chi-square test not yet implemented",
            expected=None,
            actual=None
        )

    def _eval_expr(self, results: Dict[str, Any], expr: str) -> Optional[float]:
        """
        Evaluate expression in context of results dict.

        Args:
            results: Test results dictionary
            expr: Expression to evaluate (e.g., 'ticks_run', 'damage_dealt')

        Returns:
            Evaluated value, or None if not found
        """
        if expr is None:
            return None

        # Simple variable lookup
        if expr in results:
            return results[expr]

        # Could extend this to support expressions like 'damage_dealt / ticks_run'
        # For now, just simple lookups
        return None


class Validator:
    """
    Runs validation rules and aggregates results.

    Example:
        validator = Validator([
            ExactMatchRule('Beam Damage', 'attacker.weapon.damage', 1),
            StatisticalTestRule('Hit Rate', 'binomial', 0.5171,
                              trials_expr='ticks_run', successes_expr='damage_dealt')
        ])

        results = validator.validate(context)
        has_failures = validator.has_failures(results)
    """

    def __init__(self, rules: List[ValidationRule]):
        """
        Initialize validator.

        Args:
            rules: List of ValidationRule instances
        """
        self.rules = rules

    def validate(self, context: Dict[str, Any]) -> List[ValidationResult]:
        """
        Run all validation rules.

        Args:
            context: Dictionary containing test data

        Returns:
            List of ValidationResult objects
        """
        results = []

        for rule in self.rules:
            try:
                result = rule.validate(context)
                results.append(result)
            except Exception as e:
                # Capture validation errors
                results.append(ValidationResult(
                    name=rule.name,
                    status=ValidationStatus.FAIL,
                    message=f"Validation error: {str(e)}",
                    expected=None,
                    actual=None
                ))

        return results

    def has_failures(self, results: List[ValidationResult]) -> bool:
        """
        Check if any validations failed.

        Args:
            results: List of ValidationResult objects

        Returns:
            True if any FAIL status found
        """
        return any(r.status == ValidationStatus.FAIL for r in results)

    def has_warnings(self, results: List[ValidationResult]) -> bool:
        """
        Check if any validations have warnings.

        Args:
            results: List of ValidationResult objects

        Returns:
            True if any WARN status found
        """
        return any(r.status == ValidationStatus.WARN for r in results)

    def get_summary(self, results: List[ValidationResult]) -> Dict[str, int]:
        """
        Get summary counts of validation results.

        Args:
            results: List of ValidationResult objects

        Returns:
            Dictionary with counts: {'pass': X, 'fail': Y, 'warn': Z, 'info': W}
        """
        summary = {
            'pass': 0,
            'fail': 0,
            'warn': 0,
            'info': 0
        }

        for result in results:
            status_key = result.status.value.lower()
            if status_key in summary:
                summary[status_key] += 1

        return summary
