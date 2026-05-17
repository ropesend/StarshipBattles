"""MineGroupService — PROJ-FMS-B Phase 4.

Player-facing operations on ``mine_group`` Fleets:

- Set sensitivity (LOW / MED / HIGH).
- Set laserhead expected-hit-chance threshold (continuous slider).
- Selective self-destruct (pick designs / counts to destroy).

UI screens call into this service rather than mutating Fleet state
directly. Keeps the validation/strict-domain rules in one place and
gives Phase 5's E2E tests a single seam to exercise.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from game.core.validation import ValidationResult
from game.strategy.data.bay_inventory import BayInventory
from game.strategy.data.carried_vehicle import CarriedVehicle

logger = logging.getLogger(__name__)


_VALID_SENSITIVITIES: Tuple[str, ...] = ("LOW", "MED", "HIGH")


class MineGroupService:
    """Operations on ``Fleet`` objects whose ``group_kind == "mine_group"``."""

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_sensitivity(self, mine_group: Any, label: str) -> ValidationResult:
        """Change the LOW / MED / HIGH sensitivity on a mine_group."""
        if not self._is_mine_group(mine_group):
            return ValidationResult.error("Target is not a mine_group fleet.")
        label_norm = str(label).upper()
        if label_norm not in _VALID_SENSITIVITIES:
            return ValidationResult.error(
                f"Invalid sensitivity {label!r}; expected one of "
                f"{_VALID_SENSITIVITIES}."
            )
        mine_group.sensitivity = label_norm
        return ValidationResult.success()

    def set_threshold(self, mine_group: Any, value: float) -> ValidationResult:
        """Change the continuous laserhead expected_hit_chance_threshold."""
        if not self._is_mine_group(mine_group):
            return ValidationResult.error("Target is not a mine_group fleet.")
        try:
            v = float(value)
        except (TypeError, ValueError):
            return ValidationResult.error(
                f"Threshold {value!r} is not a number."
            )
        if v < 0.0 or v > 1.0:
            return ValidationResult.error(
                f"Threshold {v} out of range [0.0, 1.0]."
            )
        mine_group.expected_hit_chance_threshold = v
        return ValidationResult.success()

    # ------------------------------------------------------------------
    # Self-destruct
    # ------------------------------------------------------------------

    def get_mine_counts_by_design(self, mine_group: Any) -> Dict[str, int]:
        """Return ``{design_id: count}`` for the mine_group's inventory."""
        if not self._is_mine_group(mine_group) or not mine_group.ships:
            return {}
        counts: Dict[str, int] = {}
        # PROJ-431 Phase 1b: read through the typed BayInventory substrate.
        for cv in mine_group.ships[0].bay_inventory.bay:
            if cv.vehicle_type != "mine":
                continue
            counts[cv.design_id] = counts.get(cv.design_id, 0) + 1
        return counts

    def self_destruct(
        self,
        mine_group: Any,
        empire: Any,
        selections: Dict[str, int],
    ) -> ValidationResult:
        """Selectively destroy mines without triggering damage.

        Args:
            mine_group: Owner-side mine_group Fleet.
            empire: The owning empire (used for fleet-list cleanup).
            selections: ``{design_id: count_to_destroy}``. Counts above
                inventory are clamped; missing design_ids are skipped.

        Returns:
            ValidationResult with the number of mines destroyed in
            ``warning_message`` when partial.
        """
        if not self._is_mine_group(mine_group):
            return ValidationResult.error("Target is not a mine_group fleet.")
        if not mine_group.ships:
            return ValidationResult.error("mine_group has no carrier ship.")

        carrier = mine_group.ships[0]
        # PROJ-431 Phase 1b: read & write through the typed BayInventory
        # substrate. The bay is homogeneous CarriedVehicle (mines on a
        # mine_group never carry pods), so no from_any() discrimination
        # is needed.
        current_bay = carrier.bay_inventory.bay
        remaining_bay: List[CarriedVehicle] = []
        budget: Dict[str, int] = {
            k: max(0, int(v)) for k, v in (selections or {}).items()
        }
        destroyed = 0
        for cv in current_bay:
            design = cv.design_id if cv.vehicle_type == "mine" else None
            if design and budget.get(design, 0) > 0:
                budget[design] -= 1
                destroyed += 1
                continue
            remaining_bay.append(cv)
        carrier.set_bay_inventory(BayInventory(bay=remaining_bay))

        # Re-sync mine_positions so they stay consistent with inventory.
        new_count = len(remaining_bay)
        if new_count < len(mine_group.mine_positions):
            mine_group.mine_positions = mine_group.mine_positions[:new_count]

        # Drop the mine_group entirely if empty.
        if not remaining_bay:
            try:
                empire.fleets.remove(mine_group)
            except (ValueError, AttributeError):
                pass

        logger.info(
            "MineGroupService.self_destruct: destroyed %d mines from group %s",
            destroyed,
            getattr(mine_group, "id", "?"),
        )
        return ValidationResult.success()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _is_mine_group(fleet: Any) -> bool:
        return getattr(fleet, "group_kind", "fleet") == "mine_group"


__all__ = ["MineGroupService"]
