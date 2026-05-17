"""Shared helpers for the five FMS command handlers (QA Observation B).

Each handler validates the exactly-one-of(fleet_id, planet_id) invariant
and counts matching CarriedVehicle entries from either a ship's bay or
a planet's staging yard. Centralising these keeps the per-handler files
small and the invariant uniform.
"""
from __future__ import annotations

from typing import Optional

from game.core.validation import ValidationResult
from game.strategy.data.carried_vehicle import CarriedVehicle


def check_issuer_invariant(cmd, action: str) -> Optional[ValidationResult]:
    """Validate exactly-one-of(fleet_id, planet_id) on FMS command DTOs.

    Returns ``None`` when the invariant holds; otherwise an error result.
    """
    has_fleet = getattr(cmd, "fleet_id", None) is not None
    has_planet = getattr(cmd, "planet_id", None) is not None
    if has_fleet and has_planet:
        return ValidationResult.error(
            f"{action}: exactly one of fleet_id / planet_id allowed."
        )
    if not has_fleet and not has_planet:
        return ValidationResult.error(
            f"{action}: one of fleet_id / planet_id required."
        )
    return None


def count_matching(items, vehicle_type: str, design_id) -> int:
    """Count CarriedVehicle entries in ``items`` matching the filter."""
    n = 0
    wants_any = (not design_id) or design_id == "auto"
    for item in items:
        cv = CarriedVehicle.from_any(item)
        if cv is None or cv.vehicle_type != vehicle_type:
            continue
        if not wants_any and cv.design_id != design_id:
            continue
        n += 1
    return n


def resolve_requested(count, count_available: int):
    """Resolve the requested count.

    Returns either an ``int`` (resolved count) or a ``ValidationResult``
    when the caller supplied a non-positive count.
    """
    if count is None:
        return count_available
    if count <= 0:
        return ValidationResult.error("Count must be > 0.")
    return int(count)


__all__ = ["check_issuer_invariant", "count_matching", "resolve_requested"]
