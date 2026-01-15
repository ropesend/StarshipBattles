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
        Resolve dot-notation path to value with detailed error reporting.

        Args:
            context: Context dictionary
            path: Dot-notation path (e.g., 'attacker.weapon.damage')

        Returns:
            Value at path

        Raises:
            ValueError: If path resolution fails, with detailed error message
        """
        parts = path.split('.')
        current = context
        path_trace = []

        for i, part in enumerate(parts):
            path_trace.append(part)

            if isinstance(current, dict):
                if part not in current:
                    available = list(current.keys())
                    raise ValueError(
                        f"Path resolution failed at '{'.'.join(path_trace)}'\n"
                        f"  Key '{part}' not found in dict.\n"
                        f"  Available keys: {available[:10]}" +  # Show first 10 keys
                        (f"... ({len(available) - 10} more)" if len(available) > 10 else "")
                    )
                current = current[part]
            else:
                # Object attribute access
                if not hasattr(current, part):
                    available = [a for a in dir(current) if not a.startswith('_')]
                    raise ValueError(
                        f"Path resolution failed at '{'.'.join(path_trace)}'\n"
                        f"  Attribute '{part}' not found on {type(current).__name__}.\n"
                        f"  Available attributes: {available[:10]}" +  # Show first 10 attributes
                        (f"... ({len(available) - 10} more)" if len(available) > 10 else "")
                    )
                current = getattr(current, part)

            if current is None:
                raise ValueError(
                    f"Path resolution encountered None at '{'.'.join(path_trace)}'\n"
                    f"  Path '{'.'.join(parts)}' cannot be fully resolved."
                )

        return current


class StatisticalTestRule(ValidationRule):
    """
    Validates that measured outcome matches expected using TOST equivalence testing.

    Uses TOST (Two One-Sided Tests) for equivalence testing:
    - H0 (Null): Actual differs from expected by MORE than equivalence margin (system is broken)
    - H1 (Alternative): Actual is WITHIN equivalence margin of expected (system works)
    - p < 0.05: Reject H0, proven equivalent → PASS ✓
    - p ≥ 0.05: Fail to reject H0, not proven equivalent → FAIL ✗

    This is the scientifically correct approach for validation testing!

    Example:
        rule = StatisticalTestRule(
            name='Beam Hit Rate',
            test_type='binomial',
            expected_probability=0.5171,
            equivalence_margin=0.02,  # ±2% is acceptable
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
        equivalence_margin: float = 0.02,  # ±2% default
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
            equivalence_margin: Acceptable deviation from expected (default 0.02 = ±2%)
            trials_expr: For binomial, expression for number of trials (e.g., 'ticks_run')
            successes_expr: For binomial, expression for successes (e.g., 'damage_dealt')
            samples_expr: For t-test, expression for sample values
            description: Human-readable description of what's being measured
        """
        super().__init__(name)
        self.test_type = test_type
        self.expected_probability = expected_probability
        self.expected_mean = expected_mean
        self.equivalence_margin = equivalence_margin
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
        Perform TOST equivalence test for proportions.

        H0 (Null): Actual rate differs from expected by MORE than margin (system broken)
        H1 (Alternative): Actual rate is WITHIN margin of expected (system works)

        Uses TOST (Two One-Sided Tests):
        - Test 1: Is actual > expected - margin? (lower bound)
        - Test 2: Is actual < expected + margin? (upper bound)
        - If both tests pass (p < 0.05), we've proven equivalence → PASS

        Args:
            context: Contains 'results' dict

        Returns:
            ValidationResult with p-value (p < 0.05 = PASS)
        """
        try:
            from scipy.stats import norm
            import math
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

        # Calculate observed rate
        observed_rate = successes / trials if trials > 0 else 0.0

        # Define equivalence bounds
        p_expected = self.expected_probability
        margin = self.equivalence_margin
        lower_bound = p_expected - margin
        upper_bound = p_expected + margin

        # Standard error using expected proportion (correct for TOST)
        se = math.sqrt(p_expected * (1 - p_expected) / trials) if trials > 0 else 1.0

        # Avoid division by zero
        if se < 1e-10:
            se = 1e-10

        # TOST Test 1: Is observed > lower_bound?
        # H0: p_obs <= lower_bound, H1: p_obs > lower_bound
        z1 = (observed_rate - lower_bound) / se
        p1 = 1 - norm.cdf(z1)  # One-sided test (upper tail)

        # TOST Test 2: Is observed < upper_bound?
        # H0: p_obs >= upper_bound, H1: p_obs < upper_bound
        z2 = (observed_rate - upper_bound) / se
        p2 = norm.cdf(z2)  # One-sided test (lower tail)

        # TOST p-value is the maximum of the two tests
        # We need BOTH tests to reject H0, so we take the worst-case p-value
        p_value = max(p1, p2)

        # NEW INTERPRETATION: p < 0.05 means PASS (proven equivalent)
        if p_value < 0.05:
            status = ValidationStatus.PASS
            symbol = "✓"
            verdict = "proven equivalent"
        else:
            status = ValidationStatus.FAIL
            symbol = "✗"
            verdict = "not proven equivalent"

        # Calculate deviation from expected
        deviation = observed_rate - p_expected
        deviation_pct = (deviation / p_expected * 100) if p_expected > 0 else 0

        # Build message
        message = (
            f"{self.name}: {symbol} Expected {p_expected:.2%}, "
            f"observed {observed_rate:.2%} ({int(successes)}/{int(trials)}), "
            f"deviation {deviation_pct:+.1f}%, "
            f"p={p_value:.4f} ({verdict})\n"
            f"  Equivalence margin: ±{margin:.1%} "
            f"[{lower_bound:.2%}, {upper_bound:.2%}]"
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
            tolerance=0.05  # p-value threshold (p < 0.05 = PASS)
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
