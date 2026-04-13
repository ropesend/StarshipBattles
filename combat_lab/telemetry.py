"""Combat-Lab-specific forensic telemetry bundle.

Captured during `run_scenario_via_run_battle` and passed alongside the
simulation-layer `BattleOutcome` into `TestScenario._run_validation`. This
bundle holds data that is:

  - Specific to Combat Lab validators (not used by strategy or visual UI)
  - Not appropriate to extend onto the simulation-layer `BattleOutcome`
    (it would leak Combat-Lab concerns into the simulation DTO — per
    PROJ-270 decisions.md Decision 6, Option B)

Currently this bundle carries:

  - `in_flight_by_role`: for each role-keyed ship, how many projectiles
    owned by that ship were still airborne when the battle ended. Used
    by `_collect_weapon_stats` to derive resolved-hit accuracy that
    excludes mid-flight shots.

Future additions (tracked on a per-need basis):
  - per-tick position tracks (for erratic-target leash tests)
  - per-hit event logs (if scenarios ever need event-level forensics
    beyond what `ShipOutcome.hits_taken` provides)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class CombatLabTelemetry:
    """Frozen forensic bundle for Combat Lab scenario validation."""

    in_flight_by_role: Dict[str, int] = field(default_factory=dict)

    def in_flight_for(self, role: str) -> int:
        """Return the in-flight projectile count for a role, or 0 if unknown."""
        return self.in_flight_by_role.get(role, 0)


EMPTY_TELEMETRY = CombatLabTelemetry()


__all__ = ["CombatLabTelemetry", "EMPTY_TELEMETRY"]
