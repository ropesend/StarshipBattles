"""
Weapons / targeting stat contributor — sensor + ECM scores.

In the current ship-stats pipeline the per-weapon damage/range numbers live
on the weapon abilities themselves and are read at fire time, not by the
stat calculator. What the calculator does compute is the targeting-side
metadata:

- ``ToHitDefenseModifier`` total (ECM defense score)
- ``ToHitAttackModifier`` total (sensor offense score)

Both go through ``ability_aggregator.get_ability_total`` with a fallback to
zero if no contributing component is active (the legacy code defended
against ``True``/``False`` payloads via ``isinstance(..., bool)`` and we
preserve that defensive cast).

PROJ-360 Phase 2 note on PROJ-359 contract reuse: the typed
``AttackRequest`` / ``AttackResolution`` contract introduced by PROJ-359
covers per-shot resolution, not stat aggregation. There is no field on the
typed contract that maps cleanly to ``ToHitDefenseModifier`` totals or
sensor scores — those are *inputs* to a future fire event, not outputs of
one. So Phase 2 leaves this module on the legacy aggregator. PROJ-360
Phase 3 may revisit if the registry pattern surfaces a natural seam.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from game.simulation.entities.ability_aggregator import get_ability_total

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def aggregate_targeting_scores(ship: "Ship", component_pool: List["Component"]) -> float:
    """Compute and store ECM defense + baseline-to-hit offense.

    Mirrors legacy ``_phase_sensor_defense_scores`` for the two ability-total
    fields. ``total_defense_score`` itself is composed elsewhere (size +
    maneuver + ecm); this contributor only owns the ECM term plus the sensor
    offensive baseline.

    Returns the ECM score so the caller can compose ``total_defense_score``
    without re-running ``get_ability_total``.
    """
    ecm_score = get_ability_total(component_pool, "ToHitDefenseModifier")
    if isinstance(ecm_score, bool):
        ecm_score = 0.0

    attack_mods = get_ability_total(component_pool, "ToHitAttackModifier")
    if isinstance(attack_mods, bool):
        attack_mods = 0.0

    ship.baseline_to_hit_offense = attack_mods
    return float(ecm_score)
