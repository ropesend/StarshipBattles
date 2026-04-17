"""A/B battle outcome DTO — pairs baseline + variant (outcome, telemetry).

Introduced by PROJ-277 to lift A/B comparisons to a first-class
orchestration pattern. `ABBattleRunner.run(baseline_spec, variant_spec)`
produces one of these; `ComparisonScenario.validate(ab)` consumes it.

Replaces the ad-hoc `_baseline_*` attribute stashing on
`ComparisonScenario` and the telemetry role-remapping (`"attacker"` →
`"baseline_attacker"`) that previously disambiguated baseline from
variant. With both (outcome, telemetry) pairs in a single DTO,
validators read `ab.baseline_telemetry.in_flight_by_role["attacker"]`
vs `ab.variant_telemetry.in_flight_by_role["attacker"]` directly.
"""
from __future__ import annotations

from dataclasses import dataclass

from combat_lab.telemetry import CombatLabTelemetry
from game.simulation.battle_outcome import BattleOutcome


@dataclass(frozen=True)
class ABBattleOutcome:
    """Paired results from a baseline + variant battle run.

    Both battles were produced by the same `ABBattleRunner.run` call, so
    the role schema (the keys of `in_flight_by_role`, the `instance_id`s
    on `ShipOutcome`, etc.) is identical across the two — validators can
    compare like-for-like without remapping.
    """

    baseline_outcome: BattleOutcome
    baseline_telemetry: CombatLabTelemetry
    variant_outcome: BattleOutcome
    variant_telemetry: CombatLabTelemetry


__all__ = ["ABBattleOutcome"]
