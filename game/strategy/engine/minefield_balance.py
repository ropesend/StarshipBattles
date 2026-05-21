"""MinefieldBalance — PROJ-FMS-B Phase 1.

Frozen dataclass + loader for ``data/balance/mines.json``. Owned by
the strategy layer so the minefield resolver can depend on it without
crossing layer boundaries upward.

The loader is cached per-process via a module-level sentinel; tests
that need to override values build a fresh :class:`MinefieldBalance`
instance and pass it directly into the resolver.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WarheadTriggerConstants:
    """Constants for the warhead-pass trigger formula.

    Formula:
        ``p_trigger = sensitivity * sigmoid(k_size * size_score -
                                              k_eva * maneuver_score - bias)``
    """

    k_size: float = 1.0
    k_eva: float = 0.5
    bias: float = 2.0


@dataclass(frozen=True)
class ScatterConstants:
    """Constants for sector-scatter PRNG and fallback radius."""

    fallback_radius_m: float = 5000.0
    seed_namespace: str = "fms.mines.scatter.v1"


@dataclass(frozen=True)
class TacticalConstants:
    """Constants for the per-tick tactical mine resolver."""

    warhead_proximity_radius: float = 600.0
    # Strategy for scaling per-tick chance: "expected_ticks_in_proximity"
    # is the only supported value at this writing — tactical-per-tick
    # chance is sized so the expected number of triggers across the time
    # a ship spends near the mine matches the strategic per-pass chance.
    per_tick_scaling: str = "expected_ticks_in_proximity"
    # PROJ-FMS-B audit Fix 5: per-tick scaling divisor. Pre-fix this was
    # a hard-coded class constant on ``TacticalMineResolver`` and the
    # balance file's claim that it was tunable was a lie. Now flows
    # from ``data/balance/mines.json::tactical.expected_ticks_in_proximity``.
    # Approximates the number of ticks a ship spends inside the
    # proximity radius; integrating per-tick triggers over those ticks
    # reproduces the strategic-pass trigger chance.
    expected_ticks_in_proximity: int = 50
    # Floor on per-tick trigger chance (avoid totally-zero floats from
    # numerical underflow).
    min_tick_chance: float = 1e-6


@dataclass(frozen=True)
class LaserheadConstants:
    """Constants for the laserhead-pass threshold gate."""

    default_threshold: float = 0.30


@dataclass(frozen=True)
class MinefieldBalance:
    """Top-level minefield balance constants."""

    warhead_trigger: WarheadTriggerConstants = field(default_factory=WarheadTriggerConstants)
    sensitivity_multipliers: Dict[str, float] = field(
        default_factory=lambda: {"LOW": 0.5, "MED": 1.0, "HIGH": 1.5}
    )
    scatter: ScatterConstants = field(default_factory=ScatterConstants)
    laserhead: LaserheadConstants = field(default_factory=LaserheadConstants)
    tactical: TacticalConstants = field(default_factory=TacticalConstants)

    def sensitivity_factor(self, label: str) -> float:
        """Return the multiplier for a sensitivity label (LOW/MED/HIGH).

        Unknown labels fall back to ``MED`` (1.0) and emit a warning.
        """
        key = (label or "MED").upper()
        if key not in self.sensitivity_multipliers:
            logger.warning(
                "MinefieldBalance: unknown sensitivity %r; defaulting to MED",
                label,
            )
            key = "MED"
        return float(self.sensitivity_multipliers[key])


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


_CACHED: Optional[MinefieldBalance] = None


def _from_dict(data: Dict[str, object]) -> MinefieldBalance:
    """Build a :class:`MinefieldBalance` from the JSON-shaped dict."""
    wh_raw = data.get("warhead_trigger", {}) or {}
    sens_raw = data.get("sensitivity_multipliers", {}) or {}
    scatter_raw = data.get("scatter", {}) or {}
    laserhead_raw = data.get("laserhead", {}) or {}
    tactical_raw = data.get("tactical", {}) or {}

    return MinefieldBalance(
        warhead_trigger=WarheadTriggerConstants(
            k_size=float(wh_raw.get("k_size", 1.0)),
            k_eva=float(wh_raw.get("k_eva", 0.5)),
            bias=float(wh_raw.get("bias", 2.0)),
        ),
        sensitivity_multipliers={
            str(k).upper(): float(v) for k, v in sens_raw.items()
        } or {"LOW": 0.5, "MED": 1.0, "HIGH": 1.5},
        scatter=ScatterConstants(
            fallback_radius_m=float(scatter_raw.get("fallback_radius_m", 5000.0)),
            seed_namespace=str(scatter_raw.get("seed_namespace", "fms.mines.scatter.v1")),
        ),
        laserhead=LaserheadConstants(
            default_threshold=float(laserhead_raw.get("default_threshold", 0.30)),
        ),
        tactical=TacticalConstants(
            warhead_proximity_radius=float(
                tactical_raw.get("warhead_proximity_radius", 600.0)
            ),
            per_tick_scaling=str(
                tactical_raw.get("per_tick_scaling", "expected_ticks_in_proximity")
            ),
            expected_ticks_in_proximity=int(
                tactical_raw.get("expected_ticks_in_proximity", 50)
            ),
            min_tick_chance=float(tactical_raw.get("min_tick_chance", 1e-6)),
        ),
    )


def load_minefield_balance(force_reload: bool = False) -> MinefieldBalance:
    """Load the canonical ``data/balance/mines.json`` (cached).

    Returns a default :class:`MinefieldBalance` when the file is missing
    or malformed. The resolver is free to be tested with an explicit
    instance, so we never raise here.
    """
    global _CACHED
    if _CACHED is not None and not force_reload:
        return _CACHED
    path = Paths.MINES_BALANCE_FILE
    # PROJ-466: route the file read through the canonical json_utils helper
    # instead of a direct json.load. `load_json` returns the sentinel on
    # missing/corrupt/permission/IO failure, preserving the
    # fallback-to-defaults behavior. `load_json` logs a missing file only at
    # DEBUG, but this is a canonical balance file whose absence is an
    # actionable config problem, so warn explicitly first (Phase 4 Task 4.4).
    if not os.path.exists(path):
        logger.warning("MinefieldBalance: %s not found; using defaults", path)
        _CACHED = MinefieldBalance()
        return _CACHED
    raw = load_json(path, default=None)
    if not raw:
        _CACHED = MinefieldBalance()
        return _CACHED
    _CACHED = _from_dict(raw)
    return _CACHED


def reset_minefield_balance_cache() -> None:
    """Test helper — drop the module cache."""
    global _CACHED
    _CACHED = None


__all__ = [
    "MinefieldBalance",
    "WarheadTriggerConstants",
    "ScatterConstants",
    "TacticalConstants",
    "LaserheadConstants",
    "load_minefield_balance",
    "reset_minefield_balance_cache",
]
