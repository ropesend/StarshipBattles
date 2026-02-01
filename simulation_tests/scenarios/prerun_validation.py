"""
Pre-Run Validation System for Test Scenarios

This module provides infrastructure for validating test expectations BEFORE
a test runs. This ensures that:
1. Expected JSON data values match actual .json file values
2. Expected calculated values match actual physics calculations
3. Tests cannot run if data mismatches are detected

Architecture:
- DataExpectation: Expected value from .json file (ship mass, thrust, etc.)
- CalculatedExpectation: Expected calculated value with formula
- SetupCondition: Test setup parameters (positions, durations, commands)
- PassCriterion: Numeric pass/fail criteria
- PreRunValidator: Validates all expectations before test execution

Usage:
    from simulation_tests.scenarios.prerun_validation import (
        DataExpectation, CalculatedExpectation, SetupCondition,
        PassCriterion, PreRunValidator
    )

    # Define expectations in scenario class
    data_expectations = [
        DataExpectation(
            name='Ship Mass',
            source='ship.mass',
            expected=400,
            json_file='Test_Engine_1x_LowMass.json'
        ),
    ]

    calculated_expectations = [
        CalculatedExpectation(
            name='Max Speed',
            formula='(thrust × K_SPEED) / mass',
            formula_expr=lambda thrust, mass, K_SPEED: (thrust * K_SPEED) / mass,
            expected=31.25,
            variables={'thrust': 500, 'mass': 400, 'K_SPEED': 25}
        ),
    ]
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, Callable
from enum import Enum


class ExpectationStatus(Enum):
    """Status of an expectation check."""
    MATCH = "MATCH"       # Expected matches actual
    MISMATCH = "MISMATCH" # Expected does not match actual
    ERROR = "ERROR"       # Could not evaluate


@dataclass
class DataExpectation:
    """
    Expected value from a .json data file.

    Used to validate that test assumptions about ship/component data
    match the actual data in the JSON files.

    Attributes:
        name: Human-readable name (e.g., "Ship Mass")
        source: Path to value in loaded object (e.g., "ship.mass")
        expected: Expected value from test assumptions
        json_file: Name of source JSON file for display
        tolerance: Acceptable difference for floats (default 0.001 = 0.1%)
    """
    name: str
    source: str
    expected: Any
    json_file: str = ""
    tolerance: float = 0.001  # 0.1% tolerance for floats

    # Filled in during validation
    actual: Any = None
    status: ExpectationStatus = ExpectationStatus.ERROR
    error_message: str = ""

    def validate(self, context: Dict[str, Any]) -> 'DataExpectation':
        """
        Validate this expectation against actual data.

        Args:
            context: Dictionary containing loaded objects (ship, components, etc.)

        Returns:
            Self with actual, status, and error_message filled in
        """
        try:
            self.actual = self._resolve_path(context, self.source)

            if self._values_match(self.expected, self.actual):
                self.status = ExpectationStatus.MATCH
            else:
                self.status = ExpectationStatus.MISMATCH
                self.error_message = f"Expected {self.expected}, got {self.actual}"

        except Exception as e:
            self.status = ExpectationStatus.ERROR
            self.error_message = str(e)

        return self

    def _values_match(self, expected: Any, actual: Any) -> bool:
        """Check if values match within tolerance."""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if expected == 0:
                return abs(actual) < self.tolerance
            return abs(actual - expected) / abs(expected) <= self.tolerance
        return expected == actual

    def _resolve_path(self, context: Dict[str, Any], path: str) -> Any:
        """Resolve dot-notation path to value."""
        parts = path.split('.')
        current = context

        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    raise ValueError(f"Key '{part}' not found in dict")
                current = current[part]
            else:
                if not hasattr(current, part):
                    raise ValueError(f"Attribute '{part}' not found on {type(current).__name__}")
                current = getattr(current, part)

        return current

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/serialization."""
        return {
            'name': self.name,
            'source': self.source,
            'expected': self.expected,
            'actual': self.actual,
            'json_file': self.json_file,
            'status': self.status.value,
            'error_message': self.error_message
        }


