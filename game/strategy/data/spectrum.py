"""``Spectrum`` electromagnetic-output dataclass.

PROJ-372 Phase 1 split: extracted from ``stars.py`` for the file-LOC
budget. Save format unchanged — old saves load identically.

External readers should import ``Spectrum`` from here, but
``stars.py`` re-exports the symbol for backwards-compat with the 15+
existing import sites.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from game.core.validation_helpers import require_keys, validate_non_negative


__all__ = ["Spectrum"]


@dataclass
class Spectrum:
    """Represents the electromagnetic spectrum intensity of a star.

    Values are relative to a standard Sol-like baseline or absolute
    flux W/m^2 (simplified).
    """
    gamma_ray: float            # < 10 pm
    xray: float                 # 10 pm - 10 nm
    ultraviolet: float          # 10 nm - 400 nm
    blue: float                 # 400 nm - 500 nm (Visible)
    green: float                # 500 nm - 600 nm (Visible)
    red: float                  # 600 nm - 700 nm (Visible)
    infrared: float             # 700 nm - 1 mm
    microwave: float            # 1 mm - 1 m
    radio: float                # > 1 m

    def get_total_output(self) -> float:
        """Total electromagnetic output across all spectrum bands."""
        return (
            self.gamma_ray + self.xray + self.ultraviolet
            + self.blue + self.green + self.red
            + self.infrared + self.microwave + self.radio
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Spectrum to dict."""
        return {
            "gamma_ray": self.gamma_ray,
            "xray": self.xray,
            "ultraviolet": self.ultraviolet,
            "blue": self.blue,
            "green": self.green,
            "red": self.red,
            "infrared": self.infrared,
            "microwave": self.microwave,
            "radio": self.radio,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Spectrum":
        """Deserialize Spectrum from dict.

        Raises:
            PersistenceException: If required keys missing or values invalid.
        """
        keys = [
            "gamma_ray", "xray", "ultraviolet", "blue", "green",
            "red", "infrared", "microwave", "radio",
        ]
        require_keys(data, keys, "Spectrum")
        for key in keys:
            validate_non_negative(data[key], key, "Spectrum")
        return cls(**{k: data[k] for k in keys})
