"""MineGroupService — PROJ-FMS-B Phase 4 + PROJ-431 Phase 2.

Player-facing operations on :class:`MineGroup` instances:

- Set sensitivity (LOW / MED / HIGH).
- Set laserhead expected-hit-chance threshold (continuous slider).
- Selective self-destruct (pick designs / counts to destroy).

UI screens call into this service rather than mutating MineGroup state
directly. Keeps the validation/strict-domain rules in one place and
gives Phase 5's E2E tests a single seam to exercise.

PROJ-431 Phase 2: every method operates on :class:`MineGroup` directly.
The legacy ``_is_mine_group(fleet)`` runtime check is gone — the
runtime type IS the discriminator (``isinstance(group, MineGroup)``).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from game.core.validation import ValidationResult
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import MineGroup

logger = logging.getLogger(__name__)


_VALID_SENSITIVITIES: Tuple[str, ...] = ("LOW", "MED", "HIGH")


class MineGroupService:
    """Operations on :class:`MineGroup` instances."""

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_sensitivity(self, mine_group: Any, label: str) -> ValidationResult:
        """Change the LOW / MED / HIGH sensitivity on a MineGroup."""
        if not isinstance(mine_group, MineGroup):
            return ValidationResult.error("Target is not a MineGroup.")
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
        if not isinstance(mine_group, MineGroup):
            return ValidationResult.error("Target is not a MineGroup.")
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
        """Return ``{design_id: count}`` for the MineGroup's inventory."""
        if not isinstance(mine_group, MineGroup):
            return {}
        counts: Dict[str, int] = {}
        for cv in mine_group.mines:
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
            mine_group: Owner-side :class:`MineGroup`.
            empire: The owning empire (used for ``deployed_groups``
                cleanup).
            selections: ``{design_id: count_to_destroy}``. Counts above
                inventory are clamped; missing design_ids are skipped.

        Returns:
            ValidationResult with the number of mines destroyed in
            ``warning_message`` when partial.
        """
        if not isinstance(mine_group, MineGroup):
            return ValidationResult.error("Target is not a MineGroup.")

        current_mines: List[CarriedVehicle] = list(mine_group.mines)
        remaining: List[CarriedVehicle] = []
        budget: Dict[str, int] = {
            k: max(0, int(v)) for k, v in (selections or {}).items()
        }
        destroyed = 0
        for cv in current_mines:
            design = cv.design_id if cv.vehicle_type == "mine" else None
            if design and budget.get(design, 0) > 0:
                budget[design] -= 1
                destroyed += 1
                continue
            remaining.append(cv)
        mine_group.mines = remaining

        # Re-sync mine_positions so they stay consistent with inventory.
        new_count = len(remaining)
        if new_count < len(mine_group.mine_positions):
            mine_group.mine_positions = mine_group.mine_positions[:new_count]

        # Drop the mine_group entirely if empty.
        if not remaining:
            # PROJ-431 Phase 2: prefer the typed ``deployed_groups``
            # collection. Fall back gracefully if the host empire is a
            # legacy test stub that still uses ``fleets``.
            for attr in ("deployed_groups", "fleets"):
                container = getattr(empire, attr, None)
                if container is None:
                    continue
                try:
                    container.remove(mine_group)
                    break
                except ValueError:
                    continue
                except AttributeError:
                    continue

        logger.info(
            "MineGroupService.self_destruct: destroyed %d mines from group %s",
            destroyed,
            getattr(mine_group, "id", "?"),
        )
        return ValidationResult.success()


__all__ = ["MineGroupService"]