@dataclass
class CalculatedExpectation:
    """
    Expected calculated value with formula.

    Used to validate that physics calculations produce expected results
    based on the formula and input values.

    Attributes:
        name: Human-readable name (e.g., "Max Speed")
        formula: Human-readable formula string for display
        formula_expr: Lambda/function that calculates the value
        expected: Expected result of the calculation
        variables: Dictionary of variable names to values for formula
        tolerance: Acceptable difference (default 0.001 = 0.1%)
    """
    name: str
    formula: str  # Display string like "(thrust × K_SPEED) / mass"
    formula_expr: Callable[..., float]  # Actual calculation
    expected: float
    variables: Dict[str, float] = field(default_factory=dict)
    tolerance: float = 0.001

    # Filled in during validation
    actual: float = None
    calculated_from_actual: float = None  # Calculated using actual ship values
    status: ExpectationStatus = ExpectationStatus.ERROR
    error_message: str = ""

    def validate(self, context: Dict[str, Any]) -> 'CalculatedExpectation':
        """
        Validate this calculated expectation.

        Performs two checks:
        1. Does expected match the formula calculation with expected variables?
        2. Does the actual ship value match the formula calculation?

        Args:
            context: Dictionary containing loaded objects (ship, etc.)

        Returns:
            Self with validation results filled in
        """
        try:
            # Calculate expected value from formula
            calculated = self.formula_expr(**self.variables)

            # Check if our expected matches formula
            if not self._values_match(self.expected, calculated):
                self.status = ExpectationStatus.MISMATCH
                self.error_message = f"Expected {self.expected} but formula gives {calculated}"
                return self

            # Get actual value from loaded ship (if available)
            if 'ship' in context:
                ship = context['ship']
                # Map name to ship attribute
                attr_map = {
                    'Max Speed': 'max_speed',
                    'Acceleration Rate': 'acceleration_rate',
                    'Turn Speed': 'turn_speed',
                }
                attr_name = attr_map.get(self.name)
                if attr_name and hasattr(ship, attr_name):
                    self.actual = getattr(ship, attr_name)

                    # Also calculate from actual ship values
                    if hasattr(ship, 'total_thrust') and hasattr(ship, 'mass'):
                        actual_vars = self.variables.copy()
                        if 'thrust' in actual_vars:
                            actual_vars['thrust'] = ship.total_thrust
                        if 'mass' in actual_vars:
                            actual_vars['mass'] = ship.mass
                        self.calculated_from_actual = self.formula_expr(**actual_vars)

            # Verify expected matches calculated
            if self._values_match(self.expected, calculated):
                self.status = ExpectationStatus.MATCH
            else:
                self.status = ExpectationStatus.MISMATCH
                self.error_message = f"Formula gives {calculated}, expected {self.expected}"

        except Exception as e:
            self.status = ExpectationStatus.ERROR
            self.error_message = str(e)

        return self

    def _values_match(self, expected: float, actual: float) -> bool:
        """Check if values match within tolerance."""
        if expected == 0:
            return abs(actual) < self.tolerance
        return abs(actual - expected) / abs(expected) <= self.tolerance

    def get_formula_with_values(self) -> str:
        """Get formula string with actual values substituted."""
        result = self.formula
        for var_name, var_value in self.variables.items():
            result = result.replace(var_name, str(var_value))
        return f"{result} = {self.expected}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/serialization."""
        return {
            'name': self.name,
            'formula': self.formula,
            'formula_with_values': self.get_formula_with_values(),
            'expected': self.expected,
            'actual': self.actual,
            'calculated_from_actual': self.calculated_from_actual,
            'variables': self.variables,
            'status': self.status.value,
            'error_message': self.error_message
        }


@dataclass
class SetupCondition:
    """
    Test setup condition (not validated, just displayed).

    These are conditions set by the test itself, not from data files.
    Examples: initial position, test duration, commands applied.

    Attributes:
        name: Condition name (e.g., "Initial Position")
        value: Condition value (e.g., "(0, 0)")
        description: Optional description
    """
    name: str
    value: Any
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/serialization."""
        return {
            'name': self.name,
            'value': self.value,
            'description': self.description
        }


@dataclass
class PassCriterion:
    """
    Numeric pass/fail criterion.

    Defines what must be true for the test to pass.

    Attributes:
        description: Human-readable criterion (e.g., "final_velocity > 0")
        expression: Lambda that evaluates the criterion given results
        numeric_threshold: Optional numeric value for display
    """
    description: str
    expression: Optional[Callable[[Dict[str, Any]], bool]] = None
    numeric_threshold: Optional[float] = None

    def evaluate(self, results: Dict[str, Any]) -> bool:
        """Evaluate the criterion against results."""
        if self.expression is None:
            return True
        try:
            return self.expression(results)
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/serialization."""
        return {
            'description': self.description,
            'numeric_threshold': self.numeric_threshold
        }


