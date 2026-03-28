"""
Three-Phase Validation System for Combat Lab Test Scenarios.

Phases:
    1. data        - Loaded JSON matches expectations (ship mass, weapon damage, etc.)
    2. precondition - Simulation behaved correctly (weapon fired, target moved, etc.)
    3. outcome      - Final results match expectations (hit rate, distance, fuel consumed)

A test passes only when ALL checks across all three phases pass.
If a test fails, `ValidationReport.failed_phase` identifies the root cause.

Usage:
    from simulation_tests.scenarios.validation import (
        Check, ValidationReport,
        check_exact, check_approx, check_tost, check_true,
    )

    def validate(self, engine) -> List[Check]:
        checks = []
        checks.append(check_exact("Ship Mass", 400, self.ship.mass))
        checks.append(check_true("Ship Moved", self.distance > 0))
        checks.append(check_approx("Max Speed", 31.25, self.ship.max_speed))
        return checks
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


PHASES = ("data", "precondition", "outcome")


# ---------------------------------------------------------------------------
# Core data model
# ---------------------------------------------------------------------------

@dataclass
class Check:
    """One validation check with phase, identity, and outcome."""
    phase: str
    name: str
    expected: Any
    actual: Any
    passed: bool
    detail: str = ""


@dataclass
class ValidationReport:
    """Complete validation results for a scenario run."""
    checks: List[Check] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True only when every check passes."""
        return len(self.checks) > 0 and all(c.passed for c in self.checks)

    @property
    def failed_phase(self) -> Optional[str]:
        """First phase containing a failure, or None."""
        for phase in PHASES:
            if any(not c.passed for c in self.checks if c.phase == phase):
                return phase
        return None

    def phase_checks(self, phase: str) -> List[Check]:
        return [c for c in self.checks if c.phase == phase]

    def summary(self) -> Dict[str, Dict[str, int]]:
        result = {}
        for phase in PHASES:
            pc = self.phase_checks(phase)
            result[phase] = {
                "total": len(pc),
                "passed": sum(1 for c in pc if c.passed),
                "failed": sum(1 for c in pc if not c.passed),
            }
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "failed_phase": self.failed_phase,
            "summary": self.summary(),
            "checks": [
                {
                    "phase": c.phase,
                    "name": c.name,
                    "expected": _safe_serialize(c.expected),
                    "actual": _safe_serialize(c.actual),
                    "passed": c.passed,
                    "detail": c.detail,
                }
                for c in self.checks
            ],
        }


def _safe_serialize(value: Any) -> Any:
    """Convert value to a JSON-safe type."""
    if isinstance(value, float):
        if value != value:  # NaN
            return None
        return value
    if isinstance(value, (int, str, bool, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_serialize(v) for v in value]
    return str(value)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_exact(
    name: str,
    expected: Any,
    actual: Any,
    phase: str = "data",
) -> Check:
    """Exact equality check. Default phase: data."""
    return Check(
        phase=phase,
        name=name,
        expected=expected,
        actual=actual,
        passed=(actual == expected),
        detail=f"expected={expected}, actual={actual}",
    )


def check_approx(
    name: str,
    expected: float,
    actual: float,
    tolerance: float = 1e-9,
    phase: str = "outcome",
) -> Check:
    """Float comparison within relative tolerance. Default phase: outcome."""
    if expected != 0:
        rel_error = abs(actual - expected) / abs(expected)
        pct_diff = (actual - expected) / expected * 100
    else:
        rel_error = abs(actual)
        pct_diff = 0.0

    passed = rel_error <= tolerance
    return Check(
        phase=phase,
        name=name,
        expected=expected,
        actual=actual,
        passed=passed,
        detail=f"relative_error={rel_error:.2e}, diff={pct_diff:+.4f}%, tolerance={tolerance}",
    )


def check_tost(
    name: str,
    expected_p: float,
    successes: int,
    trials: int,
    margin: float = 0.02,
    phase: str = "outcome",
) -> Check:
    """
    TOST equivalence test for proportions. Default phase: outcome.

    H0: actual differs from expected by more than margin (system broken).
    H1: actual is within margin of expected (system works).
    p < 0.05 -> reject H0 -> proven equivalent -> PASS.
    """
    try:
        from scipy.stats import norm
        import math
    except ImportError:
        return Check(
            phase=phase,
            name=name,
            expected=expected_p,
            actual=None,
            passed=False,
            detail="scipy not available",
        )

    if trials <= 0:
        return Check(
            phase=phase,
            name=name,
            expected=expected_p,
            actual=0.0,
            passed=False,
            detail="no trials recorded",
        )

    observed = successes / trials
    lower = expected_p - margin
    upper = expected_p + margin

    se = math.sqrt(expected_p * (1 - expected_p) / trials)
    se = max(se, 1e-10)

    # TOST: test 1 (observed > lower), test 2 (observed < upper)
    z1 = (observed - lower) / se
    p1 = 1 - norm.cdf(z1)

    z2 = (observed - upper) / se
    p2 = norm.cdf(z2)

    p_value = max(p1, p2)
    passed = p_value < 0.05

    return Check(
        phase=phase,
        name=name,
        expected=expected_p,
        actual=observed,
        passed=passed,
        detail=(
            f"TOST p={p_value:.4f}, observed={observed:.4f} "
            f"({successes}/{trials}), margin=+/-{margin:.2%}, "
            f"bounds=[{lower:.4f}, {upper:.4f}]"
        ),
    )


def check_true(
    name: str,
    condition: bool,
    actual: Any = None,
    detail: str = "",
    phase: str = "precondition",
) -> Check:
    """Boolean precondition check. Default phase: precondition."""
    return Check(
        phase=phase,
        name=name,
        expected=True,
        actual=actual if actual is not None else condition,
        passed=bool(condition),
        detail=detail,
    )
