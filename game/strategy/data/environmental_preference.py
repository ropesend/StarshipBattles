"""EnvironmentalPreference — per-axis race preference: setpoint + tolerance.

PROJ-283: the single building block for every race environmental axis
(gravity, temperature, water, total pressure, tectonic activity, magnetic
field, radiation, and each individual atmospheric gas). A race's
`preferences: Dict[str, EnvironmentalPreference]` keys by factor id (e.g.
`"gravity"`, `"gas.O2"`).

Semantics:
- `setpoint`: the race's preferred value on this axis. Free to place
  anywhere in `[min_value, max_value]` — no point cost.
- `tolerance`: the Gaussian sigma used by the habitability scorer. Wider
  = hardier race; the point-budget cost curve charges for deviating
  from the factor's default tolerance (see `race_point_budget`).
- `min_value`, `max_value`: legal slider range; also bounds the setpoint.
- `step`: the unit of one tolerance-cost step (see `race_point_budget`).
  Copied from the originating `HabitabilityFactor` so a preference is
  self-describing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from game.core.exceptions import ValidationException
from game.core.validation_helpers import require_keys


@dataclass
class EnvironmentalPreference:
    """A race's preference on a single habitability axis.

    See module docstring for field semantics. Validation runs in
    `__post_init__` so a malformed preference fails loud at construction
    rather than poisoning downstream math silently.
    """
    setpoint: float
    tolerance: float
    min_value: float
    max_value: float
    step: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.min_value > self.max_value:
            raise ValidationException(
                f"EnvironmentalPreference: min_value ({self.min_value}) > "
                f"max_value ({self.max_value})"
            )
        if not (self.min_value <= self.setpoint <= self.max_value):
            raise ValidationException(
                f"EnvironmentalPreference: setpoint ({self.setpoint}) outside "
                f"[{self.min_value}, {self.max_value}]"
            )
        if self.tolerance < 0:
            raise ValidationException(
                f"EnvironmentalPreference: tolerance must be non-negative, "
                f"got {self.tolerance}"
            )
        if self.step <= 0:
            raise ValidationException(
                f"EnvironmentalPreference: step must be positive, got {self.step}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "setpoint": self.setpoint,
            "tolerance": self.tolerance,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "step": self.step,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentalPreference":
        require_keys(
            data,
            ["setpoint", "tolerance", "min_value", "max_value", "step"],
            "EnvironmentalPreference",
        )
        return cls(
            setpoint=float(data["setpoint"]),
            tolerance=float(data["tolerance"]),
            min_value=float(data["min_value"]),
            max_value=float(data["max_value"]),
            step=float(data["step"]),
        )