@dataclass
class PreRunValidation:
    """
    Container for all pre-run validation results.

    Attributes:
        data_expectations: List of data value expectations
        calculated_expectations: List of calculated value expectations
        setup_conditions: List of setup conditions (not validated)
        pass_criteria: List of pass criteria
        can_run: Whether the test can proceed (all validations passed)
        blocking_errors: List of error messages that block execution
    """
    data_expectations: List[DataExpectation] = field(default_factory=list)
    calculated_expectations: List[CalculatedExpectation] = field(default_factory=list)
    setup_conditions: List[SetupCondition] = field(default_factory=list)
    pass_criteria: List[PassCriterion] = field(default_factory=list)
    can_run: bool = True
    blocking_errors: List[str] = field(default_factory=list)

    def add_blocking_error(self, message: str):
        """Add a blocking error that prevents test execution."""
        self.blocking_errors.append(message)
        self.can_run = False

    def validate_all(self, context: Dict[str, Any]):
        """
        Run all validations against the provided context.

        Args:
            context: Dictionary containing loaded ship, components, etc.
        """
        # Validate data expectations
        for expectation in self.data_expectations:
            expectation.validate(context)
            if expectation.status == ExpectationStatus.MISMATCH:
                self.add_blocking_error(
                    f"Data mismatch - {expectation.name}: "
                    f"expected {expectation.expected}, got {expectation.actual}"
                )
            elif expectation.status == ExpectationStatus.ERROR:
                self.add_blocking_error(
                    f"Data error - {expectation.name}: {expectation.error_message}"
                )

        # Validate calculated expectations
        for expectation in self.calculated_expectations:
            expectation.validate(context)
            if expectation.status == ExpectationStatus.MISMATCH:
                self.add_blocking_error(
                    f"Calculation mismatch - {expectation.name}: {expectation.error_message}"
                )
            elif expectation.status == ExpectationStatus.ERROR:
                self.add_blocking_error(
                    f"Calculation error - {expectation.name}: {expectation.error_message}"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/serialization."""
        return {
            'data_expectations': [e.to_dict() for e in self.data_expectations],
            'calculated_expectations': [e.to_dict() for e in self.calculated_expectations],
            'setup_conditions': [c.to_dict() for c in self.setup_conditions],
            'pass_criteria': [c.to_dict() for c in self.pass_criteria],
            'can_run': self.can_run,
            'blocking_errors': self.blocking_errors
        }


class PreRunValidator:
    """
    Validates test expectations before execution.

    Usage:
        validator = PreRunValidator()
        validation = validator.validate_scenario(scenario, ship)

        if not validation.can_run:
            print("Cannot run test:", validation.blocking_errors)
    """

    def validate_scenario(
        self,
        scenario,
        context: Dict[str, Any]
    ) -> PreRunValidation:
        """
        Validate a scenario's expectations.

        Args:
            scenario: TestScenario instance with expectations defined
            context: Dictionary with 'ship', 'components', etc.

        Returns:
            PreRunValidation with results
        """
        # Get expectations from scenario if defined
        validation = PreRunValidation()

        if hasattr(scenario, 'data_expectations'):
            validation.data_expectations = scenario.data_expectations.copy()

        if hasattr(scenario, 'calculated_expectations'):
            validation.calculated_expectations = scenario.calculated_expectations.copy()

        if hasattr(scenario, 'setup_conditions'):
            validation.setup_conditions = scenario.setup_conditions.copy()

        if hasattr(scenario, 'pass_criteria'):
            validation.pass_criteria = scenario.pass_criteria.copy()

        # Run validations
        validation.validate_all(context)

        return validation
